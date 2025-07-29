#!/usr/bin/env python3
"""
End-to-End Email and Follow-up Testing
Testing actual email sending and follow-up functionality
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
BACKEND_URL = "https://9f8a7167-d7f1-4045-b864-65d30ef37460.preview.emergentagent.com/api"
LOGIN_CREDENTIALS = {"username": "testuser", "password": "testpass123"}

class EndToEndTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_results = []
        self.created_items = {"campaigns": [], "lists": [], "templates": [], "prospects": []}
        
    async def setup_session(self):
        """Setup HTTP session and authenticate"""
        self.session = aiohttp.ClientSession()
        
        try:
            async with self.session.post(f"{BACKEND_URL}/auth/login", json=LOGIN_CREDENTIALS) as response:
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data.get("access_token")
                    logger.info("✅ Authentication successful")
                    return True
                else:
                    logger.error(f"❌ Authentication failed: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ Authentication error: {str(e)}")
            return False
    
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    def get_headers(self):
        """Get headers with auth token"""
        return {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
    
    async def test_email_provider_configuration(self):
        """Test email provider connectivity"""
        logger.info("\n🔍 TEST 1: Email Provider Configuration and Testing")
        
        try:
            # Get email providers
            async with self.session.get(f"{BACKEND_URL}/email-providers", headers=self.get_headers()) as response:
                if response.status == 200:
                    providers = await response.json()
                    logger.info(f"✅ Found {len(providers)} email providers")
                    
                    working_provider = None
                    for provider in providers:
                        provider_id = provider.get('id')
                        provider_name = provider.get('name')
                        provider_email = provider.get('email_address')
                        
                        logger.info(f"📧 Testing provider: {provider_name} ({provider_email})")
                        
                        # Test provider
                        try:
                            async with self.session.post(f"{BACKEND_URL}/email-providers/{provider_id}/test", 
                                                        headers=self.get_headers()) as test_response:
                                if test_response.status == 200:
                                    test_result = await test_response.json()
                                    logger.info(f"   Test results: {test_result}")
                                    
                                    if test_result.get('overall_status') == 'passed':
                                        working_provider = provider
                                        logger.info(f"✅ Working provider found: {provider_name}")
                                        break
                                    elif 'passed' in str(test_result.get('smtp_test', '')):
                                        working_provider = provider
                                        logger.info(f"✅ SMTP working for provider: {provider_name}")
                                        break
                                else:
                                    logger.warning(f"⚠️ Provider test failed: {test_response.status}")
                        except Exception as e:
                            logger.warning(f"⚠️ Error testing provider {provider_name}: {str(e)}")
                    
                    if working_provider:
                        self.test_results.append({"test": "Email Provider Check", "status": "PASS", 
                                                "details": f"Working provider: {working_provider['name']}"})
                        return working_provider
                    else:
                        self.test_results.append({"test": "Email Provider Check", "status": "FAIL", 
                                                "details": "No working email providers"})
                        return None
                else:
                    logger.error(f"❌ Failed to get providers: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"❌ Provider test failed: {str(e)}")
            return None
    
    async def create_test_template(self):
        """Create a test email template"""
        logger.info("\n🔍 Creating Test Template")
        
        template_data = {
            "name": "E2E Follow-up Test Template",
            "subject": "Follow-up Test Email - {{first_name}} from {{company}}",
            "content": """Hi {{first_name}},

This is a test email to verify the follow-up system is working correctly.

Your details:
- Name: {{first_name}} {{last_name}}
- Company: {{company}}
- Email: {{email}}

