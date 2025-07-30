"""
Enhanced Database Service with Follow-up and Provider Tracking Methods
"""
from app.services.database import db_service as base_db_service, DatabaseService, clean_document
from datetime import datetime
from app.utils.helpers import generate_id
import logging

logger = logging.getLogger(__name__)

class EnhancedDatabaseService(DatabaseService):
    """Enhanced database service with additional follow-up tracking methods"""
    
    async def create_or_update_thread_context(self, prospect_id: str, campaign_id: str, provider_id: str, message_data: dict):
        """Create or update thread context for prospect with provider tracking"""
        try:
            await self.connect()
            
            # Check if thread exists
            existing_thread = await self.get_thread_by_prospect_id(prospect_id)
            
            if existing_thread:
                # Update existing thread
                thread_id = existing_thread["id"]
                await self.add_message_to_thread(thread_id, message_data)
                await self.update_thread_last_activity(thread_id, datetime.utcnow())
                
                # Update thread with campaign and provider info if not set
                if not existing_thread.get("campaign_id"):
                    await self.db.threads.update_one(
                        {"id": thread_id},
                        {"$set": {"campaign_id": campaign_id, "email_provider_id": provider_id}}
                    )
                
                return existing_thread
            else:
                # Create new thread
                thread_data = {
                    "id": f"thread_{prospect_id}",
                    "prospect_id": prospect_id,
                    "campaign_id": campaign_id,
                    "email_provider_id": provider_id,
                    "messages": [message_data],
                    "last_activity": datetime.utcnow(),
                    "created_at": datetime.utcnow(),
                    "status": "active"
                }
                
                await self.create_thread_context(thread_data)
                return thread_data
                
        except Exception as e:
            logger.error(f"Error creating/updating thread context: {str(e)}")
            return None
    
    async def get_active_follow_up_campaigns_enhanced(self):
        """Get campaigns with enhanced follow-up tracking"""
        await self.connect()
        campaigns = await self.db.campaigns.find({
            "follow_up_enabled": True,
            "status": {"$in": ["active", "sending"]}  # Include 'sending' status
        }).to_list(length=100)
        return clean_document(campaigns)
    
    async def get_prospects_needing_follow_up_enhanced(self, campaign_id: str = None):
        """Enhanced method to get prospects needing follow-up with provider tracking"""
        await self.connect()
        
        query = {
            "follow_up_status": "active",
            "status": {"$ne": "unsubscribed"},
            "$or": [
                {"responded_at": {"$exists": False}},
                {"response_type": "auto_reply"}  # Continue follow-ups for auto-replies
            ]
        }
        
        if campaign_id:
            query["campaign_id"] = campaign_id
        
        prospects = await self.db.prospects.find(query).to_list(length=1000)
        return clean_document(prospects)
    
    async def get_prospect_original_provider(self, prospect_id: str):
        """Get the original email provider used for this prospect"""
        await self.connect()
        
        # First check prospect record
        prospect = await self.get_prospect_by_id(prospect_id)
        if prospect and prospect.get("email_provider_id"):
            provider = await self.get_email_provider_by_id(prospect["email_provider_id"])
            if provider:
                return provider
        
        # Fallback: Check first email sent to this prospect
        email_record = await self.db.emails.find_one({
            "prospect_id": prospect_id,
            "sent_by_us": True,
            "is_follow_up": False
        }, sort=[("sent_at", 1)])
        
        if email_record and email_record.get("email_provider_id"):
            provider = await self.get_email_provider_by_id(email_record["email_provider_id"])
            if provider:
                return provider
        
        # Final fallback: Default provider
        return await self.get_default_email_provider()
    
    async def update_campaign_follow_up_status(self, campaign_id: str, status: str):
        """Update campaign follow-up status"""
        await self.connect()
        result = await self.db.campaigns.update_one(
            {"id": campaign_id},
            {
                "$set": {
                    "follow_up_status": status,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        return result.modified_count > 0
    
    async def get_campaign_follow_up_stats(self, campaign_id: str):
        """Get follow-up statistics for a campaign"""
        await self.connect()
        
        # Get all prospects in this campaign
        prospects = await self.db.prospects.find({"campaign_id": campaign_id}).to_list(length=None)
        
        stats = {
            "total_prospects": len(prospects),
            "active_follow_ups": 0,
            "completed_follow_ups": 0,
            "stopped_follow_ups": 0,
            "responded_prospects": 0,
            "follow_up_emails_sent": 0
        }
        
        for prospect in prospects:
            if prospect.get("follow_up_status") == "active":
                stats["active_follow_ups"] += 1
            elif prospect.get("follow_up_status") == "completed":
                stats["completed_follow_ups"] += 1
            elif prospect.get("follow_up_status") == "stopped":
                stats["stopped_follow_ups"] += 1
            
            if prospect.get("responded_at"):
                stats["responded_prospects"] += 1
        
        # Count follow-up emails sent
        follow_up_emails = await self.db.emails.count_documents({
            "campaign_id": campaign_id,
            "is_follow_up": True,
            "status": "sent"
        })
        stats["follow_up_emails_sent"] = follow_up_emails
        
        return stats
    
    async def mark_follow_up_as_processed(self, prospect_id: str, follow_up_sequence: int):
        """Mark a follow-up as processed for this prospect"""
        await self.connect()
        result = await self.db.prospects.update_one(
            {"id": prospect_id},
            {
                "$set": {
                    "last_follow_up": datetime.utcnow(),
                    "follow_up_count": follow_up_sequence,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        return result.modified_count > 0
    
    async def get_follow_up_template_for_campaign(self, campaign_id: str, sequence: int):
        """Get appropriate follow-up template for campaign and sequence"""
        await self.connect()
        
        campaign = await self.get_campaign_by_id(campaign_id)
        if not campaign:
            return None
        
        # Check if campaign has specific follow-up templates
        follow_up_templates = campaign.get("follow_up_templates", [])
        if follow_up_templates and sequence <= len(follow_up_templates):
            template_id = follow_up_templates[sequence - 1]
            template = await self.get_template_by_id(template_id)
            if template:
                return template
        
        # Use the main campaign template as fallback
        template = await self.get_template_by_id(campaign.get("template_id"))
        return template

# Create enhanced database service instance
enhanced_db_service = EnhancedDatabaseService()