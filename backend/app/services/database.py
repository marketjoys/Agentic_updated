from motor.motor_asyncio import AsyncIOMotorClient
import os

class DatabaseService:
    def __init__(self):
        self.client = AsyncIOMotorClient(os.getenv("MONGO_URL"))
        self.db = self.client.email_responder
        
    async def create_prospect(self, prospect_data: dict):
        """Create a new prospect with email duplication check"""
        # Check if email already exists
        existing_prospect = await self.db.prospects.find_one({"email": prospect_data["email"]})
        if existing_prospect:
            return None, f"Prospect with email '{prospect_data['email']}' already exists"
        
        # Insert new prospect
        result = await self.db.prospects.insert_one(prospect_data)
        return result, None
        
    async def get_prospects(self, skip: int = 0, limit: int = 100):
        """Get prospects with pagination"""
        prospects = await self.db.prospects.find().skip(skip).limit(limit).to_list(length=limit)
        for prospect in prospects:
            prospect.pop('_id', None)
        return prospects
        
    async def upload_prospects(self, prospects_data: list):
        """Upload multiple prospects with email duplication handling"""
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
                
        return successful_inserts, failed_inserts
        
    async def get_prospect_by_email(self, email: str):
        """Get prospect by email"""
        prospect = await self.db.prospects.find_one({"email": email})
        if prospect:
            prospect.pop('_id', None)
        return prospect
        
    # Lists operations
    async def create_list(self, list_data: dict):
        """Create a new prospect list"""
        result = await self.db.prospect_lists.insert_one(list_data)
        return result
        
    async def get_lists(self):
        """Get all prospect lists with prospect counts"""
        lists = await self.db.prospect_lists.find().to_list(length=100)
        for list_item in lists:
            list_item.pop('_id', None)
            # Update prospect count
            count = await self.db.prospects.count_documents({"list_ids": list_item["id"]})
            list_item["prospect_count"] = count
        return lists
        
    async def get_list_by_id(self, list_id: str):
        """Get a specific list by ID"""
        list_item = await self.db.prospect_lists.find_one({"id": list_id})
        if list_item:
            list_item.pop('_id', None)
            # Get prospects in this list
            prospects = await self.db.prospects.find({"list_ids": list_id}).to_list(length=1000)
            for prospect in prospects:
                prospect.pop('_id', None)
            list_item["prospects"] = prospects
            list_item["prospect_count"] = len(prospects)
        return list_item
        
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
        for template in templates:
            template.pop('_id', None)
        return templates
        
    async def get_template_by_id(self, template_id: str):
        """Get a specific template by ID"""
        template = await self.db.templates.find_one({"id": template_id})
        if template:
            template.pop('_id', None)
        return template
        
    async def update_template(self, template_id: str, template_data: dict):
        """Update a template"""
        result = await self.db.templates.update_one(
            {"id": template_id},
            {"$set": template_data}
        )
        return result
        
    # Campaigns operations
    async def create_campaign(self, campaign_data: dict):
        """Create a new campaign"""
        result = await self.db.campaigns.insert_one(campaign_data)
        return result
        
    async def get_campaigns(self):
        """Get all campaigns"""
        campaigns = await self.db.campaigns.find().to_list(length=100)
        for campaign in campaigns:
            campaign.pop('_id', None)
        return campaigns
        
    async def get_campaign_by_id(self, campaign_id: str):
        """Get a specific campaign by ID"""
        campaign = await self.db.campaigns.find_one({"id": campaign_id})
        if campaign:
            campaign.pop('_id', None)
        return campaign
        
    async def update_campaign(self, campaign_id: str, campaign_data: dict):
        """Update a campaign"""
        result = await self.db.campaigns.update_one(
            {"id": campaign_id},
            {"$set": campaign_data}
        )
        return result
        
    # Intents operations
    async def create_intent(self, intent_data: dict):
        """Create a new intent"""
        result = await self.db.intents.insert_one(intent_data)
        return result
        
    async def get_intents(self):
        """Get all intents"""
        intents = await self.db.intents.find().to_list(length=100)
        for intent in intents:
            intent.pop('_id', None)
        return intents
        
    # Email operations
    async def create_email_record(self, email_data: dict):
        """Create an email record"""
        result = await self.db.emails.insert_one(email_data)
        return result
        
    async def update_prospect_last_contact(self, prospect_id: str, last_contact):
        """Update prospect's last contact time"""
        result = await self.db.prospects.update_one(
            {"id": prospect_id},
            {"$set": {"last_contact": last_contact}}
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
        if intent:
            intent.pop('_id', None)
        return intent
    
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
        if prospect:
            prospect.pop('_id', None)
        return prospect
    
    # Thread Context operations
    async def create_thread_context(self, thread_data: dict):
        """Create a new thread context"""
        result = await self.db.threads.insert_one(thread_data)
        return result
    
    async def get_threads(self):
        """Get all thread contexts"""
        threads = await self.db.threads.find().to_list(length=1000)
        for thread in threads:
            thread.pop('_id', None)
        return threads
    
    async def get_thread_by_id(self, thread_id: str):
        """Get specific thread by ID"""
        thread = await self.db.threads.find_one({"id": thread_id})
        if thread:
            thread.pop('_id', None)
        return thread
    
    async def get_thread_by_prospect_id(self, prospect_id: str):
        """Get thread by prospect ID"""
        thread = await self.db.threads.find_one({"prospect_id": prospect_id})
        if thread:
            thread.pop('_id', None)
        return thread
    
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

# Create global database service instance
db_service = DatabaseService()