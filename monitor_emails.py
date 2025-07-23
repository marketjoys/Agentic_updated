#!/usr/bin/env python3
"""
Email monitoring script to watch for new emails and process them
"""
import asyncio
import imaplib
import email
import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path='/app/backend/.env')

class EmailMonitor:
    def __init__(self):
        self.imap_host = os.getenv("IMAP_HOST", "imap.gmail.com")
        self.imap_port = int(os.getenv("IMAP_PORT", 993))
        self.username = os.getenv("SMTP_USERNAME")
        self.password = os.getenv("SMTP_PASSWORD")
        self.api_base = "http://localhost:8001/api"
        self.last_check = datetime.now()
        
    def check_for_new_emails(self):
        """Check for new emails and process them"""
        try:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Checking for new emails...")
            
            mail = imaplib.IMAP4_SSL(self.imap_host, self.imap_port)
            mail.login(self.username, self.password)
            mail.select('inbox')
            
            # Search for unseen emails
            status, messages = mail.search(None, 'UNSEEN')
            message_ids = messages[0].split() if messages[0] else []
            
            if message_ids:
                print(f"🎉 Found {len(message_ids)} new email(s)!")
                
                for msg_id in message_ids:
                    try:
                        # Fetch email
                        status, msg_data = mail.fetch(msg_id, "(RFC822)")
                        
                        if status == "OK":
                            email_body = msg_data[0][1]
                            email_message = email.message_from_bytes(email_body)
                            
                            # Extract email details
                            sender = email_message.get("From", "")
                            subject = email_message.get("Subject", "")
                            date = email_message.get("Date", "")
                            
                            # Extract email content
                            content = self.extract_email_content(email_message)
                            sender_email = self.extract_email_address(sender)
                            
                            print(f"📧 Processing email:")
                            print(f"   From: {sender}")
                            print(f"   Subject: {subject}")
                            print(f"   Content preview: {content[:100]}...")
                            
                            # Try to process with the API
                            response = requests.post(f"{self.api_base}/email-processing/simulate-email", 
                                json={
                                    "sender_email": sender_email,
                                    "subject": subject,
                                    "content": content
                                })
                            
                            if response.status_code == 200:
                                result = response.json()
                                if result.get("auto_response_sent"):
                                    print(f"✅ Auto-response sent successfully!")
                                    print(f"   Intents detected: {[i['intent_name'] for i in result.get('classified_intents', [])]}")
                                else:
                                    print(f"📄 Email processed, no auto-response needed")
                                    print(f"   Reason: {result.get('message', 'Unknown')}")
                            else:
                                print(f"❌ API error: {response.status_code} - {response.text}")
                            
                            # Mark as read
                            mail.store(msg_id, '+FLAGS', '\\Seen')
                            
                    except Exception as e:
                        print(f"❌ Error processing email {msg_id}: {str(e)}")
                        continue
            else:
                print(f"   No new emails found")
            
            mail.close()
            mail.logout()
            
        except Exception as e:
            print(f"❌ IMAP connection error: {str(e)}")
    
    def extract_email_content(self, email_message):
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
            print(f"Error extracting email content: {str(e)}")
            return ""
    
    def extract_email_address(self, email_string):
        """Extract email address from string"""
        try:
            if '<' in email_string and '>' in email_string:
                return email_string.split('<')[1].split('>')[0]
            return email_string.strip()
        except:
            return email_string
    
    def run_continuous_monitoring(self, interval=30):
        """Run continuous email monitoring"""
        print(f"🚀 Starting continuous email monitoring (checking every {interval} seconds)")
        print(f"📧 Monitoring: {self.username}")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                self.check_for_new_emails()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n⏹️  Monitoring stopped by user")

if __name__ == "__main__":
    import time
    
    monitor = EmailMonitor()
    
    # Check once immediately
    monitor.check_for_new_emails()
    
    # Then run continuous monitoring
    # monitor.run_continuous_monitoring()