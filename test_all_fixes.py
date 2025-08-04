#!/usr/bin/env python3
"""
Test script to verify all fixes are working correctly
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
from app.services.groq_service import groq_service
from app.utils.helpers import generate_id, personalize_template

class FixVerifier:
    def __init__(self):
        self.test_results = {}
        self.setup_complete = False
    
    async def cleanup_previous_tests(self):
        """Clean up any previous test data"""
        print("🧹 Cleaning up previous test data...")
        
        await db_service.connect()
        
        # Remove test data
        await db_service.db.campaigns.delete_many({"name": {"$regex": ".*Test.*|.*Debug.*"}})
        await db_service.db.prospects.delete_many({"email": {"$regex": ".*test.*|.*debug.*"}})
        await db_service.db.emails.delete_many({"campaign_id": {"$exists": True}})
        await db_service.db.templates.delete_many({"name": {"$regex": ".*Test.*|.*Debug.*"}})
        await db_service.db.prospect_lists.delete_many({"name": {"$regex": ".*Test.*|.*Debug.*"}})
        await db_service.db.email_providers.delete_many({"name": {"$regex": ".*Test.*|.*Debug.*"}})
        await db_service.db.intents.delete_many({"name": {"$regex": ".*Test.*|.*Debug.*"}})
        await db_service.db.threads.delete_many({})
        
        print("✅ Cleanup complete")
    
    async def setup_test_data(self):
        """Setup test data for verification"""
        print("🔧 Setting up test data for fix verification...")
        
        if self.setup_complete:
            return True
        
        await db_service.connect()
        
        # Create test email provider
        provider_data = {
            "id": generate_id(),
            "name": "Fixed Test Provider",
            "provider_type": "gmail",
            "email_address": "fixed-test@example.com",
            "display_name": "Fixed Test Provider",
            "smtp_host": "smtp.gmail.com",
            "smtp_port": 587,
            "smtp_username": "fixed-test@example.com",
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
            "name": "Fixed Test Template",
            "subject": "Fixed Test: Hello {{first_name}}",
            "content": "Hello {{first_name}}, this is a test email to verify fixes work correctly.",
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
            "name": "Fixed Test List",
            "description": "List for verifying fixes",
            "color": "#28a745",
            "tags": ["fixed", "test"],
            "prospect_count": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db_service.create_list(list_data)
        self.list_id = list_data["id"]
        print(f"✅ Created test list: {self.list_id}")
        
        # Create test prospects
        self.test_prospects = []
        for i in range(2):
            prospect_data = {
                "id": generate_id(),
                "first_name": f"FixedUser{i+1}",
                "last_name": "Tester",
                "email": f"fixed-user{i+1}@test.com",
                "company": f"Fixed Test Company {i+1}",
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
        
        # Create test campaign
        campaign_data = {
            "id": generate_id(),
            "name": "Fixed Test Campaign",
            "template_id": self.template_id,
            "list_ids": [self.list_id],
            "max_emails": 100,
            "status": "draft",
            "follow_up_enabled": True,
            "follow_up_schedule_type": "interval",
            "follow_up_intervals": [1, 3],  # 1 minute, 3 minutes for testing
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
        
        # Create test intent with auto-response
        intent_data = {
            "id": generate_id(),
            "name": "Fixed Interest Intent",
            "description": "Intent showing interest in services - fixed version",
            "keywords": ["interested", "tell me more", "learn more", "pricing"],
            "auto_respond": True,
            "is_active": True,
            "response_template": "Thank you for your interest! This is a fixed auto-response.",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db_service.create_intent(intent_data)
        self.intent_id = intent_data["id"]
        print(f"✅ Created test intent: {self.intent_id}")
        
        print("✅ Test data setup complete!")
        self.setup_complete = True
        return True
    
    async def test_fix_1_no_duplicate_emails(self):
        """Test Fix 1: No duplicate emails when campaign is sent multiple times"""
        print("\n🔍 Testing Fix 1: No duplicate emails...")
        
        try:
            # Import the fixed campaign sending function
            from app.routes.campaigns import process_campaign_emails_with_follow_up_tracking
            
            # Get template and prospects
            template = await db_service.get_template_by_id(self.template_id)
            prospects = self.test_prospects
            
            # Send campaign first time
            print("📤 Sending campaign (first time)...")
            await process_campaign_emails_with_follow_up_tracking(
                self.campaign_id, 
                prospects, 
                template, 
                self.provider_id,
                {"follow_up_enabled": True}
            )
            
            await asyncio.sleep(1)  # Small delay
            
            # Try to send campaign second time (should be prevented)
            print("📤 Attempting to send campaign (second time - should be prevented)...")
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
            
            if not duplicates_found:
                print("✅ FIX 1 VERIFIED: No duplicates found - duplicate prevention working!")
                fix_1_working = True
            else:
                print("❌ FIX 1 FAILED: Duplicates still found")
                fix_1_working = False
            
            self.test_results["fix_1_duplicates"] = {
                "working": fix_1_working,
                "total_emails": len(emails),
                "unique_prospects": len(email_by_prospect),
                "duplicates_found": duplicates_found
            }
            
        except Exception as e:
            print(f"❌ Error testing fix 1: {str(e)}")
            import traceback
            traceback.print_exc()
            self.test_results["fix_1_duplicates"] = {"error": str(e)}
    
    async def test_fix_2_follow_up_threading_consistency(self):
        """Test Fix 2: Follow-up threading consistency"""
        print("\n🔍 Testing Fix 2: Follow-up threading consistency...")
        
        try:
            # Select test prospect
            test_prospect = self.test_prospects[0]
            prospect_id = test_prospect["id"]
            
            # Set up prospect for follow-up with past contact time to trigger immediate follow-up
            await db_service.update_prospect(prospect_id, {
                "campaign_id": self.campaign_id,
                "follow_up_status": "active",
                "follow_up_count": 0,
                "last_contact": datetime.utcnow() - timedelta(minutes=2),  # 2 minutes ago
                "email_provider_id": self.provider_id
            })
            
            # Trigger follow-up engine
            from app.services.smart_follow_up_engine_enhanced import enhanced_smart_follow_up_engine
            
            print("🔄 Triggering follow-up engine...")
            await enhanced_smart_follow_up_engine._check_and_send_follow_ups()
            
            # Check emails for consistent threading
            campaign_emails = await db_service.db.emails.find({
                "prospect_id": prospect_id,
                "campaign_id": self.campaign_id,
                "is_follow_up": False
            }).to_list(length=None)
            
            follow_up_emails = await db_service.db.emails.find({
                "prospect_id": prospect_id,
                "is_follow_up": True
            }).to_list(length=None)
            
            threading_consistent = True
            expected_thread_id = f"thread_{prospect_id}"
            
            print(f"📊 Campaign emails: {len(campaign_emails)}, Follow-up emails: {len(follow_up_emails)}")
            
            # Check campaign email threading
            for email in campaign_emails:
                thread_id = email.get("thread_id")
                if thread_id != expected_thread_id:
                    print(f"❌ Campaign email threading issue: Expected '{expected_thread_id}', got '{thread_id}'")
                    threading_consistent = False
            
            # Check follow-up email threading
            for email in follow_up_emails:
                thread_id = email.get("thread_id")
                if thread_id != expected_thread_id:
                    print(f"❌ Follow-up email threading issue: Expected '{expected_thread_id}', got '{thread_id}'")
                    threading_consistent = False
            
            if threading_consistent and (campaign_emails or follow_up_emails):
                print("✅ FIX 2 VERIFIED: Threading is consistent between campaign and follow-up emails!")
                fix_2_working = True
            elif not campaign_emails and not follow_up_emails:
                print("⚠️ No emails found to test threading")
                fix_2_working = False
            else:
                print("❌ FIX 2 FAILED: Threading inconsistency detected")
                fix_2_working = False
            
            self.test_results["fix_2_threading"] = {
                "working": fix_2_working,
                "consistent": threading_consistent,
                "campaign_emails": len(campaign_emails),
                "follow_up_emails": len(follow_up_emails),
                "expected_thread_id": expected_thread_id
            }
            
        except Exception as e:
            print(f"❌ Error testing fix 2: {str(e)}")
            import traceback
            traceback.print_exc()
            self.test_results["fix_2_threading"] = {"error": str(e)}
    
    async def test_fix_3_auto_responder_working(self):
        """Test Fix 3: Auto-responder functionality"""
        print("\n🔍 Testing Fix 3: Auto-responder functionality...")
        
        try:
            # Select test prospect
            test_prospect = self.test_prospects[1]
            prospect_id = test_prospect["id"]
            
            # Create thread for this prospect
            thread_id = f"thread_{prospect_id}"
            thread_data = {
                "id": thread_id,
                "prospect_id": prospect_id,
                "campaign_id": "",
                "messages": [],
                "last_activity": datetime.utcnow(),
                "created_at": datetime.utcnow()
            }
            
            await db_service.create_thread_context(thread_data)
            
            # Test groq service directly first (should use mock version)
            print("🧠 Testing Groq service classification...")
            
            test_content = "Hi, I'm very interested in learning more about your services. Can you tell me more about pricing?"
            classified_intents = await groq_service.classify_intents(test_content, "Interest in services")
            
            print(f"📊 Classified intents: {len(classified_intents)}")
            for intent in classified_intents:
                print(f"   - {intent.get('intent_name')} (confidence: {intent.get('confidence')}) auto_respond: {intent.get('auto_respond')}")
            
            if classified_intents:
                print("✅ Intent classification working!")
                
                # Test response generation
                response_data = await groq_service.generate_response(
                    test_content, 
                    "Interest in services", 
                    classified_intents, 
                    [], 
                    test_prospect
                )
                
                if response_data and not response_data.get("error"):
                    print("✅ Response generation working!")
                    print(f"   Subject: {response_data.get('subject')}")
                    print(f"   Content: {response_data.get('content')[:100]}...")
                    
                    # Test if auto-response should trigger
                    from app.services.email_processor import email_processor
                    should_respond = await email_processor._should_auto_respond(classified_intents)
                    
                    if should_respond:
                        print("✅ FIX 3 VERIFIED: Auto-responder functionality working!")
                        fix_3_working = True
                    else:
                        print("❌ FIX 3 PARTIAL: Classification works but auto-response not triggered")
                        fix_3_working = False
                else:
                    print(f"❌ Response generation failed: {response_data.get('error') if response_data else 'No response'}")
                    fix_3_working = False
            else:
                print("❌ FIX 3 FAILED: No intents classified")
                fix_3_working = False
            
            self.test_results["fix_3_auto_responder"] = {
                "working": fix_3_working,
                "intents_classified": len(classified_intents),
                "has_response": bool(response_data and not response_data.get("error")),
                "should_auto_respond": should_respond if 'should_respond' in locals() else False
            }
            
        except Exception as e:
            print(f"❌ Error testing fix 3: {str(e)}")
            import traceback
            traceback.print_exc()
            self.test_results["fix_3_auto_responder"] = {"error": str(e)}
    
    async def test_fix_4_follow_up_response_detection(self):
        """Test Fix 4: Enhanced follow-up response detection"""
        print("\n🔍 Testing Fix 4: Follow-up stops after response detection...")
        
        try:
            # Select test prospect
            test_prospect = self.test_prospects[0]
            prospect_id = test_prospect["id"]
            
            # Set up prospect for active follow-up
            await db_service.update_prospect(prospect_id, {
                "campaign_id": self.campaign_id,
                "follow_up_status": "active",
                "follow_up_count": 1,
                "last_contact": datetime.utcnow() - timedelta(minutes=5),
                "email_provider_id": self.provider_id
            })
            
            # Simulate receiving a manual response (not auto-reply)
            thread_id = f"thread_{prospect_id}"
            
            # Check if thread exists, create if not
            existing_thread = await db_service.get_thread_by_id(thread_id)
            if not existing_thread:
                thread_data = {
                    "id": thread_id,
                    "prospect_id": prospect_id,
                    "campaign_id": self.campaign_id,
                    "email_provider_id": self.provider_id,
                    "messages": [],
                    "last_activity": datetime.utcnow(),
                    "created_at": datetime.utcnow()
                }
                await db_service.create_thread_context(thread_data)
            
            # Add a sent message to the thread first
            await db_service.add_message_to_thread(thread_id, {
                "type": "sent",
                "recipient": test_prospect["email"],
                "subject": "Test Campaign Email",
                "content": "Test content",
                "timestamp": datetime.utcnow() - timedelta(minutes=3),
                "sent_by_us": True
            })
            
            # Add a manual response
            await db_service.add_message_to_thread(thread_id, {
                "type": "received",
                "sender": test_prospect["email"],
                "subject": "Re: Test Campaign Email",
                "content": "Thanks for your email! I'm definitely interested in learning more about this.",
                "timestamp": datetime.utcnow() - timedelta(minutes=1),
                "is_response_to_our_email": True
            })
            
            print(f"✅ Simulated manual response from {test_prospect['email']}")
            
            # Process this response through the email processor
            from app.services.email_processor import email_processor
            
            # Get updated thread
            thread = await db_service.get_thread_by_id(thread_id)
            
            # Simulate handling the response
            await email_processor._handle_prospect_response(
                test_prospect, 
                "Thanks for your email! I'm definitely interested in learning more about this.",
                "Re: Test Campaign Email",
                thread
            )
            
            # Check if follow-up status was updated
            updated_prospect = await db_service.get_prospect_by_id(prospect_id)
            follow_up_status = updated_prospect.get("follow_up_status")
            response_type = updated_prospect.get("response_type")
            
            print(f"📊 Follow-up status after response: {follow_up_status}")
            print(f"📊 Response type: {response_type}")
            
            if follow_up_status == "stopped" and response_type == "manual":
                print("✅ FIX 4 VERIFIED: Follow-up correctly stopped after manual response!")
                fix_4_working = True
            else:
                print("❌ FIX 4 FAILED: Follow-up did not stop after manual response")
                fix_4_working = False
            
            self.test_results["fix_4_response_detection"] = {
                "working": fix_4_working,
                "follow_up_status": follow_up_status,
                "response_type": response_type,
                "prospect_updated": bool(updated_prospect)
            }
            
        except Exception as e:
            print(f"❌ Error testing fix 4: {str(e)}")
            import traceback
            traceback.print_exc()
            self.test_results["fix_4_response_detection"] = {"error": str(e)}
    
    async def run_all_tests(self):
        """Run all fix verification tests"""
        print("🚀 Starting comprehensive fix verification...")
        print("=" * 60)
        
        # Cleanup previous tests
        await self.cleanup_previous_tests()
        
        # Setup test data
        if not await self.setup_test_data():
            print("❌ Failed to setup test data")
            return
        
        # Run all fix tests
        await self.test_fix_1_no_duplicate_emails()
        await self.test_fix_2_follow_up_threading_consistency()
        await self.test_fix_3_auto_responder_working()
        await self.test_fix_4_follow_up_response_detection()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 FIX VERIFICATION RESULTS")
        print("=" * 60)
        
        fixes_working = 0
        total_fixes = 0
        
        for fix, result in self.test_results.items():
            total_fixes += 1
            print(f"\n{fix.upper().replace('_', ' ')}:")
            if "error" in result:
                print(f"  ❌ ERROR: {result['error']}")
            else:
                working = result.get("working", False)
                if working:
                    print(f"  ✅ WORKING")
                    fixes_working += 1
                else:
                    print(f"  ❌ NOT WORKING")
                
                # Print details
                for key, value in result.items():
                    if key != "working":
                        print(f"    - {key}: {value}")
        
        print(f"\n🎯 SUMMARY:")
        print(f"   ✅ Fixes working: {fixes_working}/{total_fixes}")
        print(f"   📈 Success rate: {(fixes_working/total_fixes*100):.1f}%")
        
        if fixes_working == total_fixes:
            print("\n🎉 ALL FIXES VERIFIED AND WORKING!")
        else:
            print(f"\n⚠️  {total_fixes - fixes_working} FIXES STILL NEED ATTENTION")
        
        return self.test_results

async def main():
    verifier = FixVerifier()
    results = await verifier.run_all_tests()
    return results

if __name__ == "__main__":
    asyncio.run(main())