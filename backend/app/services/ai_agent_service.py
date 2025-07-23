# AI Agent Service - Core conversational intelligence
import logging
import json
import re
from typing import Dict, List, Optional, Any
from datetime import datetime
from app.services.groq_service import groq_service
from app.services.action_router_service import action_router_service
from app.services.database import db_service
from app.utils.helpers import generate_id

logger = logging.getLogger(__name__)

class AIAgentService:
    def __init__(self):
        self.action_router = action_router_service
        self.groq = groq_service
        self.db = db_service
    
    async def process_conversation(self, message: str, user_id: str, session_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main conversation processing method
        """
        try:
            # Step 1: Analyze user intent and extract parameters
            intent_analysis = await self.analyze_user_intent(message, context)
            
            # Step 2: Route to appropriate action
            action_result = await self.execute_user_intent(intent_analysis, user_id)
            
            # Step 3: Generate natural language response
            response = await self.generate_response(intent_analysis, action_result)
            
            # Step 4: Generate suggestions for next actions
            suggestions = await self.generate_suggestions(intent_analysis, action_result)
            
            return {
                "response": response,
                "action_taken": intent_analysis.get('action'),
                "data": action_result.get('data'),
                "suggestions": suggestions,
                "intent_analysis": intent_analysis
            }
            
        except Exception as e:
            logger.error(f"Error processing conversation: {e}")
            return {
                "response": f"I apologize, but I encountered an error while processing your request: {str(e)}. Please try rephrasing your request or ask for help.",
                "action_taken": "error",
                "data": None,
                "suggestions": ["Try asking: 'What can you help me with?'", "Say: 'Show me my campaigns'", "Ask: 'How do I create a new prospect?'"]
            }
    
    async def analyze_user_intent(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze user message to extract intent and parameters
        """
        try:
            # Create context-aware prompt for Groq
            system_prompt = """You are an AI assistant for an email marketing application. Analyze the user's message and extract:
1. Primary intent/action
2. Entity type (campaign, prospect, template, list, etc.)
3. Operation (create, read, update, delete, send, etc.)
4. Parameters and values
5. Confidence score

Available actions:
- Campaign management: create, list, show, send, update, delete, status
- Prospect management: create, list, show, update, delete, upload, search
- Template management: create, list, show, update, delete
- List management: create, list, show, update, delete, add_prospects, remove_prospects
- Email provider management: list, show, create, update, delete, test
- Analytics: show, dashboard, campaign_analytics
- Email processing: start, stop, status, test

Return JSON format:
{
    "action": "primary_action",
    "entity": "entity_type", 
    "operation": "operation_type",
    "parameters": {
        "name": "value",
        "id": "value"
    },
    "confidence": 0.9,
    "requires_clarification": false,
    "clarification_questions": []
}"""
            
            user_prompt = f"""
User message: "{message}"
Context: {json.dumps(context)}

Analyze this message and extract the intent and parameters.
"""
            
            # Get analysis from Groq
            analysis_text = await self.groq.generate_response_with_context(
                system_prompt, user_prompt, []
            )
            
            # Parse the JSON response
            try:
                analysis = json.loads(analysis_text)
            except json.JSONDecodeError:
                # Fallback to basic intent extraction
                analysis = await self.fallback_intent_extraction(message)
            
            logger.info(f"Intent analysis: {analysis}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing intent: {e}")
            return await self.fallback_intent_extraction(message)
    
    async def fallback_intent_extraction(self, message: str) -> Dict[str, Any]:
        """
        Enhanced fallback intent extraction using improved keyword matching and pattern recognition
        """
        message_lower = message.lower()
        
        # List keywords - HIGH PRIORITY for user's issue
        if any(word in message_lower for word in ['list', 'lists']):
            if any(word in message_lower for word in ['create', 'new', 'make', 'add']):
                # Extract list name
                list_params = self.extract_list_params(message)
                return {
                    "action": "create_list",
                    "entity": "list",
                    "operation": "create",
                    "parameters": list_params,
                    "confidence": 0.9,
                    "requires_clarification": False
                }
            elif any(word in message_lower for word in ['show', 'get', 'see', 'view', 'display']):
                return {
                    "action": "list_lists",
                    "entity": "list",
                    "operation": "list",
                    "parameters": {},
                    "confidence": 0.9,
                    "requires_clarification": False
                }
        
        # Prospect keywords - HIGH PRIORITY for user's issue
        elif any(word in message_lower for word in ['prospect', 'contact', 'lead', 'person']):
            if any(word in message_lower for word in ['add', 'create', 'new', 'make']):
                # Check if this is adding to a list
                if any(word in message_lower for word in ['to list', 'to the list', 'list']):
                    prospect_params = self.extract_prospect_params(message)
                    list_params = self.extract_list_params(message)
                    return {
                        "action": "add_prospects_to_list",
                        "entity": "list", 
                        "operation": "add_prospects",
                        "parameters": {**prospect_params, **list_params},
                        "confidence": 0.9,
                        "requires_clarification": False
                    }
                else:
                    return {
                        "action": "create_prospect",
                        "entity": "prospect",
                        "operation": "create", 
                        "parameters": self.extract_prospect_params(message),
                        "confidence": 0.8,
                        "requires_clarification": False
                    }
            elif any(word in message_lower for word in ['show', 'get', 'see', 'view', 'display']):
                return {
                    "action": "list_prospects",
                    "entity": "prospect",
                    "operation": "list",
                    "parameters": {},
                    "confidence": 0.9,
                    "requires_clarification": False
                }
        
        # Campaign keywords
        elif any(word in message_lower for word in ['campaign', 'send email', 'email campaign']):
            if any(word in message_lower for word in ['create', 'new', 'make']):
                return {
                    "action": "create_campaign",
                    "entity": "campaign",
                    "operation": "create",
                    "parameters": self.extract_campaign_params(message),
                    "confidence": 0.7,
                    "requires_clarification": False
                }
            elif any(word in message_lower for word in ['send', 'launch', 'start']):
                return {
                    "action": "send_campaign",
                    "entity": "campaign", 
                    "operation": "send",
                    "parameters": self.extract_campaign_params(message),
                    "confidence": 0.8,
                    "requires_clarification": False
                }
            elif any(word in message_lower for word in ['show', 'get', 'see', 'view', 'display']):
                return {
                    "action": "list_campaigns",
                    "entity": "campaign",
                    "operation": "list",
                    "parameters": {},
                    "confidence": 0.9,
                    "requires_clarification": False
                }
        
        # Template keywords
        elif any(word in message_lower for word in ['template', 'templates']):
            if any(word in message_lower for word in ['create', 'new', 'make']):
                return {
                    "action": "create_template",
                    "entity": "template",
                    "operation": "create",
                    "parameters": self.extract_template_params(message),
                    "confidence": 0.8,
                    "requires_clarification": False
                }
            elif any(word in message_lower for word in ['show', 'get', 'see', 'view', 'display']):
                return {
                    "action": "list_templates",
                    "entity": "template",
                    "operation": "list",
                    "parameters": {},
                    "confidence": 0.9,
                    "requires_clarification": False
                }
        
        # Analytics keywords
        elif any(word in message_lower for word in ['analytics', 'stats', 'performance', 'dashboard']):
            return {
                "action": "show_analytics",
                "entity": "analytics",
                "operation": "show",
                "parameters": {},
                "confidence": 0.9,
                "requires_clarification": False
            }
        
        # Show/Display commands without specific entity
        elif any(word in message_lower for word in ['show', 'get', 'see', 'view', 'display']):
            if 'campaign' in message_lower:
                return {
                    "action": "list_campaigns",
                    "entity": "campaign",
                    "operation": "list",
                    "parameters": {},
                    "confidence": 0.8,
                    "requires_clarification": False
                }
            elif any(word in message_lower for word in ['prospect', 'contact', 'lead']):
                return {
                    "action": "list_prospects",
                    "entity": "prospect",
                    "operation": "list",
                    "parameters": {},
                    "confidence": 0.8,
                    "requires_clarification": False
                }
            elif 'list' in message_lower:
                return {
                    "action": "list_lists",
                    "entity": "list",
                    "operation": "list",
                    "parameters": {},
                    "confidence": 0.8,
                    "requires_clarification": False
                }
        
        # Default fallback
        else:
            return {
                "action": "help",
                "entity": "general",
                "operation": "help",
                "parameters": {},
                "confidence": 0.3,
                "requires_clarification": True,
                "clarification_questions": ["What would you like to do? I can help with campaigns, prospects, templates, lists, or analytics."]
            }
    
    def extract_campaign_params(self, message: str) -> Dict[str, Any]:
        """Extract campaign parameters from message"""
        params = {}
        
        # Extract campaign name
        name_patterns = [
            r'campaign (?:named|called) "([^"]+)"',
            r'campaign (?:named|called) \'([^\']+)\'',
            r'(?:create|make) (?:a|the) ([A-Z][^,\.]+) campaign'
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                params['name'] = match.group(1).strip()
                break
        
        # Extract template
        template_patterns = [
            r'using (?:the )?([A-Z][^,\.]+) template',
            r'with (?:the )?([A-Z][^,\.]+) template'
        ]
        
        for pattern in template_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                params['template'] = match.group(1).strip()
                break
        
        # Extract list/audience
        list_patterns = [
            r'to (?:the )?([A-Z][^,\.]+) list',
            r'for (?:the )?([A-Z][^,\.]+) (?:list|group|audience)'
        ]
        
        for pattern in list_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                params['list'] = match.group(1).strip()
                break
        
        return params
    
    def extract_list_params(self, message: str) -> Dict[str, Any]:
        """Enhanced list parameter extraction from message"""
        params = {}
        
        # Extract list name patterns - CRITICAL for user's issue
        name_patterns = [
            r'list (?:called|named) ["\']([^"\']+)["\']',  # "list called 'Test Marketing List'"
            r'list (?:called|named) ([A-Z][A-Za-z\s]+)',  # "list called Test Marketing List" - fixed greedy matching
            r'create (?:a|the) ([A-Z][A-Za-z\s]+) list',  # "create a Test Marketing list"
            r'new list ["\']([^"\']+)["\']',  # "new list 'Test Marketing List'"
            r'new list (?:called|named) ([A-Z][A-Za-z\s]+)',  # "new list called Test Marketing List" - fixed greedy matching
            r'(?:create|make|add) (?:a )?(?:new )?list (?:called|named) ([A-Z][A-Za-z\s]+)',  # Fixed greedy matching
            r'(?:make|create) (?:a|the) (?:new )?list (?:named|called) ([A-Z][A-Za-z\s]+)',  # "make a new list named VIP Customers"
            r'(?:add|create) a list called ([A-Z][A-Za-z\s]+)',  # "add a list called Technology Companies"
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                extracted_name = match.group(1).strip()
                # Clean up trailing words that might be captured incorrectly
                extracted_name = re.sub(r'\s+(for|with|to|at|in|on).*$', '', extracted_name, flags=re.IGNORECASE)
                params['name'] = extracted_name
                break
        
        # Extract description if present
        desc_patterns = [
            r'description ["\']([^"\']+)["\']',
            r'for ([A-Z][A-Za-z\s]+) purposes?',
            r'to (?:track|manage|organize) ([A-Za-z\s]+)'
        ]
        
        for pattern in desc_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                params['description'] = match.group(1).strip()
                break
        
        # Extract color if mentioned
        colors = ['red', 'blue', 'green', 'yellow', 'purple', 'orange', 'pink', 'gray', 'black']
        for color in colors:
            if color in message.lower():
                params['color'] = f'#{color}'
                break
        
        # If no name found, use generic name
        if 'name' not in params:
            params['name'] = f"New List {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        return params
    
    def extract_template_params(self, message: str) -> Dict[str, Any]:
        """Extract template parameters from message"""
        params = {}
        
        # Extract template name
        name_patterns = [
            r'template (?:called|named) ["\']([^"\']+)["\']',
            r'template (?:called|named) ([A-Z][A-Za-z\s]+?)(?:\s|$|\.)',
            r'create (?:a|the) ([A-Z][A-Za-z\s]+?) template',
            r'new template ["\']([^"\']+)["\']'
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                params['name'] = match.group(1).strip()
                break
        
        # Extract template type
        if any(word in message.lower() for word in ['welcome', 'greeting', 'initial']):
            params['type'] = 'initial'
        elif any(word in message.lower() for word in ['follow', 'followup', 'follow-up']):
            params['type'] = 'follow_up'
        elif any(word in message.lower() for word in ['auto', 'automatic', 'response']):
            params['type'] = 'auto_response'
        else:
            params['type'] = 'initial'
        
        # Extract subject if present
        subject_patterns = [
            r'subject ["\']([^"\']+)["\']',
            r'with subject ([A-Za-z\s]+?)(?:\s|$|\.)'
        ]
        
        for pattern in subject_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                params['subject'] = match.group(1).strip()
                break
        
        return params
    
    def extract_prospect_params(self, message: str) -> Dict[str, Any]:
        """Enhanced prospect parameter extraction from message - CRITICAL for user's issue"""
        params = {}
        
        # Enhanced name extraction patterns - FIXED for complex name formats
        name_patterns = [
            r'(?:prospect|contact|person|lead) (?:named|called) ([A-Z][a-z]+ [A-Z][a-z]+)',  # "prospect named John Smith"
            r'add (?:a )?(?:prospect|contact|person|lead)? (?:named|called)? ([A-Z][a-z]+ [A-Z][a-z]+)',  # "add John Smith" or "add a prospect John Smith"
            r'create (?:a )?(?:prospect|contact) (?:named|called)? ([A-Z][a-z]+ [A-Z][a-z]+)',  # "create prospect John Smith"
            r'new (?:prospect|contact) (?:named|called)? ([A-Z][a-z]+ [A-Z][a-z]+)',  # "new prospect John Smith"
            r'([A-Z][a-z]+ [A-Z][a-z]+) (?:from|at|to|with|of)',  # "John Smith from TechCorp"
            r'(?:add|create) (?:a )?(?:prospect|contact)?(?:\s+named|\s+called)?\s+([A-Z][a-z]+ [A-Z][a-z]+)',  # More flexible patterns
            r'([A-Z][a-z]+ [A-Z][a-z]+\d*) (?:from|at|to|with)',  # Handle names with numbers from test
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                full_name = match.group(1).strip()
                name_parts = full_name.split()
                if len(name_parts) >= 2:
                    params['first_name'] = name_parts[0]
                    params['last_name'] = ' '.join(name_parts[1:])
                break
        
        # Enhanced company extraction patterns - FIXED for complex company names
        company_patterns = [
            r'from ([A-Z][A-Za-z\s&\.\-0-9]+?)(?:\s+(?:company|corp|inc|ltd|llc))?(?:\s|$|\.|,|with|email)',  # "from TechCorp" or "from DataScience AI"
            r'at ([A-Z][A-Za-z\s&\.\-0-9]+?)(?:\s+(?:company|corp|inc|ltd|llc))?(?:\s|$|\.|,)',  # "at DataScience AI"
            r'(?:works )?(?:with|for) ([A-Z][A-Za-z\s&\.\-0-9]+?)(?:\s+(?:company|corp|inc|ltd|llc))?(?:\s|$|\.|,)',  # "works with TechCorp"
            r'company (?:called|named)? ([A-Z][A-Za-z\s&\.\-0-9]+?)(?:\s|$|\.|,)',  # "company TechCorp"
            r'(?:of|with) ([A-Z][A-Za-z\s&\.\-0-9]+) (?:company|corp|inc|ltd)',  # "of TechCorp company"
            r'([A-Z][A-Za-z\s&\.\-0-9]+?)(?:\s+(?:Inc|Corp|LLC|Ltd|Company))(?:\s|$|\.|,)',  # "DataScience AI Inc"
        ]
        
        for pattern in company_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                company_name = match.group(1).strip()
                # Clean up common suffixes that might be captured
                company_name = re.sub(r'\s+(company|corp|inc|ltd|llc)$', '', company_name, flags=re.IGNORECASE)
                # Remove trailing words that might be captured incorrectly  
                company_name = re.sub(r'\s+(email|with|and|the|of|for|at)$', '', company_name, flags=re.IGNORECASE)
                params['company'] = company_name.strip()
                break
        
        # Extract email if present
        email_patterns = [
            r'(\w+@\w+\.\w+)',  # Basic email pattern
            r'email (\w+@\w+\.\w+)',  # "email john@techcorp.com"
        ]
        
        for pattern in email_patterns:
            match = re.search(pattern, message)
            if match:
                params['email'] = match.group(1)
                break
        
        # Extract job title if present
        title_patterns = [
            r'(?:title|position|role) ([A-Za-z\s]+?)(?:\s|$|\.|,)',
            r'(?:as|is) (?:a |an )?([A-Za-z\s]+?)(?:\s|$|\.|,|at)',
            r'([A-Za-z\s]+?) at [A-Z]',  # "Marketing Manager at TechCorp"
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                # Filter out common words that aren't job titles
                if not any(word in title.lower() for word in ['from', 'with', 'the', 'and', 'company']):
                    params['job_title'] = title
                    break
        
        # Extract phone if present
        phone_patterns = [
            r'phone (\+?[\d\s\-\(\)]+)',
            r'(\+?[\d\s\-\(\)]{10,})'  # Basic phone pattern
        ]
        
        for pattern in phone_patterns:
            match = re.search(pattern, message)
            if match:
                params['phone'] = match.group(1).strip()
                break
        
        # Generate email if not provided but we have name and company
        if 'email' not in params and 'first_name' in params and 'company' in params:
            first_name = params['first_name'].lower()
            company = params['company'].lower().replace(' ', '').replace('&', '').replace('.', '')
            params['email'] = f"{first_name}@{company}.com"
        
        return params
    
    async def execute_user_intent(self, intent_analysis: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        Execute the user's intent using the action router
        """
        try:
            action = intent_analysis.get('action')
            entity = intent_analysis.get('entity')
            operation = intent_analysis.get('operation')
            parameters = intent_analysis.get('parameters', {})
            
            # Route to appropriate action
            result = await self.action_router.execute_action(
                action=action,
                entity=entity,
                operation=operation,
                parameters=parameters,
                user_id=user_id
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing intent: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": None
            }
    
    async def generate_response(self, intent_analysis: Dict[str, Any], action_result: Dict[str, Any]) -> str:
        """
        Generate natural language response based on intent and action result
        """
        try:
            action = intent_analysis.get('action')
            success = action_result.get('success', False)
            data = action_result.get('data')
            error = action_result.get('error')
            
            if not success:
                return f"I wasn't able to complete that action. {error or 'Please try again or ask for help.'}"
            
            # Generate contextual responses based on action type
            if action == 'list_campaigns':
                campaigns = data or []
                if not campaigns:
                    return "You don't have any campaigns yet. Would you like to create one?"
                return f"Here are your campaigns:\n" + "\n".join([
                    f"• {c.get('name', 'Unnamed')} - Status: {c.get('status', 'unknown')}"
                    for c in campaigns[:5]
                ]) + (f"\n...and {len(campaigns) - 5} more" if len(campaigns) > 5 else "")
            
            elif action == 'create_campaign':
                campaign_name = data.get('name', 'New Campaign') if data else 'New Campaign'
                return f"Great! I've created the '{campaign_name}' campaign for you. Would you like to send it now or make any modifications first?"
            
            elif action == 'send_campaign':
                sent_count = data.get('total_sent', 0) if data else 0
                return f"Perfect! Your campaign has been sent successfully to {sent_count} prospects. I'll monitor the results for you."
            
            elif action == 'list_prospects':
                prospects = data or []
                if not prospects:
                    return "Your prospect database is empty. Would you like to add some prospects or upload a CSV file?"
                return f"You have {len(prospects)} prospects in your database. Here are the most recent ones:\n" + "\n".join([
                    f"• {p.get('first_name', '')} {p.get('last_name', '')} - {p.get('company', 'No company')}"
                    for p in prospects[:3]
                ])
            
            elif action == 'create_prospect':
                prospect_name = f"{data.get('first_name', '')} {data.get('last_name', '')}" if data else 'New prospect'
                return f"Excellent! I've added {prospect_name.strip()} to your prospect database. They're ready to be added to campaigns."
            
            elif action == 'show_analytics':
                if data:
                    return f"Here's your performance overview:\n• Total Campaigns: {data.get('total_campaigns', 0)}\n• Total Prospects: {data.get('total_prospects', 0)}\n• Emails Sent: {data.get('total_emails_sent', 0)}\n• Average Open Rate: {data.get('average_open_rate', 0)}%"
                return "Here are your current analytics and performance metrics."
            
            elif action == 'help':
                return "I'm here to help you manage your email marketing! I can help you with:\n• Creating and sending campaigns\n• Managing prospects and templates\n• Viewing analytics and performance\n• Processing emails automatically\n\nJust tell me what you'd like to do in natural language!"
            
            else:
                return f"I've completed the {action.replace('_', ' ')} action successfully!"
                
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I've processed your request. Is there anything else I can help you with?"
    
    async def generate_suggestions(self, intent_analysis: Dict[str, Any], action_result: Dict[str, Any]) -> List[str]:
        """
        Generate contextual suggestions for next actions
        """
        try:
            action = intent_analysis.get('action')
            success = action_result.get('success', False)
            
            if not success:
                return [
                    "Try asking: 'What can you help me with?'",
                    "Say: 'Show me my campaigns'",
                    "Ask: 'How many prospects do I have?'"
                ]
            
            # Context-aware suggestions
            if action == 'list_campaigns':
                return [
                    "Create a new campaign",
                    "Send an existing campaign",
                    "Show campaign analytics",
                    "View my templates"
                ]
            
            elif action == 'create_campaign':
                return [
                    "Send this campaign now",
                    "Preview the campaign", 
                    "Add more prospects to the list",
                    "Create another campaign"
                ]
            
            elif action == 'list_prospects':
                return [
                    "Add a new prospect",
                    "Upload prospects from CSV",
                    "Create a new list",
                    "Start a campaign with these prospects"
                ]
            
            elif action == 'create_prospect':
                return [
                    "Add this prospect to a list",
                    "Create a campaign for this prospect",
                    "Add another prospect",
                    "Upload more prospects from CSV"
                ]
            
            elif action == 'show_analytics':
                return [
                    "Show campaign-specific analytics",
                    "View prospect engagement",
                    "Check email processing status",
                    "Export analytics report"
                ]
            
            else:
                return [
                    "Show me my dashboard",
                    "What else can I do?",
                    "Create a new campaign",
                    "View my analytics"
                ]
                
        except Exception as e:
            logger.error(f"Error generating suggestions: {e}")
            return ["What would you like to do next?"]
    
    async def get_agent_capabilities(self) -> Dict[str, Any]:
        """
        Return comprehensive agent capabilities
        """
        return {
            "campaign_management": {
                "actions": ["create", "list", "show", "send", "update", "delete", "status"],
                "description": "Full campaign lifecycle management"
            },
            "prospect_management": {
                "actions": ["create", "list", "show", "update", "delete", "upload", "search"],
                "description": "Complete prospect database management"
            },
            "template_management": {
                "actions": ["create", "list", "show", "update", "delete"],
                "description": "Email template creation and management"
            },
            "list_management": {
                "actions": ["create", "list", "show", "update", "delete", "add_prospects", "remove_prospects"],
                "description": "Prospect list organization"
            },
            "email_providers": {
                "actions": ["list", "show", "create", "update", "delete", "test"],
                "description": "Email provider configuration"
            },
            "analytics": {
                "actions": ["dashboard", "campaign_analytics", "export"],
                "description": "Performance analytics and reporting"
            },
            "email_processing": {
                "actions": ["start", "stop", "status", "test"],
                "description": "Automated email processing and AI responses"
            },
            "conversation": {
                "actions": ["help", "capabilities", "examples"],
                "description": "Conversational assistance and guidance"
            }
        }

# Global instance
ai_agent_service = AIAgentService()