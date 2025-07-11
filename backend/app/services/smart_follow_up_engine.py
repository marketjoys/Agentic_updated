import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
import re
from app.models import FollowUpRule, FollowUpStatus
from app.services.database import db_service
from app.services.email_provider_service import email_provider_service
from app.services.groq_service import groq_service
from app.utils.helpers import generate_id, personalize_template

logger = logging.getLogger(__name__)

class SmartFollowUpEngine:
    def __init__(self):
        self.auto_reply_indicators = [
            "out of office", "vacation", "away", "automatic reply", "auto-reply",
            "currently unavailable", "on holiday", "leave", "maternity leave",
            "sick leave", "conference", "traveling", "will be back"
        ]
        self.processing = False
    
    async def start_follow_up_engine(self):
        """Start the smart follow-up engine"""
        if self.processing:
            return {"status": "already_running"}
        
        self.processing = True
        logger.info("Starting smart follow-up engine...")
        
        try:
            # Start follow-up processing in background
            asyncio.create_task(self._process_follow_ups())
            return {"status": "started", "message": "Smart follow-up engine started"}
        except Exception as e:
            self.processing = False
            logger.error(f"Failed to start follow-up engine: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def stop_follow_up_engine(self):
        """Stop the smart follow-up engine"""
        self.processing = False
        logger.info("Smart follow-up engine stopped")
        return {"status": "stopped"}
    
    async def _process_follow_ups(self):
        """Main follow-up processing loop"""
        while self.processing:
            try:
                await self._check_and_send_follow_ups()
                await asyncio.sleep(300)  # Check every 5 minutes
            except Exception as e:
                logger.error(f"Error in follow-up processing: {str(e)}")
                await asyncio.sleep(600)  # Wait longer on error
    
    async def _check_and_send_follow_ups(self):
        """Check for prospects that need follow-ups and send them"""
        try:
            # Get active campaigns with follow-up enabled
            campaigns = await db_service.get_campaigns()
            active_campaigns = [c for c in campaigns if c.get("follow_up_enabled", False) and c.get("status") == "active"]
            
            for campaign in active_campaigns:
                await self._process_campaign_follow_ups(campaign)
                
        except Exception as e:
            logger.error(f"Error checking follow-ups: {str(e)}")
    
    async def _process_campaign_follow_ups(self, campaign: Dict):
        """Process follow-ups for a specific campaign"""
        try:
            campaign_id = campaign["id"]
            follow_up_rule_id = campaign.get("follow_up_rule_id")
            
            # Get follow-up rule
            follow_up_rule = None
            if follow_up_rule_id:
                follow_up_rule = await db_service.get_follow_up_rule_by_id(follow_up_rule_id)
            
            # Use default follow-up intervals if no rule specified
            follow_up_intervals = campaign.get("follow_up_intervals", [3, 7, 14])
            if follow_up_rule:
                follow_up_intervals = [follow_up_rule["trigger_after_days"]]
            
            # Get prospects for this campaign
            all_prospects = await db_service.get_prospects()
            campaign_prospects = [p for p in all_prospects if p.get("campaign_id") == campaign_id]
            
            for prospect in campaign_prospects:
                await self._check_prospect_follow_up(prospect, campaign, follow_up_rule, follow_up_intervals)
                
        except Exception as e:
            logger.error(f"Error processing campaign follow-ups: {str(e)}")
    
    async def _check_prospect_follow_up(self, prospect: Dict, campaign: Dict, 
                                      follow_up_rule: Optional[Dict], follow_up_intervals: List[int]):
        """Check if a prospect needs a follow-up email"""
        try:
            prospect_id = prospect["id"]
            
            # Skip if prospect has responded or follow-up is stopped
            if prospect.get("follow_up_status") in [FollowUpStatus.COMPLETED, FollowUpStatus.STOPPED]:
                return
            
            # Skip if prospect has responded (unless auto-reply)
            if prospect.get("responded_at") and not await self._is_auto_reply_response(prospect_id):
                await self._stop_prospect_follow_ups(prospect_id, "manual_response")
                return
            
            # Check follow-up limits
            follow_up_count = prospect.get("follow_up_count", 0)
            max_follow_ups = follow_up_rule.get("max_follow_ups", 3) if follow_up_rule else 3
            
            if follow_up_count >= max_follow_ups:
                await self._stop_prospect_follow_ups(prospect_id, "limit_reached")
                return
            
            # Check if it's time for next follow-up
            last_contact = prospect.get("last_contact") or prospect.get("created_at")
            last_follow_up = prospect.get("last_follow_up")
            
            if not last_contact:
                return
            
            # Determine next follow-up interval
            if follow_up_count < len(follow_up_intervals):
                interval_days = follow_up_intervals[follow_up_count]
            else:
                interval_days = follow_up_intervals[-1]  # Use last interval for remaining follow-ups
            
            # Check if enough time has passed
            time_since_last = datetime.utcnow() - last_contact
            if last_follow_up:
                time_since_last = datetime.utcnow() - last_follow_up
            
            if time_since_last.days >= interval_days:
                # Check time window if specified
                if follow_up_rule and not await self._is_in_time_window(follow_up_rule):
                    return
                
                # Send follow-up
                await self._send_follow_up_email(prospect, campaign, follow_up_rule, follow_up_count + 1)
                
        except Exception as e:
            logger.error(f"Error checking prospect follow-up {prospect.get('id', 'unknown')}: {str(e)}")
    
    async def _send_follow_up_email(self, prospect: Dict, campaign: Dict, 
                                  follow_up_rule: Optional[Dict], follow_up_sequence: int):
        """Send a follow-up email to a prospect"""
        try:
            prospect_id = prospect["id"]
            campaign_id = campaign["id"]
            
            # Get follow-up template
            template = await self._get_follow_up_template(campaign, follow_up_rule, follow_up_sequence)
            if not template:
                logger.warning(f"No follow-up template found for prospect {prospect_id}, sequence {follow_up_sequence}")
                return
            
            # Get email provider
            provider_id = campaign.get("email_provider_id")
            if not provider_id:
                # Use default provider
                default_provider = await email_provider_service.get_default_provider()
                if not default_provider:
                    logger.error("No email provider available for follow-up")
                    return
                provider_id = default_provider["id"]
            
            # Personalize email content
            personalized_content = personalize_template(template["content"], prospect)
            personalized_subject = personalize_template(template["subject"], prospect)
            
            # Add follow-up context
            personalized_subject = f"Re: {personalized_subject}" if follow_up_sequence > 1 else personalized_subject
            
            # Send email
            success, error = await email_provider_service.send_email(
                provider_id, prospect["email"], personalized_subject, personalized_content
            )
            
            if success:
                # Create email record
                email_record = {
                    "id": generate_id(),
                    "prospect_id": prospect_id,
                    "campaign_id": campaign_id,
                    "email_provider_id": provider_id,
                    "subject": personalized_subject,
                    "content": personalized_content,
                    "status": "sent",
                    "sent_at": datetime.utcnow(),
                    "is_follow_up": True,
                    "follow_up_sequence": follow_up_sequence,
                    "created_at": datetime.utcnow()
                }
                
                await db_service.create_email_record(email_record)
                
                # Update prospect follow-up tracking
                await db_service.update_prospect(prospect_id, {
                    "follow_up_count": follow_up_sequence,
                    "last_follow_up": datetime.utcnow(),
                    "follow_up_status": FollowUpStatus.ACTIVE
                })
                
                logger.info(f"Follow-up email sent to {prospect['email']} (sequence: {follow_up_sequence})")
                
            else:
                logger.error(f"Failed to send follow-up email to {prospect['email']}: {error}")
                
        except Exception as e:
            logger.error(f"Error sending follow-up email: {str(e)}")
    
    async def _get_follow_up_template(self, campaign: Dict, follow_up_rule: Optional[Dict], 
                                    follow_up_sequence: int) -> Optional[Dict]:
        """Get the appropriate follow-up template"""
        try:
            # Try to get template from follow-up rule first
            if follow_up_rule:
                template_ids = follow_up_rule.get("template_ids", [])
                if template_ids and follow_up_sequence <= len(template_ids):
                    template_id = template_ids[follow_up_sequence - 1]
                    template = await db_service.get_template_by_id(template_id)
                    if template:
                        return template
            
            # Try to get template from campaign follow-up templates
            follow_up_templates = campaign.get("follow_up_templates", [])
            if follow_up_templates and follow_up_sequence <= len(follow_up_templates):
                template_id = follow_up_templates[follow_up_sequence - 1]
                template = await db_service.get_template_by_id(template_id)
                if template:
                    return template
            
            # Get generic follow-up templates
            all_templates = await db_service.get_templates()
            follow_up_templates = [t for t in all_templates if t.get("type") == "follow_up"]
            
            if follow_up_templates:
                # Use templates in order, or repeat last one
                if follow_up_sequence <= len(follow_up_templates):
                    return follow_up_templates[follow_up_sequence - 1]
                else:
                    return follow_up_templates[-1]  # Use last template for remaining follow-ups
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting follow-up template: {str(e)}")
            return None
    
    async def _is_in_time_window(self, follow_up_rule: Dict) -> bool:
        """Check if current time is within the allowed sending window"""
        try:
            now = datetime.utcnow()
            
            # Check day of week
            send_days = follow_up_rule.get("send_days", ["monday", "tuesday", "wednesday", "thursday", "friday"])
            current_day = now.strftime("%A").lower()
            
            if follow_up_rule.get("exclude_weekends", True) and current_day in ["saturday", "sunday"]:
                return False
            
            if current_day not in send_days:
                return False
            
            # Check time window
            start_time = follow_up_rule.get("send_time_start", "09:00")
            end_time = follow_up_rule.get("send_time_end", "17:00")
            
            current_time = now.strftime("%H:%M")
            
            if start_time <= current_time <= end_time:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking time window: {str(e)}")
            return True  # Default to allowing send
    
    async def _is_auto_reply_response(self, prospect_id: str) -> bool:
        """Check if the last response from prospect was an auto-reply"""
        try:
            # Get thread for prospect
            thread = await db_service.get_thread_by_prospect_id(prospect_id)
            if not thread:
                return False
            
            # Get last received message
            messages = thread.get("messages", [])
            received_messages = [m for m in messages if m.get("type") == "received"]
            
            if not received_messages:
                return False
            
            last_message = received_messages[-1]
            content = last_message.get("content", "").lower()
            subject = last_message.get("subject", "").lower()
            
            # Check for auto-reply indicators
            for indicator in self.auto_reply_indicators:
                if indicator in content or indicator in subject:
                    return True
            
            # Check for specific auto-reply patterns
            auto_reply_patterns = [
                r"i am (currently )?out of (the )?office",
                r"automatic reply",
                r"will be (back|returning) on",
                r"on vacation until",
                r"away until",
                r"currently unavailable"
            ]
            
            for pattern in auto_reply_patterns:
                if re.search(pattern, content) or re.search(pattern, subject):
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking auto-reply: {str(e)}")
            return False
    
    async def _stop_prospect_follow_ups(self, prospect_id: str, reason: str):
        """Stop follow-ups for a prospect"""
        try:
            await db_service.update_prospect(prospect_id, {
                "follow_up_status": FollowUpStatus.STOPPED,
                "response_type": reason
            })
            
            logger.info(f"Follow-ups stopped for prospect {prospect_id}: {reason}")
            
        except Exception as e:
            logger.error(f"Error stopping follow-ups for prospect {prospect_id}: {str(e)}")
    
    async def process_email_response(self, prospect_id: str, email_content: str, subject: str):
        """Process an email response and determine if follow-ups should continue"""
        try:
            # Check if it's an auto-reply
            is_auto_reply = await self._detect_auto_reply(email_content, subject)
            
            if is_auto_reply:
                # Update prospect but don't stop follow-ups
                await db_service.update_prospect(prospect_id, {
                    "responded_at": datetime.utcnow(),
                    "response_type": "auto_reply"
                })
                
                logger.info(f"Auto-reply detected for prospect {prospect_id}, continuing follow-ups")
                return {"action": "continue", "reason": "auto_reply"}
            else:
                # Manual response - stop follow-ups
                await self._stop_prospect_follow_ups(prospect_id, "manual_response")
                
                await db_service.update_prospect(prospect_id, {
                    "responded_at": datetime.utcnow(),
                    "response_type": "manual"
                })
                
                logger.info(f"Manual response detected for prospect {prospect_id}, stopping follow-ups")
                return {"action": "stop", "reason": "manual_response"}
            
        except Exception as e:
            logger.error(f"Error processing email response: {str(e)}")
            return {"action": "continue", "reason": "error"}
    
    async def _detect_auto_reply(self, email_content: str, subject: str) -> bool:
        """Detect if an email is an automatic reply"""
        try:
            content_lower = email_content.lower()
            subject_lower = subject.lower()
            
            # Check for auto-reply indicators
            for indicator in self.auto_reply_indicators:
                if indicator in content_lower or indicator in subject_lower:
                    return True
            
            # Use AI for more sophisticated detection
            ai_result = await groq_service.client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": "You are an expert at detecting automatic email replies. Respond with only 'true' if the email is an automatic reply, or 'false' if it's a manual response."},
                    {"role": "user", "content": f"Subject: {subject}\n\nContent: {email_content[:500]}"}
                ],
                temperature=0.1,
                max_tokens=10
            )
            
            ai_response = ai_result.choices[0].message.content.strip().lower()
            return "true" in ai_response
            
        except Exception as e:
            logger.error(f"Error detecting auto-reply: {str(e)}")
            return False
    
    async def get_follow_up_statistics(self) -> Dict:
        """Get follow-up statistics"""
        try:
            all_prospects = await db_service.get_prospects()
            
            total_prospects = len(all_prospects)
            active_follow_ups = len([p for p in all_prospects if p.get("follow_up_status") == FollowUpStatus.ACTIVE])
            stopped_follow_ups = len([p for p in all_prospects if p.get("follow_up_status") == FollowUpStatus.STOPPED])
            completed_follow_ups = len([p for p in all_prospects if p.get("follow_up_status") == FollowUpStatus.COMPLETED])
            
            # Calculate response rates
            responded_prospects = len([p for p in all_prospects if p.get("responded_at")])
            response_rate = (responded_prospects / total_prospects * 100) if total_prospects > 0 else 0
            
            # Get follow-up counts
            follow_up_counts = {}
            for prospect in all_prospects:
                count = prospect.get("follow_up_count", 0)
                follow_up_counts[count] = follow_up_counts.get(count, 0) + 1
            
            return {
                "total_prospects": total_prospects,
                "active_follow_ups": active_follow_ups,
                "stopped_follow_ups": stopped_follow_ups,
                "completed_follow_ups": completed_follow_ups,
                "response_rate": round(response_rate, 2),
                "follow_up_distribution": follow_up_counts,
                "engine_status": "running" if self.processing else "stopped"
            }
            
        except Exception as e:
            logger.error(f"Error getting follow-up statistics: {str(e)}")
            return {}

# Create global smart follow-up engine instance
smart_follow_up_engine = SmartFollowUpEngine()