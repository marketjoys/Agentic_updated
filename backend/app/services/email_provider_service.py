import os
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import asyncio
import logging
from app.models import EmailProvider, EmailProviderType
from app.services.database import db_service
from app.utils.helpers import generate_id

logger = logging.getLogger(__name__)

class EmailProviderService:
    def __init__(self):
        self.provider_configs = {
            EmailProviderType.GMAIL: {
                "smtp_host": "smtp.gmail.com",
                "smtp_port": 587,
                "imap_host": "imap.gmail.com",
                "imap_port": 993,
                "smtp_use_tls": True,
                "imap_use_ssl": True
            },
            EmailProviderType.OUTLOOK: {
                "smtp_host": "smtp-mail.outlook.com",
                "smtp_port": 587,
                "imap_host": "outlook.office365.com",
                "imap_port": 993,
                "smtp_use_tls": True,
                "imap_use_ssl": True
            },
            EmailProviderType.YAHOO: {
                "smtp_host": "smtp.mail.yahoo.com",
                "smtp_port": 587,
                "imap_host": "imap.mail.yahoo.com",
                "imap_port": 993,
                "smtp_use_tls": True,
                "imap_use_ssl": True
            }
        }
    
    async def create_email_provider(self, provider_data: Dict) -> Tuple[Optional[str], Optional[str]]:
        """Create a new email provider"""
        try:
            # Generate ID
            provider_id = generate_id()
            provider_data["id"] = provider_id
            
            # Auto-configure based on provider type
            if provider_data["provider_type"] in self.provider_configs:
                config = self.provider_configs[provider_data["provider_type"]]
                for key, value in config.items():
                    if key not in provider_data or not provider_data[key]:
                        provider_data[key] = value
            
            # Validate provider configuration
            validation_error = await self._validate_provider_config(provider_data)
            if validation_error:
                return None, validation_error
            
            # Test connection only if credentials are provided and skip_test is not set
            skip_test = provider_data.get("skip_connection_test", False)
            if not skip_test and provider_data.get("smtp_password") and provider_data.get("imap_password"):
                connection_error = await self._test_provider_connection(provider_data)
                if connection_error:
                    # Log the error but don't fail - allow test providers
                    logger.warning(f"Connection test failed for provider {provider_id}: {connection_error}")
                    provider_data["connection_test_failed"] = True
                    provider_data["connection_error"] = connection_error
                    provider_data["is_active"] = False  # Mark as inactive until credentials are fixed
            
            # Save to database
            result = await db_service.create_email_provider(provider_data)
            if result:
                return provider_id, None
            else:
                return None, "Failed to save email provider"
                
        except Exception as e:
            logger.error(f"Error creating email provider: {str(e)}")
            return None, str(e)
    
    async def get_email_providers(self) -> List[Dict]:
        """Get all email providers"""
        try:
            providers = await db_service.get_email_providers()
            return providers
        except Exception as e:
            logger.error(f"Error getting email providers: {str(e)}")
            return []
    
    async def get_email_provider_by_id(self, provider_id: str) -> Optional[Dict]:
        """Get email provider by ID"""
        try:
            await db_service.connect()
            provider = await db_service.get_email_provider_by_id(provider_id)
            return provider
        except Exception as e:
            logger.error(f"Error getting email provider {provider_id}: {str(e)}")
            return None
    
    async def update_email_provider(self, provider_id: str, provider_data: Dict) -> Tuple[bool, Optional[str]]:
        """Update an email provider"""
        try:
            # Validate provider configuration
            validation_error = await self._validate_provider_config(provider_data)
            if validation_error:
                return False, validation_error
            
            # Test connection if credentials changed
            if any(key in provider_data for key in ["smtp_password", "imap_password", "oauth2_refresh_token"]):
                connection_error = await self._test_provider_connection(provider_data)
                if connection_error:
                    return False, f"Connection test failed: {connection_error}"
            
            # Update in database
            provider_data["updated_at"] = datetime.utcnow()
            result = await db_service.update_email_provider(provider_id, provider_data)
            return bool(result), None
            
        except Exception as e:
            logger.error(f"Error updating email provider {provider_id}: {str(e)}")
            return False, str(e)
    
    async def delete_email_provider(self, provider_id: str) -> Tuple[bool, Optional[str]]:
        """Delete an email provider"""
        try:
            # Check if provider is used in active campaigns
            campaigns = await db_service.get_campaigns_by_provider_id(provider_id)
            if campaigns:
                return False, "Cannot delete provider: it's being used in active campaigns"
            
            # Delete from database
            result = await db_service.delete_email_provider(provider_id)
            return bool(result), None
            
        except Exception as e:
            logger.error(f"Error deleting email provider {provider_id}: {str(e)}")
            return False, str(e)
    
    async def send_email(self, provider_id: str, to_email: str, subject: str, content: str, 
                        content_type: str = "html") -> Tuple[bool, Optional[str]]:
        """Send email using specific provider"""
        try:
            # Get provider configuration
            provider = await self.get_email_provider_by_id(provider_id)
            if not provider:
                return False, "Email provider not found"
            
            if not provider["is_active"]:
                return False, "Email provider is not active"
            
            # Check rate limits
            if not await self._check_rate_limits(provider_id):
                return False, "Rate limit exceeded"
            
            # Send email
            success = await self._send_email_smtp(provider, to_email, subject, content, content_type)
            
            if success:
                # Update send counts
                await self._update_send_counts(provider_id)
                return True, None
            else:
                return False, "Failed to send email"
                
        except Exception as e:
            logger.error(f"Error sending email via provider {provider_id}: {str(e)}")
            return False, str(e)
    
    async def get_emails(self, provider_id: str, folder: str = "INBOX", limit: int = 100) -> List[Dict]:
        """Get emails from provider"""
        try:
            provider = await self.get_email_provider_by_id(provider_id)
            if not provider:
                return []
            
            emails = await self._get_emails_imap(provider, folder, limit)
            return emails
            
        except Exception as e:
            logger.error(f"Error getting emails from provider {provider_id}: {str(e)}")
            return []
    
    async def get_default_provider(self) -> Optional[Dict]:
        """Get default email provider"""
        try:
            provider = await db_service.get_default_email_provider()
            return provider
        except Exception as e:
            logger.error(f"Error getting default provider: {str(e)}")
            return None
    
    async def set_default_provider(self, provider_id: str) -> bool:
        """Set default email provider"""
        try:
            # Remove default flag from all providers
            await db_service.update_all_email_providers({"is_default": False})
            
            # Set new default
            result = await db_service.update_email_provider(provider_id, {"is_default": True})
            return bool(result)
            
        except Exception as e:
            logger.error(f"Error setting default provider {provider_id}: {str(e)}")
            return False
    
    async def _validate_provider_config(self, provider_data: Dict) -> Optional[str]:
        """Validate provider configuration"""
        required_fields = ["name", "provider_type", "email_address"]
        
        for field in required_fields:
            if field not in provider_data or not provider_data[field]:
                return f"Missing required field: {field}"
        
        # Validate email address
        if not "@" in provider_data["email_address"]:
            return "Invalid email address"
        
        # Validate provider type
        if provider_data["provider_type"] not in [e.value for e in EmailProviderType]:
            return "Invalid provider type"
        
        # For test providers, don't require SMTP configuration
        if provider_data.get("skip_connection_test", False):
            return None
            
        # Validate SMTP configuration for custom providers
        if provider_data["provider_type"] == EmailProviderType.CUSTOM_SMTP:
            if not provider_data.get("smtp_host") or not provider_data.get("smtp_port"):
                return "SMTP host and port are required for custom providers"
        
        return None
    
    async def _test_provider_connection(self, provider_data: Dict) -> Optional[str]:
        """Test provider connection"""
        try:
            # Test SMTP connection
            if provider_data.get("smtp_host") and provider_data.get("smtp_password"):
                try:
                    server = smtplib.SMTP(provider_data["smtp_host"], provider_data["smtp_port"])
                    if provider_data.get("smtp_use_tls"):
                        server.starttls()
                    server.login(provider_data.get("smtp_username", provider_data["email_address"]), 
                               provider_data["smtp_password"])
                    server.quit()
                except Exception as e:
                    return f"SMTP connection failed: {str(e)}"
            
            # Test IMAP connection
            if provider_data.get("imap_host") and provider_data.get("imap_password"):
                try:
                    if provider_data.get("imap_use_ssl"):
                        server = imaplib.IMAP4_SSL(provider_data["imap_host"], provider_data["imap_port"])
                    else:
                        server = imaplib.IMAP4(provider_data["imap_host"], provider_data["imap_port"])
                    
                    server.login(provider_data.get("imap_username", provider_data["email_address"]), 
                               provider_data["imap_password"])
                    server.logout()
                except Exception as e:
                    return f"IMAP connection failed: {str(e)}"
            
            return None
            
        except Exception as e:
            return f"Connection test error: {str(e)}"
    
    async def _send_email_smtp(self, provider: Dict, to_email: str, subject: str, 
                              content: str, content_type: str = "html") -> bool:
        """Send email via SMTP"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{provider.get('display_name', '')} <{provider['email_address']}>"
            msg['To'] = to_email
            
            # Add content
            if content_type == "html":
                html_part = MIMEText(content, 'html')
                msg.attach(html_part)
            else:
                text_part = MIMEText(content, 'plain')
                msg.attach(text_part)
            
            # Send email
            server = smtplib.SMTP(provider["smtp_host"], provider["smtp_port"])
            if provider.get("smtp_use_tls"):
                server.starttls()
            
            server.login(provider.get("smtp_username", provider["email_address"]), 
                        provider["smtp_password"])
            
            text = msg.as_string()
            server.sendmail(provider["email_address"], to_email, text)
            server.quit()
            
            return True
            
        except Exception as e:
            logger.error(f"SMTP send error: {str(e)}")
            return False
    
    async def _get_emails_imap(self, provider: Dict, folder: str, limit: int) -> List[Dict]:
        """Get emails via IMAP"""
        try:
            emails = []
            
            # Connect to IMAP server
            if provider.get("imap_use_ssl"):
                server = imaplib.IMAP4_SSL(provider["imap_host"], provider["imap_port"])
            else:
                server = imaplib.IMAP4(provider["imap_host"], provider["imap_port"])
            
            server.login(provider.get("imap_username", provider["email_address"]), 
                        provider["imap_password"])
            
            server.select(folder)
            
            # Search for emails
            status, messages = server.search(None, "ALL")
            
            if status == "OK":
                message_ids = messages[0].split()
                message_ids = message_ids[-limit:]  # Get latest emails
                
                for msg_id in message_ids:
                    try:
                        status, msg_data = server.fetch(msg_id, "(RFC822)")
                        if status == "OK":
                            email_message = email.message_from_bytes(msg_data[0][1])
                            
                            # Extract email details
                            email_dict = {
                                "id": msg_id.decode(),
                                "subject": email_message.get("Subject", ""),
                                "from": email_message.get("From", ""),
                                "to": email_message.get("To", ""),
                                "date": email_message.get("Date", ""),
                                "content": self._extract_email_content(email_message)
                            }
                            emails.append(email_dict)
                    except Exception as e:
                        logger.error(f"Error processing email {msg_id}: {str(e)}")
                        continue
            
            server.close()
            server.logout()
            
            return emails
            
        except Exception as e:
            logger.error(f"IMAP get emails error: {str(e)}")
            return []
    
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
    
    async def _check_rate_limits(self, provider_id: str) -> bool:
        """Check if provider is within rate limits"""
        try:
            provider = await self.get_email_provider_by_id(provider_id)
            if not provider:
                return False
            
            # Check daily limit
            if provider.get("current_daily_count", 0) >= provider.get("daily_send_limit", 500):
                return False
            
            # Check hourly limit
            if provider.get("current_hourly_count", 0) >= provider.get("hourly_send_limit", 50):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking rate limits: {str(e)}")
            return False
    
    async def _update_send_counts(self, provider_id: str):
        """Update send counts for rate limiting"""
        try:
            # Increment counts
            await db_service.increment_provider_send_counts(provider_id)
            
            # Reset counters if needed (this could be a scheduled task)
            await self._reset_rate_limit_counters_if_needed(provider_id)
            
        except Exception as e:
            logger.error(f"Error updating send counts: {str(e)}")
    
    async def _reset_rate_limit_counters_if_needed(self, provider_id: str):
        """Reset rate limit counters if time period has passed"""
        try:
            provider = await self.get_email_provider_by_id(provider_id)
            if not provider:
                return
            
            now = datetime.utcnow()
            last_sync = provider.get("last_sync")
            
            if last_sync:
                # Reset hourly counter if an hour has passed
                if now - last_sync > timedelta(hours=1):
                    await db_service.update_email_provider(provider_id, {
                        "current_hourly_count": 0,
                        "last_sync": now
                    })
                
                # Reset daily counter if a day has passed
                if now - last_sync > timedelta(days=1):
                    await db_service.update_email_provider(provider_id, {
                        "current_daily_count": 0,
                        "current_hourly_count": 0,
                        "last_sync": now
                    })
            
        except Exception as e:
            logger.error(f"Error resetting rate limit counters: {str(e)}")

# Create global email provider service instance
email_provider_service = EmailProviderService()