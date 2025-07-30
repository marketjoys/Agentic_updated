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
from app.services.enhanced_database import enhanced_db_service
from app.services.email_provider_service import email_provider_service
from app.services.groq_service import groq_service
from app.utils.helpers import generate_id, personalize_template

logger = logging.getLogger(__name__)

class EnhancedSmartFollowUpEngine:
    def __init__(self):
        self.auto_reply_indicators = [
            "out of office", "vacation", "away", "automatic reply", "auto-reply",
            "currently unavailable", "on holiday", "leave", "maternity leave",
            "sick leave", "conference", "traveling", "will be back"
        ]
        self.processing = False
    
    async def start_follow_up_engine(self):
        """Start the enhanced smart follow-up engine"""
        if self.processing:
            return {"status": "already_running"}
        
        self.processing = True
        logger.info("Starting enhanced smart follow-up engine with provider consistency...")
        
        try:
            # Start follow-up processing in background
            asyncio.create_task(self._process_follow_ups())
            return {"status": "started", "message": "Enhanced smart follow-up engine started"}
        except Exception as e:
            self.processing = False
            logger.error(f"Failed to start enhanced follow-up engine: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def stop_follow_up_engine(self):
        """Stop the smart follow-up engine"""
        self.processing = False
        logger.info("Enhanced smart follow-up engine stopped")
        return {"status": "stopped"}
    
    async def _process_follow_ups(self):
        """Main follow-up processing loop with enhanced provider tracking"""
        while self.processing:
            try:
                await self._check_and_send_follow_ups()
                await asyncio.sleep(60)  # Check every minute for precise timing
            except Exception as e:
                logger.error(f"Error in enhanced follow-up processing: {str(e)}")
                await asyncio.sleep(120)  # Wait longer on error
    
    async def _check_and_send_follow_ups(self):
        """Check for prospects that need follow-ups with enhanced provider consistency"""
        try:
            # Get active campaigns with follow-up enabled using enhanced method
            campaigns = await enhanced_db_service.get_active_follow_up_campaigns_enhanced()
            
            logger.info(f"Found {len(campaigns)} active follow-up campaigns")
            
            for campaign in campaigns:
                await self._process_campaign_follow_ups_enhanced(campaign)
                
        except Exception as e:
            logger.error(f"Error checking enhanced follow-ups: {str(e)}")
    
    async def _process_campaign_follow_ups_enhanced(self, campaign: Dict):
        """Process follow-ups for a specific campaign with enhanced provider consistency"""
        try:
            campaign_id = campaign["id"]
            follow_up_rule_id = campaign.get("follow_up_rule_id")
            
            # Get follow-up rule
            follow_up_rule = None
            if follow_up_rule_id:
                follow_up_rule = await db_service.get_follow_up_rule_by_id(follow_up_rule_id)
            
            # Use campaign follow-up intervals or default
            follow_up_intervals = campaign.get("follow_up_intervals", [3, 7, 14])
            if follow_up_rule:
                follow_up_intervals = [follow_up_rule["trigger_after_days"]]
            
            # Get prospects needing follow-up for this campaign using enhanced method
            prospects_needing_follow_up = await enhanced_db_service.get_prospects_needing_follow_up_enhanced(campaign_id)
            
            logger.info(f"Found {len(prospects_needing_follow_up)} prospects needing follow-up for campaign {campaign_id}")
            
            for prospect in prospects_needing_follow_up:
                await self._check_prospect_follow_up_enhanced(
                    prospect, campaign, follow_up_rule, follow_up_intervals
                )
                
        except Exception as e:
            logger.error(f"Error processing enhanced campaign follow-ups: {str(e)}")
    
    async def _check_prospect_follow_up_enhanced(self, prospect: Dict, campaign: Dict, 
                                               follow_up_rule: Optional[Dict], follow_up_intervals: List[int]):
        """Check if a prospect needs a follow-up email with enhanced datetime scheduling and provider consistency"""
        try:
            prospect_id = prospect["id"]
            
            # Skip if prospect has responded or follow-up is stopped
            if prospect.get("follow_up_status") in [FollowUpStatus.COMPLETED, FollowUpStatus.STOPPED]:
                return
            
            # Enhanced response detection - check if prospect responded after our last email
            last_email_sent_at = prospect.get("last_follow_up") or prospect.get("last_contact")
            if last_email_sent_at:
                has_responded = await db_service.check_prospect_response_after_our_email(
                    prospect_id, last_email_sent_at
                )
                
                if has_responded:
                    logger.info(f"Prospect {prospect_id} has responded after our email, stopping follow-ups")
                    await self._stop_prospect_follow_ups(prospect_id, "manual_response")
                    return
            
            # Check if this is an auto-reply response only
            if prospect.get("responded_at") and not await self._is_auto_reply_response(prospect_id):
                await self._stop_prospect_follow_ups(prospect_id, "manual_response")
                return
            
            # Check follow-up limits
            follow_up_count = prospect.get("follow_up_count", 0)
            max_follow_ups = follow_up_rule.get("max_follow_ups", 3) if follow_up_rule else 3
            
            if follow_up_count >= max_follow_ups:
                await self._stop_prospect_follow_ups(prospect_id, "limit_reached")
                return
            
            # Enhanced datetime-based follow-up scheduling with minute precision
            should_send_follow_up = await self._should_send_follow_up_now_enhanced(
                prospect, campaign, follow_up_rule, follow_up_intervals, follow_up_count
            )
            
            if should_send_follow_up:
                # Send follow-up with enhanced provider consistency
                await self._send_follow_up_email_enhanced(
                    prospect, campaign, follow_up_rule, follow_up_count + 1
                )
                
        except Exception as e:
            logger.error(f"Error checking enhanced prospect follow-up {prospect.get('id', 'unknown')}: {str(e)}")
    
    async def _should_send_follow_up_now_enhanced(self, prospect: Dict, campaign: Dict, 
                                                 follow_up_rule: Optional[Dict], follow_up_intervals: List[int],
                                                 follow_up_count: int) -> bool:
        """Enhanced follow-up timing logic with minute-level precision and timezone support"""
        try:
            import pytz
            from datetime import datetime, timedelta
            
            # Get campaign timezone
            campaign_timezone = campaign.get("follow_up_timezone", "UTC")
            tz = pytz.timezone(campaign_timezone)
            current_time = datetime.now(tz)
            
            # Check if campaign uses precise datetime scheduling
            schedule_type = campaign.get("follow_up_schedule_type", "interval")
            
            if schedule_type == "datetime" and campaign.get("follow_up_dates"):
                # Use precise datetime scheduling with minute precision
                follow_up_dates = campaign.get("follow_up_dates", [])
                
                if follow_up_count < len(follow_up_dates):
                    target_datetime = follow_up_dates[follow_up_count]
                    
                    # Handle both datetime objects and ISO strings
                    if isinstance(target_datetime, str):
                        target_datetime = datetime.fromisoformat(target_datetime.replace('Z', '+00:00'))
                    
                    # Convert to campaign timezone if needed
                    if target_datetime.tzinfo is None:
                        target_datetime = tz.localize(target_datetime)
                    else:
                        target_datetime = target_datetime.astimezone(tz)
                    
                    # Check if it's time to send (within 1 minute window for precision)
                    time_diff = (current_time - target_datetime).total_seconds()
                    if -60 <= time_diff <= 60:  # 1 minute window for precise scheduling
                        logger.info(f"Precise datetime follow-up ready for prospect {prospect['id']} at {target_datetime}")
                        return await self._is_in_campaign_time_window(campaign, current_time)
                    
                    return False
            
            # Fallback to interval-based scheduling with enhanced minute precision
            last_contact = prospect.get("last_contact") or prospect.get("created_at")
            last_follow_up = prospect.get("last_follow_up")
            
            if not last_contact:
                return False
            
            # Determine next follow-up interval with minute precision support
            if follow_up_count < len(follow_up_intervals):
                interval_value = follow_up_intervals[follow_up_count]
            else:
                interval_value = follow_up_intervals[-1]  # Use last interval for remaining follow-ups
            
            # Check if enough time has passed (timezone aware with minute precision)
            reference_time = last_follow_up or last_contact
            if reference_time.tzinfo is None:
                reference_time = pytz.UTC.localize(reference_time)
            
            reference_time = reference_time.astimezone(tz)
            time_since_last = current_time - reference_time
            
            # Enhanced interval handling: < 1440 treated as minutes, >= 1440 as days
            if interval_value < 1440:  # Less than 24 hours = minute-based
                minutes_since_last = time_since_last.total_seconds() / 60
                if minutes_since_last >= interval_value:
                    logger.info(f"Minute-based follow-up ready: {minutes_since_last:.1f} minutes >= {interval_value} minutes")
                    time_check_passed = True
                else:
                    time_check_passed = False
            else:
                # Day-based intervals (convert minutes to days)
                interval_days = interval_value / 1440  # Convert minutes to days
                days_since_last = time_since_last.total_seconds() / (24 * 3600)
                if days_since_last >= interval_days:
                    time_check_passed = True
                else:
                    time_check_passed = False
            
            if time_check_passed:
                # Check time window if specified
                if follow_up_rule and not await self._is_in_time_window(follow_up_rule):
                    return False
                
                # Check campaign-specific time window
                return await self._is_in_campaign_time_window(campaign, current_time)
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking enhanced follow-up timing: {str(e)}")
            return False
    
    async def _send_follow_up_email_enhanced(self, prospect: Dict, campaign: Dict, 
                                           follow_up_rule: Optional[Dict], follow_up_sequence: int):
        """Send a follow-up email with enhanced provider consistency and tracking"""
        try:
            prospect_id = prospect["id"]
            campaign_id = campaign["id"]
            
            # Get the ORIGINAL email provider used for this prospect
            original_provider = await enhanced_db_service.get_prospect_original_provider(prospect_id)
            if not original_provider:
                logger.error(f"No email provider available for follow-up to prospect {prospect_id}")
                return
            
            # Get follow-up template
            template = await self._get_follow_up_template_enhanced(campaign, follow_up_rule, follow_up_sequence)
            if not template:
                logger.warning(f"No follow-up template found for prospect {prospect_id}, sequence {follow_up_sequence}")
                return
            
            # Personalize email content
            personalized_content = personalize_template(template["content"], prospect)
            personalized_subject = personalize_template(template["subject"], prospect)
            
            # Add follow-up context to subject
            if follow_up_sequence > 1:
                personalized_subject = f"Re: {personalized_subject}"
            
            logger.info(f"Sending follow-up {follow_up_sequence} to {prospect['email']} via {original_provider['name']}")
            
            # Send email using the SAME provider as original campaign
            success, error = await email_provider_service.send_email(
                original_provider["id"], 
                prospect["email"], 
                personalized_subject, 
                personalized_content
            )
            
            if success:
                # Create enhanced email record with complete tracking
                email_id = generate_id()
                email_record = {
                    "id": email_id,
                    "prospect_id": prospect_id,
                    "campaign_id": campaign_id,
                    "email_provider_id": original_provider["id"],  # Same provider as original
                    "recipient_email": prospect["email"],
                    "subject": personalized_subject,
                    "content": personalized_content,
                    "status": "sent",
                    "sent_at": datetime.utcnow(),
                    "is_follow_up": True,
                    "follow_up_sequence": follow_up_sequence,
                    "created_at": datetime.utcnow(),
                    "sent_by_us": True,
                    "thread_id": f"thread_{prospect_id}",
                    "template_id": template["id"],
                    "provider_name": original_provider["name"]
                }
                
                await db_service.create_email_record(email_record)
                
                # Mark email as sent by us
                await db_service.mark_email_as_sent_by_us(email_id, f"thread_{prospect_id}")
                
                # Update prospect follow-up tracking
                await enhanced_db_service.mark_follow_up_as_processed(prospect_id, follow_up_sequence)
                
                # Update thread context with follow-up message
                await enhanced_db_service.create_or_update_thread_context(
                    prospect_id,
                    campaign_id,
                    original_provider["id"],
                    {
                        "type": "sent",
                        "recipient": prospect["email"],
                        "subject": personalized_subject,
                        "content": personalized_content,
                        "timestamp": datetime.utcnow(),
                        "is_follow_up": True,
                        "follow_up_sequence": follow_up_sequence,
                        "email_id": email_id,
                        "template_id": template["id"],
                        "provider_id": original_provider["id"],
                        "sent_by_us": True
                    }
                )
                
                logger.info(f"Enhanced follow-up email sent to {prospect['email']} (sequence: {follow_up_sequence}) via {original_provider['name']}")
                
            else:
                logger.error(f"Failed to send enhanced follow-up email to {prospect['email']}: {error}")
                
        except Exception as e:
            logger.error(f"Error sending enhanced follow-up email: {str(e)}")
    
    async def _get_follow_up_template_enhanced(self, campaign: Dict, follow_up_rule: Optional[Dict], 
                                             follow_up_sequence: int) -> Optional[Dict]:
        """Get the appropriate follow-up template with enhanced logic"""
        try:
            campaign_id = campaign["id"]
            
            # Try enhanced database method first
            template = await enhanced_db_service.get_follow_up_template_for_campaign(campaign_id, follow_up_sequence)
            if template:
                return template
            
            # Fallback to original logic
            if follow_up_rule:
                template_ids = follow_up_rule.get("template_ids", [])
                if template_ids and follow_up_sequence <= len(template_ids):
                    template_id = template_ids[follow_up_sequence - 1]
                    template = await db_service.get_template_by_id(template_id)
                    if template:
                        return template
            
            # Try campaign follow-up templates
            follow_up_templates = campaign.get("follow_up_templates", [])
            if follow_up_templates and follow_up_sequence <= len(follow_up_templates):
                template_id = follow_up_templates[follow_up_sequence - 1]
                template = await db_service.get_template_by_id(template_id)
                if template:
                    return template
            
            # Use main campaign template as final fallback
            template = await db_service.get_template_by_id(campaign.get("template_id"))
            if template:
                # Create a follow-up variant
                template["subject"] = f"Follow-up: {template.get('subject', '')}"
                return template
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting enhanced follow-up template: {str(e)}")
            return None
    
    async def _is_in_campaign_time_window(self, campaign: Dict, current_time) -> bool:
        """Check if current time is within campaign's allowed sending window"""
        try:
            # Check day of week
            current_day = current_time.strftime("%A").lower()
            allowed_days = campaign.get("follow_up_days_of_week", 
                                     ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"])
            
            if current_day not in allowed_days:
                return False
            
            # Check time window
            start_time = campaign.get("follow_up_time_window_start", "00:00")  # Allow 24/7 by default
            end_time = campaign.get("follow_up_time_window_end", "23:59")
            current_time_str = current_time.strftime("%H:%M")
            
            if start_time <= current_time_str <= end_time:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking enhanced campaign time window: {str(e)}")
            return True  # Default to allowing send
    
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
                "response_type": reason,
                "updated_at": datetime.utcnow()
            })
            
            logger.info(f"Follow-ups stopped for prospect {prospect_id}: {reason}")
            
        except Exception as e:
            logger.error(f"Error stopping follow-ups for prospect {prospect_id}: {str(e)}")
    
    async def get_enhanced_follow_up_statistics(self) -> Dict:
        """Get enhanced follow-up statistics with provider tracking"""
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
            provider_usage = {}
            
            for prospect in all_prospects:
                count = prospect.get("follow_up_count", 0)
                follow_up_counts[count] = follow_up_counts.get(count, 0) + 1
                
                # Track provider usage
                provider_id = prospect.get("email_provider_id", "unknown")
                provider_usage[provider_id] = provider_usage.get(provider_id, 0) + 1
            
            return {
                "total_prospects": total_prospects,
                "active_follow_ups": active_follow_ups,
                "stopped_follow_ups": stopped_follow_ups,
                "completed_follow_ups": completed_follow_ups,
                "response_rate": round(response_rate, 2),
                "follow_up_distribution": follow_up_counts,
                "provider_usage": provider_usage,
                "engine_status": "running" if self.processing else "stopped",
                "enhancement_version": "2.0"
            }
            
        except Exception as e:
            logger.error(f"Error getting enhanced follow-up statistics: {str(e)}")
            return {}

# Create enhanced global smart follow-up engine instance
enhanced_smart_follow_up_engine = EnhancedSmartFollowUpEngine()