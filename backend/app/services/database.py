from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import os
from bson import ObjectId
from typing import Any, Dict, List, Union
from app.utils.helpers import generate_id

def clean_document(doc: Union[Dict, List, Any]) -> Union[Dict, List, Any]:
    """
    Recursively clean MongoDB documents by converting ObjectId to string
    and removing/converting non-serializable fields
    """
    if isinstance(doc, dict):
        cleaned = {}
        for key, value in doc.items():
            if key == '_id':
                # Skip MongoDB's _id field entirely
                continue
            elif isinstance(value, ObjectId):
                # Convert ObjectId to string
                cleaned[key] = str(value)
            elif isinstance(value, (dict, list)):
                # Recursively clean nested structures
                cleaned[key] = clean_document(value)
            else:
                cleaned[key] = value
        return cleaned
    elif isinstance(doc, list):
        return [clean_document(item) for item in doc]
    elif isinstance(doc, ObjectId):
        return str(doc)
    else:
        return doc

class DatabaseService:
    def __init__(self):
        self.client = None
        self.db = None
        
    async def connect(self):
        """Connect to the database"""
        if not self.client:
            self.client = AsyncIOMotorClient(os.getenv("MONGO_URL"))
            self.db = self.client.email_responder
            
    async def disconnect(self):
        """Disconnect from the database"""
        if self.client:
            self.client.close()
            self.client = None
            self.db = None
        
    async def create_prospect(self, prospect_data: dict):
        """Create a new prospect with email duplication check"""
        await self.connect()
        # Check if email already exists
        existing_prospect = await self.db.prospects.find_one({"email": prospect_data["email"]})
        if existing_prospect:
            return None, f"Prospect with email '{prospect_data['email']}' already exists"
        
        # Insert new prospect
        result = await self.db.prospects.insert_one(prospect_data)
        # Clean the result object to remove ObjectId fields
        cleaned_result = {
            "acknowledged": result.acknowledged,
            "inserted_id": str(result.inserted_id) if result.inserted_id else None
        }
        return cleaned_result, None
        
    async def get_prospects(self, skip: int = 0, limit: int = 100):
        """Get prospects with pagination"""
        await self.connect()
        prospects = await self.db.prospects.find().skip(skip).limit(limit).to_list(length=limit)
        return clean_document(prospects)
        
    async def upload_prospects(self, prospects_data: list):
        """Upload multiple prospects with email duplication handling"""
        await self.connect()
        successful_inserts = []
        failed_inserts = []
        
        for prospect_data in prospects_data:
            # Check for duplicate email
            existing_prospect = await self.db.prospects.find_one({"email": prospect_data["email"]})
            if existing_prospect:
                failed_inserts.append({
                    "email": prospect_data["email"],
                    "error": "Email already exists"
                })
                continue
                
            try:
                await self.db.prospects.insert_one(prospect_data)
                successful_inserts.append(prospect_data["email"])
            except Exception as e:
                failed_inserts.append({
                    "email": prospect_data["email"],
                    "error": str(e)
                })
        
        return {
            "successful_inserts": successful_inserts,
            "failed_inserts": failed_inserts
        }
        
    async def get_prospect_by_email(self, email: str):
        """Get prospect by email"""
        prospect = await self.db.prospects.find_one({"email": email})
        return clean_document(prospect) if prospect else None
        
    # Lists operations
    async def create_list(self, list_data: dict):
        """Create a new prospect list"""
        result = await self.db.prospect_lists.insert_one(list_data)
        return result
        
    async def get_lists(self):
        """Get all prospect lists with prospect counts"""
        lists = await self.db.prospect_lists.find().to_list(length=100)
        cleaned_lists = []
        for list_item in lists:
            # Update prospect count
            count = await self.db.prospects.count_documents({"list_ids": list_item["id"]})
            list_item["prospect_count"] = count
            cleaned_lists.append(clean_document(list_item))
        return cleaned_lists
        
    async def get_list_by_id(self, list_id: str):
        """Get a specific list by ID"""
        list_item = await self.db.prospect_lists.find_one({"id": list_id})
        if list_item:
            # Get prospects in this list
            prospects = await self.db.prospects.find({"list_ids": list_id}).to_list(length=1000)
            cleaned_prospects = [clean_document(prospect) for prospect in prospects]
            list_item["prospects"] = cleaned_prospects
            list_item["prospect_count"] = len(prospects)
            return clean_document(list_item)
        return None
        
    async def update_list(self, list_id: str, list_data: dict):
        """Update a prospect list"""
        result = await self.db.prospect_lists.update_one(
            {"id": list_id},
            {"$set": list_data}
        )
        return result
        
    async def delete_list(self, list_id: str):
        """Delete a prospect list and remove it from all prospects"""
        # Remove list from all prospects
        await self.db.prospects.update_many(
            {"list_ids": list_id},
            {"$pull": {"list_ids": list_id}}
        )
        
        # Delete the list
        result = await self.db.prospect_lists.delete_one({"id": list_id})
        return result
        
    async def add_prospects_to_list(self, list_id: str, prospect_ids: list):
        """Add prospects to a list"""
        result = await self.db.prospects.update_many(
            {"id": {"$in": prospect_ids}},
            {"$addToSet": {"list_ids": list_id}}
        )
        return result
        
    async def remove_prospects_from_list(self, list_id: str, prospect_ids: list):
        """Remove prospects from a list"""
        result = await self.db.prospects.update_many(
            {"id": {"$in": prospect_ids}},
            {"$pull": {"list_ids": list_id}}
        )
        return result
        
    # Templates operations
    async def create_template(self, template_data: dict):
        """Create a new template"""
        result = await self.db.templates.insert_one(template_data)
        return result
        
    async def get_templates(self):
        """Get all templates"""
        templates = await self.db.templates.find().to_list(length=100)
        return clean_document(templates)
        
    async def get_template_by_id(self, template_id: str):
        """Get a specific template by ID"""
        template = await self.db.templates.find_one({"id": template_id})
        return clean_document(template) if template else None
        
    async def update_template(self, template_id: str, template_data: dict):
        """Update a template"""
        result = await self.db.templates.update_one(
            {"id": template_id},
            {"$set": template_data}
        )
        return result
        
    async def delete_template(self, template_id: str):
        """Delete a template"""
        result = await self.db.templates.delete_one({"id": template_id})
        return result
    
    async def delete_prospect(self, prospect_id: str):
        """Delete a prospect"""
        result = await self.db.prospects.delete_one({"id": prospect_id})
        return result
        
    # Campaigns operations
    async def create_campaign(self, campaign_data: dict):
        """Create a new campaign"""
        result = await self.db.campaigns.insert_one(campaign_data)
        return result
        
    async def get_campaigns(self):
        """Get all campaigns"""
        campaigns = await self.db.campaigns.find().to_list(length=100)
        return clean_document(campaigns)
        
    async def get_campaign_by_id(self, campaign_id: str):
        """Get a specific campaign by ID"""
        campaign = await self.db.campaigns.find_one({"id": campaign_id})
        return clean_document(campaign) if campaign else None
        
    async def update_campaign(self, campaign_id: str, campaign_data: dict):
        """Update a campaign"""
        result = await self.db.campaigns.update_one(
            {"id": campaign_id},
            {"$set": campaign_data}
        )
        return result
        
    async def delete_campaign(self, campaign_id: str):
        """Delete a campaign"""
        result = await self.db.campaigns.delete_one({"id": campaign_id})
        return result
        
    # Intents operations
    async def create_intent(self, intent_data: dict):
        """Create a new intent"""
        result = await self.db.intents.insert_one(intent_data)
        return result
        
    async def get_intents(self):
        """Get all intents"""
        intents = await self.db.intents.find().to_list(length=100)
        return clean_document(intents)
        
    # Email operations
    async def create_email_record(self, email_data: dict):
        """Create an email record"""
        result = await self.db.emails.insert_one(email_data)
        # Clean the result object to remove ObjectId fields
        cleaned_result = {
            "acknowledged": result.acknowledged,
            "inserted_id": str(result.inserted_id) if result.inserted_id else None
        }
        return cleaned_result
        
    async def update_prospect_last_contact(self, prospect_id: str, last_contact):
        """Update prospect's last contact time"""
        result = await self.db.prospects.update_one(
            {"id": prospect_id},
            {"$set": {"last_contact": last_contact}}
        )
        return result
    
    async def update_prospect_status(self, prospect_id: str, status: str):
        """Update prospect status"""
        result = await self.db.prospects.update_one(
            {"id": prospect_id},
            {"$set": {"status": status}}
        )
        return result
    
    async def update_prospect(self, prospect_id: str, update_data: dict):
        """Update prospect with any data"""
        result = await self.db.prospects.update_one(
            {"id": prospect_id},
            {"$set": update_data}
        )
        return result
    
    async def cancel_pending_follow_ups(self, prospect_id: str):
        """Cancel pending follow-up emails for a prospect"""
        result = await self.db.emails.update_many(
            {
                "prospect_id": prospect_id,
                "status": "pending"
            },
            {"$set": {"status": "cancelled"}}
        )
        return result
        
    # Analytics operations
    async def get_campaign_analytics(self, campaign_id: str):
        """Get campaign analytics"""
        pipeline = [
            {"$match": {"campaign_id": campaign_id}},
            {
                "$group": {
                    "_id": "$status",
                    "count": {"$sum": 1}
                }
            }
        ]
        
        stats = await self.db.emails.aggregate(pipeline).to_list(length=10)
        
        analytics = {
            "total_sent": 0,
            "total_failed": 0,
            "total_opened": 0,
            "total_replied": 0
        }
        
        for stat in stats:
            if stat["_id"] == "sent":
                analytics["total_sent"] = stat["count"]
            elif stat["_id"] == "failed":
                analytics["total_failed"] = stat["count"]
        
        # Get opened and replied counts
        opened_count = await self.db.emails.count_documents({
            "campaign_id": campaign_id,
            "opened_at": {"$exists": True}
        })
        
        replied_count = await self.db.emails.count_documents({
            "campaign_id": campaign_id,
            "replied_at": {"$exists": True}
        })
        
        analytics["total_opened"] = opened_count
        analytics["total_replied"] = replied_count
        
        return analytics
    
    # Enhanced Intent operations
    async def get_intent_by_id(self, intent_id: str):
        """Get specific intent by ID"""
        intent = await self.db.intents.find_one({"id": intent_id})
        return clean_document(intent) if intent else None
    
    async def update_intent(self, intent_id: str, intent_data: dict):
        """Update an intent"""
        result = await self.db.intents.update_one(
            {"id": intent_id},
            {"$set": intent_data}
        )
        return result
    
    async def delete_intent(self, intent_id: str):
        """Delete an intent"""
        result = await self.db.intents.delete_one({"id": intent_id})
        return result
    
    # Enhanced Prospect operations
    async def get_prospect_by_id(self, prospect_id: str):
        """Get prospect by ID"""
        prospect = await self.db.prospects.find_one({"id": prospect_id})
        return clean_document(prospect) if prospect else None
    
    # Thread Context operations
    async def create_thread_context(self, thread_data: dict):
        """Create a new thread context"""
        result = await self.db.threads.insert_one(thread_data)
        return result
    
    async def get_threads(self):
        """Get all thread contexts"""
        threads = await self.db.threads.find().to_list(length=1000)
        return clean_document(threads)
    
    async def get_thread_by_id(self, thread_id: str):
        """Get specific thread by ID"""
        thread = await self.db.threads.find_one({"id": thread_id})
        return clean_document(thread) if thread else None
    
    async def get_thread_by_prospect_id(self, prospect_id: str):
        """Get thread by prospect ID"""
        thread = await self.db.threads.find_one({"prospect_id": prospect_id})
        return clean_document(thread) if thread else None
    
    async def add_message_to_thread(self, thread_id: str, message_data: dict):
        """Add message to thread"""
        result = await self.db.threads.update_one(
            {"id": thread_id},
            {"$push": {"messages": message_data}}
        )
        return result
    
    async def update_thread_last_activity(self, thread_id: str, last_activity):
        """Update thread last activity"""
        result = await self.db.threads.update_one(
            {"id": thread_id},
            {"$set": {"last_activity": last_activity}}
        )
        return result
    
    async def delete_thread(self, thread_id: str):
        """Delete thread"""
        result = await self.db.threads.delete_one({"id": thread_id})
        return result
    
    # Email Provider operations
    async def create_email_provider(self, provider_data: dict):
        """Create a new email provider"""
        result = await self.db.email_providers.insert_one(provider_data)
        return result
    
    async def get_email_providers(self):
        """Get all email providers"""
        providers = await self.db.email_providers.find().to_list(length=100)
        return clean_document(providers)
    
    async def get_email_provider_by_id(self, provider_id: str):
        """Get email provider by ID"""
        provider = await self.db.email_providers.find_one({"id": provider_id})
        return clean_document(provider) if provider else None
    
    async def update_email_provider(self, provider_id: str, provider_data: dict):
        """Update an email provider"""
        result = await self.db.email_providers.update_one(
            {"id": provider_id},
            {"$set": provider_data}
        )
        return result
    
    async def delete_email_provider(self, provider_id: str):
        """Delete an email provider"""
        result = await self.db.email_providers.delete_one({"id": provider_id})
        return result
    
    async def get_default_email_provider(self):
        """Get default email provider"""
        await self.connect()
        provider = await self.db.email_providers.find_one({"is_default": True})
        return clean_document(provider) if provider else None
    
    async def update_all_email_providers(self, update_data: dict):
        """Update all email providers"""
        result = await self.db.email_providers.update_many({}, {"$set": update_data})
        return result
    
    async def get_campaigns_by_provider_id(self, provider_id: str):
        """Get campaigns using specific provider"""
        campaigns = await self.db.campaigns.find({"email_provider_id": provider_id}).to_list(length=100)
        return campaigns
    
    async def increment_provider_send_counts(self, provider_id: str):
        """Increment send counts for rate limiting"""
        result = await self.db.email_providers.update_one(
            {"id": provider_id},
            {
                "$inc": {
                    "current_daily_count": 1,
                    "current_hourly_count": 1
                }
            }
        )
        return result
    
    async def unset_default_email_providers(self):
        """Unset all email providers as default"""
        result = await self.db.email_providers.update_many(
            {"is_default": True},
            {"$set": {"is_default": False}}
        )
        return result
    
    # Knowledge Base operations
    async def create_knowledge_article(self, article_data: dict):
        """Create a new knowledge article"""
        result = await self.db.knowledge_base.insert_one(article_data)
        return result
    
    async def get_knowledge_articles(self, category: str = None, active_only: bool = True):
        """Get knowledge articles"""
        query = {}
        if category:
            query["category"] = category
        if active_only:
            query["is_active"] = True
        
        articles = await self.db.knowledge_base.find(query).to_list(length=100)
        return clean_document(articles)
    
    async def get_knowledge_article_by_id(self, article_id: str):
        """Get knowledge article by ID"""
        article = await self.db.knowledge_base.find_one({"id": article_id})
        return clean_document(article) if article else None
    
    async def update_knowledge_article(self, article_id: str, article_data: dict):
        """Update a knowledge article"""
        result = await self.db.knowledge_base.update_one(
            {"id": article_id},
            {"$set": article_data}
        )
        return result
    
    async def delete_knowledge_article(self, article_id: str):
        """Delete a knowledge article"""
        result = await self.db.knowledge_base.delete_one({"id": article_id})
        return result
    
    async def search_knowledge_articles(self, query: str, category: str = None, limit: int = 10):
        """Search knowledge articles"""
        search_query = {"$text": {"$search": query}} if query else {}
        if category:
            search_query["category"] = category
        
        articles = await self.db.knowledge_base.find(search_query).limit(limit).to_list(length=limit)
        return clean_document(articles)
    
    async def get_knowledge_statistics(self):
        """Get knowledge base statistics"""
        total_articles = await self.db.knowledge_base.count_documents({})
        active_articles = await self.db.knowledge_base.count_documents({"is_active": True})
        categories = await self.db.knowledge_base.distinct("category")
        
        return {
            "total_articles": total_articles,
            "active_articles": active_articles,
            "categories": categories
        }
    
    async def increment_knowledge_article_usage(self, article_id: str):
        """Increment knowledge article usage count"""
        result = await self.db.knowledge_base.update_one(
            {"id": article_id},
            {
                "$inc": {"usage_count": 1},
                "$set": {"last_used": datetime.utcnow()}
            }
        )
        return result
    
    # System Prompt operations
    async def create_system_prompt(self, prompt_data: dict):
        """Create a new system prompt"""
        result = await self.db.system_prompts.insert_one(prompt_data)
        return result
    
    async def get_system_prompts(self):
        """Get all system prompts"""
        prompts = await self.db.system_prompts.find().to_list(length=100)
        return clean_document(prompts)
    
    async def get_system_prompt_by_id(self, prompt_id: str):
        """Get system prompt by ID"""
        prompt = await self.db.system_prompts.find_one({"id": prompt_id})
        return clean_document(prompt) if prompt else None
    
    async def update_system_prompt(self, prompt_id: str, prompt_data: dict):
        """Update a system prompt"""
        result = await self.db.system_prompts.update_one(
            {"id": prompt_id},
            {"$set": prompt_data}
        )
        return result
    
    async def delete_system_prompt(self, prompt_id: str):
        """Delete a system prompt"""
        result = await self.db.system_prompts.delete_one({"id": prompt_id})
        return result
    
    async def get_default_system_prompt(self, prompt_type: str = "general"):
        """Get default system prompt by type"""
        await self.connect()
        prompt = await self.db.system_prompts.find_one({
            "prompt_type": prompt_type,
            "is_default": True,
            "is_active": True
        })
        return clean_document(prompt) if prompt else None
    
    async def unset_default_system_prompts(self, prompt_type: str):
        """Unset all system prompts of a specific type as default"""
        await self.connect()
        result = await self.db.system_prompts.update_many(
            {"prompt_type": prompt_type, "is_default": True},
            {"$set": {"is_default": False}}
        )
        return result
    
    async def update_knowledge_article_usage(self, article_id: str):
        """Update knowledge article usage count"""
        await self.connect()
        result = await self.db.knowledge_base.update_one(
            {"id": article_id},
            {
                "$inc": {"usage_count": 1},
                "$set": {"last_used": datetime.utcnow()}
            }
        )
        return result.modified_count > 0
    
    # Follow-up Rule operations
    async def create_follow_up_rule(self, rule_data: dict):
        """Create a new follow-up rule"""
        result = await self.db.follow_up_rules.insert_one(rule_data)
        return result
    
    async def get_follow_up_rules(self):
        """Get all follow-up rules"""
        rules = await self.db.follow_up_rules.find().to_list(length=100)
        return clean_document(rules)
    
    async def get_follow_up_rule_by_id(self, rule_id: str):
        """Get follow-up rule by ID"""
        rule = await self.db.follow_up_rules.find_one({"id": rule_id})
        return clean_document(rule) if rule else None
    
    async def update_follow_up_rule(self, rule_id: str, rule_data: dict):
        """Update a follow-up rule"""
        result = await self.db.follow_up_rules.update_one(
            {"id": rule_id},
            {"$set": rule_data}
        )
        return result
    
    async def delete_follow_up_rule(self, rule_id: str):
        """Delete a follow-up rule"""
        result = await self.db.follow_up_rules.delete_one({"id": rule_id})
        return result
    
    # Response Verification operations
    async def create_response_verification(self, verification_data: dict):
        """Create a response verification record"""
        result = await self.db.response_verifications.insert_one(verification_data)
        # Clean the result object to remove ObjectId fields
        cleaned_result = {
            "acknowledged": result.acknowledged,
            "inserted_id": str(result.inserted_id) if result.inserted_id else None
        }
        return cleaned_result
    
    async def get_pending_verifications(self):
        """Get pending verifications"""
        verifications = await self.db.response_verifications.find({
            "status": {"$in": ["pending", "needs_review"]}
        }).to_list(length=100)
        return clean_document(verifications)
    
    async def get_response_verification_by_id(self, verification_id: str):
        """Get response verification by ID"""
        verification = await self.db.response_verifications.find_one({"id": verification_id})
        return clean_document(verification) if verification else None
    
    async def update_response_verification(self, verification_id: str, verification_data: dict):
        """Update a response verification"""
        result = await self.db.response_verifications.update_one(
            {"id": verification_id},
            {"$set": verification_data}
        )
        return result
    
    async def get_verification_statistics(self):
        """Get verification statistics"""
        total_verifications = await self.db.response_verifications.count_documents({})
        pending_verifications = await self.db.response_verifications.count_documents({"status": "pending"})
        approved_verifications = await self.db.response_verifications.count_documents({"status": "approved"})
        rejected_verifications = await self.db.response_verifications.count_documents({"status": "rejected"})
        
        return {
            "total_verifications": total_verifications,
            "pending_verifications": pending_verifications,
            "approved_verifications": approved_verifications,
            "rejected_verifications": rejected_verifications
        }
    
    async def get_prospects_by_list_id(self, list_id: str):
        """Get prospects by list ID"""
        await self.connect()
        prospects = await self.db.prospects.find({"list_ids": list_id}).to_list(length=1000)
        return clean_document(prospects)

# Create global database service instance
db_service = DatabaseService()