import asyncio
import imaplib
import email
from email.header import decode_header
from datetime import datetime
import logging
from typing import Dict, List, Optional
import os
from app.services.database import db_service
from app.services.groq_service import groq_service
from app.utils.helpers import send_email, generate_id, personalize_template

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailProcessor:
    def __init__(self):
        self.imap_host = os.getenv("IMAP_HOST", "imap.gmail.com")
        self.imap_port = int(os.getenv("IMAP_PORT", 993))
        self.email_username = os.getenv("SMTP_USERNAME")
        self.email_password = os.getenv("SMTP_PASSWORD")
        self.processing = False
        
    async def start_monitoring(self):
        """Start IMAP email monitoring"""
        if self.processing:
            return {"status": "already_running"}
        
        self.processing = True
        logger.info("Starting email monitoring...")
        
        try:
            # Start monitoring in background
            asyncio.create_task(self._monitor_emails())
            return {"status": "started", "message": "Email monitoring started"}
        except Exception as e:
            self.processing = False
            logger.error(f"Failed to start email monitoring: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def stop_monitoring(self):
        """Stop email monitoring"""
        self.processing = False
        logger.info("Email monitoring stopped")
        return {"status": "stopped"}
    
    async def _monitor_emails(self):
        """Monitor IMAP for new emails"""
        while self.processing:
            try:
                await self._check_for_new_emails()
                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"Error in email monitoring: {str(e)}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _check_for_new_emails(self):
        """Check for new emails via IMAP with enhanced monitoring"""
        scan_start_time = datetime.utcnow()
        scan_result = {
            "new_emails_found": 0,
            "emails_processed": 0,
            "errors": [],
            "scan_duration_seconds": 0
        }
        
        try:
            # Connect to IMAP server
            mail = imaplib.IMAP4_SSL(self.imap_host, self.imap_port)
            mail.login(self.email_username, self.email_password)
            mail.select("inbox")
            
            # Search for unread emails
            status, messages = mail.search(None, "UNSEEN")
            
            if status == "OK":
                message_ids = messages[0].split()
                scan_result["new_emails_found"] = len(message_ids)
                
                logger.info(f"Found {len(message_ids)} new emails to process")
                
                for msg_id in message_ids:
                    try:
                        # Fetch email
                        status, msg_data = mail.fetch(msg_id, "(RFC822)")
                        
                        if status == "OK":
                            # Parse email
                            email_body = msg_data[0][1]
                            email_message = email.message_from_bytes(email_body)
                            
                            # Process the email
                            processed = await self._process_email(email_message)
                            if processed:
                                scan_result["emails_processed"] += 1
                            
                            # Mark as read
                            mail.store(msg_id, '+FLAGS', '\\Seen')
                            
                    except Exception as e:
                        error_msg = f"Error processing email {msg_id}: {str(e)}"
                        logger.error(error_msg)
                        scan_result["errors"].append(error_msg)
                        continue
            
            mail.close()
            mail.logout()
            
        except Exception as e:
            error_msg = f"IMAP connection error: {str(e)}"
            logger.error(error_msg)
            scan_result["errors"].append(error_msg)
        
        # Calculate scan duration
        scan_duration = (datetime.utcnow() - scan_start_time).total_seconds()
        scan_result["scan_duration_seconds"] = scan_duration
        
        # Log scan activity
        try:
            await db_service.log_imap_scan_activity(scan_result)
        except Exception as e:
            logger.error(f"Failed to log scan activity: {str(e)}")
        
        # Log summary
        if scan_result["new_emails_found"] > 0:
            logger.info(f"IMAP scan completed: {scan_result['new_emails_found']} new emails found, "
                       f"{scan_result['emails_processed']} processed, {len(scan_result['errors'])} errors")
        
        return scan_result
    
    async def _process_email(self, email_message):
        """Process individual email with enhanced follow-up detection"""
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
            
            logger.info(f"Processing email from: {sender_email}")
            
            # Create/update thread context
            thread_context = await self._get_or_create_thread_context(prospect["id"], sender_email)
            
            # Check if this is a response to our email
            is_response_to_our_email = await self._check_if_response_to_our_email(
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
            
            # Enhanced follow-up stopping logic
            if is_response_to_our_email:
                await self._handle_prospect_response(prospect, content, subject, thread_context)
            
            # Classify intents using Groq AI
            classified_intents = await groq_service.classify_intents(content, subject)
            
            if not classified_intents:
                logger.info("No intents classified for email")
                return True
            
            logger.info(f"Classified intents: {classified_intents}")
            
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
            
            # Check if any intent requires auto-response
            should_auto_respond = await self._should_auto_respond(classified_intents)
            
            if should_auto_respond:
                # Send automatic response
                await self._send_automatic_response(
                    prospect, 
                    response_data, 
                    thread_context["id"]
                )
                
                logger.info(f"Automatic response sent to: {sender_email}")
            else:
                logger.info("Email processed but no auto-response required")
            
            return True
                
        except Exception as e:
            logger.error(f"Error processing email: {str(e)}")
            return False
    
    async def _check_if_response_to_our_email(self, prospect_id: str, content: str, subject: str, thread_context: dict):
        """Check if this email is a response to our email"""
        try:
            # Check if subject contains Re: or similar reply indicators
            reply_indicators = ["re:", "reply:", "response:", "regarding:", "about:"]
            subject_lower = subject.lower()
            
            for indicator in reply_indicators:
                if indicator in subject_lower:
                    logger.info(f"Email appears to be a reply based on subject: {subject}")
                    return True
            
            # Check if we sent any emails to this prospect recently
            thread_messages = thread_context.get("messages", [])
            our_recent_emails = [
                msg for msg in thread_messages 
                if msg.get("type") == "sent" and msg.get("sent_by_us", False)
            ]
            
            if our_recent_emails:
                logger.info(f"Found {len(our_recent_emails)} emails we sent to this prospect")
                return True
            
            # Check database for sent emails
            sent_emails = await db_service.get_sent_emails_in_thread(thread_context["id"])
            if sent_emails:
                logger.info(f"Found {len(sent_emails)} sent emails in thread {thread_context['id']}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking if response to our email: {str(e)}")
            return False
    
    async def _handle_prospect_response(self, prospect: dict, content: str, subject: str, thread_context: dict):
        """Handle when a prospect responds to our email"""
        try:
            prospect_id = prospect["id"]
            
            # Check if this is an auto-reply
            is_auto_reply = await self._detect_auto_reply(content, subject)
            
            if is_auto_reply:
                logger.info(f"Auto-reply detected from prospect {prospect_id}, not stopping follow-ups")
                # Mark as auto-reply but don't stop follow-ups
                await db_service.update_prospect(prospect_id, {
                    "last_auto_reply": datetime.utcnow(),
                    "auto_reply_count": prospect.get("auto_reply_count", 0) + 1
                })
                return
            
            # This is a manual response - stop follow-ups
            logger.info(f"Manual response detected from prospect {prospect_id}, stopping follow-ups")
            
            # Mark prospect as responded and stop follow-ups
            await db_service.mark_prospect_as_responded(prospect_id, "manual")
            
            # Cancel any pending follow-up emails
            await db_service.cancel_pending_follow_ups(prospect_id)
            
            # Update thread with response flag
            await db_service.update_thread_with_sent_flag(thread_context["id"], {
                "type": "prospect_response",
                "response_type": "manual",
                "timestamp": datetime.utcnow(),
                "follow_ups_stopped": True
            })
            
            logger.info(f"Follow-ups stopped for prospect {prospect_id} due to manual response")
            
        except Exception as e:
            logger.error(f"Error handling prospect response: {str(e)}")
    
    async def _detect_auto_reply(self, content: str, subject: str):
        """Enhanced auto-reply detection"""
        try:
            content_lower = content.lower()
            subject_lower = subject.lower()
            
            # Extended auto-reply indicators
            auto_reply_indicators = [
                "out of office", "vacation", "away", "automatic reply", "auto-reply",
                "currently unavailable", "on holiday", "leave", "maternity leave",
                "sick leave", "conference", "traveling", "will be back",
                "not available", "away message", "vacation message", "out of the office",
                "currently out", "temporarily unavailable", "on leave", "parental leave",
                "sabbatical", "business trip", "attending conference", "away from desk"
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
                r"limited access to email"
            ]
            
            for pattern in auto_reply_patterns:
                if re.search(pattern, content_lower) or re.search(pattern, subject_lower):
                    logger.info(f"Auto-reply detected: matched pattern '{pattern}'")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error detecting auto-reply: {str(e)}")
            return False
    
    async def _get_or_create_thread_context(self, prospect_id: str, sender_email: str) -> Dict:
        """Get or create thread context for prospect"""
        try:
            # Check if thread exists
            existing_thread = await db_service.get_thread_by_prospect_id(prospect_id)
            
            if existing_thread:
                return existing_thread
            
            # Create new thread
            thread_data = {
                "id": generate_id(),
                "prospect_id": prospect_id,
                "campaign_id": "",  # Will be set if part of campaign
                "messages": [],
                "last_activity": datetime.utcnow(),
                "created_at": datetime.utcnow()
            }
            
            await db_service.create_thread_context(thread_data)
            return thread_data
            
        except Exception as e:
            logger.error(f"Error creating thread context: {str(e)}")
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
    
    async def _should_auto_respond(self, classified_intents: List[Dict]) -> bool:
        """Check if any intent requires auto-response"""
        try:
            for intent in classified_intents:
                intent_details = await db_service.get_intent_by_id(intent["intent_id"])
                if intent_details and intent_details.get("auto_respond", False):
                    return True
            return False
        except Exception as e:
            logger.error(f"Error checking auto-response: {str(e)}")
            return False
    
    async def _send_automatic_response(self, prospect: Dict, response_data: Dict, thread_id: str):
        """Send automatic response with enhanced tracking"""
        try:
            # Personalize response
            personalized_content = personalize_template(response_data["content"], prospect)
            personalized_subject = personalize_template(response_data["subject"], prospect)
            
            # Send email
            success = await send_email(
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
                    "is_auto_response": True
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
                    "email_id": email_id
                })
                
                logger.info(f"Automatic response sent successfully to: {prospect['email']}")
            else:
                logger.error(f"Failed to send automatic response to: {prospect['email']}")
                
        except Exception as e:
            logger.error(f"Error sending automatic response: {str(e)}")
    
    async def _stop_follow_ups_for_prospect(self, prospect_id: str):
        """Stop any scheduled follow-ups for a prospect who has responded"""
        try:
            # Update prospect status to indicate they've responded
            await db_service.update_prospect_status(prospect_id, "responded")
            
            # Mark any pending follow-up emails as cancelled
            await db_service.cancel_pending_follow_ups(prospect_id)
            
            logger.info(f"Follow-ups stopped for prospect: {prospect_id}")
            
        except Exception as e:
            logger.error(f"Error stopping follow-ups: {str(e)}")
    
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

# Create global email processor instance
email_processor = EmailProcessor()