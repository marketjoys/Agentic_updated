#!/usr/bin/env python3
"""
Comprehensive debug script to identify and reproduce all reported issues:
1. Same email being sent twice when campaign is scheduled
2. Follow-up emails not stopping after receiving a response  
3. Follow-up emails not being sent in the same thread as campaigns
4. Auto-responder not responding to emails even when there's a clear intent of interest
"""
import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add the backend app to the Python path
sys.path.append('/app/backend')

from app.services.database import db_service
from app.services.enhanced_database import enhanced_db_service
from app.services.email_provider_service import email_provider_service
from app.utils.helpers import generate_id, personalize_template

class IssueDebugger:
    def __init__(self):
        self.test_results = {}
    
    async def setup_test_data(self):
        """Setup minimal test data to reproduce issues"""
        print("🔧 Setting up test data...")
        
        await db_service.connect()
        
        # Create test email provider
        provider_data = {
            "id": generate_id(),
            "name": "Test Debug Provider",
            "provider_type": "gmail",
            "email_address": "test@example.com",
            "display_name": "Test Provider",
            "smtp_host": "smtp.gmail.com",
            "smtp_port": 587,
            "smtp_username": "test@example.com",
            "smtp_password": "test_password",
            "smtp_use_tls": True,
            "daily_send_limit": 500,
            "hourly_send_limit": 50,
            "is_default": True,
            "is_active": True,
            "skip_connection_test": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db_service.create_email_provider(provider_data)
        self.provider_id = provider_data["id"]
        print(f"✅ Created test provider: {self.provider_id}")
        
        # Create test template
        template_data = {
            "id": generate_id(),
            "name": "Test Debug Template",
            "subject": "Test Subject for {{first_name}}",
            "content": "Hello {{first_name}}, this is a test email.",
            "type": "campaign",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db_service.create_template(template_data)
        self.template_id = template_data["id"]
        print(f"✅ Created test template: {self.template_id}")
        
        # Create test list
        list_data = {
            "id": generate_id(),
            "name": "Debug Test List",
            "description": "List for debugging issues",
            "color": "#ff6b6b",
            "tags": ["debug", "test"],
            "prospect_count": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db_service.create_list(list_data)
        self.list_id = list_data["id"]
        print(f"✅ Created test list: {self.list_id}")
        
        # Create test prospects
        self.test_prospects = []
        for i in range(3):
            prospect_data = {
                "id": generate_id(),
                "first_name": f"TestUser{i+1}",
                "last_name": "Debugger",
                "email": f"testuser{i+1}@debug.com",
                "company": f"Debug Company {i+1}",
                "list_ids": [self.list_id],
                "status": "active",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result, error = await db_service.create_prospect(prospect_data)
            if result:
                self.test_prospects.append(prospect_data)
                print(f"✅ Created test prospect: {prospect_data['email']}")
            else:
                print(f"❌ Failed to create prospect: {error}")
        
        # Create test campaign with follow-up
        campaign_data = {
            "id": generate_id(),
            "name": "Debug Test Campaign",
            "template_id": self.template_id,
            "list_ids": [self.list_id],
            "max_emails": 100,
            "status": "draft",
            "follow_up_enabled": True,
            "follow_up_schedule_type": "interval",
            "follow_up_intervals": [1, 3, 7],  # 1 minute, 3 minutes, 7 minutes for testing
            "follow_up_timezone": "UTC",
            "follow_up_time_window_start": "00:00",
            "follow_up_time_window_end": "23:59",
            "follow_up_days_of_week": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
            "follow_up_templates": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db_service.create_campaign(campaign_data)
        self.campaign_id = campaign_data["id"]
        print(f"✅ Created test campaign: {self.campaign_id}")
        
        print("✅ Test data setup complete!")
        return True
    
    async def test_issue_1_duplicate_emails(self):
        """Test Issue 1: Same email being sent twice"""
        print("\n🔍 Testing Issue 1: Duplicate email sending...")
        
        try:
            # Import the campaign sending function
            from app.routes.campaigns import process_campaign_emails_with_follow_up_tracking
            
            # Get template and prospects
            template = await db_service.get_template_by_id(self.template_id)
            prospects = self.test_prospects
            
            # Send campaign twice to simulate duplicate issue
            print("📤 Sending campaign (first time)...")
            await process_campaign_emails_with_follow_up_tracking(
                self.campaign_id, 
                prospects, 
                template, 
                self.provider_id,
                {"follow_up_enabled": True}
            )
            
            await asyncio.sleep(1)  # Small delay
            
            print("📤 Sending campaign (second time to test duplicates)...")
            await process_campaign_emails_with_follow_up_tracking(
                self.campaign_id, 
                prospects, 
                template, 
                self.provider_id,
                {"follow_up_enabled": True}
            )
            
            # Check for duplicate emails
            emails = await db_service.db.emails.find({
                "campaign_id": self.campaign_id,
                "is_follow_up": False
            }).to_list(length=None)
            
            # Group emails by prospect
            email_by_prospect = {}
            for email in emails:
                prospect_id = email.get("prospect_id")
                if prospect_id not in email_by_prospect:
                    email_by_prospect[prospect_id] = []
                email_by_prospect[prospect_id].append(email)
            
            duplicates_found = False
            for prospect_id, prospect_emails in email_by_prospect.items():
                if len(prospect_emails) > 1:
                    duplicates_found = True
                    print(f"❌ DUPLICATE FOUND: Prospect {prospect_id} has {len(prospect_emails)} emails")
                    for email in prospect_emails:
                        print(f"   - Email ID: {email.get('id')[:8]} | Sent: {email.get('sent_at')}")
            
            if not duplicates_found:
                print("✅ No duplicates found - this might be working correctly")
            
            self.test_results["issue_1_duplicates"] = {
                "duplicates_found": duplicates_found,
                "total_emails": len(emails),
                "unique_prospects": len(email_by_prospect)
            }
            
        except Exception as e:
            print(f"❌ Error testing issue 1: {str(e)}")
            import traceback
            traceback.print_exc()
            self.test_results["issue_1_duplicates"] = {"error": str(e)}
    
    async def test_issue_2_follow_up_not_stopping(self):
        """Test Issue 2: Follow-up not stopping after response"""
        print("\n🔍 Testing Issue 2: Follow-up not stopping after response...")
        
        try:
            # Select a test prospect
            test_prospect = self.test_prospects[0]
            prospect_id = test_prospect["id"]
            
            # Set up the prospect for follow-up
            await db_service.update_prospect(prospect_id, {
                "campaign_id": self.campaign_id,
                "follow_up_status": "active",
                "follow_up_count": 0,
                "last_contact": datetime.utcnow() - timedelta(minutes=2),
                "email_provider_id": self.provider_id
            })
            
            # Create a thread and simulate receiving a response
            thread_data = {
                "id": f"thread_{prospect_id}",
                "prospect_id": prospect_id,
                "campaign_id": self.campaign_id,
                "email_provider_id": self.provider_id,
                "messages": [
                    {
                        "type": "sent",
                        "recipient": test_prospect["email"],
                        "subject": "Test Email",
                        "content": "Test content",
                        "timestamp": datetime.utcnow() - timedelta(minutes=2),
                        "sent_by_us": True
                    },
                    {
                        "type": "received",
                        "sender": test_prospect["email"],
                        "subject": "Re: Test Email",
                        "content": "Thanks for your email! I'm interested in learning more.",
                        "timestamp": datetime.utcnow() - timedelta(minutes=1),
                        "is_response_to_our_email": True
                    }
                ],
                "last_activity": datetime.utcnow() - timedelta(minutes=1),
                "created_at": datetime.utcnow() - timedelta(minutes=2)
            }
            
            await db_service.create_thread_context(thread_data)
            print(f"✅ Created thread with response for prospect: {test_prospect['email']}")
            
            # Now check if the follow-up engine properly detects the response
            from app.services.smart_follow_up_engine_enhanced import enhanced_smart_follow_up_engine
            
            print("🔄 Running follow-up engine to test response detection...")
            await enhanced_smart_follow_up_engine._check_and_send_follow_ups()
            
            # Check if follow-up status was updated
            updated_prospect = await db_service.get_prospect_by_id(prospect_id)
            follow_up_status = updated_prospect.get("follow_up_status")
            
            print(f"📊 Follow-up status after response: {follow_up_status}")
            
            if follow_up_status == "stopped":
                print("✅ Follow-up correctly stopped after response")
                issue_2_working = True
            else:
                print("❌ Follow-up did NOT stop after response - BUG CONFIRMED")
                issue_2_working = False
            
            # Check if any follow-up emails were sent despite the response
            follow_up_emails = await db_service.db.emails.find({
                "prospect_id": prospect_id,
                "is_follow_up": True,
                "sent_at": {"$gte": datetime.utcnow() - timedelta(minutes=1)}
            }).to_list(length=None)
            
            if follow_up_emails:
                print(f"❌ Follow-up emails were sent despite response: {len(follow_up_emails)}")
                issue_2_working = False
            
            self.test_results["issue_2_follow_up_stopping"] = {
                "working": issue_2_working,
                "follow_up_status": follow_up_status,
                "follow_up_emails_sent": len(follow_up_emails)
            }
            
        except Exception as e:
            print(f"❌ Error testing issue 2: {str(e)}")
            import traceback
            traceback.print_exc()
            self.test_results["issue_2_follow_up_stopping"] = {"error": str(e)}
    
    async def test_issue_3_threading_consistency(self):
        """Test Issue 3: Threading consistency between campaigns and follow-ups"""
        print("\n🔍 Testing Issue 3: Threading consistency...")
        
        try:
            # Select test prospect
            test_prospect = self.test_prospects[1]
            prospect_id = test_prospect["id"]
            
            # Set up prospect for follow-up with past contact time
            await db_service.update_prospect(prospect_id, {
                "campaign_id": self.campaign_id,
                "follow_up_status": "active",
                "follow_up_count": 0,
                "last_contact": datetime.utcnow() - timedelta(minutes=3),
                "email_provider_id": self.provider_id
            })
            
            # Create initial email record (campaign email)
            campaign_email_id = generate_id()
            campaign_email = {
                "id": campaign_email_id,
                "prospect_id": prospect_id,
                "campaign_id": self.campaign_id,
                "email_provider_id": self.provider_id,
                "recipient_email": test_prospect["email"],
                "subject": "Campaign Email",
                "content": "Initial campaign email",
                "status": "sent",
                "sent_at": datetime.utcnow() - timedelta(minutes=3),
                "created_at": datetime.utcnow() - timedelta(minutes=3),
                "is_follow_up": False,
                "follow_up_sequence": 0,
                "sent_by_us": True,
                "thread_id": f"thread_{prospect_id}",
                "template_id": self.template_id
            }
            
            await db_service.create_email_record(campaign_email)
            print(f"✅ Created campaign email with thread_id: thread_{prospect_id}")
            
            # Force send follow-up
            from app.services.smart_follow_up_engine_enhanced import enhanced_smart_follow_up_engine
            
            print("🔄 Triggering follow-up engine...")
            await enhanced_smart_follow_up_engine._check_and_send_follow_ups()
            
            # Check if follow-up was sent and uses same thread
            follow_up_emails = await db_service.db.emails.find({
                "prospect_id": prospect_id,
                "is_follow_up": True
            }).to_list(length=None)
            
            threading_consistent = True
            expected_thread_id = f"thread_{prospect_id}"
            
            print(f"📊 Follow-up emails found: {len(follow_up_emails)}")
            
            for email in follow_up_emails:
                email_thread_id = email.get("thread_id")
                print(f"   - Email: {email.get('id')[:8]} | Thread: {email_thread_id}")
                
                if email_thread_id != expected_thread_id:
                    print(f"❌ Threading inconsistency: Expected '{expected_thread_id}', got '{email_thread_id}'")
                    threading_consistent = False
            
            if threading_consistent and follow_up_emails:
                print("✅ Threading is consistent between campaign and follow-up emails")
            elif not follow_up_emails:
                print("⚠️ No follow-up emails sent - cannot test threading")
            else:
                print("❌ Threading inconsistency detected - BUG CONFIRMED")
            
            self.test_results["issue_3_threading"] = {
                "consistent": threading_consistent,
                "follow_up_emails_count": len(follow_up_emails),
                "expected_thread_id": expected_thread_id
            }
            
        except Exception as e:
            print(f"❌ Error testing issue 3: {str(e)}")
            import traceback
            traceback.print_exc()
            self.test_results["issue_3_threading"] = {"error": str(e)}
    
    async def test_issue_4_auto_responder(self):
        """Test Issue 4: Auto-responder not responding"""
        print("\n🔍 Testing Issue 4: Auto-responder functionality...")
        
        try:
            # Create test intent with auto-response enabled
            intent_data = {
                "id": generate_id(),
                "name": "Interest Intent",
                "description": "Intent showing interest in services",
                "keywords": ["interested", "tell me more", "learn more", "pricing"],
                "auto_respond": True,
                "is_active": True,
                "response_template": "Thank you for your interest! We'll be in touch soon.",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            await db_service.create_intent(intent_data)
            print(f"✅ Created test intent: {intent_data['id']}")
            
            # Select test prospect
            test_prospect = self.test_prospects[2]
            prospect_id = test_prospect["id"]
            
            # Create thread for this prospect
            thread_data = {
                "id": f"thread_{prospect_id}",
                "prospect_id": prospect_id,
                "campaign_id": "",
                "messages": [],
                "last_activity": datetime.utcnow(),
                "created_at": datetime.utcnow()
            }
            
            await db_service.create_thread_context(thread_data)
            
            # Simulate incoming email with clear intent
            from app.services.email_processor import email_processor
            
            # Create a mock email message
            class MockEmailMessage:
                def __init__(self):
                    self.headers = {
                        "From": f"Test User <{test_prospect['email']}>",
                        "Subject": "Re: Interest in your services",
                        "Date": datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S %z")
                    }
                    self.content = "Hi, I'm very interested in learning more about your services. Can you tell me more about pricing?"
                
                def get(self, header, default=""):
                    return self.headers.get(header, default)
            
            mock_email = MockEmailMessage()
            
            print("📨 Processing mock email with interest intent...")
            
            # Test the email processing
            result = await email_processor._process_email(mock_email)
            
            if result:
                print("✅ Email processed successfully")
                
                # Check if auto-response was sent
                auto_responses = await db_service.db.emails.find({
                    "recipient_email": test_prospect["email"],
                    "is_auto_response": True,
                    "sent_at": {"$gte": datetime.utcnow() - timedelta(minutes=1)}
                }).to_list(length=None)
                
                if auto_responses:
                    print(f"✅ Auto-response sent: {len(auto_responses)} responses")
                    for response in auto_responses:
                        print(f"   - Subject: {response.get('subject')}")
                        print(f"   - Content: {response.get('content')[:50]}...")
                    auto_responder_working = True
                else:
                    print("❌ No auto-response sent despite clear intent - BUG CONFIRMED")
                    auto_responder_working = False
            else:
                print("❌ Email processing failed")
                auto_responder_working = False
            
            self.test_results["issue_4_auto_responder"] = {
                "working": auto_responder_working,
                "email_processed": result,
                "auto_responses_sent": len(auto_responses) if 'auto_responses' in locals() else 0
            }
            
        except Exception as e:
            print(f"❌ Error testing issue 4: {str(e)}")
            import traceback
            traceback.print_exc()
            self.test_results["issue_4_auto_responder"] = {"error": str(e)}
    
    async def run_all_tests(self):
        """Run all issue tests"""
        print("🚀 Starting comprehensive issue debugging...")
        print("=" * 60)
        
        # Setup test data
        if not await self.setup_test_data():
            print("❌ Failed to setup test data")
            return
        
        # Run all tests
        await self.test_issue_1_duplicate_emails()
        await self.test_issue_2_follow_up_not_stopping()
        await self.test_issue_3_threading_consistency()
        await self.test_issue_4_auto_responder()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST RESULTS SUMMARY")
        print("=" * 60)
        
        for issue, result in self.test_results.items():
            print(f"\n{issue.upper().replace('_', ' ')}:")
            if "error" in result:
                print(f"  ❌ ERROR: {result['error']}")
            else:
                for key, value in result.items():
                    print(f"  - {key}: {value}")
        
        # Identify which issues need fixing
        issues_to_fix = []
        
        if self.test_results.get("issue_1_duplicates", {}).get("duplicates_found"):
            issues_to_fix.append("1. Duplicate email sending")
        
        if not self.test_results.get("issue_2_follow_up_stopping", {}).get("working"):
            issues_to_fix.append("2. Follow-up not stopping after response")
        
        if not self.test_results.get("issue_3_threading", {}).get("consistent"):
            issues_to_fix.append("3. Threading consistency")
        
        if not self.test_results.get("issue_4_auto_responder", {}).get("working"):
            issues_to_fix.append("4. Auto-responder functionality")
        
        print(f"\n🎯 ISSUES THAT NEED FIXING:")
        if issues_to_fix:
            for issue in issues_to_fix:
                print(f"  ❌ {issue}")
        else:
            print("  ✅ All tests passed! No issues detected.")
        
        return self.test_results

async def main():
    debugger = IssueDebugger()
    results = await debugger.run_all_tests()
    return results

if __name__ == "__main__":
    asyncio.run(main())