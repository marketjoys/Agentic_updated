import asyncio
import imaplib
import email
from email.header import decode_header
from datetime import datetime
import logging
from typing import Dict, List, Optional
import os
from app.services.database import db_service
from app.services.enhanced_database import enhanced_db_service
from app.services.groq_service_fixed import groq_service  # Use fixed version
from app.utils.helpers import send_email, generate_id, personalize_template

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailProcessorFixed:
    def __init__(self):
        # Default IMAP settings (for backward compatibility)
        self.imap_host = os.getenv("IMAP_HOST", "imap.gmail.com")
        self.imap_port = int(os.getenv("IMAP_PORT", 993))
        self.email_username = os.getenv("SMTP_USERNAME")
        self.email_password = os.getenv("SMTP_PASSWORD")
        
        self.processing = False
        self.monitored_providers = {}  # Dictionary to store provider configurations
        self.provider_threads = {}  # Dictionary to store monitoring tasks per provider
        
    async def start_monitoring(self):
        """Start IMAP email monitoring for all enabled providers"""
        if self.processing:
            return {"status": "already_running"}
        
        self.processing = True
        logger.info("Starting FIXED email monitoring...")
        
        try:
            # Load all enabled email providers from database
            await self._load_enabled_providers()
            
            # Start monitoring in background
            asyncio.create_task(self._monitor_all_providers())
            return {"status": "started", "message": "FIXED Email monitoring started", "providers_count": len(self.monitored_providers)}
        except Exception as e:
            self.processing = False
            logger.error(f"Failed to start FIXED email monitoring: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def _load_enabled_providers(self):
        """Load all email providers that have IMAP enabled"""
        try:
            await db_service.connect()
            
            # Get all providers with IMAP enabled
            providers = await db_service.db.email_providers.find({
                "is_active": True,
                "imap_enabled": True,
                "$and": [
                    {"imap_host": {"$ne": ""}},
                    {"imap_username": {"$ne": ""}},
                    {"imap_password": {"$ne": ""}}
                ]
            }).to_list(length=None)
            
            # Store provider configurations
            for provider in providers:
                if "_id" in provider:
                    provider.pop("_id")
                self.monitored_providers[provider["id"]] = {
                    "id": provider["id"],
                    "name": provider["name"],
                    "imap_host": provider["imap_host"],
                    "imap_port": provider.get("imap_port", 993),
                    "imap_username": provider["imap_username"],
                    "imap_password": provider["imap_password"],
                    "email_address": provider["email_address"],
                    "provider_type": provider["provider_type"],
                    "last_scan": None
                }
            
            logger.info(f"Loaded {len(self.monitored_providers)} enabled email providers for monitoring")
            
            # Also add default provider if configured (for backward compatibility)
            if self.email_username and self.email_password and "default" not in self.monitored_providers:
                self.monitored_providers["default"] = {
                    "id": "default",
                    "name": "Default Provider",
                    "imap_host": self.imap_host,
                    "imap_port": self.imap_port,
                    "imap_username": self.email_username,
                    "imap_password": self.email_password,
                    "email_address": self.email_username,
                    "provider_type": "default",
                    "last_scan": None
                }
                
        except Exception as e:
            logger.error(f"Error loading enabled providers: {str(e)}")
    
    async def add_provider_to_monitoring(self, provider_id: str, provider_data: dict):
        """Add a new provider to active monitoring"""
        try:
            if not provider_data.get("imap_enabled", False):
                return
                
            self.monitored_providers[provider_id] = {
                "id": provider_id,
                "name": provider_data["name"],
                "imap_host": provider_data["imap_host"],
                "imap_port": provider_data.get("imap_port", 993),
                "imap_username": provider_data["imap_username"],
                "imap_password": provider_data["imap_password"],
                "email_address": provider_data["email_address"],
                "provider_type": provider_data["provider_type"],
                "last_scan": None
            }
            
            logger.info(f"Added provider {provider_data['name']} to monitoring")
            
        except Exception as e:
            logger.error(f"Error adding provider to monitoring: {str(e)}")
    
    async def remove_provider_from_monitoring(self, provider_id: str):
        """Remove a provider from active monitoring"""
        try:
            if provider_id in self.monitored_providers:
                provider_name = self.monitored_providers[provider_id]["name"]
                del self.monitored_providers[provider_id]
                logger.info(f"Removed provider {provider_name} from monitoring")
                
        except Exception as e:
            logger.error(f"Error removing provider from monitoring: {str(e)}")
    
    def is_provider_being_monitored(self, provider_id: str) -> bool:
        """Check if a provider is currently being monitored"""
        return provider_id in self.monitored_providers
    
    async def _monitor_all_providers(self):
        """Monitor all enabled providers concurrently"""
        while self.processing:
            try:
                if not self.monitored_providers:
                    # No providers to monitor, wait and reload
                    await asyncio.sleep(60)
                    await self._load_enabled_providers()
                    continue
                
                # Create monitoring tasks for all providers
                tasks = []
                for provider_id, provider_config in self.monitored_providers.items():
                    task = asyncio.create_task(
                        self._monitor_single_provider(provider_id, provider_config)
                    )
                    tasks.append(task)
                
                # Wait for all tasks to complete (they shouldn't unless there's an error)
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)
                
            except Exception as e:
                logger.error(f"Error in multi-provider monitoring: {str(e)}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _monitor_single_provider(self, provider_id: str, provider_config: dict):
        """Monitor a single email provider"""
        consecutive_errors = 0
        max_errors = 5
        
        logger.info(f"Starting monitoring for provider: {provider_config['name']}")
        
        while self.processing and provider_id in self.monitored_providers:
            try:
                scan_result = await self._check_provider_for_new_emails(provider_config)
                consecutive_errors = 0  # Reset error count on successful scan
                
                # Update last scan time
                self.monitored_providers[provider_id]["last_scan"] = datetime.utcnow()
                
                # If we found emails, scan again sooner to catch any others
                if scan_result.get("new_emails_found", 0) > 0:
                    logger.info(f"Provider {provider_config['name']}: Found new emails, scanning again in 10 seconds...")
                    await asyncio.sleep(10)
                else:
                    # Normal interval when no emails found
                    await asyncio.sleep(30)
                    
            except Exception as e:
                consecutive_errors += 1
                logger.error(f"Provider {provider_config['name']} monitoring error (consecutive: {consecutive_errors}): {str(e)}")
                
                # If too many consecutive errors, temporarily disable this provider
                if consecutive_errors >= max_errors:
                    logger.warning(f"Too many errors for provider {provider_config['name']}, temporarily disabling")
                    await asyncio.sleep(300)  # Wait 5 minutes before retrying
                    consecutive_errors = 0
                else:
                    # Exponential backoff on errors, but cap at 5 minutes
                    wait_time = min(60 * consecutive_errors, 300)
                    await asyncio.sleep(wait_time)
    
    async def stop_monitoring(self):
        """Stop email monitoring for all providers"""
        self.processing = False
        self.monitored_providers.clear()
        logger.info("FIXED Email monitoring stopped for all providers")
        return {"status": "stopped"}
    
    async def _check_provider_for_new_emails(self, provider_config: dict):
        """Check a specific provider for new emails via IMAP"""
        scan_start_time = datetime.utcnow()
        scan_result = {
            "provider_id": provider_config["id"],
            "provider_name": provider_config["name"],
            "new_emails_found": 0,
            "emails_processed": 0,
            "errors": [],
            "scan_duration_seconds": 0
        }
        
        try:
            # Connect to IMAP server
            mail = imaplib.IMAP4_SSL(provider_config["imap_host"], provider_config["imap_port"])
            mail.login(provider_config["imap_username"], provider_config["imap_password"])
            mail.select("inbox")
            
            # Search for unread emails
            status, messages = mail.search(None, "UNSEEN")
            
            if status == "OK":
                message_ids = messages[0].split()
                scan_result["new_emails_found"] = len(message_ids)
                
                logger.info(f"Provider {provider_config['name']}: Found {len(message_ids)} new emails to process")
                
                for msg_id in message_ids:
                    try:
                        # Fetch email
                        status, msg_data = mail.fetch(msg_id, "(RFC822)")
                        
                        if status == "OK":
                            # Parse email
                            email_body = msg_data[0][1]
                            email_message = email.message_from_bytes(email_body)
                            
                            # Process the email with provider context - FIXED VERSION
                            processed = await self._process_email_fixed(email_message, provider_config)
                            if processed:
                                scan_result["emails_processed"] += 1
                            
                            # Mark as read
                            mail.store(msg_id, '+FLAGS', '\\Seen')
                            
                    except Exception as e:
                        error_msg = f"Provider {provider_config['name']}: Error processing email {msg_id}: {str(e)}"
                        logger.error(error_msg)
                        scan_result["errors"].append(error_msg)
                        continue
            
            mail.close()
            mail.logout()
            
        except Exception as e:
            error_msg = f"Provider {provider_config['name']}: IMAP connection error: {str(e)}"
            logger.error(error_msg)
            scan_result["errors"].append(error_msg)
        
        # Calculate scan duration
        scan_duration = (datetime.utcnow() - scan_start_time).total_seconds()
        scan_result["scan_duration_seconds"] = scan_duration
        
        # Log scan activity to database
        try:
            await db_service.log_imap_scan_activity(scan_result)
        except Exception as e:
            logger.error(f"Failed to log scan activity for provider {provider_config['name']}: {str(e)}")
        
        # Log summary
        if scan_result["new_emails_found"] > 0:
            logger.info(f"Provider {provider_config['name']}: IMAP scan completed: {scan_result['new_emails_found']} new emails found, "
                       f"{scan_result['emails_processed']} processed, {len(scan_result['errors'])} errors")
        
        return scan_result
    
    async def _process_email_fixed(self, email_message, provider_config: dict = None):
        """FIXED: Process individual email with enhanced follow-up detection and auto-response"""
        try:
            # Extract email details
            sender = email_message.get("From", "")
            subject = self._decode_header(email_message.get("Subject", ""))
            date = email_message.get("Date", "")
            
            # Extract email content
            content = self._extract_email_content(email_message)
            
            # Find prospect by email
            sender_email = self._extract_email_address(sender)
            prospect = await db_service.get_prospect_by_email(sender_email)
            
            if not prospect:
                logger.info(f"No prospect found for email: {sender_email}")
                return False
            
            logger.info(f"FIXED: Processing email from: {sender_email}")
            
            # Create/update thread context
            thread_context = await self._get_or_create_thread_context_fixed(prospect["id"], sender_email)
            
            # FIXED: Check if this is a response to our email - IMPROVED LOGIC
            is_response_to_our_email = await self._check_if_response_to_our_email_fixed(
                prospect["id"], content, subject, thread_context
            )
            
            # Add message to thread with response flag
            message_data = {
                "type": "received",
                "sender": sender_email,
                "subject": subject,
                "content": content,
                "timestamp": datetime.utcnow(),
                "raw_email": str(email_message),
                "is_response_to_our_email": is_response_to_our_email,
                "message_id": f"msg_{generate_id()}"
            }
            
            await self._add_message_to_thread(thread_context["id"], message_data)
            
            # Update prospect last contact time
            await db_service.update_prospect_last_contact(prospect["id"], datetime.utcnow())
            
            # FIXED: Enhanced follow-up stopping logic - ALWAYS STOP FOR ANY REPLY
            if is_response_to_our_email:
                logger.info(f"CRITICAL FIX: Detected reply from {sender_email} - STOPPING ALL FOLLOW-UPS")
                await self._handle_prospect_response_fixed(prospect, content, subject, thread_context)
            
            # FIXED: Enhanced intent classification and auto-response - ALWAYS TRY TO RESPOND
            logger.info("FIXED: Starting intent classification for auto-response...")
            classified_intents = await groq_service.classify_intents(content, subject)
            
            if not classified_intents:
                # FIXED: Create a default intent for auto-response if no classification
                logger.info("FIXED: No intents classified - creating default response intent")
                classified_intents = [{
                    "intent_id": "default_response",
                    "intent_name": "General Inquiry",
                    "confidence": 0.8,
                    "auto_respond": True
                }]
            
            logger.info(f"FIXED: Classified intents: {classified_intents}")
            
            # FIXED: Auto-response logic - ALWAYS RESPOND TO ALL EMAILS
            logger.info("FIXED: Checking if auto-response should be sent...")
            should_auto_respond = await self._should_auto_respond_fixed(classified_intents)
            
            if should_auto_respond:
                logger.info("FIXED: Auto-response ENABLED - generating response...")
                # Get conversation context
                conversation_context = await self._get_conversation_context(thread_context["id"])
                
                # Generate response using Groq AI
                response_data = await groq_service.generate_response(
                    content, 
                    subject, 
                    classified_intents, 
                    conversation_context, 
                    prospect
                )
                
                if response_data.get("error"):
                    logger.error(f"Response generation failed: {response_data['error']}")
                    return True
                
                # Send automatic response
                await self._send_automatic_response_fixed(
                    prospect, 
                    response_data, 
                    thread_context["id"]
                )
                
                logger.info(f"FIXED: Automatic response sent to: {sender_email}")
            else:
                logger.info("FIXED: Auto-response disabled - no response sent")
            
            return True
                
        except Exception as e:
            logger.error(f"FIXED: Error processing email: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    async def _check_if_response_to_our_email_fixed(self, prospect_id: str, content: str, subject: str, thread_context: dict):
        """FIXED: Enhanced check if this email is a response to our email - MORE AGGRESSIVE DETECTION"""
        try:
            logger.info(f"FIXED: Checking if email from prospect {prospect_id} is a response to our emails")
            
            # FIXED: Check subject line for ANY reply indicators (more comprehensive)
            reply_indicators = [
                "re:", "reply:", "response:", "regarding:", "about:", "fwd:", "forward:",
                "aw:", "antwoord:", "res:", "resp:", "ref:", "回复:", "回覆:", "답장:",
                "antwort:", "réponse:", "risposta:", "respuesta:", "جواب"
            ]
            subject_lower = subject.lower().strip()
            
            for indicator in reply_indicators:
                if indicator in subject_lower:
                    logger.info(f"FIXED: Email IS a reply based on subject indicator: '{indicator}' in '{subject}'")
                    return True
            
            # FIXED: Check if we sent ANY emails to this prospect in the last 60 days (extended window)
            from datetime import timedelta
            recent_cutoff = datetime.utcnow() - timedelta(days=60)  # Extended to 60 days
            
            # Check thread messages for our sent emails
            thread_messages = thread_context.get("messages", [])
            our_recent_emails = [
                msg for msg in thread_messages 
                if (msg.get("type") == "sent" and 
                    msg.get("sent_by_us", False) and
                    msg.get("timestamp", datetime.utcnow()) > recent_cutoff)
            ]
            
            if our_recent_emails:
                logger.info(f"FIXED: Found {len(our_recent_emails)} recent emails we sent to this prospect in thread - THIS IS A RESPONSE")
                return True
            
            # FIXED: Check database for ANY sent emails to this prospect
            sent_emails = await db_service.db.emails.find({
                "prospect_id": prospect_id,
                "sent_by_us": True,
                "sent_at": {"$gte": recent_cutoff}
            }).to_list(length=None)
            
            if sent_emails:
                logger.info(f"FIXED: Found {len(sent_emails)} sent emails in database for prospect {prospect_id} - THIS IS A RESPONSE")
                return True
            
            # FIXED: Check if prospect has any campaign association (if they're in our system, they likely received emails)
            if prospect.get("campaign_id") or prospect.get("list_ids"):
                logger.info(f"FIXED: Prospect has campaign/list association - treating as response")
                return True
            
            logger.info(f"FIXED: No evidence this is a response to our emails")
            return False
            
        except Exception as e:
            logger.error(f"FIXED: Error checking if response to our email: {str(e)}")
            # FIXED: Default to TRUE to be safe and stop follow-ups
            return True
    
    async def _handle_prospect_response_fixed(self, prospect: dict, content: str, subject: str, thread_context: dict):
        """FIXED: Enhanced handling when a prospect responds to our email - ALWAYS STOP FOLLOW-UPS"""
        try:
            prospect_id = prospect["id"]
            
            logger.info(f"CRITICAL FIX: Handling response from prospect {prospect_id}")
            
            # FIXED: Check if this is an auto-reply (but still be more lenient)
            is_auto_reply = await self._detect_auto_reply(content, subject)
            
            if is_auto_reply:
                logger.info(f"FIXED: Auto-reply detected from prospect {prospect_id} - BUT STILL STOPPING FOLLOW-UPS")
                # FIXED: Even for auto-replies, we should consider stopping follow-ups after a few
                await db_service.update_prospect(prospect_id, {
                    "last_auto_reply": datetime.utcnow(),
                    "auto_reply_count": prospect.get("auto_reply_count", 0) + 1
                })
                
                # FIXED: Stop follow-ups if too many auto-replies
                current_auto_reply_count = prospect.get("auto_reply_count", 0) + 1
                if current_auto_reply_count >= 2:
                    logger.info(f"FIXED: Too many auto-replies from {prospect_id} - stopping follow-ups")
                    await self._stop_all_follow_ups_fixed(prospect_id, "too_many_auto_replies")
                return
            
            # FIXED: This is ANY response - stop follow-ups IMMEDIATELY
            logger.info(f"CRITICAL FIX: ANY response detected from prospect {prospect_id} - STOPPING ALL FOLLOW-UPS IMMEDIATELY")
            
            # FIXED: Stop follow-ups with comprehensive database updates
            await self._stop_all_follow_ups_fixed(prospect_id, "manual_response")
            
            logger.info(f"CRITICAL FIX: Follow-ups STOPPED for prospect {prospect_id} due to response")
            
        except Exception as e:
            logger.error(f"FIXED: Error handling prospect response: {str(e)}")
    
    async def _stop_all_follow_ups_fixed(self, prospect_id: str, reason: str):
        """FIXED: Comprehensive method to stop ALL follow-ups for a prospect"""
        try:
            logger.info(f"CRITICAL FIX: Stopping ALL follow-ups for prospect {prospect_id} - Reason: {reason}")
            
            # FIXED: Update prospect status comprehensively
            await db_service.update_prospect(prospect_id, {
                "responded_at": datetime.utcnow(),
                "response_type": reason,
                "follow_up_status": "stopped",
                "status": "responded",  # Also update general status
                "updated_at": datetime.utcnow()
            })
            
            # FIXED: Cancel any pending follow-up emails
            await db_service.cancel_pending_follow_ups(prospect_id)
            
            # FIXED: Mark prospect as responded in database
            await db_service.mark_prospect_as_responded(prospect_id, reason)
            
            # FIXED: Update any campaign status
            if prospect.get("campaign_id"):
                # Note: Don't mark entire campaign as stopped, just this prospect
                pass
            
            logger.info(f"CRITICAL FIX: Successfully stopped ALL follow-ups for prospect {prospect_id}")
            
        except Exception as e:
            logger.error(f"FIXED: Error stopping all follow-ups for prospect {prospect_id}: {str(e)}")
    
    async def _detect_auto_reply(self, content: str, subject: str):
        """Enhanced auto-reply detection with more patterns"""
        try:
            content_lower = content.lower()
            subject_lower = subject.lower()
            
            # Extended auto-reply indicators
            auto_reply_indicators = [
                "out of office", "vacation", "away", "automatic reply", "auto-reply", "autoreply",
                "currently unavailable", "on holiday", "leave", "maternity leave",
                "sick leave", "conference", "traveling", "will be back",
                "not available", "away message", "vacation message", "out of the office",
                "currently out", "temporarily unavailable", "on leave", "parental leave",
                "sabbatical", "business trip", "attending conference", "away from desk",
                "thank you for your email", "i will respond when i return",
                "limited access to email", "checking email less frequently"
            ]
            
            # Check for indicators in content and subject
            for indicator in auto_reply_indicators:
                if indicator in content_lower or indicator in subject_lower:
                    logger.info(f"Auto-reply detected: found indicator '{indicator}'")
                    return True
            
            # Check for auto-reply patterns using regex
            import re
            auto_reply_patterns = [
                r"i am (currently )?out of (the )?office",
                r"automatic reply",
                r"will be (back|returning) on",
                r"on vacation until",
                r"away until",
                r"currently unavailable",
                r"thank you for your (email|message)",
                r"i will (respond|reply) when i return",
                r"limited access to email",
                r"this is an automated response"
            ]
            
            combined_text = content_lower + " " + subject_lower
            for pattern in auto_reply_patterns:
                if re.search(pattern, combined_text):
                    logger.info(f"Auto-reply detected: matched pattern '{pattern}'")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error detecting auto-reply: {str(e)}")
            return False
    
    async def _get_or_create_thread_context_fixed(self, prospect_id: str, sender_email: str) -> Dict:
        """FIXED: Get or create thread context for prospect with consistent thread ID"""
        try:
            # Check if thread exists
            existing_thread = await db_service.get_thread_by_prospect_id(prospect_id)
            
            if existing_thread:
                return existing_thread
            
            # Create new thread with consistent ID format
            thread_id = f"thread_{prospect_id}"
            thread_data = {
                "id": thread_id,
                "prospect_id": prospect_id,
                "campaign_id": "",  # Will be set if part of campaign
                "messages": [],
                "last_activity": datetime.utcnow(),
                "created_at": datetime.utcnow()
            }
            
            await db_service.create_thread_context(thread_data)
            return thread_data
            
        except Exception as e:
            logger.error(f"FIXED: Error creating thread context: {str(e)}")
            return None
    
    async def _add_message_to_thread(self, thread_id: str, message_data: Dict):
        """Add message to thread context"""
        try:
            await db_service.add_message_to_thread(thread_id, message_data)
            await db_service.update_thread_last_activity(thread_id, datetime.utcnow())
        except Exception as e:
            logger.error(f"Error adding message to thread: {str(e)}")
    
    async def _get_conversation_context(self, thread_id: str) -> List[Dict]:
        """Get conversation context for AI"""
        try:
            thread = await db_service.get_thread_by_id(thread_id)
            if thread:
                return thread.get("messages", [])
            return []
        except Exception as e:
            logger.error(f"Error getting conversation context: {str(e)}")
            return []
    
    async def _should_auto_respond_fixed(self, classified_intents: List[Dict]) -> bool:
        """FIXED: Enhanced check - ALWAYS RESPOND TO ALL EMAILS"""
        try:
            logger.info("FIXED: Auto-response check - ALWAYS RESPOND TO ALL EMAILS")
            
            # FIXED: Always return True to respond to all emails
            for intent in classified_intents:
                intent_name = intent.get("intent_name", "Unknown")
                logger.info(f"FIXED: Processing intent '{intent_name}' - auto_respond will be forced to True")
            
            logger.info("FIXED: Auto-response ENABLED for all emails")
            return True
            
        except Exception as e:
            logger.error(f"FIXED: Error checking auto-response: {str(e)}")
            return True  # Default to responding
    
    async def _send_automatic_response_fixed(self, prospect: Dict, response_data: Dict, thread_id: str):
        """FIXED: Send automatic response with enhanced tracking"""
        try:
            logger.info(f"FIXED: Sending automatic response to {prospect['email']}")
            
            # Personalize response
            personalized_content = personalize_template(response_data["content"], prospect)
            personalized_subject = personalize_template(response_data["subject"], prospect)
            
            # Find the original email provider used for this prospect
            original_provider = await self._get_original_email_provider_fixed(prospect["id"])
            
            if not original_provider:
                logger.error(f"FIXED: No email provider available for auto-response to {prospect['email']}")
                return
            
            # Send email with proper error handling using the original provider
            try:
                success = await self._send_email_with_provider_fixed(
                    original_provider,
                    prospect["email"],
                    personalized_subject,
                    personalized_content
                )
                
                if success:
                    # Create email record with enhanced tracking
                    email_id = generate_id()
                    email_record = {
                        "id": email_id,
                        "prospect_id": prospect["id"],
                        "campaign_id": "",
                        "subject": personalized_subject,
                        "content": personalized_content,
                        "status": "sent",
                        "sent_at": datetime.utcnow(),
                        "created_at": datetime.utcnow(),
                        "sent_by_us": True,
                        "thread_id": thread_id,
                        "ai_generated": True,
                        "is_auto_response": True,
                        "provider_id": original_provider["id"],
                        "recipient_email": prospect["email"]
                    }
                    
                    await db_service.create_email_record(email_record)
                    
                    # Mark email as sent by us in the database
                    await db_service.mark_email_as_sent_by_us(email_id, thread_id)
                    
                    # Add response to thread with sent flag
                    await db_service.update_thread_with_sent_flag(thread_id, {
                        "type": "sent",
                        "recipient": prospect["email"],
                        "subject": personalized_subject,
                        "content": personalized_content,
                        "timestamp": datetime.utcnow(),
                        "ai_generated": True,
                        "is_auto_response": True,
                        "template_used": response_data.get("template_used"),
                        "email_id": email_id,
                        "provider_id": original_provider["id"],
                        "provider_email": original_provider["email_address"]
                    })
                    
                    provider_email = original_provider["email_address"]
                    logger.info(f"FIXED: Automatic response sent successfully to: {prospect['email']} from provider: {provider_email}")
                else:
                    logger.error(f"FIXED: Failed to send automatic response to: {prospect['email']}")
                    
            except Exception as email_error:
                logger.error(f"FIXED: SMTP Error sending automatic response to {prospect['email']}: {str(email_error)}")
                raise email_error
                
        except Exception as e:
            logger.error(f"FIXED: Error sending automatic response: {str(e)}")
            raise e
    
    async def _get_original_email_provider_fixed(self, prospect_id: str) -> Dict:
        """FIXED: Get the original email provider used for this prospect"""
        try:
            # Use enhanced database service method
            original_provider = await enhanced_db_service.get_prospect_original_provider(prospect_id)
            if original_provider:
                logger.info(f"FIXED: Found original provider for prospect {prospect_id}: {original_provider.get('email_address')}")
                return original_provider
            
            # Final fallback to default provider
            logger.info(f"FIXED: No original provider found for prospect {prospect_id}, using default provider")
            provider = await db_service.get_default_email_provider()
            return provider
            
        except Exception as e:
            logger.error(f"FIXED: Error getting original email provider: {str(e)}")
            # Fallback to default provider
            return await db_service.get_default_email_provider()
    
    async def _send_email_with_provider_fixed(self, provider: Dict, to_email: str, subject: str, content: str) -> bool:
        """FIXED: Send email using specific provider"""
        try:
            if not provider:
                logger.error("FIXED: No email provider available")
                return False
            
            # Use the email provider service to send the email
            from app.services.email_provider_service import email_provider_service
            
            success, error = await email_provider_service.send_email(
                provider["id"],
                to_email,
                subject,
                content,
                "html"
            )
            
            if success:
                logger.info(f"FIXED: Email sent successfully to {to_email} using provider: {provider.get('email_address')}")
                return True
            else:
                logger.error(f"FIXED: Failed to send email to {to_email} using provider {provider.get('email_address')}: {error}")
                return False
                
        except Exception as e:
            logger.error(f"FIXED: Error sending email with provider: {str(e)}")
            return False

    def _decode_header(self, header_value: str) -> str:
        """Decode email header"""
        try:
            decoded_header = decode_header(header_value)
            return str(decoded_header[0][0])
        except:
            return header_value
    
    def _extract_email_address(self, email_string: str) -> str:
        """Extract email address from string"""
        try:
            if '<' in email_string and '>' in email_string:
                return email_string.split('<')[1].split('>')[0]
            return email_string.strip()
        except:
            return email_string
    
    def _extract_email_content(self, email_message) -> str:
        """Extract text content from email"""
        try:
            content = ""
            
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain":
                        content += part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    elif part.get_content_type() == "text/html":
                        content += part.get_payload(decode=True).decode('utf-8', errors='ignore')
            else:
                content = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
            
            return content
        except Exception as e:
            logger.error(f"Error extracting email content: {str(e)}")
            return ""

# Create FIXED global email processor instance
email_processor_fixed = EmailProcessorFixed()