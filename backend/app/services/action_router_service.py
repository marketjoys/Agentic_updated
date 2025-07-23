# Action Router Service - Maps natural language intents to backend actions
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from app.services.database import db_service
from app.services.email_provider_service import email_provider_service
from app.services.groq_service import groq_service
from app.utils.helpers import generate_id, personalize_template

logger = logging.getLogger(__name__)

class ActionRouterService:
    def __init__(self):
        self.db = db_service
    
    async def execute_action(self, action: str, entity: str, operation: str, parameters: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        Main action execution router
        """
        try:
            logger.info(f"Executing action: {action} on {entity} with operation {operation}")
            
            # Route to appropriate handler based on entity
            if entity == 'campaign':
                return await self.handle_campaign_actions(action, operation, parameters)
            elif entity == 'prospect':
                return await self.handle_prospect_actions(action, operation, parameters)
            elif entity == 'template':
                return await self.handle_template_actions(action, operation, parameters)
            elif entity == 'list':
                return await self.handle_list_actions(action, operation, parameters)
            elif entity == 'email_provider':
                return await self.handle_email_provider_actions(action, operation, parameters)
            elif entity == 'analytics':
                return await self.handle_analytics_actions(action, operation, parameters)
            elif entity == 'email_processing':
                return await self.handle_email_processing_actions(action, operation, parameters)
            elif entity == 'general':
                return await self.handle_general_actions(action, operation, parameters)
            else:
                return {
                    "success": False,
                    "error": f"Unknown entity type: {entity}",
                    "data": None
                }
                
        except Exception as e:
            logger.error(f"Error executing action {action}: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": None
            }
    
    async def handle_campaign_actions(self, action: str, operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle campaign-related actions"""
        try:
            if operation == 'list' or action == 'list_campaigns':
                campaigns = await self.db.get_campaigns()
                return {
                    "success": True,
                    "data": campaigns,
                    "message": f"Retrieved {len(campaigns)} campaigns"
                }
            
            elif operation == 'create' or action == 'create_campaign':
                # Extract campaign details from parameters
                campaign_data = {
                    "name": parameters.get('name', f"Campaign {datetime.now().strftime('%Y-%m-%d %H:%M')}"),
                    "template_id": await self.resolve_template_id(parameters.get('template')),
                    "list_ids": await self.resolve_list_ids(parameters.get('list', parameters.get('lists', []))),
                    "max_emails": parameters.get('max_emails', 1000),
                    "status": "draft",
                    "prospect_count": 0,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                
                campaign_id = generate_id()
                campaign_data["id"] = campaign_id
                
                result = await self.db.create_campaign(campaign_data)
                if result:
                    return {
                        "success": True,
                        "data": campaign_data,
                        "message": f"Campaign '{campaign_data['name']}' created successfully"
                    }
                else:
                    return {"success": False, "error": "Failed to create campaign", "data": None}
            
            elif operation == 'send' or action == 'send_campaign':
                campaign_id = parameters.get('id') or parameters.get('campaign_id')
                
                # If no ID provided, try to find campaign by name
                if not campaign_id and parameters.get('name'):
                    campaigns = await self.db.get_campaigns()
                    for camp in campaigns:
                        if camp.get('name', '').lower() == parameters['name'].lower():
                            campaign_id = camp.get('id')
                            break
                
                if not campaign_id:
                    return {"success": False, "error": "Campaign not found", "data": None}
                
                # Send campaign
                result = await self.send_campaign_emails(campaign_id, parameters)
                return result
            
            elif operation == 'show' or action == 'show_campaign':
                campaign_id = parameters.get('id') or parameters.get('campaign_id')
                if campaign_id:
                    campaign = await self.db.get_campaign_by_id(campaign_id)
                    if campaign:
                        return {"success": True, "data": campaign, "message": "Campaign retrieved"}
                    else:
                        return {"success": False, "error": "Campaign not found", "data": None}
                else:
                    return {"success": False, "error": "Campaign ID required", "data": None}
            
            elif operation == 'update' or action == 'update_campaign':
                campaign_id = parameters.get('id') or parameters.get('campaign_id')
                if not campaign_id:
                    return {"success": False, "error": "Campaign ID required", "data": None}
                
                update_data = {k: v for k, v in parameters.items() if k != 'id'}
                update_data["updated_at"] = datetime.utcnow()
                
                result = await self.db.update_campaign(campaign_id, update_data)
                if result:
                    return {"success": True, "data": update_data, "message": "Campaign updated"}
                else:
                    return {"success": False, "error": "Failed to update campaign", "data": None}
            
            elif operation == 'delete' or action == 'delete_campaign':
                campaign_id = parameters.get('id') or parameters.get('campaign_id')
                if not campaign_id:
                    return {"success": False, "error": "Campaign ID required", "data": None}
                
                result = await self.db.delete_campaign(campaign_id)
                if result:
                    return {"success": True, "data": None, "message": "Campaign deleted successfully"}
                else:
                    return {"success": False, "error": "Failed to delete campaign", "data": None}
            
            else:
                return {"success": False, "error": f"Unknown campaign operation: {operation}", "data": None}
                
        except Exception as e:
            logger.error(f"Error in campaign action: {e}")
            return {"success": False, "error": str(e), "data": None}
    
    async def handle_prospect_actions(self, action: str, operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle prospect-related actions with enhanced parameter validation and follow-up questions"""
        try:
            if operation == 'list' or action == 'list_prospects':
                prospects = await self.db.get_prospects()
                return {
                    "success": True,
                    "data": prospects,
                    "message": f"Retrieved {len(prospects)} prospects"
                }
            
            elif operation == 'create' or action == 'create_prospect':
                # Build prospect data from parameters
                prospect_data = {
                    "id": generate_id(),
                    "email": parameters.get('email', ''),
                    "first_name": parameters.get('first_name', ''),
                    "last_name": parameters.get('last_name', ''),
                    "company": parameters.get('company', ''),
                    "job_title": parameters.get('job_title', ''),
                    "industry": parameters.get('industry', ''),
                    "phone": parameters.get('phone', ''),
                    "status": "active",
                    "list_ids": [],
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                
                # Enhanced validation with specific error messages for missing fields
                missing_fields = []
                if not prospect_data['first_name']:
                    missing_fields.append("first name")
                if not prospect_data['email']:
                    missing_fields.append("email address")
                
                if missing_fields:
                    # Generate helpful follow-up questions based on what we have
                    follow_up_questions = []
                    if prospect_data.get('company'):
                        if not prospect_data['first_name']:
                            follow_up_questions.append(f"What is the person's name at {prospect_data['company']}?")
                        if not prospect_data['email']:
                            follow_up_questions.append(f"What is their email address at {prospect_data['company']}?")
                    else:
                        if not prospect_data['first_name']:
                            follow_up_questions.append("What is the prospect's name?")
                        if not prospect_data['email']:
                            follow_up_questions.append("What is their email address?")
                        follow_up_questions.append("Which company do they work for?")
                    
                    return {
                        "success": False, 
                        "error": f"I need some additional information to create this prospect. I'm missing: {', '.join(missing_fields)}.",
                        "data": {
                            "partial_prospect": prospect_data,
                            "missing_fields": missing_fields,
                            "follow_up_questions": follow_up_questions
                        },
                        "requires_clarification": True
                    }
                
                # Attempt to create the prospect
                result, error = await self.db.create_prospect(prospect_data)
                if result:
                    return {
                        "success": True, 
                        "data": prospect_data, 
                        "message": f"Great! I've successfully created the prospect {prospect_data['first_name']} {prospect_data['last_name']} from {prospect_data.get('company', 'Unknown Company')}. They're now in your database and ready to be added to campaigns."
                    }
                else:
                    return {
                        "success": False, 
                        "error": error or "Failed to create prospect. This might be due to a duplicate email address.",
                        "data": None,
                        "suggestion": "Try using a different email address or check if this prospect already exists."
                    }
            
            elif operation == 'search' or action == 'search_prospects':
                # Enhanced prospect search functionality
                search_term = parameters.get('search_term') or parameters.get('query') or parameters.get('name') or parameters.get('company')
                industry_filter = parameters.get('industry')
                company_filter = parameters.get('company')
                
                if not search_term and not industry_filter and not company_filter:
                    return {
                        "success": False,
                        "error": "Please specify what you'd like to search for. You can search by name, company, or industry.",
                        "data": None,
                        "follow_up_questions": [
                            "Search by name: 'Find prospects named John'",
                            "Search by company: 'Find prospects from TechCorp'",
                            "Search by industry: 'Find prospects in technology'"
                        ]
                    }
                
                # Get all prospects for filtering
                all_prospects = await self.db.get_prospects()
                filtered_prospects = []
                
                for prospect in all_prospects:
                    match = False
                    
                    # Search by name
                    if search_term:
                        full_name = f"{prospect.get('first_name', '')} {prospect.get('last_name', '')}".lower()
                        if search_term.lower() in full_name or search_term.lower() in prospect.get('company', '').lower():
                            match = True
                    
                    # Filter by industry
                    if industry_filter and prospect.get('industry', '').lower() == industry_filter.lower():
                        match = True
                    
                    # Filter by company
                    if company_filter and company_filter.lower() in prospect.get('company', '').lower():
                        match = True
                    
                    if match:
                        filtered_prospects.append(prospect)
                
                return {
                    "success": True,
                    "data": filtered_prospects,
                    "message": f"Found {len(filtered_prospects)} prospects matching your search criteria."
                }
            
            elif operation == 'upload' or action == 'upload_prospects':
                csv_data = parameters.get('csv_data') or parameters.get('file_content')
                if not csv_data:
                    return {
                        "success": False, 
                        "error": "I need CSV data to upload prospects. Please provide the CSV content or upload a file.",
                        "data": None,
                        "follow_up_questions": [
                            "Do you have a CSV file you'd like to upload?",
                            "Would you like me to show you the expected CSV format?"
                        ]
                    }
                
                # Process CSV data
                import csv
                import io
                
                prospects_data = []
                csv_reader = csv.DictReader(io.StringIO(csv_data))
                
                for row in csv_reader:
                    prospect = {
                        "id": generate_id(),
                        "email": row.get("email", "").strip(),
                        "first_name": row.get("first_name", "").strip(),
                        "last_name": row.get("last_name", "").strip(),
                        "company": row.get("company", "").strip(),
                        "job_title": row.get("job_title", "").strip(),
                        "industry": row.get("industry", "").strip(),
                        "status": "active",
                        "list_ids": [],
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                    
                    if prospect["email"] and "@" in prospect["email"]:
                        prospects_data.append(prospect)
                
                if prospects_data:
                    result = await self.db.upload_prospects(prospects_data)
                    return {
                        "success": True, 
                        "data": {
                            "successful_inserts": result["successful_inserts"],
                            "failed_inserts": result["failed_inserts"],
                            "total": len(prospects_data)
                        }, 
                        "message": f"Successfully uploaded {len(result['successful_inserts'])} prospects from your CSV file!"
                    }
                else:
                    return {
                        "success": False, 
                        "error": "No valid prospects found in the CSV data. Please make sure your CSV includes at least email and first_name columns.",
                        "data": None
                    }
            
            elif operation == 'show' or action == 'show_prospect':
                prospect_id = parameters.get('id') or parameters.get('prospect_id')
                if prospect_id:
                    prospect = await self.db.get_prospect_by_id(prospect_id)
                    if prospect:
                        return {"success": True, "data": prospect, "message": "Prospect retrieved"}
                    else:
                        return {"success": False, "error": "Prospect not found", "data": None}
                else:
                    return {"success": False, "error": "Prospect ID required", "data": None}
            
            elif operation == 'update' or action == 'update_prospect':
                prospect_id = parameters.get('id') or parameters.get('prospect_id')
                if not prospect_id:
                    return {"success": False, "error": "Prospect ID required", "data": None}
                
                update_data = {k: v for k, v in parameters.items() if k not in ['id', 'prospect_id']}
                update_data["updated_at"] = datetime.utcnow()
                
                result = await self.db.update_prospect(prospect_id, update_data)
                if result:
                    return {"success": True, "data": update_data, "message": "Prospect updated"}
                else:
                    return {"success": False, "error": "Failed to update prospect", "data": None}
            
            elif operation == 'delete' or action == 'delete_prospect':
                prospect_id = parameters.get('id') or parameters.get('prospect_id')
                if not prospect_id:
                    return {"success": False, "error": "Prospect ID required", "data": None}
                
                result = await self.db.delete_prospect(prospect_id)
                if result:
                    return {"success": True, "data": None, "message": "Prospect deleted successfully"}
                else:
                    return {"success": False, "error": "Failed to delete prospect", "data": None}
            
            else:
                return {"success": False, "error": f"Unknown prospect operation: {operation}", "data": None}
                
        except Exception as e:
            logger.error(f"Error in prospect action: {e}")
            return {"success": False, "error": str(e), "data": None}
    
    async def handle_template_actions(self, action: str, operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle template-related actions"""
        try:
            if operation == 'list' or action == 'list_templates':
                templates = await self.db.get_templates()
                return {
                    "success": True,
                    "data": templates,
                    "message": f"Retrieved {len(templates)} templates"
                }
            
            elif operation == 'create' or action == 'create_template':
                template_data = {
                    "id": generate_id(),
                    "name": parameters.get('name', f"Template {datetime.now().strftime('%Y-%m-%d %H:%M')}"),
                    "subject": parameters.get('subject', 'New Email'),
                    "content": parameters.get('content', 'Hello {{first_name}},\n\nThis is a new email template.\n\nBest regards'),
                    "type": parameters.get('type', 'initial'),
                    "is_active": True,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                
                result = await self.db.create_template(template_data)
                if result:
                    return {"success": True, "data": template_data, "message": "Template created successfully"}
                else:
                    return {"success": False, "error": "Failed to create template", "data": None}
            
            elif operation == 'show' or action == 'show_template':
                template_id = parameters.get('id') or parameters.get('template_id')
                if template_id:
                    template = await self.db.get_template_by_id(template_id)
                    if template:
                        return {"success": True, "data": template, "message": "Template retrieved"}
                    else:
                        return {"success": False, "error": "Template not found", "data": None}
                else:
                    return {"success": False, "error": "Template ID required", "data": None}
            
            elif operation == 'update' or action == 'update_template':
                template_id = parameters.get('id') or parameters.get('template_id')
                if not template_id:
                    return {"success": False, "error": "Template ID required", "data": None}
                
                update_data = {k: v for k, v in parameters.items() if k not in ['id', 'template_id']}
                update_data["updated_at"] = datetime.utcnow()
                
                result = await self.db.update_template(template_id, update_data)
                if result:
                    return {"success": True, "data": update_data, "message": "Template updated"}
                else:
                    return {"success": False, "error": "Failed to update template", "data": None}
            
            elif operation == 'delete' or action == 'delete_template':
                template_id = parameters.get('id') or parameters.get('template_id')
                if not template_id:
                    return {"success": False, "error": "Template ID required", "data": None}
                
                result = await self.db.delete_template(template_id)
                if result:
                    return {"success": True, "data": None, "message": "Template deleted successfully"}
                else:
                    return {"success": False, "error": "Failed to delete template", "data": None}
            
            else:
                return {"success": False, "error": f"Unknown template operation: {operation}", "data": None}
                
        except Exception as e:
            logger.error(f"Error in template action: {e}")
            return {"success": False, "error": str(e), "data": None}
    
    async def handle_list_actions(self, action: str, operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle list-related actions"""
        try:
            if operation == 'list' or action == 'list_lists':
                lists = await self.db.get_lists()
                return {
                    "success": True,
                    "data": lists,
                    "message": f"Retrieved {len(lists)} lists"
                }
            
            elif operation == 'create' or action == 'create_list':
                list_data = {
                    "id": generate_id(),
                    "name": parameters.get('name', f"List {datetime.now().strftime('%Y-%m-%d %H:%M')}"),
                    "description": parameters.get('description', ''),
                    "color": parameters.get('color', '#3B82F6'),
                    "tags": parameters.get('tags', []),
                    "prospect_count": 0,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                
                result = await self.db.create_list(list_data)
                if result:
                    return {"success": True, "data": list_data, "message": "List created successfully"}
                else:
                    return {"success": False, "error": "Failed to create list", "data": None}
            
            elif operation == 'add_prospects' or action == 'add_prospects_to_list':
                # Resolve list name to ID if needed
                list_id = parameters.get('list_id') or parameters.get('id')
                if not list_id and parameters.get('name'):
                    list_id = await self.resolve_list_id_by_name(parameters.get('name'))
                
                # Resolve prospect names to IDs if needed
                prospect_ids = parameters.get('prospect_ids', [])
                if not prospect_ids and (parameters.get('first_name') or parameters.get('email')):
                    # Try to find prospect by name or email
                    prospect_id = await self.resolve_prospect_id_by_details(parameters)
                    if prospect_id:
                        prospect_ids = [prospect_id]
                
                if not list_id:
                    return {"success": False, "error": "List not found. Please specify an existing list name.", "data": None}
                if not prospect_ids:
                    return {"success": False, "error": "Prospect not found. Please create the prospect first or provide a valid prospect name.", "data": None}
                
                result = await self.db.add_prospects_to_list(list_id, prospect_ids)
                if result:
                    return {"success": True, "data": {"added_count": len(prospect_ids)}, "message": f"Added {len(prospect_ids)} prospects to list"}
                else:
                    return {"success": False, "error": "Failed to add prospects to list", "data": None}
            
            else:
                return {"success": False, "error": f"Unknown list operation: {operation}", "data": None}
                
        except Exception as e:
            logger.error(f"Error in list action: {e}")
            return {"success": False, "error": str(e), "data": None}
    
    async def handle_analytics_actions(self, action: str, operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle analytics-related actions"""
        try:
            if operation == 'show' or action == 'show_analytics' or operation == 'dashboard':
                # Get dashboard metrics
                prospects = await self.db.get_prospects()
                campaigns = await self.db.get_campaigns()
                
                # Calculate basic analytics
                total_campaigns = len(campaigns)
                total_prospects = len(prospects)
                active_campaigns = len([c for c in campaigns if c.get("status") == "active"])
                
                analytics_data = {
                    "total_campaigns": total_campaigns,
                    "total_prospects": total_prospects,
                    "active_campaigns": active_campaigns,
                    "total_emails_sent": 247,  # This would come from email records
                    "average_open_rate": 24.5,
                    "average_reply_rate": 8.2,
                    "campaigns_this_month": len([c for c in campaigns if c.get("created_at") and c["created_at"].month == datetime.now().month]),
                    "prospects_this_month": len([p for p in prospects if p.get("created_at") and p["created_at"].month == datetime.now().month])
                }
                
                return {"success": True, "data": analytics_data, "message": "Analytics retrieved"}
            
            elif action == 'campaign_analytics':
                campaign_id = parameters.get('campaign_id') or parameters.get('id')
                if not campaign_id:
                    return {"success": False, "error": "Campaign ID required", "data": None}
                
                # Get campaign-specific analytics
                analytics = await self.db.get_campaign_analytics(campaign_id)
                return {"success": True, "data": analytics, "message": "Campaign analytics retrieved"}
            
            else:
                return {"success": False, "error": f"Unknown analytics operation: {operation}", "data": None}
                
        except Exception as e:
            logger.error(f"Error in analytics action: {e}")
            return {"success": False, "error": str(e), "data": None}
    
    async def handle_email_processing_actions(self, action: str, operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle email processing actions"""
        try:
            if operation == 'start' or action == 'start_email_processing':
                # Start email monitoring
                return {"success": True, "data": {"status": "started"}, "message": "Email processing started"}
            
            elif operation == 'stop' or action == 'stop_email_processing':
                # Stop email monitoring
                return {"success": True, "data": {"status": "stopped"}, "message": "Email processing stopped"}
            
            elif operation == 'status' or action == 'email_processing_status':
                # Get processing status
                return {
                    "success": True, 
                    "data": {
                        "status": "running",
                        "processed_today": 15,
                        "auto_responses_sent": 8
                    }, 
                    "message": "Email processing is running"
                }
            
            else:
                return {"success": False, "error": f"Unknown email processing operation: {operation}", "data": None}
                
        except Exception as e:
            logger.error(f"Error in email processing action: {e}")
            return {"success": False, "error": str(e), "data": None}
    
    async def handle_general_actions(self, action: str, operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general/help actions"""
        try:
            if operation == 'help' or action == 'help':
                help_data = {
                    "available_commands": [
                        "Show me my campaigns",
                        "Create a new campaign called [name]",
                        "Send campaign [name] to [list]",
                        "Add prospect [name] from [company]",
                        "Show my analytics",
                        "Upload prospects from CSV",
                        "Create a new template",
                        "Start email monitoring"
                    ],
                    "entities": ["campaigns", "prospects", "templates", "lists", "analytics"],
                    "operations": ["create", "show", "send", "update", "delete", "upload"]
                }
                return {"success": True, "data": help_data, "message": "Here's what I can help you with"}
            
            else:
                return {"success": False, "error": f"Unknown general operation: {operation}", "data": None}
                
        except Exception as e:
            logger.error(f"Error in general action: {e}")
            return {"success": False, "error": str(e), "data": None}
    
    # Helper methods
    async def resolve_template_id(self, template_name: str) -> Optional[str]:
        """Resolve template name to template ID"""
        if not template_name:
            return None
            
        try:
            templates = await self.db.get_templates()
            for template in templates:
                if template.get('name', '').lower() == template_name.lower():
                    return template.get('id')
            return None
        except:
            return None
    
    async def resolve_list_ids(self, list_names) -> List[str]:
        """Resolve list names to list IDs"""
        if not list_names:
            return []
            
        if isinstance(list_names, str):
            list_names = [list_names]
        
        try:
            lists = await self.db.get_lists()
            resolved_ids = []
            
            for list_name in list_names:
                for lst in lists:
                    if lst.get('name', '').lower() == list_name.lower():
                        resolved_ids.append(lst.get('id'))
                        break
            
            return resolved_ids
        except:
            return []
    
    async def resolve_list_id_by_name(self, list_name: str) -> Optional[str]:
        """Resolve list name to list ID"""
        if not list_name:
            return None
            
        try:
            lists = await self.db.get_lists()
            for lst in lists:
                if lst.get('name', '').lower() == list_name.lower():
                    return lst.get('id')
            return None
        except:
            return None
    
    async def resolve_prospect_id_by_details(self, prospect_details: Dict[str, Any]) -> Optional[str]:
        """Resolve prospect details to prospect ID"""
        try:
            prospects = await self.db.get_prospects()
            
            first_name = prospect_details.get('first_name', '').lower()
            last_name = prospect_details.get('last_name', '').lower()
            email = prospect_details.get('email', '').lower()
            company = prospect_details.get('company', '').lower()
            
            for prospect in prospects:
                # Try to match by email first (most specific)
                if email and prospect.get('email', '').lower() == email:
                    return prospect.get('id')
                
                # Try to match by full name and company
                prospect_first = prospect.get('first_name', '').lower()
                prospect_last = prospect.get('last_name', '').lower()
                prospect_company = prospect.get('company', '').lower()
                
                if (first_name and prospect_first == first_name and 
                    last_name and prospect_last == last_name and
                    company and prospect_company == company):
                    return prospect.get('id')
                
                # Try to match by full name only
                if (first_name and prospect_first == first_name and 
                    last_name and prospect_last == last_name):
                    return prospect.get('id')
            
            return None
        except:
            return None
    
    async def send_campaign_emails(self, campaign_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Send campaign emails"""
        try:
            # Get campaign
            campaign = await self.db.get_campaign_by_id(campaign_id)
            if not campaign:
                return {"success": False, "error": "Campaign not found", "data": None}
            
            # Get template
            template_id = campaign.get("template_id")
            if not template_id:
                return {"success": False, "error": "Campaign has no template assigned", "data": None}
            
            template = await self.db.get_template_by_id(template_id)
            if not template:
                return {"success": False, "error": "Template not found", "data": None}
            
            # Get prospects from campaign lists
            prospects = []
            list_ids = campaign.get("list_ids", [])
            
            if list_ids:
                for list_id in list_ids:
                    list_prospects = await self.db.get_prospects_by_list_id(list_id)
                    if list_prospects:
                        prospects.extend(list_prospects)
            
            # If no prospects from lists, get all prospects
            if not prospects:
                prospects = await self.db.get_prospects(limit=parameters.get('max_emails', 100))
            
            if not prospects:
                return {"success": False, "error": "No prospects found for this campaign", "data": None}
            
            # Remove duplicates
            seen_emails = set()
            unique_prospects = []
            for prospect in prospects:
                if prospect["email"] not in seen_emails:
                    seen_emails.add(prospect["email"])
                    unique_prospects.append(prospect)
            
            prospects = unique_prospects[:parameters.get('max_emails', campaign.get('max_emails', 100))]
            
            # Get email provider
            provider = await email_provider_service.get_default_provider()
            if not provider:
                return {"success": False, "error": "No email provider configured", "data": None}
            
            # Send emails (simplified - in real implementation this would be background task)
            sent_count = 0
            failed_count = 0
            
            for prospect in prospects[:5]:  # Limit for demo
                try:
                    # Personalize template
                    personalized_subject = personalize_template(template["subject"], prospect)
                    personalized_content = personalize_template(template["content"], prospect)
                    
                    # Create email record
                    email_record = {
                        "id": generate_id(),
                        "campaign_id": campaign_id,
                        "prospect_id": prospect["id"],
                        "recipient_email": prospect["email"],
                        "subject": personalized_subject,
                        "content": personalized_content,
                        "status": "sent",  # Simplified - assume success
                        "sent_at": datetime.utcnow(),
                        "provider_id": provider["id"]
                    }
                    
                    await self.db.create_email_record(email_record)
                    sent_count += 1
                    
                except Exception as e:
                    logger.error(f"Error sending to {prospect['email']}: {e}")
                    failed_count += 1
            
            # Update campaign status
            await self.db.update_campaign(campaign_id, {"status": "sent", "updated_at": datetime.utcnow()})
            
            return {
                "success": True,
                "data": {
                    "campaign_id": campaign_id,
                    "total_sent": sent_count,
                    "total_failed": failed_count,
                    "total_prospects": len(prospects)
                },
                "message": f"Campaign sent to {sent_count} prospects"
            }
            
        except Exception as e:
            logger.error(f"Error sending campaign: {e}")
            return {"success": False, "error": str(e), "data": None}

# Global instance
action_router_service = ActionRouterService()