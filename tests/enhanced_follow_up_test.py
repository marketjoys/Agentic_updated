#!/usr/bin/env python3
"""
Enhanced Auto Follow-ups and Auto Responders System Testing - December 2024
Testing the enhanced functionality as requested in the review:

1. Service Status Testing: Verify both smart_follow_up_engine and email_processor are running
2. Enhanced Campaign Creation: Test creating campaigns with precise datetime follow-ups and timezone support
3. Follow-up Configuration: Test the new follow_up_schedule_type, follow_up_dates, follow_up_timezone fields
4. Auto-Start Functionality: Verify that when campaigns are sent, the services auto-start
5. Service Management: Test the new /api/services/status, /api/services/start-all, /api/services/stop-all endpoints
6. Timezone Handling: Test campaigns with different timezones (UTC, America/New_York, Europe/London)
7. Follow-up Engine Endpoints: Test /api/follow-up-engine/status and /api/email-processing/status
"""

import requests
import json
import sys
from datetime import datetime, timedelta
import pytz

# Configuration
BASE_URL = "https://24e4a959-d97d-4946-9c07-cd62f1a8669c.preview.emergentagent.com/api"
USERNAME = "testuser"
PASSWORD = "testpass123"

class EnhancedFollowUpTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.created_resources = {
            'campaigns': [],
            'templates': [],
            'prospects': [],
            'lists': []
        }
        
    def authenticate(self):
        """Authenticate and get access token"""
        try:
            response = self.session.post(f"{BASE_URL}/auth/login", json={
                "username": USERNAME,
                "password": PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                print("✅ Authentication successful")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def test_service_status(self):
        """Test 1: Service Status Testing - Verify both smart_follow_up_engine and email_processor are running"""
        print("\n🧪 Test 1: Service Status Testing")
        
        try:
            response = self.session.get(f"{BASE_URL}/services/status")
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code != 200:
                print("❌ CRITICAL: Services status endpoint not accessible")
                return False
            
            data = response.json()
            
            # Check for required services
            if "services" not in data:
                print("❌ CRITICAL: No services information in response")
                return False
            
            services = data["services"]
            
            # Check smart_follow_up_engine
            if "smart_follow_up_engine" not in services:
                print("❌ CRITICAL: smart_follow_up_engine service not found")
                return False
            
            # Check email_processor
            if "email_processor" not in services:
                print("❌ CRITICAL: email_processor service not found")
                return False
            
            follow_up_status = services["smart_follow_up_engine"]["status"]
            email_processor_status = services["email_processor"]["status"]
            
            print(f"✅ Smart Follow-up Engine Status: {follow_up_status}")
            print(f"✅ Email Processor Status: {email_processor_status}")
            print(f"✅ Overall Status: {data.get('overall_status', 'unknown')}")
            
            return True
                
        except Exception as e:
            print(f"❌ Service status test error: {str(e)}")
            return False
    
    def test_service_management_endpoints(self):
        """Test 5: Service Management - Test the new /api/services/start-all, /api/services/stop-all endpoints"""
        print("\n🧪 Test 5: Service Management Endpoints")
        
        try:
            # Test start-all endpoint
            print("Testing /api/services/start-all endpoint...")
            response = self.session.post(f"{BASE_URL}/services/start-all")
            
            print(f"Start-all Status Code: {response.status_code}")
            print(f"Start-all Response: {response.text}")
            
            if response.status_code != 200:
                print("❌ CRITICAL: Start-all services endpoint failed")
                return False
            
            start_data = response.json()
            if "results" not in start_data:
                print("❌ CRITICAL: No results in start-all response")
                return False
            
            print("✅ Start-all services endpoint working")
            
            # Test stop-all endpoint
            print("Testing /api/services/stop-all endpoint...")
            response = self.session.post(f"{BASE_URL}/services/stop-all")
            
            print(f"Stop-all Status Code: {response.status_code}")
            print(f"Stop-all Response: {response.text}")
            
            if response.status_code != 200:
                print("❌ CRITICAL: Stop-all services endpoint failed")
                return False
            
            stop_data = response.json()
            if "results" not in stop_data:
                print("❌ CRITICAL: No results in stop-all response")
                return False
            
            print("✅ Stop-all services endpoint working")
            
            # Restart services for other tests
            print("Restarting services for other tests...")
            self.session.post(f"{BASE_URL}/services/start-all")
            
            return True
                
        except Exception as e:
            print(f"❌ Service management endpoints test error: {str(e)}")
            return False
    
    def create_test_template(self):
        """Create a test template for campaigns"""
        try:
            template_data = {
                "name": "Enhanced Follow-up Test Template",
                "subject": "Follow-up: {{first_name}}, let's connect!",
                "content": "<p>Hi {{first_name}},</p><p>I wanted to follow up on our previous conversation about {{company}}.</p><p>Best regards,<br>Test Team</p>",
                "type": "follow_up",
                "placeholders": ["first_name", "company"]
            }
            
            response = self.session.post(f"{BASE_URL}/templates", json=template_data)
            
            if response.status_code == 200:
                template = response.json()
                template_id = template.get("id")
                if template_id:
                    self.created_resources['templates'].append(template_id)
                    print(f"✅ Created test template: {template_id}")
                    return template_id
            
            print(f"❌ Failed to create test template: {response.status_code} - {response.text}")
            return None
            
        except Exception as e:
            print(f"❌ Error creating test template: {str(e)}")
            return None
    
    def create_test_prospect(self):
        """Create a test prospect for campaigns"""
        try:
            import time
            import random
            unique_id = int(time.time()) + random.randint(1000, 9999)
            
            prospect_data = {
                "email": f"test.prospect.{unique_id}@example.com",
                "first_name": "Test",
                "last_name": "Prospect",
                "company": "Test Company Inc",
                "job_title": "Test Manager",
                "industry": "Technology"
            }
            
            response = self.session.post(f"{BASE_URL}/prospects", json=prospect_data)
            
            if response.status_code == 200:
                prospect = response.json()
                prospect_id = prospect.get("id")
                if prospect_id:
                    self.created_resources['prospects'].append(prospect_id)
                    print(f"✅ Created test prospect: {prospect_id}")
                    return prospect_id
            
            print(f"❌ Failed to create test prospect: {response.status_code} - {response.text}")
            return None
            
        except Exception as e:
            print(f"❌ Error creating test prospect: {str(e)}")
            return None
    
    def create_test_list(self, prospect_id):
        """Create a test list with the prospect"""
        try:
            list_data = {
                "name": "Enhanced Follow-up Test List",
                "description": "Test list for enhanced follow-up testing",
                "color": "#3B82F6",
                "tags": ["test", "follow-up"]
            }
            
            response = self.session.post(f"{BASE_URL}/lists", json=list_data)
            
            if response.status_code == 200:
                list_obj = response.json()
                list_id = list_obj.get("id")
                if list_id:
                    self.created_resources['lists'].append(list_id)
                    
                    # Add prospect to list
                    add_request = {"prospect_ids": [prospect_id]}
                    self.session.post(f"{BASE_URL}/lists/{list_id}/prospects", json=add_request)
                    
                    print(f"✅ Created test list with prospect: {list_id}")
                    return list_id
            
            print(f"❌ Failed to create test list: {response.status_code} - {response.text}")
            return None
            
        except Exception as e:
            print(f"❌ Error creating test list: {str(e)}")
            return None
    
    def test_enhanced_campaign_creation_interval_mode(self):
        """Test 2: Enhanced Campaign Creation - Test interval-based follow-ups"""
        print("\n🧪 Test 2a: Enhanced Campaign Creation (Interval Mode)")
        
        try:
            # Create prerequisites
            template_id = self.create_test_template()
            prospect_id = self.create_test_prospect()
            list_id = self.create_test_list(prospect_id)
            
            if not all([template_id, prospect_id, list_id]):
                print("❌ Failed to create prerequisites for campaign test")
                return False
            
            # Create campaign with interval-based follow-ups
            campaign_data = {
                "name": "Enhanced Follow-up Test Campaign (Interval)",
                "template_id": template_id,
                "list_ids": [list_id],
                "max_emails": 100,
                "schedule": None,
                
                # Enhanced Follow-up Configuration (Interval Mode)
                "follow_up_enabled": True,
                "follow_up_schedule_type": "interval",
                "follow_up_intervals": [3, 7, 14, 30],  # days
                "follow_up_timezone": "UTC",
                "follow_up_time_window_start": "09:00",
                "follow_up_time_window_end": "17:00",
                "follow_up_days_of_week": ["monday", "tuesday", "wednesday", "thursday", "friday"],
                "follow_up_templates": [template_id]
            }
            
            response = self.session.post(f"{BASE_URL}/campaigns", json=campaign_data)
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code != 200:
                print("❌ CRITICAL: Enhanced campaign creation (interval mode) failed")
                return False
            
            campaign = response.json()
            campaign_id = campaign.get("id")
            
            if not campaign_id:
                print("❌ CRITICAL: No campaign ID in response")
                return False
            
            self.created_resources['campaigns'].append(campaign_id)
            
            # Verify enhanced follow-up configuration
            if campaign.get("follow_up_enabled") != True:
                print("❌ Follow-up not enabled in created campaign")
                return False
            
            if campaign.get("follow_up_schedule_type") != "interval":
                print("❌ Follow-up schedule type not set correctly")
                return False
            
            if campaign.get("follow_up_intervals") != [3, 7, 14, 30]:
                print("❌ Follow-up intervals not set correctly")
                return False
            
            print("✅ Enhanced campaign creation (interval mode) successful")
            print(f"✅ Campaign ID: {campaign_id}")
            print(f"✅ Follow-up enabled: {campaign.get('follow_up_enabled')}")
            print(f"✅ Schedule type: {campaign.get('follow_up_schedule_type')}")
            print(f"✅ Intervals: {campaign.get('follow_up_intervals')}")
            
            return True
                
        except Exception as e:
            print(f"❌ Enhanced campaign creation test error: {str(e)}")
            return False
    
    def test_enhanced_campaign_creation_datetime_mode(self):
        """Test 2b: Enhanced Campaign Creation - Test datetime-based follow-ups with timezone support"""
        print("\n🧪 Test 2b: Enhanced Campaign Creation (Datetime Mode)")
        
        try:
            # Create prerequisites
            template_id = self.create_test_template()
            prospect_id = self.create_test_prospect()
            list_id = self.create_test_list(prospect_id)
            
            if not all([template_id, prospect_id, list_id]):
                print("❌ Failed to create prerequisites for datetime campaign test")
                return False
            
            # Generate future datetime strings for follow-ups
            now = datetime.utcnow()
            follow_up_dates = [
                (now + timedelta(days=3)).isoformat() + "Z",
                (now + timedelta(days=7)).isoformat() + "Z",
                (now + timedelta(days=14)).isoformat() + "Z"
            ]
            
            # Create campaign with datetime-based follow-ups
            campaign_data = {
                "name": "Enhanced Follow-up Test Campaign (Datetime)",
                "template_id": template_id,
                "list_ids": [list_id],
                "max_emails": 100,
                "schedule": None,
                
                # Enhanced Follow-up Configuration (Datetime Mode)
                "follow_up_enabled": True,
                "follow_up_schedule_type": "datetime",
                "follow_up_dates": follow_up_dates,
                "follow_up_timezone": "America/New_York",
                "follow_up_time_window_start": "10:00",
                "follow_up_time_window_end": "16:00",
                "follow_up_days_of_week": ["monday", "tuesday", "wednesday", "thursday", "friday"],
                "follow_up_templates": [template_id]
            }
            
            response = self.session.post(f"{BASE_URL}/campaigns", json=campaign_data)
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code != 200:
                print("❌ CRITICAL: Enhanced campaign creation (datetime mode) failed")
                return False
            
            campaign = response.json()
            campaign_id = campaign.get("id")
            
            if not campaign_id:
                print("❌ CRITICAL: No campaign ID in response")
                return False
            
            self.created_resources['campaigns'].append(campaign_id)
            
            # Verify enhanced follow-up configuration
            if campaign.get("follow_up_enabled") != True:
                print("❌ Follow-up not enabled in created campaign")
                return False
            
            if campaign.get("follow_up_schedule_type") != "datetime":
                print("❌ Follow-up schedule type not set correctly")
                return False
            
            if campaign.get("follow_up_timezone") != "America/New_York":
                print("❌ Follow-up timezone not set correctly")
                return False
            
            print("✅ Enhanced campaign creation (datetime mode) successful")
            print(f"✅ Campaign ID: {campaign_id}")
            print(f"✅ Follow-up enabled: {campaign.get('follow_up_enabled')}")
            print(f"✅ Schedule type: {campaign.get('follow_up_schedule_type')}")
            print(f"✅ Timezone: {campaign.get('follow_up_timezone')}")
            print(f"✅ Follow-up dates: {len(campaign.get('follow_up_dates', []))} dates configured")
            
            return True
                
        except Exception as e:
            print(f"❌ Enhanced campaign creation (datetime) test error: {str(e)}")
            return False
    
    def test_timezone_handling(self):
        """Test 6: Timezone Handling - Test campaigns with different timezones"""
        print("\n🧪 Test 6: Timezone Handling")
        
        timezones_to_test = ["UTC", "America/New_York", "Europe/London"]
        results = []
        
        for timezone in timezones_to_test:
            try:
                print(f"Testing timezone: {timezone}")
                
                # Create prerequisites
                template_id = self.create_test_template()
                prospect_id = self.create_test_prospect()
                list_id = self.create_test_list(prospect_id)
                
                if not all([template_id, prospect_id, list_id]):
                    print(f"❌ Failed to create prerequisites for {timezone} test")
                    results.append(False)
                    continue
                
                # Generate timezone-aware datetime
                tz = pytz.timezone(timezone)
                now = datetime.now(tz)
                follow_up_date = (now + timedelta(days=1)).isoformat()
                
                campaign_data = {
                    "name": f"Timezone Test Campaign ({timezone})",
                    "template_id": template_id,
                    "list_ids": [list_id],
                    "max_emails": 10,
                    "follow_up_enabled": True,
                    "follow_up_schedule_type": "datetime",
                    "follow_up_dates": [follow_up_date],
                    "follow_up_timezone": timezone
                }
                
                response = self.session.post(f"{BASE_URL}/campaigns", json=campaign_data)
                
                if response.status_code == 200:
                    campaign = response.json()
                    campaign_id = campaign.get("id")
                    if campaign_id:
                        self.created_resources['campaigns'].append(campaign_id)
                        print(f"✅ {timezone} campaign created successfully")
                        results.append(True)
                    else:
                        print(f"❌ {timezone} campaign creation failed - no ID")
                        results.append(False)
                else:
                    print(f"❌ {timezone} campaign creation failed: {response.status_code}")
                    results.append(False)
                    
            except Exception as e:
                print(f"❌ {timezone} test error: {str(e)}")
                results.append(False)
        
        success_count = sum(results)
        total_count = len(results)
        
        if success_count == total_count:
            print(f"✅ Timezone handling test passed: {success_count}/{total_count} timezones working")
            return True
        else:
            print(f"❌ Timezone handling test failed: {success_count}/{total_count} timezones working")
            return False
    
    def test_auto_start_functionality(self):
        """Test 4: Auto-Start Functionality - Verify that when campaigns are sent, the services auto-start"""
        print("\n🧪 Test 4: Auto-Start Functionality")
        
        try:
            # First, stop all services to test auto-start
            print("Stopping all services to test auto-start...")
            self.session.post(f"{BASE_URL}/services/stop-all")
            
            # Verify services are stopped
            status_response = self.session.get(f"{BASE_URL}/services/status")
            if status_response.status_code == 200:
                status_data = status_response.json()
                services = status_data.get("services", {})
                follow_up_status = services.get("smart_follow_up_engine", {}).get("status", "unknown")
                email_status = services.get("email_processor", {}).get("status", "unknown")
                print(f"Services status before campaign send - Follow-up: {follow_up_status}, Email: {email_status}")
            
            # Create and send a campaign to trigger auto-start
            template_id = self.create_test_template()
            prospect_id = self.create_test_prospect()
            list_id = self.create_test_list(prospect_id)
            
            if not all([template_id, prospect_id, list_id]):
                print("❌ Failed to create prerequisites for auto-start test")
                return False
            
            campaign_data = {
                "name": "Auto-Start Test Campaign",
                "template_id": template_id,
                "list_ids": [list_id],
                "max_emails": 1,
                "follow_up_enabled": True,
                "follow_up_schedule_type": "interval",
                "follow_up_intervals": [7]
            }
            
            # Create campaign
            response = self.session.post(f"{BASE_URL}/campaigns", json=campaign_data)
            if response.status_code != 200:
                print("❌ Failed to create campaign for auto-start test")
                return False
            
            campaign = response.json()
            campaign_id = campaign.get("id")
            self.created_resources['campaigns'].append(campaign_id)
            
            # Send campaign (this should auto-start services)
            print("Sending campaign to trigger auto-start...")
            send_request = {
                "send_immediately": True,
                "max_emails": 1,
                "follow_up_enabled": True
            }
            
            send_response = self.session.post(f"{BASE_URL}/campaigns/{campaign_id}/send", json=send_request)
            
            print(f"Campaign send status: {send_response.status_code}")
            print(f"Campaign send response: {send_response.text}")
            
            if send_response.status_code != 200:
                print("❌ Campaign send failed")
                return False
            
            # Check if services auto-started
            print("Checking if services auto-started...")
            status_response = self.session.get(f"{BASE_URL}/services/status")
            
            if status_response.status_code != 200:
                print("❌ Failed to check services status after campaign send")
                return False
            
            status_data = status_response.json()
            services = status_data.get("services", {})
            follow_up_status = services.get("smart_follow_up_engine", {}).get("status", "unknown")
            email_status = services.get("email_processor", {}).get("status", "unknown")
            
            print(f"Services status after campaign send - Follow-up: {follow_up_status}, Email: {email_status}")
            
            # Check if at least one service auto-started
            if follow_up_status == "running" or email_status == "running":
                print("✅ Auto-start functionality working - services started after campaign send")
                return True
            else:
                print("❌ Auto-start functionality failed - services did not start after campaign send")
                return False
                
        except Exception as e:
            print(f"❌ Auto-start functionality test error: {str(e)}")
            return False
    
    def test_follow_up_engine_endpoints(self):
        """Test 7: Follow-up Engine Endpoints - Test /api/follow-up-engine/status and /api/email-processing/status"""
        print("\n🧪 Test 7: Follow-up Engine Endpoints")
        
        try:
            # Test follow-up engine status endpoint
            print("Testing /api/follow-up-engine/status endpoint...")
            response = self.session.get(f"{BASE_URL}/follow-up-engine/status")
            
            print(f"Follow-up engine status code: {response.status_code}")
            print(f"Follow-up engine response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                if "status" in data:
                    print(f"✅ Follow-up engine status: {data['status']}")
                    follow_up_success = True
                else:
                    print("❌ Follow-up engine status missing 'status' field")
                    follow_up_success = False
            else:
                print("❌ Follow-up engine status endpoint failed")
                follow_up_success = False
            
            # Test email processing status endpoint
            print("Testing /api/email-processing/status endpoint...")
            response = self.session.get(f"{BASE_URL}/email-processing/status")
            
            print(f"Email processing status code: {response.status_code}")
            print(f"Email processing response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                if "status" in data:
                    print(f"✅ Email processing status: {data['status']}")
                    email_success = True
                else:
                    print("❌ Email processing status missing 'status' field")
                    email_success = False
            else:
                print("❌ Email processing status endpoint failed")
                email_success = False
            
            if follow_up_success and email_success:
                print("✅ Both follow-up engine endpoints working")
                return True
            else:
                print("❌ One or both follow-up engine endpoints failed")
                return False
                
        except Exception as e:
            print(f"❌ Follow-up engine endpoints test error: {str(e)}")
            return False
    
    def cleanup_resources(self):
        """Clean up created test resources"""
        print("\n🧹 Cleaning up test resources...")
        
        # Delete campaigns
        for campaign_id in self.created_resources['campaigns']:
            try:
                response = self.session.delete(f"{BASE_URL}/campaigns/{campaign_id}")
                if response.status_code == 200:
                    print(f"   ✅ Deleted campaign {campaign_id}")
                else:
                    print(f"   ⚠️ Failed to delete campaign {campaign_id}")
            except Exception as e:
                print(f"   ❌ Error deleting campaign {campaign_id}: {str(e)}")
        
        # Delete lists
        for list_id in self.created_resources['lists']:
            try:
                response = self.session.delete(f"{BASE_URL}/lists/{list_id}")
                if response.status_code == 200:
                    print(f"   ✅ Deleted list {list_id}")
                else:
                    print(f"   ⚠️ Failed to delete list {list_id}")
            except Exception as e:
                print(f"   ❌ Error deleting list {list_id}: {str(e)}")
        
        # Delete prospects
        for prospect_id in self.created_resources['prospects']:
            try:
                response = self.session.delete(f"{BASE_URL}/prospects/{prospect_id}")
                if response.status_code == 200:
                    print(f"   ✅ Deleted prospect {prospect_id}")
                else:
                    print(f"   ⚠️ Failed to delete prospect {prospect_id}")
            except Exception as e:
                print(f"   ❌ Error deleting prospect {prospect_id}: {str(e)}")
        
        # Delete templates
        for template_id in self.created_resources['templates']:
            try:
                response = self.session.delete(f"{BASE_URL}/templates/{template_id}")
                if response.status_code == 200:
                    print(f"   ✅ Deleted template {template_id}")
                else:
                    print(f"   ⚠️ Failed to delete template {template_id}")
            except Exception as e:
                print(f"   ❌ Error deleting template {template_id}: {str(e)}")
    
    def run_comprehensive_test(self):
        """Run all Enhanced Auto Follow-ups and Auto Responders tests"""
        print("🚀 ENHANCED AUTO FOLLOW-UPS AND AUTO RESPONDERS TESTING - DECEMBER 2024")
        print("=" * 90)
        print("Testing enhanced functionality as requested in review:")
        print("1. Service Status Testing")
        print("2. Enhanced Campaign Creation (Interval & Datetime modes)")
        print("3. Follow-up Configuration")
        print("4. Auto-Start Functionality")
        print("5. Service Management")
        print("6. Timezone Handling")
        print("7. Follow-up Engine Endpoints")
        print("=" * 90)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ CRITICAL: Authentication failed - cannot proceed with testing")
            return False
        
        # Run all tests
        test_results = {
            "service_status": self.test_service_status(),
            "enhanced_campaign_interval": self.test_enhanced_campaign_creation_interval_mode(),
            "enhanced_campaign_datetime": self.test_enhanced_campaign_creation_datetime_mode(),
            "auto_start_functionality": self.test_auto_start_functionality(),
            "service_management": self.test_service_management_endpoints(),
            "timezone_handling": self.test_timezone_handling(),
            "follow_up_engine_endpoints": self.test_follow_up_engine_endpoints()
        }
        
        # Summary
        print("\n" + "=" * 90)
        print("🎯 ENHANCED AUTO FOLLOW-UPS AND AUTO RESPONDERS TEST RESULTS")
        print("=" * 90)
        
        passed_tests = sum(test_results.values())
        total_tests = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
        
        print(f"\nOverall Results: {passed_tests}/{total_tests} tests passed ({(passed_tests/total_tests)*100:.1f}%)")
        
        if passed_tests == 0:
            print("\n🚨 CRITICAL FINDING: ALL ENHANCED FOLLOW-UP TESTS FAILED")
            print("ROOT CAUSE: Enhanced Auto Follow-ups and Auto Responders system is NOT WORKING")
            print("IMPACT: All 7 requested test scenarios from review failed")
            print("RECOMMENDATION: Fix enhanced follow-up system implementation")
        elif passed_tests < total_tests:
            print(f"\n⚠️ PARTIAL FUNCTIONALITY: {total_tests - passed_tests} tests failed")
            print("RECOMMENDATION: Address failing test scenarios")
        else:
            print("\n🎉 ALL ENHANCED FOLLOW-UP TESTS PASSED")
            print("Enhanced Auto Follow-ups and Auto Responders system is fully operational")
        
        # Cleanup
        self.cleanup_resources()
        
        return passed_tests == total_tests

if __name__ == "__main__":
    tester = EnhancedFollowUpTester()
    success = tester.run_comprehensive_test()
    
    if not success:
        sys.exit(1)
    else:
        sys.exit(0)