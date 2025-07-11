import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
import re
import json
from app.models import FollowUpStatus
from app.services.database import db_service
from app.services.email_provider_service import email_provider_service
from app.services.groq_service import groq_service
from app.services.response_verification_service import response_verification_service
from app.services.knowledge_base_service import knowledge_base_service
from app.services.smart_follow_up_engine import smart_follow_up_engine
from app.utils.helpers import generate_id, personalize_template

logger = logging.getLogger(__name__)

class EnhancedEmailProcessor:
    def __init__(self):
        self.processing = False
        self.email_queue = []
        self.response_patterns = {
            "positive": ["yes", "interested", "tell me more", "sounds good", "would like to"],
            "negative": ["not interested", "no thanks", "remove me", "unsubscribe"],
            "neutral": ["maybe", "not sure", "let me think", "not now"]
        }
    
    async def start_email_processing(self):
        """Start the enhanced email processing engine"""
        if self.processing:
            return {"status": "already_running"}
        
        self.processing = True
        logger.info("Starting enhanced email processing engine...")
        
        try:
            # Start email processing in background
            asyncio.create_task(self._process_emails_continuously())
            return {"status": "started", "message": "Enhanced email processing engine started"}
        except Exception as e:
            self.processing = False
            logger.error(f"Failed to start email processing engine: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def stop_email_processing(self):
        """Stop the enhanced email processing engine"""
        self.processing = False
        logger.info("Enhanced email processing engine stopped")
        return {"status": "stopped"}
    
    async def _process_emails_continuously(self):
        """Continuously process emails from all providers"""
        while self.processing:
            try:
                await self._check_all_providers_for_emails()
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in continuous email processing: {str(e)}")
                await asyncio.sleep(300)  # Wait longer on error
    
    async def _check_all_providers_for_emails(self):
        """Check all email providers for new emails"""
        try:
            # Get all active email providers
            providers = await email_provider_service.get_all_providers()
            active_providers = [p for p in providers if p.get("is_active", True)]
            
            for provider in active_providers:
                await self._check_provider_for_emails(provider)
                
        except Exception as e:
            logger.error(f"Error checking providers for emails: {str(e)}")
    
    async def _check_provider_for_emails(self, provider: Dict):
        """Check a specific provider for new emails"""
        try:
            provider_id = provider["id"]
            
            # Get new emails from the provider
            new_emails = await email_provider_service.retrieve_emails(provider_id)
            
            for email_data in new_emails:
                await self._process_incoming_email(email_data, provider_id)
                
        except Exception as e:
            logger.error(f"Error checking provider {provider.get('id', 'unknown')}: {str(e)}")
    
    async def _process_incoming_email(self, email_data: Dict, provider_id: str):
        """Process a single incoming email"""
        try:
            sender_email = email_data.get("sender_email", "")
            subject = email_data.get("subject", "")
            content = email_data.get("content", "")
            message_id = email_data.get("message_id", "")
            
            # Find the prospect associated with this email
            prospect = await db_service.get_prospect_by_email(sender_email)
            if not prospect:
                logger.info(f"No prospect found for email: {sender_email}")
                return
            
            prospect_id = prospect["id"]
            
            # Check if this email is part of an existing thread
            thread = await db_service.get_thread_by_prospect_id(prospect_id)
            if not thread:
                # Create new thread
                thread_data = {
                    "id": generate_id(),
                    "prospect_id": prospect_id,
                    "campaign_id": prospect.get("campaign_id", ""),
                    "email_provider_id": provider_id,
                    "messages": [],
                    "status": "active",
                    "created_at": datetime.utcnow(),
                    "last_activity": datetime.utcnow()
                }
                await db_service.create_thread_context(thread_data)
                thread = thread_data
            
            # Add message to thread
            message_data = {
                "id": generate_id(),
                "type": "received",
                "content": content,
                "subject": subject,
                "sender": sender_email,
                "message_id": message_id,
                "timestamp": datetime.utcnow()
            }
            
            await db_service.add_message_to_thread(thread["id"], message_data)
            
            # Process the email for follow-up decisions
            follow_up_result = await smart_follow_up_engine.process_email_response(
                prospect_id, content, subject
            )
            
            # Classify intents using enhanced AI
            classified_intents = await groq_service.classify_intents(
                content, subject, use_custom_prompt=True
            )
            
            # Generate AI response if auto-response is enabled
            if classified_intents and any(intent.get("auto_respond", False) for intent in classified_intents):
                response_data = await self._generate_ai_response(
                    prospect, content, subject, classified_intents, thread
                )
                
                if response_data and not response_data.get("error"):
                    # Verify response quality
                    verification_result = await response_verification_service.verify_response(
                        message_data["id"], response_data.get("content", ""),
                        content, classified_intents, thread.get("messages", []), prospect
                    )
                    
                    # Send response if verification passes
                    if verification_result.get("status") == "approved":
                        await self._send_ai_response(
                            prospect, response_data, provider_id, thread["id"]
                        )
                    elif verification_result.get("status") == "needs_review":
                        logger.info(f"Response for {prospect_id} needs manual review")
                        await self._queue_for_manual_review(verification_result)
            
            # Update thread activity
            await db_service.update_thread_last_activity(thread["id"], datetime.utcnow())
            
            logger.info(f"Processed email from {sender_email} for prospect {prospect_id}")
            
        except Exception as e:
            logger.error(f"Error processing incoming email: {str(e)}")
    
    async def _generate_ai_response(self, prospect: Dict, original_content: str, 
                                  subject: str, classified_intents: List[Dict], 
                                  thread: Dict) -> Dict:
        """Generate AI response using enhanced Groq service"""
        try:
            # Get conversation context
            conversation_context = thread.get("messages", [])
            
            # Generate response using enhanced AI
            response_data = await groq_service.generate_response(
                original_content, subject, classified_intents,
                conversation_context, prospect,
                use_knowledge_base=True, use_custom_prompt=True
            )
            
            return response_data
            
        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            return {"error": str(e)}
    
    async def _send_ai_response(self, prospect: Dict, response_data: Dict, 
                               provider_id: str, thread_id: str):
        """Send AI-generated response"""
        try:
            prospect_email = prospect["email"]
            response_subject = response_data.get("subject", "")
            response_content = response_data.get("content", "")
            
            # Send email using email provider service
            success, error = await email_provider_service.send_email(
                provider_id, prospect_email, response_subject, response_content
            )
            
            if success:
                # Create email record
                email_record = {
                    "id": generate_id(),
                    "prospect_id": prospect["id"],
                    "campaign_id": prospect.get("campaign_id", ""),
                    "email_provider_id": provider_id,
                    "subject": response_subject,
                    "content": response_content,
                    "status": "sent",
                    "sent_at": datetime.utcnow(),
                    "ai_generated": True,
                    "verification_status": "approved",
                    "created_at": datetime.utcnow()
                }
                
                await db_service.create_email_record(email_record)
                
                # Add to thread
                message_data = {
                    "id": generate_id(),
                    "type": "sent",
                    "content": response_content,
                    "subject": response_subject,
                    "recipient": prospect_email,
                    "timestamp": datetime.utcnow(),
                    "ai_generated": True
                }
                
                await db_service.add_message_to_thread(thread_id, message_data)
                
                logger.info(f"AI response sent to {prospect_email}")
                
            else:
                logger.error(f"Failed to send AI response to {prospect_email}: {error}")
                
        except Exception as e:
            logger.error(f"Error sending AI response: {str(e)}")
    
    async def _queue_for_manual_review(self, verification_result: Dict):
        """Queue verification for manual review"""
        try:
            # Implementation for manual review queue
            # This could be integrated with a review dashboard
            logger.info(f"Queued verification {verification_result.get('id')} for manual review")
            
        except Exception as e:
            logger.error(f"Error queuing for manual review: {str(e)}")
    
    async def process_campaign_emails(self, campaign_id: str) -> Dict:
        """Process emails for a specific campaign with enhanced AI"""
        try:
            # Get campaign details
            campaign = await db_service.get_campaign_by_id(campaign_id)
            if not campaign:
                return {"error": "Campaign not found"}
            
            # Get all prospects for this campaign
            prospects = await db_service.get_prospects()
            campaign_prospects = [p for p in prospects if p.get("campaign_id") == campaign_id]
            
            if not campaign_prospects:
                return {"error": "No prospects found for this campaign"}
            
            # Get template
            template = await db_service.get_template_by_id(campaign["template_id"])
            if not template:
                return {"error": "Template not found"}
            
            # Get email provider
            provider_id = campaign.get("email_provider_id")
            if not provider_id:
                # Use default provider
                default_provider = await email_provider_service.get_default_provider()
                if not default_provider:
                    return {"error": "No email provider configured"}
                provider_id = default_provider["id"]
            
            # Process each prospect
            results = {
                "total_prospects": len(campaign_prospects),
                "emails_sent": 0,
                "emails_failed": 0,
                "enhanced_responses": 0,
                "errors": []
            }
            
            for prospect in campaign_prospects:
                try:
                    # Use knowledge base to enhance template
                    enhanced_content = await self._enhance_template_with_knowledge(
                        template, prospect, campaign
                    )
                    
                    # Personalize content
                    personalized_content = personalize_template(enhanced_content, prospect)
                    personalized_subject = personalize_template(template["subject"], prospect)
                    
                    # Send email
                    success, error = await email_provider_service.send_email(
                        provider_id, prospect["email"], personalized_subject, personalized_content
                    )
                    
                    if success:
                        results["emails_sent"] += 1
                        if enhanced_content != template["content"]:
                            results["enhanced_responses"] += 1
                        
                        # Create email record
                        email_record = {
                            "id": generate_id(),
                            "prospect_id": prospect["id"],
                            "campaign_id": campaign_id,
                            "email_provider_id": provider_id,
                            "subject": personalized_subject,
                            "content": personalized_content,
                            "status": "sent",
                            "sent_at": datetime.utcnow(),
                            "ai_generated": enhanced_content != template["content"],
                            "created_at": datetime.utcnow()
                        }
                        
                        await db_service.create_email_record(email_record)
                        
                        # Update prospect last contact
                        await db_service.update_prospect_last_contact(prospect["id"], datetime.utcnow())
                        
                    else:
                        results["emails_failed"] += 1
                        results["errors"].append(f"Failed to send to {prospect['email']}: {error}")
                        
                except Exception as e:
                    results["emails_failed"] += 1
                    results["errors"].append(f"Error processing {prospect.get('email', 'unknown')}: {str(e)}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error processing campaign emails: {str(e)}")
            return {"error": str(e)}
    
    async def _enhance_template_with_knowledge(self, template: Dict, prospect: Dict, 
                                             campaign: Dict) -> str:
        """Enhance template content with knowledge base information"""
        try:
            # Get relevant knowledge articles
            prospect_industry = prospect.get("industry", "")
            prospect_company = prospect.get("company", "")
            
            # Search for relevant knowledge
            relevant_knowledge = await knowledge_base_service.get_knowledge_for_personalization(prospect)
            
            if not relevant_knowledge:
                return template["content"]
            
            # Use AI to enhance template with knowledge
            enhancement_prompt = f"""
            Enhance the following email template with relevant knowledge base information for better personalization.
            
            Original Template:
            {template["content"]}
            
            Prospect Information:
            - Company: {prospect_company}
            - Industry: {prospect_industry}
            - Job Title: {prospect.get("job_title", "")}
            
            Relevant Knowledge:
            {chr(10).join([f"- {article['title']}: {article['content'][:200]}..." for article in relevant_knowledge[:3]])}
            
            Instructions:
            1. Integrate relevant knowledge naturally into the template
            2. Maintain the original tone and structure
            3. Add industry-specific insights where appropriate
            4. Keep personalization placeholders intact
            5. Make the content more compelling and relevant
            
            Return only the enhanced template content.
            """
            
            response = await groq_service.client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": "You are an expert email copywriter who enhances templates with relevant knowledge."},
                    {"role": "user", "content": enhancement_prompt}
                ],
                temperature=0.3,
                max_tokens=800
            )
            
            enhanced_content = response.choices[0].message.content.strip()
            
            # Update knowledge usage
            for article in relevant_knowledge[:3]:
                await db_service.increment_knowledge_article_usage(article["id"])
            
            return enhanced_content
            
        except Exception as e:
            logger.error(f"Error enhancing template with knowledge: {str(e)}")
            return template["content"]
    
    async def get_processing_statistics(self) -> Dict:
        """Get email processing statistics"""
        try:
            # Get recent email statistics
            recent_emails = await db_service.db.emails.find({
                "created_at": {"$gte": datetime.utcnow() - timedelta(days=7)}
            }).to_list(length=1000)
            
            stats = {
                "total_processed": len(recent_emails),
                "ai_generated": len([e for e in recent_emails if e.get("ai_generated", False)]),
                "verification_approved": len([e for e in recent_emails if e.get("verification_status") == "approved"]),
                "verification_pending": len([e for e in recent_emails if e.get("verification_status") == "pending"]),
                "engine_status": "running" if self.processing else "stopped",
                "last_processed": datetime.utcnow().isoformat() if recent_emails else None
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting processing statistics: {str(e)}")
            return {"error": str(e)}

# Create global enhanced email processor instance
enhanced_email_processor = EnhancedEmailProcessor()