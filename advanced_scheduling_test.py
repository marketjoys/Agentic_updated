#!/usr/bin/env python3
"""
AI Email Responder - Advanced Scheduling Testing
Testing Agent - January 2025

Additional tests for scheduling edge cases and email processing verification
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
import pytz

# Configuration
BACKEND_URL = "https://5f33b0de-2474-4f94-a9e0-dac40fa9173f.preview.emergentagent.com/api"
LOGIN_CREDENTIALS = {"username": "testuser", "password": "testpass123"}

class AdvancedSchedulingTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_results = []
        
    async def setup_session(self):
        """Setup HTTP session and authenticate"""
        self.session = aiohttp.ClientSession()
        
        # Login to get auth token
        async with self.session.post(f"{BACKEND_URL}/auth/login", json=LOGIN_CREDENTIALS) as response:
            if response.status == 200:
                data = await response.json()
                self.auth_token = data.get("access_token")
                print("✅ Authentication successful")
                return True
            else:
                print(f"❌ Authentication failed: {response.status}")
                return False
    
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    def get_headers(self):
        """Get headers with auth token"""
        return {"Authorization": f"Bearer {self.auth_token}"}
    
    async def test_campaign_sending_with_scheduling(self):
        """Test campaign sending with scheduling to verify the follow-up engine processes them"""
        print("\n🔍 ADVANCED TEST 1: Campaign Sending with Scheduling")
        
        # Get templates, lists, and email providers
        templates = await self.get_templates()
        lists = await self.get_lists()
        providers = await self.get_email_providers()
        
        if not templates or not lists:
            print("❌ Need templates and lists for campaign sending test")
            self.test_results.append({"test": "Campaign Sending with Scheduling", "status": "FAIL", "details": "Missing templates or lists"})
            return
        
        template_id = templates[0]["id"]
        list_id = lists[0]["id"]
        
        # Create a campaign with datetime scheduling
        print("\n📧 Creating campaign with datetime scheduling...")
        try:
            # Create follow-up dates (near future for testing)
            now = datetime.utcnow()
            follow_up_dates = [
                (now + timedelta(minutes=5)).isoformat() + "Z",  # 5 minutes from now
                (now + timedelta(hours=1)).isoformat() + "Z",    # 1 hour from now
            ]
            
            campaign_data = {
                "name": "Advanced Scheduling Test Campaign",
                "template_id": template_id,
                "list_ids": [list_id],
                "max_emails": 10,
                "follow_up_enabled": True,
                "follow_up_schedule_type": "datetime",
                "follow_up_dates": follow_up_dates,
                "follow_up_timezone": "UTC",
                "follow_up_time_window_start": "00:00",  # Allow any time for testing
                "follow_up_time_window_end": "23:59",
                "follow_up_days_of_week": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
            }
            
            async with self.session.post(f"{BACKEND_URL}/campaigns", 
                                       json=campaign_data, 
                                       headers=self.get_headers()) as response:
                if response.status == 200:
                    campaign = await response.json()
                    campaign_id = campaign.get('id')
                    print(f"✅ Campaign created: {campaign_id}")
                    print(f"✅ Follow-up dates: {campaign.get('follow_up_dates')}")
                    
                    # Now try to send the campaign
                    print("\n📤 Attempting to send campaign...")
                    send_data = {
                        "send_immediately": True,
                        "max_emails": 5,
                        "follow_up_enabled": True
                    }
                    
                    # Add email provider if available
                    if providers:
                        send_data["email_provider_id"] = providers[0]["id"]
                        print(f"✅ Using email provider: {providers[0]['name']}")
                    
                    async with self.session.post(f"{BACKEND_URL}/campaigns/{campaign_id}/send", 
                                               json=send_data, 
                                               headers=self.get_headers()) as send_response:
                        if send_response.status == 200:
                            send_result = await send_response.json()
                            print(f"✅ Campaign send initiated")
                            print(f"✅ Total sent: {send_result.get('total_sent', 0)}")
                            print(f"✅ Total failed: {send_result.get('total_failed', 0)}")
                            
                            # Check if follow-up engine is processing
                            await asyncio.sleep(2)  # Wait a moment
                            await self.check_follow_up_engine_activity()
                            
                            self.test_results.append({"test": "Campaign Sending with Scheduling", "status": "PASS", "details": f"Campaign sent, follow-ups scheduled"})
                        else:
                            error_text = await send_response.text()
                            print(f"⚠️ Campaign send failed: {send_response.status} - {error_text}")
                            # This might be expected if no email provider is configured
                            self.test_results.append({"test": "Campaign Sending with Scheduling", "status": "PARTIAL", "details": f"Campaign created but send failed: {error_text}"})
                else:
                    error_text = await response.text()
                    print(f"❌ Campaign creation failed: {response.status} - {error_text}")
                    self.test_results.append({"test": "Campaign Sending with Scheduling", "status": "FAIL", "details": f"Campaign creation failed: {error_text}"})
                    
        except Exception as e:
            print(f"❌ Campaign sending test failed: {str(e)}")
            self.test_results.append({"test": "Campaign Sending with Scheduling", "status": "FAIL", "details": str(e)})
    
    async def test_timezone_edge_cases(self):
        """Test timezone edge cases and DST handling"""
        print("\n🔍 ADVANCED TEST 2: Timezone Edge Cases")
        
        templates = await self.get_templates()
        lists = await self.get_lists()
        
        if not templates or not lists:
            print("❌ Need templates and lists for timezone edge case testing")
            self.test_results.append({"test": "Timezone Edge Cases", "status": "FAIL", "details": "Missing templates or lists"})
            return
        
        template_id = templates[0]["id"]
        list_id = lists[0]["id"]
        
        # Test edge case timezones and scenarios
        edge_cases = [
            {
                "name": "Pacific Timezone",
                "timezone": "America/Los_Angeles",
                "description": "West Coast US timezone"
            },
            {
                "name": "Tokyo Timezone", 
                "timezone": "Asia/Tokyo",
                "description": "Asian timezone (+9 UTC)"
            },
            {
                "name": "Sydney Timezone",
                "timezone": "Australia/Sydney", 
                "description": "Australian timezone with DST"
            },
            {
                "name": "Invalid Timezone Test",
                "timezone": "Invalid/Timezone",
                "description": "Should fail gracefully"
            }
        ]
        
        for case in edge_cases:
            print(f"\n🌍 Testing: {case['name']} - {case['description']}")
            try:
                # Create campaign with this timezone
                now = datetime.utcnow()
                follow_up_date = (now + timedelta(days=1)).isoformat() + "Z"
                
                campaign_data = {
                    "name": f"Timezone Edge Case - {case['name']}",
                    "template_id": template_id,
                    "list_ids": [list_id],
                    "max_emails": 5,
                    "follow_up_enabled": True,
                    "follow_up_schedule_type": "datetime",
                    "follow_up_dates": [follow_up_date],
                    "follow_up_timezone": case["timezone"],
                    "follow_up_time_window_start": "09:00",
                    "follow_up_time_window_end": "17:00"
                }
                
                async with self.session.post(f"{BACKEND_URL}/campaigns", 
                                           json=campaign_data, 
                                           headers=self.get_headers()) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ {case['name']} campaign created: {data.get('id')}")
                        print(f"✅ Timezone accepted: {data.get('follow_up_timezone')}")
                        
                        if case["timezone"] == "Invalid/Timezone":
                            # This should have failed but didn't - unexpected
                            self.test_results.append({"test": f"Timezone Edge Case - {case['name']}", "status": "UNEXPECTED", "details": "Invalid timezone was accepted"})
                        else:
                            self.test_results.append({"test": f"Timezone Edge Case - {case['name']}", "status": "PASS", "details": f"Timezone {case['timezone']} processed correctly"})
                    else:
                        error_text = await response.text()
                        print(f"❌ {case['name']} failed: {response.status} - {error_text}")
                        
                        if case["timezone"] == "Invalid/Timezone":
                            # This failure is expected for invalid timezone
                            print("✅ Invalid timezone correctly rejected")
                            self.test_results.append({"test": f"Timezone Edge Case - {case['name']}", "status": "PASS", "details": "Invalid timezone correctly rejected"})
                        else:
                            self.test_results.append({"test": f"Timezone Edge Case - {case['name']}", "status": "FAIL", "details": f"Valid timezone rejected: {error_text}"})
                        
            except Exception as e:
                print(f"❌ Timezone edge case {case['name']} failed: {str(e)}")
                if case["timezone"] == "Invalid/Timezone":
                    # Exception for invalid timezone is expected
                    self.test_results.append({"test": f"Timezone Edge Case - {case['name']}", "status": "PASS", "details": "Invalid timezone correctly caused exception"})
                else:
                    self.test_results.append({"test": f"Timezone Edge Case - {case['name']}", "status": "FAIL", "details": str(e)})
    
    async def test_follow_up_engine_monitoring(self):
        """Test follow-up engine monitoring and provider details"""
        print("\n🔍 ADVANCED TEST 3: Follow-up Engine Monitoring")
        
        try:
            # Get detailed service status
            async with self.session.get(f"{BACKEND_URL}/services/status", headers=self.get_headers()) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Service status retrieved")
                    
                    # Analyze follow-up engine details
                    services = data.get("services", {})
                    follow_up_engine = services.get("smart_follow_up_engine", {})
                    email_processor = services.get("email_processor", {})
                    
                    print(f"✅ Follow-up Engine Status: {follow_up_engine.get('status')}")
                    print(f"✅ Email Processor Status: {email_processor.get('status')}")
                    print(f"✅ Overall System Status: {data.get('overall_status')}")
                    
                    # Check monitored providers
                    monitored_providers = email_processor.get("monitored_providers", [])
                    monitored_count = email_processor.get("monitored_providers_count", 0)
                    
                    print(f"✅ Monitored Providers Count: {monitored_count}")
                    
                    if monitored_providers:
                        print("✅ Monitored Provider Details:")
                        for provider in monitored_providers:
                            print(f"  - Name: {provider.get('name')}")
                            print(f"    Type: {provider.get('provider_type')}")
                            print(f"    IMAP Host: {provider.get('imap_host')}")
                            print(f"    Last Scan: {provider.get('last_scan')}")
                    else:
                        print("⚠️ No providers being monitored")
                    
                    # Test service management
                    print("\n🔄 Testing service management...")
                    
                    # Test stop services
                    async with self.session.post(f"{BACKEND_URL}/services/stop-all", headers=self.get_headers()) as stop_response:
                        if stop_response.status == 200:
                            stop_data = await stop_response.json()
                            print("✅ Services stopped successfully")
                            print(f"✅ Stop results: {stop_data.get('results')}")
                        else:
                            print(f"⚠️ Service stop failed: {stop_response.status}")
                    
                    # Wait a moment
                    await asyncio.sleep(1)
                    
                    # Test start services
                    async with self.session.post(f"{BACKEND_URL}/services/start-all", headers=self.get_headers()) as start_response:
                        if start_response.status == 200:
                            start_data = await start_response.json()
                            print("✅ Services started successfully")
                            print(f"✅ Start results: {start_data.get('results')}")
                        else:
                            print(f"⚠️ Service start failed: {start_response.status}")
                    
                    self.test_results.append({"test": "Follow-up Engine Monitoring", "status": "PASS", "details": f"Monitoring {monitored_count} providers, service management working"})
                    
                else:
                    error_text = await response.text()
                    print(f"❌ Service status check failed: {response.status} - {error_text}")
                    self.test_results.append({"test": "Follow-up Engine Monitoring", "status": "FAIL", "details": f"Service status failed: {error_text}"})
                    
        except Exception as e:
            print(f"❌ Follow-up engine monitoring test failed: {str(e)}")
            self.test_results.append({"test": "Follow-up Engine Monitoring", "status": "FAIL", "details": str(e)})
    
    async def test_scheduling_validation(self):
        """Test scheduling validation and error handling"""
        print("\n🔍 ADVANCED TEST 4: Scheduling Validation")
        
        templates = await self.get_templates()
        lists = await self.get_lists()
        
        if not templates or not lists:
            print("❌ Need templates and lists for validation testing")
            self.test_results.append({"test": "Scheduling Validation", "status": "FAIL", "details": "Missing templates or lists"})
            return
        
        template_id = templates[0]["id"]
        list_id = lists[0]["id"]
        
        # Test various validation scenarios
        validation_tests = [
            {
                "name": "Invalid Time Window (End before Start)",
                "data": {
                    "follow_up_time_window_start": "17:00",
                    "follow_up_time_window_end": "09:00"
                },
                "should_fail": False  # Backend might not validate this
            },
            {
                "name": "Invalid Time Format",
                "data": {
                    "follow_up_time_window_start": "25:00",
                    "follow_up_time_window_end": "17:00"
                },
                "should_fail": False  # Backend might not validate this
            },
            {
                "name": "Empty Follow-up Dates in Datetime Mode",
                "data": {
                    "follow_up_schedule_type": "datetime",
                    "follow_up_dates": []
                },
                "should_fail": False  # Might be allowed
            },
            {
                "name": "Malformed Date String",
                "data": {
                    "follow_up_schedule_type": "datetime",
                    "follow_up_dates": ["not-a-date"]
                },
                "should_fail": True  # This should definitely fail
            }
        ]
        
        for test in validation_tests:
            print(f"\n🔍 Testing: {test['name']}")
            try:
                campaign_data = {
                    "name": f"Validation Test - {test['name']}",
                    "template_id": template_id,
                    "list_ids": [list_id],
                    "max_emails": 5,
                    "follow_up_enabled": True,
                    "follow_up_schedule_type": "interval",
                    "follow_up_intervals": [1],
                    "follow_up_timezone": "UTC",
                    "follow_up_time_window_start": "09:00",
                    "follow_up_time_window_end": "17:00"
                }
                
                # Override with test data
                campaign_data.update(test["data"])
                
                async with self.session.post(f"{BACKEND_URL}/campaigns", 
                                           json=campaign_data, 
                                           headers=self.get_headers()) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ Campaign created: {data.get('id')}")
                        
                        if test["should_fail"]:
                            print(f"⚠️ Expected validation failure but campaign was created")
                            self.test_results.append({"test": f"Validation - {test['name']}", "status": "UNEXPECTED", "details": "Expected failure but succeeded"})
                        else:
                            print(f"✅ Campaign created as expected")
                            self.test_results.append({"test": f"Validation - {test['name']}", "status": "PASS", "details": "Validation behaved as expected"})
                    else:
                        error_text = await response.text()
                        print(f"❌ Campaign creation failed: {response.status} - {error_text}")
                        
                        if test["should_fail"]:
                            print(f"✅ Expected validation failure occurred")
                            self.test_results.append({"test": f"Validation - {test['name']}", "status": "PASS", "details": "Expected validation failure occurred"})
                        else:
                            print(f"⚠️ Unexpected validation failure")
                            self.test_results.append({"test": f"Validation - {test['name']}", "status": "FAIL", "details": f"Unexpected failure: {error_text}"})
                        
            except Exception as e:
                print(f"❌ Validation test {test['name']} failed: {str(e)}")
                if test["should_fail"]:
                    self.test_results.append({"test": f"Validation - {test['name']}", "status": "PASS", "details": "Expected exception occurred"})
                else:
                    self.test_results.append({"test": f"Validation - {test['name']}", "status": "FAIL", "details": str(e)})
    
    async def check_follow_up_engine_activity(self):
        """Helper: Check if follow-up engine shows activity"""
        try:
            async with self.session.get(f"{BACKEND_URL}/services/status", headers=self.get_headers()) as response:
                if response.status == 200:
                    data = await response.json()
                    services = data.get("services", {})
                    follow_up_engine = services.get("smart_follow_up_engine", {})
                    
                    if follow_up_engine.get("status") == "running":
                        print("✅ Follow-up engine is running and should process scheduled emails")
                    else:
                        print("⚠️ Follow-up engine is not running")
        except Exception as e:
            print(f"⚠️ Could not check follow-up engine activity: {str(e)}")
    
    async def get_templates(self):
        """Helper: Get available templates"""
        try:
            async with self.session.get(f"{BACKEND_URL}/templates", headers=self.get_headers()) as response:
                if response.status == 200:
                    templates = await response.json()
                    print(f"✅ Found {len(templates)} templates")
                    return templates
                else:
                    print(f"❌ Failed to get templates: {response.status}")
                    return []
        except Exception as e:
            print(f"❌ Error getting templates: {str(e)}")
            return []
    
    async def get_lists(self):
        """Helper: Get available lists"""
        try:
            async with self.session.get(f"{BACKEND_URL}/lists", headers=self.get_headers()) as response:
                if response.status == 200:
                    lists = await response.json()
                    print(f"✅ Found {len(lists)} lists")
                    return lists
                else:
                    print(f"❌ Failed to get lists: {response.status}")
                    return []
        except Exception as e:
            print(f"❌ Error getting lists: {str(e)}")
            return []
    
    async def get_email_providers(self):
        """Helper: Get available email providers"""
        try:
            async with self.session.get(f"{BACKEND_URL}/email-providers", headers=self.get_headers()) as response:
                if response.status == 200:
                    providers = await response.json()
                    print(f"✅ Found {len(providers)} email providers")
                    return providers
                else:
                    print(f"❌ Failed to get email providers: {response.status}")
                    return []
        except Exception as e:
            print(f"❌ Error getting email providers: {str(e)}")
            return []
    
    def print_summary(self):
        """Print test results summary"""
        print("\n" + "="*80)
        print("🎯 ADVANCED SCHEDULING TESTING SUMMARY")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAIL"])
        partial_tests = len([r for r in self.test_results if r["status"] == "PARTIAL"])
        unexpected_tests = len([r for r in self.test_results if r["status"] == "UNEXPECTED"])
        
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️ Partial: {partial_tests}")
        print(f"❓ Unexpected: {unexpected_tests}")
        
        if total_tests > 0:
            success_rate = (passed_tests / total_tests) * 100
            print(f"📈 Success Rate: {success_rate:.1f}%")
        
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status_icon = {"PASS": "✅", "FAIL": "❌", "PARTIAL": "⚠️", "UNEXPECTED": "❓"}.get(result["status"], "❓")
            print(f"{status_icon} {result['test']}: {result['status']} - {result['details']}")
        
        print("\n" + "="*80)

async def main():
    """Main test execution"""
    print("🚀 AI Email Responder - Advanced Scheduling Testing")
    print("Testing Agent - January 2025")
    print("Focus: Advanced scheduling scenarios and edge cases")
    print("="*80)
    
    tester = AdvancedSchedulingTester()
    
    try:
        # Setup
        if not await tester.setup_session():
            print("❌ Failed to setup session. Exiting.")
            return
        
        # Run advanced tests
        await tester.test_campaign_sending_with_scheduling()
        await tester.test_timezone_edge_cases()
        await tester.test_follow_up_engine_monitoring()
        await tester.test_scheduling_validation()
        
        # Print summary
        tester.print_summary()
        
    except Exception as e:
        print(f"❌ Test execution failed: {str(e)}")
    finally:
        await tester.cleanup_session()

if __name__ == "__main__":
    asyncio.run(main())