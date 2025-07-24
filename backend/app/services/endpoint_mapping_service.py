# Endpoint Mapping Service - Maps intents to backend endpoints
import logging
from typing import Dict, List, Optional, Any
from app.models.conversation_models import EndpointMapping

logger = logging.getLogger(__name__)

class EndpointMappingService:
    """Service to map user intents to backend endpoints with validation"""
    
    def __init__(self):
        self.endpoint_mappings = self._initialize_endpoint_mappings()
    
    def _initialize_endpoint_mappings(self) -> Dict[str, EndpointMapping]:
        """Initialize all available endpoint mappings"""
        return {
            # Campaign Management
            "list_campaigns": EndpointMapping(
                endpoint="/api/campaigns",
                method="GET",
                required_params=[],
                optional_params=["status", "limit"],
                description="Get all campaigns from database",
                examples=["Show me all my campaigns", "List campaigns", "What campaigns do I have?"]
            ),
            "create_campaign": EndpointMapping(
                endpoint="/api/campaigns",
                method="POST", 
                required_params=["name", "template_id"],
                optional_params=["list_ids", "max_emails", "schedule"],
                description="Create a new email campaign",
                examples=["Create campaign 'Summer Sale'", "Make new campaign using Welcome template"]
            ),
            "get_campaign": EndpointMapping(
                endpoint="/api/campaigns/{campaign_id}",
                method="GET",
                required_params=["campaign_id"],
                optional_params=[],
                description="Get specific campaign details",
                examples=["Show campaign details", "Get campaign info"]
            ),
            "update_campaign": EndpointMapping(
                endpoint="/api/campaigns/{campaign_id}",
                method="PUT",
                required_params=["campaign_id"],
                optional_params=["name", "template_id", "list_ids", "max_emails"],
                description="Update an existing campaign",
                examples=["Update campaign name", "Change campaign template"]
            ),
            "delete_campaign": EndpointMapping(
                endpoint="/api/campaigns/{campaign_id}",
                method="DELETE",
                required_params=["campaign_id"],
                optional_params=[],
                description="Delete a campaign",
                examples=["Delete campaign", "Remove campaign"]
            ),
            "send_campaign": EndpointMapping(
                endpoint="/api/campaigns/{campaign_id}/send",
                method="POST",
                required_params=["campaign_id"],
                optional_params=["email_provider_id", "max_emails", "schedule_type"],
                description="Send campaign emails to prospects",
                examples=["Send campaign now", "Launch Summer Sale campaign"]
            ),
            
            # Prospect Management  
            "list_prospects": EndpointMapping(
                endpoint="/api/prospects",
                method="GET",
                required_params=[],
                optional_params=["skip", "limit"],
                description="Get all prospects from database",
                examples=["Show my prospects", "List all contacts", "Who are my prospects?"]
            ),
            "create_prospect": EndpointMapping(
                endpoint="/api/prospects",
                method="POST",
                required_params=["email"],
                optional_params=["first_name", "last_name", "company", "job_title", "industry", "phone"],
                description="Create a new prospect",
                examples=["Add John Smith from TechCorp", "Create prospect with email john@company.com"]
            ),
            "update_prospect": EndpointMapping(
                endpoint="/api/prospects/{prospect_id}",
                method="PUT",
                required_params=["prospect_id"],
                optional_params=["first_name", "last_name", "company", "job_title", "industry", "phone", "email"],
                description="Update prospect information",
                examples=["Update prospect details", "Change prospect company"]
            ),
            "delete_prospect": EndpointMapping(
                endpoint="/api/prospects/{prospect_id}",
                method="DELETE",
                required_params=["prospect_id"],
                optional_params=[],
                description="Delete a prospect",
                examples=["Delete prospect", "Remove contact"]
            ),
            "upload_prospects": EndpointMapping(
                endpoint="/api/prospects/upload",
                method="POST",
                required_params=["file_content"],
                optional_params=[],
                description="Upload prospects from CSV data",
                examples=["Upload CSV prospects", "Import contacts from CSV"]
            ),
            
            # Template Management
            "list_templates": EndpointMapping(
                endpoint="/api/templates",
                method="GET",
                required_params=[],
                optional_params=["type"],
                description="Get all email templates",
                examples=["Show templates", "List my templates", "What templates do I have?"]
            ),
            "create_template": EndpointMapping(
                endpoint="/api/templates",
                method="POST",
                required_params=["name", "subject", "content"],
                optional_params=["type", "description"],
                description="Create a new email template",
                examples=["Create Welcome template", "Make new email template"]
            ),
            "update_template": EndpointMapping(
                endpoint="/api/templates/{template_id}",
                method="PUT",
                required_params=["template_id"],
                optional_params=["name", "subject", "content", "type", "description"],
                description="Update an email template",
                examples=["Update template content", "Change template subject"]
            ),
            "delete_template": EndpointMapping(
                endpoint="/api/templates/{template_id}",
                method="DELETE",
                required_params=["template_id"],
                optional_params=[],
                description="Delete an email template",
                examples=["Delete template", "Remove email template"]
            ),
            
            # List Management
            "list_lists": EndpointMapping(
                endpoint="/api/lists",
                method="GET",
                required_params=[],
                optional_params=[],
                description="Get all prospect lists",
                examples=["Show my lists", "What lists do I have?", "List prospect lists"]
            ),
            "create_list": EndpointMapping(
                endpoint="/api/lists",
                method="POST",
                required_params=["name"],
                optional_params=["description", "color", "tags"],
                description="Create a new prospect list",
                examples=["Create VIP list", "Make new prospect list called Technology"]
            ),
            "get_list": EndpointMapping(
                endpoint="/api/lists/{list_id}",
                method="GET",
                required_params=["list_id"],
                optional_params=[],
                description="Get specific list details",
                examples=["Show list details", "Get list information"]
            ),
            "update_list": EndpointMapping(
                endpoint="/api/lists/{list_id}",
                method="PUT",
                required_params=["list_id"],
                optional_params=["name", "description", "color", "tags"],
                description="Update a prospect list",
                examples=["Update list name", "Change list description"]
            ),
            "delete_list": EndpointMapping(
                endpoint="/api/lists/{list_id}",
                method="DELETE",
                required_params=["list_id"],
                optional_params=[],
                description="Delete a prospect list",
                examples=["Delete list", "Remove prospect list"]
            ),
            "add_prospects_to_list": EndpointMapping(
                endpoint="/api/lists/{list_id}/prospects",
                method="POST",
                required_params=["list_id", "prospect_ids"],
                optional_params=[],
                description="Add prospects to a list",
                examples=["Add John to VIP list", "Put prospects in Technology list"]
            ),
            "remove_prospects_from_list": EndpointMapping(
                endpoint="/api/lists/{list_id}/prospects",
                method="DELETE",
                required_params=["list_id", "prospect_ids"],
                optional_params=[],
                description="Remove prospects from a list",
                examples=["Remove prospects from list", "Take out prospects from VIP list"]
            ),
            "get_list_prospects": EndpointMapping(
                endpoint="/api/lists/{list_id}/prospects",
                method="GET",
                required_params=["list_id"],
                optional_params=[],
                description="Get prospects in a specific list",
                examples=["Show prospects in VIP list", "Who is in Technology list?"]
            ),
            
            # Email Provider Management
            "list_email_providers": EndpointMapping(
                endpoint="/api/email-providers",
                method="GET",
                required_params=[],
                optional_params=[],
                description="Get all email providers",
                examples=["Show email providers", "List my email accounts"]
            ),
            "create_email_provider": EndpointMapping(
                endpoint="/api/email-providers",
                method="POST",
                required_params=["name", "provider_type", "email_address"],
                optional_params=["smtp_host", "smtp_port", "smtp_username", "smtp_password", "smtp_use_tls"],
                description="Create a new email provider",
                examples=["Add Gmail provider", "Create email provider"]
            ),
            "update_email_provider": EndpointMapping(
                endpoint="/api/email-providers/{provider_id}",
                method="PUT",
                required_params=["provider_id"],
                optional_params=["name", "email_address", "smtp_host", "smtp_port"],
                description="Update email provider settings",
                examples=["Update email provider", "Change SMTP settings"]
            ),
            "delete_email_provider": EndpointMapping(
                endpoint="/api/email-providers/{provider_id}",
                method="DELETE",
                required_params=["provider_id"],
                optional_params=[],
                description="Delete an email provider",
                examples=["Delete email provider", "Remove email account"]
            ),
            "test_email_provider": EndpointMapping(
                endpoint="/api/email-providers/{provider_id}/test",
                method="POST",
                required_params=["provider_id"],
                optional_params=[],
                description="Test email provider connection",
                examples=["Test Gmail connection", "Check email provider"]
            ),
            
            # Analytics
            "show_analytics": EndpointMapping(
                endpoint="/api/analytics",
                method="GET",
                required_params=[],
                optional_params=[],
                description="Get overall system analytics",
                examples=["Show analytics", "What's my performance?", "Dashboard metrics"]
            ),
            "get_campaign_analytics": EndpointMapping(
                endpoint="/api/analytics/campaign/{campaign_id}",
                method="GET",
                required_params=["campaign_id"],
                optional_params=[],
                description="Get analytics for specific campaign",
                examples=["Show campaign performance", "Campaign analytics"]
            ),
            "get_dashboard_metrics": EndpointMapping(
                endpoint="/api/real-time/dashboard-metrics",
                method="GET",
                required_params=[],
                optional_params=[],
                description="Get real-time dashboard metrics",
                examples=["Dashboard metrics", "Current stats"]
            ),
        }
    
    def get_endpoint_mapping(self, action: str) -> Optional[EndpointMapping]:
        """Get endpoint mapping for a specific action"""
        return self.endpoint_mappings.get(action)
    
    def find_matching_actions(self, user_message: str) -> List[str]:
        """Find actions that might match the user's message"""
        message_lower = user_message.lower()
        matching_actions = []
        
        for action, mapping in self.endpoint_mappings.items():
            # Check if any example matches
            for example in mapping.examples:
                if any(word in message_lower for word in example.lower().split()):
                    matching_actions.append(action)
                    break
            
            # Check action name components
            action_words = action.replace('_', ' ').split()
            if any(word in message_lower for word in action_words):
                if action not in matching_actions:
                    matching_actions.append(action)
        
        return matching_actions
    
    def validate_parameters(self, action: str, parameters: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate parameters for an action"""
        mapping = self.get_endpoint_mapping(action)
        if not mapping:
            return {"errors": ["Unknown action"], "missing_required": [], "missing_optional": []}
        
        provided_params = set(parameters.keys())
        required_params = set(mapping.required_params)
        optional_params = set(mapping.optional_params)
        
        missing_required = list(required_params - provided_params)
        missing_optional = list(optional_params - provided_params)
        
        # Check for invalid parameters
        valid_params = required_params | optional_params
        invalid_params = list(provided_params - valid_params)
        
        return {
            "missing_required": missing_required,
            "missing_optional": missing_optional,
            "invalid_params": invalid_params,
            "errors": []
        }
    
    def get_parameter_questions(self, action: str, missing_params: List[str]) -> Dict[str, str]:
        """Generate questions for missing parameters"""
        questions = {}
        
        # Parameter-specific questions
        question_templates = {
            "name": "What would you like to name this {entity}?",
            "email": "What is the email address?",
            "first_name": "What is the first name?", 
            "last_name": "What is the last name?",
            "company": "What company are they from?",
            "job_title": "What is their job title?",
            "industry": "What industry are they in?",
            "phone": "What is their phone number? (optional)",
            "subject": "What should the email subject be?",
            "content": "What content would you like in the template?",
            "template_id": "Which template would you like to use? (I can show you available templates)",
            "campaign_id": "Which campaign would you like to work with? (I can show you available campaigns)",
            "list_id": "Which list would you like to use? (I can show you available lists)",
            "list_ids": "Which prospect lists should this campaign target? (I can show you available lists)",
            "prospect_id": "Which prospect would you like to work with? (I can show you available prospects)",
            "prospect_ids": "Which prospects would you like to add? (I can show you available prospects)",
            "provider_id": "Which email provider would you like to use? (I can show you available providers)",
            "email_provider_id": "Which email provider should send this campaign? (I can show you available providers)",
            "description": "Would you like to add a description? (optional)",
            "max_emails": "What's the maximum number of emails to send? (default: 1000)",
            "file_content": "Please provide the CSV content to upload (including headers)",
            "color": "What color would you like for this list? (optional)",
            "tags": "Any tags for this list? (optional, comma-separated)"
        }
        
        # Get entity type from action
        entity_map = {
            "campaign": "campaign",
            "prospect": "prospect", 
            "template": "template",
            "list": "list",
            "email_provider": "email provider"
        }
        
        entity = "item"
        for key, value in entity_map.items():
            if key in action:
                entity = value
                break
        
        for param in missing_params:
            if param in question_templates:
                question = question_templates[param].replace("{entity}", entity)
                questions[param] = question
            else:
                questions[param] = f"Please provide the {param.replace('_', ' ')}:"
        
        return questions
    
    def generate_confirmation_message(self, action: str, parameters: Dict[str, Any]) -> str:
        """Generate confirmation message for the action"""
        mapping = self.get_endpoint_mapping(action)
        if not mapping:
            return "I'm ready to execute this action. Should I proceed?"
        
        # Action-specific confirmation messages
        if action == "create_campaign":
            name = parameters.get("name", "New Campaign")
            template = parameters.get("template_id", "selected template")
            lists = parameters.get("list_ids", [])
            list_text = f" targeting {len(lists)} list(s)" if lists else ""
            return f"I'm ready to create the campaign '{name}' using {template}{list_text}. Should I proceed?"
        
        elif action == "send_campaign":
            campaign_id = parameters.get("campaign_id", "selected campaign")
            max_emails = parameters.get("max_emails", "default limit")
            return f"I'm ready to send campaign {campaign_id} with a limit of {max_emails} emails. This will send real emails to prospects. Should I proceed?"
        
        elif action == "create_prospect":
            name = f"{parameters.get('first_name', '')} {parameters.get('last_name', '')}".strip()
            email = parameters.get("email", "provided email")
            company = parameters.get("company", "")
            company_text = f" from {company}" if company else ""
            return f"I'm ready to add {name or 'new prospect'}{company_text} with email {email} to your database. Should I proceed?"
        
        elif action == "delete_campaign" or action == "delete_prospect" or action == "delete_template" or action == "delete_list":
            entity = action.split("_")[1]
            return f"⚠️ I'm ready to permanently delete this {entity}. This action cannot be undone. Are you sure you want to proceed?"
        
        elif action == "add_prospects_to_list":
            list_id = parameters.get("list_id", "selected list")
            prospect_count = len(parameters.get("prospect_ids", []))
            return f"I'm ready to add {prospect_count} prospect(s) to list {list_id}. Should I proceed?"
        
        elif action == "upload_prospects":
            return "I'm ready to upload prospects from the provided CSV data to your database. Should I proceed?"
        
        else:
            return f"I'm ready to {action.replace('_', ' ')} with the provided parameters. Should I proceed?"

# Global instance
endpoint_mapping_service = EndpointMappingService()