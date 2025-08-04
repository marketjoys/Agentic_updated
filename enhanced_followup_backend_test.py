#!/usr/bin/env python3
"""
Enhanced Follow-up Scheduling Backend Test
Tests the enhanced follow-up functionality for email campaigns
"""

import requests
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, Any

class EnhancedFollowUpTester:
    def __init__(self, base_url="https://24e4a959-d97d-4946-9c07-cd62f1a8669c.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.created_campaign_id = None

    def log_test(self, name: str, success: bool, details: str = ""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED {details}")
        else:
            print(f"❌ {name} - FAILED {details}")

    def run_test(self, name: str, method: str, endpoint: str, expected_status: int, data: Dict = None, headers: Dict = None) -> tuple:
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        
        # Default headers
        test_headers = {'Content-Type': 'application/json'}
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        if headers:
            test_headers.update(headers)

        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        if data:
            print(f"   Data: {json.dumps(data, indent=2)}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=30)

            print(f"   Status: {response.status_code}")
            
            success = response.status_code == expected_status
            response_data = {}
            
            try:
                response_data = response.json()
                if success:
                    print(f"   Response: {json.dumps(response_data, indent=2)}")
                else:
                    print(f"   Error Response: {json.dumps(response_data, indent=2)}")
            except:
                if not success:
                    print(f"   Raw Response: {response.text}")

            self.log_test(name, success, f"(Status: {response.status_code})")
            return success, response_data

        except Exception as e:
            print(f"   Exception: {str(e)}")
            self.log_test(name, False, f"(Exception: {str(e)})")
            return False, {}

    def test_login(self) -> bool:
        """Test login and get token"""
        print("\n" + "="*60)
        print("TESTING AUTHENTICATION")
        print("="*60)
        
        success, response = self.run_test(
            "User Login",
            "POST",
            "auth/login",
            200,
            data={"username": "testuser", "password": "testpass123"}
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            return True
        return False

    def test_services_status(self) -> bool:
        """Test services status endpoint"""
        print("\n" + "="*60)
        print("TESTING SERVICES STATUS")
        print("="*60)
        
        success, response = self.run_test(
            "Services Status Check",
            "GET",
            "services/status",
            200
        )
        
        if success:
            services = response.get('services', {})
            follow_up_status = services.get('smart_follow_up_engine', {}).get('status')
            email_processor_status = services.get('email_processor', {}).get('status')
            
            print(f"   Smart Follow-up Engine: {follow_up_status}")
            print(f"   Email Processor: {email_processor_status}")
            
            if follow_up_status == "running" and email_processor_status == "running":
                self.log_test("All Services Running", True)
                return True
            else:
                self.log_test("All Services Running", False, f"Follow-up: {follow_up_status}, Email: {email_processor_status}")
        
        return success

    def test_get_required_data(self) -> Dict[str, Any]:
        """Get required data for campaign creation"""
        print("\n" + "="*60)
        print("TESTING REQUIRED DATA RETRIEVAL")
        print("="*60)
        
        required_data = {
            'email_providers': [],
            'templates': [],
            'lists': []
        }
        
        # Get email providers
        success, providers = self.run_test(
            "Get Email Providers",
            "GET",
            "email-providers",
            200
        )
        if success:
            required_data['email_providers'] = providers
        
        # Get templates
        success, templates = self.run_test(
            "Get Templates",
            "GET",
            "templates",
            200
        )
        if success:
            required_data['templates'] = templates
        
        # Get lists
        success, lists = self.run_test(
            "Get Lists",
            "GET",
            "lists",
            200
        )
        if success:
            required_data['lists'] = lists
        
        return required_data

    def test_enhanced_campaign_creation(self, required_data: Dict[str, Any]) -> bool:
        """Test creating campaign with enhanced follow-up configuration"""
        print("\n" + "="*60)
        print("TESTING ENHANCED CAMPAIGN CREATION")
        print("="*60)
        
        # Prepare follow-up dates (tomorrow at 10:00 AM and day after at 2:00 PM)
        tomorrow = datetime.now() + timedelta(days=1)
        day_after = datetime.now() + timedelta(days=2)
        
        follow_up_date_1 = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
        follow_up_date_2 = day_after.replace(hour=14, minute=0, second=0, microsecond=0)
        
        # Get first available template and list
        template_id = ""
        list_ids = []
        
        if required_data['templates']:
            template_id = required_data['templates'][0].get('id', '')
        
        if required_data['lists']:
            list_ids = [required_data['lists'][0].get('id', '')]
        
        campaign_data = {
            "name": "DateTime Follow-up Test Campaign",
            "template_id": template_id,
            "list_ids": list_ids,
            "max_emails": 1000,
            "schedule": None,
            
            # Enhanced Follow-up Configuration
            "follow_up_enabled": True,
            "follow_up_schedule_type": "datetime",  # Using datetime mode
            "follow_up_intervals": [3, 7, 14],  # This should be ignored in datetime mode
            "follow_up_dates": [
                follow_up_date_1.isoformat(),
                follow_up_date_2.isoformat()
            ],
            "follow_up_timezone": "America/New_York",
            "follow_up_time_window_start": "09:00",
            "follow_up_time_window_end": "17:00",
            "follow_up_days_of_week": ["monday", "tuesday", "wednesday", "thursday", "friday"],
            "follow_up_templates": []
        }
        
        success, response = self.run_test(
            "Create Enhanced Follow-up Campaign",
            "POST",
            "campaigns",
            200,
            data=campaign_data
        )
        
        if success:
            self.created_campaign_id = response.get('id')
            
            # Verify response contains enhanced follow-up data
            expected_fields = [
                'follow_up_enabled', 'follow_up_schedule_type', 
                'follow_up_dates', 'follow_up_timezone'
            ]
            
            missing_fields = []
            for field in expected_fields:
                if field not in response:
                    missing_fields.append(field)
            
            if missing_fields:
                self.log_test("Enhanced Follow-up Response Fields", False, f"Missing: {missing_fields}")
            else:
                self.log_test("Enhanced Follow-up Response Fields", True)
                
                # Verify specific values
                if response.get('follow_up_schedule_type') == 'datetime':
                    self.log_test("Follow-up Schedule Type", True, "(datetime)")
                else:
                    self.log_test("Follow-up Schedule Type", False, f"Expected 'datetime', got '{response.get('follow_up_schedule_type')}'")
                
                if response.get('follow_up_timezone') == 'America/New_York':
                    self.log_test("Follow-up Timezone", True, "(America/New_York)")
                else:
                    self.log_test("Follow-up Timezone", False, f"Expected 'America/New_York', got '{response.get('follow_up_timezone')}'")
        
        return success

    def test_campaign_data_verification(self) -> bool:
        """Verify the created campaign contains all enhanced follow-up fields"""
        if not self.created_campaign_id:
            self.log_test("Campaign Data Verification", False, "No campaign ID available")
            return False
        
        print("\n" + "="*60)
        print("TESTING CAMPAIGN DATA VERIFICATION")
        print("="*60)
        
        # Get all campaigns
        success, campaigns = self.run_test(
            "Get All Campaigns",
            "GET",
            "campaigns",
            200
        )
        
        if not success:
            return False
        
        # Find our created campaign
        created_campaign = None
        for campaign in campaigns:
            if campaign.get('id') == self.created_campaign_id:
                created_campaign = campaign
                break
        
        if not created_campaign:
            self.log_test("Find Created Campaign", False, f"Campaign {self.created_campaign_id} not found")
            return False
        
        self.log_test("Find Created Campaign", True)
        
        # Verify enhanced follow-up fields
        required_fields = {
            'follow_up_enabled': True,
            'follow_up_schedule_type': 'datetime',
            'follow_up_timezone': 'America/New_York',
            'follow_up_time_window_start': '09:00',
            'follow_up_time_window_end': '17:00'
        }
        
        all_fields_correct = True
        for field, expected_value in required_fields.items():
            actual_value = created_campaign.get(field)
            if actual_value == expected_value:
                self.log_test(f"Field {field}", True, f"({actual_value})")
            else:
                self.log_test(f"Field {field}", False, f"Expected {expected_value}, got {actual_value}")
                all_fields_correct = False
        
        # Check follow_up_dates array
        follow_up_dates = created_campaign.get('follow_up_dates', [])
        if isinstance(follow_up_dates, list) and len(follow_up_dates) >= 2:
            self.log_test("Follow-up Dates Array", True, f"({len(follow_up_dates)} dates)")
        else:
            self.log_test("Follow-up Dates Array", False, f"Expected array with 2+ dates, got {follow_up_dates}")
            all_fields_correct = False
        
        # Check follow_up_days_of_week array
        days_of_week = created_campaign.get('follow_up_days_of_week', [])
        expected_days = ["monday", "tuesday", "wednesday", "thursday", "friday"]
        if isinstance(days_of_week, list) and set(days_of_week) == set(expected_days):
            self.log_test("Follow-up Days of Week", True, f"({len(days_of_week)} days)")
        else:
            self.log_test("Follow-up Days of Week", False, f"Expected {expected_days}, got {days_of_week}")
            all_fields_correct = False
        
        return all_fields_correct

    def test_interval_based_campaign(self) -> bool:
        """Test creating campaign with interval-based follow-up"""
        print("\n" + "="*60)
        print("TESTING INTERVAL-BASED CAMPAIGN")
        print("="*60)
        
        campaign_data = {
            "name": "Interval Follow-up Test Campaign",
            "template_id": "",
            "list_ids": [],
            "max_emails": 1000,
            "follow_up_enabled": True,
            "follow_up_schedule_type": "interval",  # Using interval mode
            "follow_up_intervals": [1, 3, 7],  # 1, 3, and 7 days
            "follow_up_dates": [],  # Should be ignored in interval mode
            "follow_up_timezone": "UTC",
            "follow_up_time_window_start": "08:00",
            "follow_up_time_window_end": "18:00",
            "follow_up_days_of_week": ["monday", "tuesday", "wednesday", "thursday", "friday"],
            "follow_up_templates": []
        }
        
        success, response = self.run_test(
            "Create Interval-based Campaign",
            "POST",
            "campaigns",
            200,
            data=campaign_data
        )
        
        if success:
            # Verify interval-based response
            if response.get('follow_up_schedule_type') == 'interval':
                self.log_test("Interval Schedule Type", True)
            else:
                self.log_test("Interval Schedule Type", False, f"Expected 'interval', got '{response.get('follow_up_schedule_type')}'")
            
            # Should have intervals, not dates
            if 'follow_up_intervals' in response:
                self.log_test("Interval Response Contains Intervals", True)
            else:
                self.log_test("Interval Response Contains Intervals", False)
        
        return success

    def run_all_tests(self) -> int:
        """Run all enhanced follow-up tests"""
        print("🚀 Starting Enhanced Follow-up Backend Tests")
        print("=" * 80)
        
        # Test 1: Authentication
        if not self.test_login():
            print("❌ Authentication failed, stopping tests")
            return 1
        
        # Test 2: Services Status
        self.test_services_status()
        
        # Test 3: Get required data
        required_data = self.test_get_required_data()
        
        # Test 4: Enhanced campaign creation (datetime mode)
        if not self.test_enhanced_campaign_creation(required_data):
            print("❌ Enhanced campaign creation failed")
        
        # Test 5: Campaign data verification
        self.test_campaign_data_verification()
        
        # Test 6: Interval-based campaign
        self.test_interval_based_campaign()
        
        # Print final results
        print("\n" + "="*80)
        print("FINAL TEST RESULTS")
        print("="*80)
        print(f"📊 Tests Run: {self.tests_run}")
        print(f"✅ Tests Passed: {self.tests_passed}")
        print(f"❌ Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"📈 Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL TESTS PASSED!")
            return 0
        else:
            print("⚠️  SOME TESTS FAILED")
            return 1

def main():
    """Main test execution"""
    tester = EnhancedFollowUpTester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())