This email was sent at: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """

Best regards,
Follow-up Test System
            """,
            "type": "initial",
            "is_html_enabled": False
        }
        
        try:
            async with self.session.post(f"{BACKEND_URL}/templates", json=template_data, headers=self.get_headers()) as response:
                if response.status == 200:
                    template = await response.json()
                    template_id = template.get('id')
                    self.created_items['templates'].append(template_id)
                    logger.info(f"✅ Template created: {template_id}")
                    return template_id
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Template creation failed: {response.status} - {error_text}")
                    return None
        except Exception as e:
            logger.error(f"❌ Template creation error: {str(e)}")
            return None
    
    async def create_test_prospects_and_list(self):
        """Create test prospects and list"""
        logger.info("\n🔍 Creating Test Prospects and List")
        
        # Create a prospect list
        list_data = {
            "name": "E2E Follow-up Test List",
            "description": "Test list for end-to-end follow-up testing",
            "color": "#3B82F6",
            "tags": ["test", "e2e", "followup"]
        }
        
        try:
            async with self.session.post(f"{BACKEND_URL}/lists", json=list_data, headers=self.get_headers()) as response:
                if response.status == 200:
                    list_result = await response.json()
                    list_id = list_result.get('id')
                    self.created_items['lists'].append(list_id)
                    logger.info(f"✅ List created: {list_id}")
                else:
                    logger.error(f"❌ List creation failed: {response.status}")
                    return None, []
        except Exception as e:
            logger.error(f"❌ List creation error: {str(e)}")
            return None, []
        
        # Create test prospects
        test_prospects = [
            {
                "first_name": "Test",
                "last_name": "User1",
                "email": "testuser1@example.com",  # Using example.com for safety
                "company": "Test Company 1",
                "job_title": "Test Manager",
                "list_ids": [list_id]
            },
            {
                "first_name": "Demo",
                "last_name": "User2", 
                "email": "demouser2@example.com",  # Using example.com for safety
                "company": "Demo Company 2",
                "job_title": "Demo Director",
                "list_ids": [list_id]
            }
        ]
        
        created_prospects = []
        for prospect_data in test_prospects:
            try:
                # Check if prospect already exists
                async with self.session.get(f"{BACKEND_URL}/prospects", headers=self.get_headers()) as response:
                    if response.status == 200:
                        existing_prospects = await response.json()
                        existing_emails = [p.get('email') for p in existing_prospects]
                        
                        if prospect_data['email'] not in existing_emails:
                            # Create prospect (simplified - we'll need to implement the endpoint or use bulk upload)
                            # For now, let's assume prospects already exist
                            logger.info(f"📧 Test prospect: {prospect_data['email']}")
                            created_prospects.append(prospect_data)
                        else:
                            logger.info(f"📧 Prospect already exists: {prospect_data['email']}")
                            # Find the existing prospect and add to list
                            existing_prospect = next(p for p in existing_prospects if p.get('email') == prospect_data['email'])
                            created_prospects.append(existing_prospect)
                            
            except Exception as e:
                logger.error(f"❌ Error checking prospects: {str(e)}")
        
        return list_id, created_prospects
    
    async def create_campaign_with_followup(self, template_id, list_id, provider):
        """Create a campaign with follow-up enabled"""
        logger.info("\n🔍 Creating Campaign with Follow-up Enabled")
        
        # Create follow-up dates (5 minutes, 10 minutes, and 1 hour from now for quick testing)
        now = datetime.utcnow()
        follow_up_dates = [
            (now + timedelta(minutes=5)).isoformat() + "Z",
            (now + timedelta(minutes=10)).isoformat() + "Z",
            (now + timedelta(hours=1)).isoformat() + "Z"
        ]
        
        campaign_data = {
            "name": "E2E Follow-up Test Campaign",
            "template_id": template_id,
            "list_ids": [list_id],
            "max_emails": 10,
            "follow_up_enabled": True,
            "follow_up_schedule_type": "datetime",
            "follow_up_dates": follow_up_dates,
            "follow_up_timezone": "UTC",
            "follow_up_time_window_start": "00:00",  # Allow sending at any time for testing
            "follow_up_time_window_end": "23:59",
            "follow_up_days_of_week": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        }
        
        try:
            async with self.session.post(f"{BACKEND_URL}/campaigns", json=campaign_data, headers=self.get_headers()) as response:
                if response.status == 200:
                    campaign = await response.json()
                    campaign_id = campaign.get('id')
                    self.created_items['campaigns'].append(campaign_id)
                    logger.info(f"✅ Campaign created: {campaign_id}")
                    logger.info(f"📅 Follow-up dates: {follow_up_dates}")
                    return campaign_id
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Campaign creation failed: {response.status} - {error_text}")
                    return None
        except Exception as e:
            logger.error(f"❌ Campaign creation error: {str(e)}")
            return None
    
    async def send_campaign_and_verify(self, campaign_id, provider):
        """Send campaign and verify emails are sent"""
        logger.info(f"\n🔍 Sending Campaign {campaign_id}")
        
        send_data = {
            "send_immediately": True,
            "max_emails": 10,
            "follow_up_enabled": True,
            "email_provider_id": provider['id']
        }
        
        try:
            async with self.session.post(f"{BACKEND_URL}/campaigns/{campaign_id}/send", 
                                       json=send_data, headers=self.get_headers()) as response:
                if response.status == 200:
                    send_result = await response.json()
                    total_sent = send_result.get('total_sent', 0)
                    total_failed = send_result.get('total_failed', 0)
                    
                    logger.info(f"✅ Campaign send completed")
                    logger.info(f"📊 Total sent: {total_sent}")
                    logger.info(f"📊 Total failed: {total_failed}")
                    
                    # Verify campaign status changed to active (for follow-ups)
                    async with self.session.get(f"{BACKEND_URL}/campaigns/{campaign_id}", headers=self.get_headers()) as status_response:
                        if status_response.status == 200:
                            campaign_data = await status_response.json()
                            status = campaign_data.get('status')
                            logger.info(f"📋 Campaign status after send: {status}")
                            
                            if status == 'active':
                                logger.info("✅ Campaign is active - follow-ups will be processed")
                                self.test_results.append({
                                    "test": "Campaign Sending", 
                                    "status": "PASS",
                                    "details": f"Sent {total_sent} emails, status: {status}"
                                })
                                return True
                            else:
                                logger.warning(f"⚠️ Campaign status is {status}, expected 'active'")
                    
                    return total_sent > 0
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Campaign send failed: {response.status} - {error_text}")
                    return False
        except Exception as e:
            logger.error(f"❌ Campaign send error: {str(e)}")
            return False
    
    async def verify_followup_engine_status(self):
        """Verify follow-up engine is running"""
        logger.info("\n🔍 Verifying Follow-up Engine Status")
        
        try:
            async with self.session.get(f"{BACKEND_URL}/services/status", headers=self.get_headers()) as response:
                if response.status == 200:
                    status_data = await response.json()
                    services = status_data.get('services', {})
                    followup_engine = services.get('smart_follow_up_engine', {})
                    
                    engine_status = followup_engine.get('status')
                    logger.info(f"🔄 Follow-up engine status: {engine_status}")
                    
                    if engine_status == 'running':
                        logger.info("✅ Follow-up engine is running")
                        self.test_results.append({
                            "test": "Follow-up Engine Status",
                            "status": "PASS", 
                            "details": "Engine is running"
                        })
                        return True
                    else:
                        logger.warning(f"⚠️ Follow-up engine status: {engine_status}")
                        # Try to start it
                        await self.start_followup_engine()
                        return False
                else:
                    logger.error(f"❌ Failed to get service status: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ Engine status check error: {str(e)}")
            return False
    
    async def start_followup_engine(self):
        """Start the follow-up engine"""
        logger.info("🔄 Starting Follow-up Engine")
        
        try:
            async with self.session.post(f"{BACKEND_URL}/services/start-all", headers=self.get_headers()) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"✅ Services started: {result}")
                    return True
                else:
                    logger.error(f"❌ Failed to start services: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ Engine start error: {str(e)}")
            return False
    
    async def monitor_followup_execution(self, campaign_id, wait_minutes=15):
        """Monitor follow-up execution for a specified time"""
        logger.info(f"\n🔍 Monitoring Follow-up Execution for {wait_minutes} minutes")
        
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=wait_minutes)
        
        logger.info(f"⏰ Monitoring from {start_time.strftime('%H:%M:%S')} to {end_time.strftime('%H:%M:%S')}")
        
        followups_detected = 0
        
        while datetime.now() < end_time:
            try:
                # Check campaign details for follow-up activity
                async with self.session.get(f"{BACKEND_URL}/campaigns/{campaign_id}", headers=self.get_headers()) as response:
                    if response.status == 200:
                        campaign_data = await response.json()
                        email_records = campaign_data.get('email_records', [])
                        
                        # Count follow-up emails
                        followup_emails = [email for email in email_records if email.get('is_follow_up', False)]
                        current_followups = len(followup_emails)
                        
                        if current_followups > followups_detected:
                            new_followups = current_followups - followups_detected
                            followups_detected = current_followups
                            logger.info(f"📧 {new_followups} new follow-up email(s) detected! Total: {followups_detected}")
                            
                            # Log details of new follow-ups
                            for email in followup_emails[-new_followups:]:
                                logger.info(f"   Follow-up #{email.get('follow_up_sequence')}: {email.get('recipient_email')} at {email.get('sent_at')}")
                
                # Check engine status
                async with self.session.get(f"{BACKEND_URL}/services/status", headers=self.get_headers()) as response:
                    if response.status == 200:
                        status_data = await response.json()
                        services = status_data.get('services', {})
                        followup_engine = services.get('smart_follow_up_engine', {})
                        
                        engine_status = followup_engine.get('status')
                        if engine_status != 'running':
                            logger.warning(f"⚠️ Follow-up engine not running: {engine_status}")
            
            except Exception as e:
                logger.error(f"❌ Monitoring error: {str(e)}")
            
            await asyncio.sleep(30)  # Check every 30 seconds
        
        if followups_detected > 0:
            logger.info(f"✅ Follow-up monitoring completed: {followups_detected} follow-ups sent")
            self.test_results.append({
                "test": "Follow-up Execution",
                "status": "PASS",
                "details": f"{followups_detected} follow-ups sent during monitoring"
            })
        else:
            logger.warning("⚠️ No follow-ups detected during monitoring period")
            self.test_results.append({
                "test": "Follow-up Execution", 
                "status": "FAIL",
                "details": "No follow-ups detected"
            })
        
        return followups_detected > 0
    
    async def verify_database_records(self, campaign_id):
        """Verify database records are properly created"""
        logger.info("\n🔍 Verifying Database Records")
        
        try:
            # Check campaign details
            async with self.session.get(f"{BACKEND_URL}/campaigns/{campaign_id}", headers=self.get_headers()) as response:
                if response.status == 200:
                    campaign_data = await response.json()
                    
                    # Verify campaign data
                    follow_up_enabled = campaign_data.get('follow_up_enabled', False)
                    follow_up_dates = campaign_data.get('follow_up_dates', [])
                    status = campaign_data.get('status')
                    email_records = campaign_data.get('email_records', [])
                    
                    logger.info(f"📊 Campaign Analysis:")
                    logger.info(f"   Follow-up enabled: {follow_up_enabled}")
                    logger.info(f"   Follow-up dates count: {len(follow_up_dates)}")
                    logger.info(f"   Campaign status: {status}")
                    logger.info(f"   Email records: {len(email_records)}")
                    
                    # Analyze email records
                    initial_emails = [e for e in email_records if not e.get('is_follow_up', False)]
                    followup_emails = [e for e in email_records if e.get('is_follow_up', False)]
                    
                    logger.info(f"   Initial emails: {len(initial_emails)}")
                    logger.info(f"   Follow-up emails: {len(followup_emails)}")
                    
                    # Verify records are complete
                    records_valid = True
                    if not follow_up_enabled:
                        logger.error("❌ Follow-up not enabled in campaign")
                        records_valid = False
                    
                    if len(follow_up_dates) == 0:
                        logger.error("❌ No follow-up dates in campaign") 
                        records_valid = False
                    
                    if status not in ['active', 'sent']:
                        logger.error(f"❌ Invalid campaign status: {status}")
                        records_valid = False
                    
                    if records_valid:
                        logger.info("✅ Database records are valid")
                        self.test_results.append({
                            "test": "Database Verification",
                            "status": "PASS",
                            "details": f"Valid records: {len(email_records)} emails, status: {status}"
                        })
                    else:
                        self.test_results.append({
                            "test": "Database Verification",
                            "status": "FAIL", 
                            "details": "Invalid database records"
                        })
                    
                    return records_valid
                else:
                    logger.error(f"❌ Failed to get campaign data: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ Database verification error: {str(e)}")
            return False
    
    def print_summary(self):
        """Print test results summary"""
        logger.info("\n" + "="*80)
        logger.info("🎯 END-TO-END EMAIL AND FOLLOW-UP TEST SUMMARY")
        logger.info("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAIL"])
        
        logger.info(f"📊 Total Tests: {total_tests}")
        logger.info(f"✅ Passed: {passed_tests}")
        logger.info(f"❌ Failed: {failed_tests}")
        
        if total_tests > 0:
            success_rate = (passed_tests / total_tests) * 100
            logger.info(f"📈 Success Rate: {success_rate:.1f}%")
        
        logger.info("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status_icon = {"PASS": "✅", "FAIL": "❌"}.get(result["status"], "❓")
            logger.info(f"{status_icon} {result['test']}: {result['status']} - {result['details']}")
        
        logger.info("\n📝 CREATED ITEMS FOR CLEANUP:")
        for item_type, items in self.created_items.items():
            if items:
                logger.info(f"  {item_type.title()}: {items}")
        
        logger.info("="*80)

async def main():
    """Main test execution"""
    logger.info("🚀 End-to-End Email and Follow-up Testing")
    logger.info("Testing actual email sending and follow-up functionality")
    logger.info("="*80)
    
    tester = EndToEndTester()
    
    try:
        # Setup
        if not await tester.setup_session():
            logger.error("❌ Failed to setup session. Exiting.")
            return
        
        # Test 1: Email Provider Configuration
        provider = await tester.test_email_provider_configuration()
        if not provider:
            logger.error("❌ No working email provider found. Cannot continue.")
            tester.print_summary()
            return
        
        # Test 2: Create Test Template
        template_id = await tester.create_test_template()
        if not template_id:
            logger.error("❌ Failed to create template. Cannot continue.")
            tester.print_summary()
            return
        
        # Test 3: Create Test Prospects and List
        list_id, prospects = await tester.create_test_prospects_and_list()
        if not list_id:
            logger.error("❌ Failed to create list. Cannot continue.")
            tester.print_summary()
            return
        
        # Test 4: Create Campaign with Follow-up
        campaign_id = await tester.create_campaign_with_followup(template_id, list_id, provider)
        if not campaign_id:
            logger.error("❌ Failed to create campaign. Cannot continue.")
            tester.print_summary()
            return
        
        # Test 5: Send Campaign
        send_success = await tester.send_campaign_and_verify(campaign_id, provider)
        if not send_success:
            logger.warning("⚠️ Campaign send had issues, but continuing...")
        
        # Test 6: Verify Follow-up Engine Status
        engine_running = await tester.verify_followup_engine_status()
        if not engine_running:
            logger.warning("⚠️ Follow-up engine not running, attempting to start...")
            await tester.start_followup_engine()
        
        # Test 7: Monitor Follow-up Execution
        logger.info("\n⏰ Starting follow-up monitoring...")
        logger.info("This will monitor for 15 minutes to detect follow-up emails")
        logger.info("(Follow-ups are scheduled for 5 and 10 minutes after initial send)")
        
        await tester.monitor_followup_execution(campaign_id, wait_minutes=15)
        
        # Test 8: Verify Database Records
        await tester.verify_database_records(campaign_id)
        
        # Print final summary
        tester.print_summary()
        
    except Exception as e:
        logger.error(f"❌ Test execution failed: {str(e)}")
    finally:
        await tester.cleanup_session()

if __name__ == "__main__":
    asyncio.run(main())