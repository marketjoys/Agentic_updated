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
        Main conversation processing method with industry data access
        """
        try:
            # Load industry data for context if needed
            if any(keyword in message.lower() for keyword in ['industry', 'sector', 'field', 'business type']):
                context['available_industries'] = await self.get_available_industries()
            
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
            try:
                fallback_result = await self.fallback_intent_extraction(message)
                logger.info(f"Fallback intent analysis: {fallback_result}")
                return fallback_result
            except Exception as fallback_error:
                logger.error(f"Error in fallback intent extraction: {fallback_error}")
                return {
                    "action": "help",
                    "entity": "general",
                    "operation": "help",
                    "parameters": {},
                    "confidence": 0.3,
                    "requires_clarification": True,
                    "clarification_questions": ["I'm having trouble understanding your request. What would you like to do?"]
                }
    
    async def fallback_intent_extraction(self, message: str) -> Dict[str, Any]:
        """
        Enhanced fallback intent extraction using improved keyword matching and pattern recognition
        """
        message_lower = message.lower()
        
        # Check for specific "add to list" patterns first - HIGH PRIORITY
        if any(phrase in message_lower for phrase in ['add to list', 'add to the list', 'to list', 'to the list']):
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
        
        # Campaign keywords - MOVED TO HIGH PRIORITY to prevent misinterpretation as list creation
        elif any(word in message_lower for word in ['campaign', 'send email', 'email campaign']):
            if any(word in message_lower for word in ['create', 'new', 'make']):
                return {
                    "action": "create_campaign",
                    "entity": "campaign",
                    "operation": "create",
                    "parameters": self.extract_campaign_params(message),
                    "confidence": 0.9,  # Increased confidence
                    "requires_clarification": False
                }
            elif any(word in message_lower for word in ['send', 'launch', 'start']):
                campaign_params = self.extract_campaign_params(message)
                return {
                    "action": "send_campaign",
                    "entity": "campaign", 
                    "operation": "send",
                    "parameters": campaign_params,
                    "confidence": 0.9,  # Increased confidence for better matching
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
            elif any(word in message_lower for word in ['schedule', 'plan', 'set time', 'later']):
                campaign_params = self.extract_campaign_params(message)
                campaign_params.update(self.extract_scheduling_params(message))
                return {
                    "action": "schedule_campaign",
                    "entity": "campaign",
                    "operation": "schedule",
                    "parameters": campaign_params,
                    "confidence": 0.9,
                    "requires_clarification": False
                }
        
        # Email Processing & Monitoring - NEW HIGH PRIORITY
        elif any(phrase in message_lower for phrase in ['email monitoring', 'start monitoring', 'email processing', 'follow-up system', 'auto response', 'monitoring system']):
            if any(word in message_lower for word in ['start', 'begin', 'activate', 'enable', 'turn on']):
                return {
                    "action": "start_email_processing",
                    "entity": "email_processing",
                    "operation": "start",
                    "parameters": {},
                    "confidence": 0.9,
                    "requires_clarification": False
                }
            elif any(word in message_lower for word in ['stop', 'end', 'deactivate', 'disable', 'turn off']):
                return {
                    "action": "stop_email_processing",
                    "entity": "email_processing",
                    "operation": "stop",
                    "parameters": {},
                    "confidence": 0.9,
                    "requires_clarification": False
                }
            elif any(word in message_lower for word in ['status', 'check', 'show', 'view']):
                return {
                    "action": "email_processing_status",
                    "entity": "email_processing",
                    "operation": "status",
                    "parameters": {},
                    "confidence": 0.9,
                    "requires_clarification": False
                }
        
        # Search/Find patterns - HIGH PRIORITY for AI prospecting
        elif any(word in message_lower for word in ['search', 'find', 'look for', 'locate']):
            if any(word in message_lower for word in ['prospect', 'prospects', 'contact', 'contacts', 'lead', 'leads']):
                search_params = {}
                
                # Extract search criteria
                if 'named' in message_lower or 'called' in message_lower:
                    name_patterns = [
                        r'(?:named|called) ([A-Z][A-Za-z\s]+)',
                        r'find (?:prospects? )?(?:named |called )?([A-Z][A-Za-z\s]+)'
                    ]
                    for pattern in name_patterns:
                        match = re.search(pattern, message, re.IGNORECASE)
                        if match:
                            search_params['search_term'] = match.group(1).strip()
                            break
                
                # Extract company search
                if 'from' in message_lower or 'at' in message_lower:
                    company_patterns = [
                        r'(?:from|at) ([A-Z][A-Za-z\s&\.]+)',
                        r'find prospects from ([A-Z][A-Za-z\s&\.]+)'
                    ]
                    for pattern in company_patterns:
                        match = re.search(pattern, message, re.IGNORECASE)
                        if match:
                            search_params['company'] = match.group(1).strip()
                            break
                
                # Extract industry search
                if 'industry' in message_lower or 'in technology' in message_lower or 'in finance' in message_lower:
                    industry_patterns = [
                        r'in (?:the )?([A-Za-z\s]+) industry',
                        r'(?:in|from) ([A-Za-z]+) (?:sector|field)',
                        r'in (technology|finance|healthcare|marketing|sales|consulting|software|retail)'
                    ]
                    for pattern in industry_patterns:
                        match = re.search(pattern, message, re.IGNORECASE)
                        if match:
                            search_params['industry'] = match.group(1).strip()
                            break
                
                return {
                    "action": "search_prospects",
                    "entity": "prospect",
                    "operation": "search",
                    "parameters": search_params,
                    "confidence": 0.9,
                    "requires_clarification": False
                }
        
        # Prospect keywords - HIGH PRIORITY for user's issue
        elif any(word in message_lower for word in ['prospect', 'contact', 'lead', 'person']):
            if any(word in message_lower for word in ['add', 'create', 'new', 'make']):
                prospect_params = self.extract_prospect_params(message)
                return {
                    "action": "create_prospect",
                    "entity": "prospect",
                    "operation": "create", 
                    "parameters": prospect_params,
                    "confidence": 0.8,
                    "requires_clarification": len(prospect_params) < 2  # Require clarification if we have less than 2 parameters
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
        
        # List keywords - MOVED AFTER CAMPAIGN to prevent conflicts
        elif any(word in message_lower for word in ['list', 'lists']):
            # Exclude campaign-related phrases that might contain "list"
            if not any(phrase in message_lower for phrase in ['campaign', 'email campaign']):
                if any(word in message_lower for word in ['create', 'new', 'make', 'add']) and not any(phrase in message_lower for phrase in ['add to', 'to list', 'to the']):
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
        
        # AI Prospecting/Suggestions - NEW FUNCTIONALITY
        elif any(phrase in message_lower for phrase in ['suggest prospects', 'recommend prospects', 'ai prospects', 'find similar']):
            return {
                "action": "ai_suggest_prospects",
                "entity": "prospect",
                "operation": "ai_suggest",
                "parameters": {"criteria": message},
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
        """Enhanced campaign parameter extraction from message"""
        params = {}
        
        # Extract campaign name - IMPROVED patterns for better extraction
        name_patterns = [
            r'campaign (?:named|called) ["\']([^"\']+)["\']',  # "campaign named 'Summer Sale'"
            r'campaign (?:named|called) ([A-Z][A-Za-z\s]+?)(?:\s+using|\s+with|\s+for|$)',  # "campaign named Summer Sale using..."
            r'(?:create|make|new) (?:a |the )?campaign (?:named|called) ([A-Z][A-Za-z\s]+?)(?:\s+using|\s+with|\s+for|$)',  # "create a campaign named Summer Sale"
            r'(?:create|make|new) (?:a |the )?([A-Z][A-Za-z\s]+?) campaign',  # "create a Summer Sale campaign"
            r'(?:send|launch|start) (?:the |campaign )?([A-Z][A-Za-z\s]+?)(?:\s+now|\s+campaign|\s*$)',  # "send the Test Campaign"
            r'(?:send|launch|start) ([A-Z][A-Za-z\s]+?)(?:\s+now|\s*$)',  # "send Test Campaign now"
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                extracted_name = match.group(1).strip()
                # Clean up extracted name
                extracted_name = re.sub(r'\s+(using|with|for|to|at|in|on|now).*$', '', extracted_name, flags=re.IGNORECASE)
                params['name'] = extracted_name
                break
        
        # Extract campaign ID if present
        id_patterns = [
            r'campaign (?:id|ID) ([a-f0-9\-]{36})',  # "campaign id 6ab1f315-88df-4e9f-a380-a789060b2531"
            r'(?:campaign|id|ID)\s+([a-f0-9\-]{36})',  # "send campaign 6ab1f315-88df-4e9f-a380-a789060b2531"
        ]
        
        for pattern in id_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                params['id'] = match.group(1).strip()
                break
        
        # Extract template - IMPROVED patterns
        template_patterns = [
            r'using (?:the )?([A-Z][A-Za-z\s]+?) template',  # "using Welcome template"
            r'with (?:the )?([A-Z][A-Za-z\s]+?) template',   # "with Welcome template"
            r'template (?:named|called) ([A-Z][A-Za-z\s]+?)(?:\s+for|\s+to|$)',  # "template named Welcome"
        ]
        
        for pattern in template_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                template_name = match.group(1).strip()
                # Clean up template name
                template_name = re.sub(r'\s+(for|to|with|and|the|of|at|in|on).*$', '', template_name, flags=re.IGNORECASE)
                params['template'] = template_name
                break
        
        # Extract list/audience - IMPROVED patterns
        list_patterns = [
            r'(?:to|for) (?:the )?([A-Z][A-Za-z\s]+?) (?:list|customers|prospects|audience|group)',  # "for VIP Customers list"
            r'(?:to|for) (?:the )?([A-Z][A-Za-z\s]+?)(?:\s+list|\s|$)',  # "to VIP Customers"
            r'send (?:to|for) (?:the )?([A-Z][A-Za-z\s]+)',  # "send to VIP Customers"
        ]
        
        for pattern in list_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                list_name = match.group(1).strip()
                # Clean up list name
                list_name = re.sub(r'\s+(with|and|the|of|at|in|on|using).*$', '', list_name, flags=re.IGNORECASE)
                params['list'] = list_name
                break
        
        # Extract email provider if mentioned
        provider_patterns = [
            r'(?:via|using|through) (?:the )?([A-Z][A-Za-z\s]+?) (?:provider|email)',  # "via Gmail provider"
            r'email provider ([A-Z][A-Za-z\s]+)',  # "email provider Gmail"
        ]
        
        for pattern in provider_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                provider_name = match.group(1).strip()
                params['email_provider'] = provider_name
                break
        
        # Extract max emails if mentioned
        max_email_patterns = [
            r'(?:max|maximum|up to|limit) (\d+) emails?',  # "max 500 emails"
            r'send (\d+) emails?',  # "send 1000 emails"
        ]
        
        for pattern in max_email_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                params['max_emails'] = int(match.group(1))
                break
        
        return params
    
    def extract_scheduling_params(self, message: str) -> Dict[str, Any]:
        """Extract scheduling parameters from message"""
        params = {}
        
        # Extract time/date patterns
        time_patterns = [
            r'(?:at|time) (\d{1,2}:\d{2}(?:\s*[AP]M)?)',  # "at 2:30PM"
            r'(?:at|time) (\d{1,2}\s*[AP]M)',  # "at 2PM"
        ]
        
        date_patterns = [
            r'(?:on|date) (\w+day)',  # "on Monday"
            r'(?:on|date) (\w+\s+\d{1,2})',  # "on March 15"
            r'(tomorrow|next week|next month)',  # relative dates - capture the word
            r'(?:in) (\d+) (?:hours?|days?|weeks?)',  # "in 2 hours"
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                params['send_time'] = match.group(1).strip()
                break
        
        for pattern in date_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                params['send_date'] = match.group(0).strip()
                break
        
        # Extract follow-up settings
        if any(word in message.lower() for word in ['follow up', 'follow-up', 'followup']):
            params['enable_follow_up'] = True
            
            # Extract follow-up intervals
            interval_patterns = [
                r'(?:after|in) (\d+) (?:and|,)?\s*(\d+)? days?',  # "after 5 and 10 days"
                r'(\d+),?\s*(\d+),?\s*(\d+) days?',  # "3, 7, 14 days"
                r'(?:after|in) (\d+) days?',  # "after 3 days" - single interval
            ]
            
            for pattern in interval_patterns:
                match = re.search(pattern, message, re.IGNORECASE)
                if match:
                    if len(match.groups()) == 1:
                        params['follow_up_intervals'] = [int(match.group(1))]
                    else:
                        intervals = [int(g) for g in match.groups() if g]
                        params['follow_up_intervals'] = intervals
                    break
        
        return params
    
    def extract_list_params(self, message: str) -> Dict[str, Any]:
        """Enhanced list parameter extraction from message"""
        params = {}
        
        # Extract list name patterns - CRITICAL for user's issue
        name_patterns = [
            # Patterns for "add to list" operations
            r'to (?:the )?([A-Z][A-Za-z\s]+?) list',  # "to VIP Customers list"
            r'to (?:the )?([A-Z][A-Za-z\s]+?)(?:\s|$)',  # "to VIP Customers"
            # Patterns for list creation
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
        """Enhanced prospect parameter extraction from message - FIXED for complex name formats"""
        params = {}
        
        # Enhanced name extraction patterns - COMPREHENSIVE for all name formats
        name_patterns = [
            # Basic name patterns - FIXED to not overlap with email/company
            r'(?:prospect|contact|person|lead) (?:named|called) ([A-Z][a-z]+(?:\s+[A-Z][a-z\']+)*?)(?:\s+from|\s+at|\s+with|\s+email|$)',  # "prospect named John Smith from..."
            r'(?:add|create) (?:a )?(?:prospect|contact|person|lead)? (?:named|called)? ([A-Z][a-z]+(?:\s+[A-Z][a-z\']+)*?)(?:\s+from|\s+at|\s+with|\s+email|$)',  # "add John Smith from..."
            r'new (?:prospect|contact) (?:named|called)? ([A-Z][a-z]+(?:\s+[A-Z][a-z\']+)*?)(?:\s+from|\s+at|\s+with|\s+email|$)',  # "new prospect John Smith from..."
            
            # Context-based name extraction (before company) - IMPROVED
            r'^(?:add|create)(?:\s+a)?(?:\s+prospect)?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z\']+)*?)\s+(?:from|at|with|of|works?\s+(?:at|for|with))',  # "add John Smith from TechCorp"
        ]
        
        extracted_name = None
        for pattern in name_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                extracted_name = match.group(1).strip()
                # Clean up any trailing artifacts
                extracted_name = re.sub(r'\d+$', '', extracted_name).strip()
                break
        
        if extracted_name:
            name_parts = extracted_name.split()
            if len(name_parts) >= 1:
                params['first_name'] = name_parts[0]
                if len(name_parts) >= 2:
                    params['last_name'] = ' '.join(name_parts[1:])
                else:
                    # If only one name part, use it as first name and generate a last name
                    params['last_name'] = 'Unknown'
        
        # Enhanced company extraction patterns - FIXED to prevent overlap with email
        company_patterns = [
            # Standard patterns with common company suffixes - IMPROVED
            r'from ([A-Z][A-Za-z\s&\.\-0-9\']+?(?:\s+(?:Inc|Corp|LLC|Ltd|Company|Solutions|Technologies|Systems|Group|AI|Software|Services|Consulting|International|Global|Enterprises))?)(?:\s+with\s+email|\s+email|\s|$)',
            r'at ([A-Z][A-Za-z\s&\.\-0-9\']+?(?:\s+(?:Inc|Corp|LLC|Ltd|Company|Solutions|Technologies|Systems|Group|AI|Software|Services|Consulting|International|Global|Enterprises))?)(?:\s+with\s+email|\s+email|\s|$)',
            
            # Work-related patterns - IMPROVED
            r'(?:works?|employed) (?:at|for|with) ([A-Z][A-Za-z\s&\.\-0-9\']+?)(?:\s+with\s+email|\s+email|\s|$)',
            
            # Explicit company mentions - IMPROVED  
            r'company (?:called|named)? ([A-Z][A-Za-z\s&\.\-0-9\']+?)(?:\s+with\s+email|\s+email|\s|$)',
        ]
        
        for pattern in company_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                company_name = match.group(1).strip()
                # Clean up trailing context words and punctuation
                company_name = re.sub(r'[,\.]+$', '', company_name).strip()
                if company_name and len(company_name) > 1:  # Ensure it's not just a single character
                    params['company'] = company_name
                    break
        
        # Enhanced email extraction - FIXED pattern
        email_patterns = [
            r'with\s+email\s+(\w+(?:[\.\-_]\w+)*@\w+(?:[\.\-]\w+)*\.\w+)',  # "with email john@techcorp.com"
            r'email\s+(?:is\s+|address\s+is\s+)?(\w+(?:[\.\-_]\w+)*@\w+(?:[\.\-]\w+)*\.\w+)',  # "email is john@techcorp.com"
            r'(\w+(?:[\.\-_]\w+)*@\w+(?:[\.\-]\w+)*\.\w+)',  # Direct email pattern
        ]
        
        for pattern in email_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                params['email'] = match.group(1).lower()
                break
        
        # Extract job title if present - IMPROVED
        title_patterns = [
            r'(?:title|position|role|job)\s+(?:is\s+)?([A-Za-z\s]+?)(?:\s+at|\s+with|\s+from|\s|$|\.|,)',
            r'(?:as|is)\s+(?:a\s+|an\s+)?([A-Za-z\s]+?)(?:\s+at|\s+with|\s+from|\s|$|\.|,)',
            r'([A-Za-z\s]+?)\s+at\s+[A-Z]',  # "Marketing Manager at TechCorp"
            r'(?:works?\s+as|employed\s+as)\s+(?:a\s+|an\s+)?([A-Za-z\s]+?)(?:\s+at|\s+with|\s+from|\s|$)',
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                # Filter out common words that aren't job titles
                if not any(word in title.lower() for word in ['from', 'with', 'the', 'and', 'company', 'prospect', 'contact', 'person', 'email']):
                    params['job_title'] = title
                    break
        
        # Extract phone if present - UNCHANGED (working)
        phone_patterns = [
            r'phone\s+(?:number\s+)?(?:is\s+)?(\+?[\d\s\-\(\)\.]+)',
            r'(?:call|contact)\s+(?:at\s+)?(\+?[\d\s\-\(\)\.]{10,})',
            r'(\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4})'  # US phone pattern
        ]
        
        for pattern in phone_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                phone = re.sub(r'[^\d\+\-\(\)\s\.]', '', match.group(1)).strip()
                if len(phone.replace('-', '').replace('(', '').replace(')', '').replace(' ', '').replace('.', '')) >= 10:
                    params['phone'] = phone
                    break
        
        # Enhanced email generation if not provided but we have name and company - IMPROVED
        if 'email' not in params and 'first_name' in params:
            first_name = params['first_name'].lower()
            
            if 'company' in params:
                # Generate email based on company
                company = params['company'].lower()
                # Clean up company name for email domain
                company_clean = re.sub(r'[^a-z0-9]', '', company.replace(' ', '').replace('&', 'and'))
                # Remove common company suffixes for cleaner domain
                company_clean = re.sub(r'(inc|corp|llc|ltd|company|solutions|technologies|systems|group|software|services)$', '', company_clean)
                
                if company_clean and len(company_clean) > 1:
                    params['email'] = f"{first_name}@{company_clean}.com"
                else:
                    params['email'] = f"{first_name}@company.com"
            else:
                # Generate generic email if no company
                params['email'] = f"{first_name}@example.com"
        
        # Extract industry if mentioned - UNCHANGED (working)
        industry_patterns = [
            r'(?:in|from)\s+(?:the\s+)?([A-Za-z\s]+?)\s+(?:industry|sector|field)',
            r'(?:works?\s+in|specializes?\s+in)\s+([A-Za-z\s]+)',
        ]
        
        for pattern in industry_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                industry = match.group(1).strip()
                if not any(word in industry.lower() for word in ['prospect', 'contact', 'person']):
                    params['industry'] = industry.title()
                    break
        
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
            requires_clarification = action_result.get('requires_clarification', False)
            
            # Handle clarification requirements with follow-up questions
            if requires_clarification and not success:
                follow_up_questions = action_result.get('data', {}).get('follow_up_questions', [])
                if follow_up_questions:
                    return f"{error}\n\nTo help you complete this, please let me know:\n" + "\n".join([f"• {q}" for q in follow_up_questions])
                else:
                    return f"{error} Could you provide more details?"
            
            if not success:
                suggestion = action_result.get('suggestion', '')
                return f"I wasn't able to complete that action. {error or 'Please try again or ask for help.'} {suggestion}"
            
            # Generate contextual responses based on action type
            if action == 'list_campaigns':
                campaigns = data or []
                if not campaigns:
                    return "You don't have any campaigns yet. Would you like to create one? Just say 'Create a new campaign' and I'll help you set it up!"
                return f"Here are your campaigns:\n" + "\n".join([
                    f"• {c.get('name', 'Unnamed')} - Status: {c.get('status', 'unknown')}"
                    for c in campaigns[:5]
                ]) + (f"\n...and {len(campaigns) - 5} more" if len(campaigns) > 5 else "")
            
            elif action == 'create_campaign':
                campaign_name = data.get('name', 'New Campaign') if data else 'New Campaign'
                return f"Great! I've created the '{campaign_name}' campaign for you. Would you like to send it now or make any modifications first?"
            
            elif action == 'send_campaign':
                sent_count = data.get('total_sent', 0) if data else 0
                follow_up_enabled = data.get('follow_up_enabled', False) if data else False
                follow_up_intervals = data.get('follow_up_intervals', []) if data else []
                
                response = f"Perfect! Your campaign has been sent successfully to {sent_count} prospects."
                
                if follow_up_enabled and follow_up_intervals:
                    interval_text = ", ".join([f"{i} days" for i in follow_up_intervals])
                    response += f" I've also set up automatic follow-up emails to be sent after {interval_text}."
                    response += " I'll monitor responses and stop follow-ups automatically when prospects reply."
                
                return response
            
            elif action == 'schedule_campaign':
                if action_result.get('requires_confirmation') and data:
                    details = data.get('confirmation_details', {})
                    campaign_name = details.get('campaign_name', data.get('name', 'your campaign'))
                    send_time = details.get('send_time', data.get('send_time', 'Not specified'))
                    send_date = details.get('send_date', data.get('send_date', 'Not specified'))
                    follow_up_enabled = details.get('follow_up_enabled', data.get('enable_follow_up', False))
                    follow_up_intervals = details.get('follow_up_intervals', data.get('follow_up_intervals', []))
                    
                    response = f"I've scheduled '{campaign_name}' for you! Here are the details:\n"
                    response += f"• Send Date: {send_date}\n"
                    response += f"• Send Time: {send_time}\n"
                    response += f"• Follow-up Enabled: {'Yes' if follow_up_enabled else 'No'}\n"
                    
                    if follow_up_enabled and follow_up_intervals:
                        interval_text = ", ".join([f"{i} days" for i in follow_up_intervals])
                        response += f"• Follow-up Schedule: {interval_text} after initial send\n"
                    
                    response += "\nThe campaign will be automatically sent at the scheduled time, and I'll monitor responses to manage follow-ups intelligently."
                    return response
                else:
                    campaign_name = data.get('name', 'your campaign') if data else 'your campaign'
                    return f"Great! I've scheduled '{campaign_name}' and it will be sent automatically at the specified time with intelligent follow-up management."
            
            elif action == 'list_prospects':
                prospects = data or []
                if not prospects:
                    return "Your prospect database is empty. Would you like to add some prospects or upload a CSV file? Just say 'Add a prospect named [Name] from [Company]' or 'Upload prospects from CSV'."
                return f"You have {len(prospects)} prospects in your database. Here are the most recent ones:\n" + "\n".join([
                    f"• {p.get('first_name', '')} {p.get('last_name', '')} - {p.get('company', 'No company')} ({p.get('email', 'no email')})"
                    for p in prospects[:5]
                ]) + (f"\n...and {len(prospects) - 5} more" if len(prospects) > 5 else "")
            
            elif action == 'create_prospect':
                if data:
                    prospect_name = f"{data.get('first_name', '')} {data.get('last_name', '')}"
                    company = data.get('company', '')
                    email = data.get('email', '')
                    company_text = f" from {company}" if company else ""
                    return f"Excellent! I've successfully added {prospect_name.strip()}{company_text} to your prospect database with email {email}. They're ready to be added to campaigns or lists!"
                else:
                    return "I've added the new prospect to your database!"
            
            elif action == 'search_prospects':
                prospects = data or []
                if not prospects:
                    return "I couldn't find any prospects matching your search criteria. Would you like to try a different search term or add new prospects to your database?"
                
                search_summary = "Here's what I found:\n" + "\n".join([
                    f"• {p.get('first_name', '')} {p.get('last_name', '')} - {p.get('company', 'No company')} ({p.get('email', 'no email')})"
                    for p in prospects[:5]
                ]) + (f"\n...and {len(prospects) - 5} more matches" if len(prospects) > 5 else "")
                
                return f"{search_summary}\n\nWould you like me to add any of these to a specific list or create a campaign for them?"
            
            elif action == 'create_list':
                list_name = data.get('name', 'New List') if data else 'New List'
                return f"Perfect! I've created the '{list_name}' list for you. You can now add prospects to this list by saying 'Add [prospect name] to {list_name} list'."
            
            elif action == 'list_lists':
                lists = data or []
                if not lists:
                    return "You don't have any prospect lists yet. Would you like to create one? Just say 'Create a new list called [Name]'."
                return f"Here are your prospect lists:\n" + "\n".join([
                    f"• {lst.get('name', 'Unnamed')} - {lst.get('prospect_count', 0)} prospects"
                    for lst in lists[:5]
                ]) + (f"\n...and {len(lists) - 5} more" if len(lists) > 5 else "")
            
            elif action == 'add_prospects_to_list':
                added_count = data.get('added_count', 0) if data else 0
                return f"Great! I've successfully added {added_count} prospect(s) to the list. They're now ready for your next campaign!"
            
            elif action == 'list_templates':
                templates = data or []
                if not templates:
                    return "You don't have any email templates yet. Would you like to create one? Just say 'Create a new template' and I'll help you!"
                return f"Here are your email templates:\n" + "\n".join([
                    f"• {t.get('name', 'Unnamed')} - Type: {t.get('type', 'unknown')}"
                    for t in templates[:5]
                ]) + (f"\n...and {len(templates) - 5} more" if len(templates) > 5 else "")
            
            elif action == 'show_analytics':
                if data:
                    return f"Here's your performance overview:\n• Total Campaigns: {data.get('total_campaigns', 0)}\n• Total Prospects: {data.get('total_prospects', 0)}\n• Active Campaigns: {data.get('active_campaigns', 0)}\n• Emails Sent: {data.get('total_emails_sent', 0)}\n• Average Open Rate: {data.get('average_open_rate', 0)}%"
                return "Here are your current analytics and performance metrics."
            
            elif action == 'upload_prospects':
                if data:
                    successful = data.get('successful_inserts', [])
                    failed = data.get('failed_inserts', [])
                    return f"CSV upload completed! Successfully added {len(successful)} prospects to your database." + (f" {len(failed)} entries had issues and were skipped." if failed else "")
                return "Your prospects have been uploaded successfully!"
            
            elif action == 'ai_suggest_prospects':
                return "I'm analyzing your existing prospects to suggest similar ones. This feature is coming soon! For now, you can search existing prospects or add new ones manually."
            
            elif action == 'help':
                return "I'm here to help you manage your email marketing! I can help you with:\n\n• **Prospects**: 'Add John Smith from TechCorp', 'Search prospects in technology', 'Show all prospects'\n• **Lists**: 'Create a VIP list', 'Add John to VIP list', 'Show my lists'\n• **Campaigns**: 'Create a campaign', 'Send campaign to VIP list', 'Show campaigns'\n• **Templates**: 'Create a template', 'Show templates'\n• **Analytics**: 'Show my analytics', 'Dashboard performance'\n\nJust tell me what you'd like to do in natural language!"
            
            else:
                return f"I've completed the {action.replace('_', ' ')} action successfully! Is there anything else I can help you with?"
                
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
    
    async def get_available_industries(self) -> List[Dict[str, Any]]:
        """
        Get available industries for AI Agent suggestions
        """
        try:
            await self.db.connect()
            industries = await self.db.get_industry_tags()
            
            # Return formatted industry data for AI Agent
            industry_data = []
            for industry in industries:
                industry_data.append({
                    "id": industry.get("id"),
                    "external_id": industry.get("external_id"),
                    "industry": industry.get("industry"),
                    "description": industry.get("description", ""),
                    "url": f"/api/industries/{industry.get('external_id')}"
                })
            
            return industry_data
            
        except Exception as e:
            logger.error(f"Error getting available industries: {e}")
            return []
    
    async def suggest_industries_for_prospect(self, company_name: str = "", existing_industry: str = "") -> List[str]:
        """
        Suggest relevant industries based on company name or existing industry
        """
        try:
            industries = await self.get_available_industries()
            suggestions = []
            
            if company_name:
                company_lower = company_name.lower()
                
                # Industry keywords mapping
                tech_keywords = ['tech', 'software', 'app', 'digital', 'data', 'ai', 'cloud', 'cyber']
                finance_keywords = ['bank', 'capital', 'invest', 'finance', 'fund', 'credit']
                health_keywords = ['health', 'medical', 'pharma', 'bio', 'clinic', 'hospital']
                
                # Suggest based on company name
                if any(keyword in company_lower for keyword in tech_keywords):
                    tech_industries = [i for i in industries if any(term in i['industry'].lower() 
                                     for term in ['technology', 'software', 'computer', 'internet'])]
                    suggestions.extend([i['industry'] for i in tech_industries[:3]])
                
                elif any(keyword in company_lower for keyword in finance_keywords):
                    finance_industries = [i for i in industries if any(term in i['industry'].lower() 
                                        for term in ['financial', 'banking', 'investment', 'capital'])]
                    suggestions.extend([i['industry'] for i in finance_industries[:3]])
                
                elif any(keyword in company_lower for keyword in health_keywords):
                    health_industries = [i for i in industries if any(term in i['industry'].lower() 
                                       for term in ['health', 'medical', 'pharmaceutical', 'biotechnology'])]
                    suggestions.extend([i['industry'] for i in health_industries[:3]])
            
            # If no specific suggestions, return common industries
            if not suggestions:
                common_industries = ['Information Technology & Services', 'Marketing & Advertising', 
                                   'Financial Services', 'Healthcare', 'Consulting']
                suggestions = [i for i in common_industries if any(ind['industry'] == i for ind in industries)]
            
            return suggestions[:5]  # Return top 5 suggestions
            
        except Exception as e:
            logger.error(f"Error suggesting industries: {e}")
            return ['Technology', 'Services', 'Consulting', 'Marketing', 'Finance']
    
    async def get_industry_url(self, industry_name: str) -> str:
        """
        Get URL for a specific industry
        """
        try:
            industries = await self.get_available_industries()
            
            # Find industry by name (case-insensitive)
            for industry in industries:
                if industry['industry'].lower() == industry_name.lower():
                    return industry['url']
            
            # If not found, try partial match
            for industry in industries:
                if industry_name.lower() in industry['industry'].lower():
                    return industry['url']
            
            return f"/api/industries/search/{industry_name}"
            
        except Exception as e:
            logger.error(f"Error getting industry URL: {e}")
            return f"/api/industries/search/{industry_name}"

# Global instance
ai_agent_service = AIAgentService()