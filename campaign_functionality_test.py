#!/usr/bin/env python3
"""
Campaign Functionality Testing - December 2024
Testing the specific campaign functionality requested in the review:

1. Test Multiple Campaign Send Prevention: 
   - Create a test campaign 
   - Send the campaign once (should work)
   - Try to send the same campaign again (should fail with appropriate error message)
   - Verify the backend properly validates and prevents re-sending campaigns

2. Test Campaign Details/View Functionality:
   - Test the GET /api/campaigns/{id} endpoint to ensure it returns detailed campaign information
   - Verify it includes: campaign data, template info, email records, analytics, list information
   - Test with both existing and non-existent campaign IDs

3. Test Campaign Status Tracking:
   - Verify campaigns progress through statuses correctly (draft -> sent/completed)
   - Test that only draft campaigns can be sent
   - Verify analytics are calculated correctly
"""

import requests
import json
import time
from datetime import datetime

# Get backend URL from frontend .env file
BACKEND_URL = "https://b5f20154-c131-4ea5-9b47-ef59aae7ea1b.preview.emergentagent.com"

class CampaignFunctionalityTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.auth_token = None
        self.headers = {}
        self.test_results = {}
        self.created_resources = {
            'prospects': [],
            'templates': [],
            'lists': [],
            'campaigns': [],
            'email_providers': []
        }
    
    def log_result(self, test_name, success, message="", details=None):
        """Log test results"""
        self.test_results[test_name] = {
            'success': success,
            'message': message,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if details:
            print(f"   Details: {details}")
    
    def authenticate(self):
        """Authenticate and get token"""
        try:
            login_data = {"username": "testuser", "password": "testpass123"}
            response = requests.post(f"{self.base_url}/api/auth/login", json=login_data)
            
            if response.status_code != 200:
                self.log_result("Authentication", False, f"HTTP {response.status_code}", response.text)
                return False
            
            auth_result = response.json()
            if 'access_token' not in auth_result:
                self.log_result("Authentication", False, "No access token in response", auth_result)
                return False
            
            self.auth_token = auth_result['access_token']
            self.headers = {"Authorization": f"Bearer {self.auth_token}"}
            self.log_result("Authentication", True, "Login successful")
            return True
            
        except Exception as e:
            self.log_result("Authentication", False, f"Exception: {str(e)}")
            return False
    
    def setup_test_data(self):
        """Create necessary test data (template, prospects, list)"""
        try:
            # Create a test template
            template_data = {
                "name": "Campaign Test Template",
                "subject": "Test Campaign - {{first_name}}",
                "content": "<p>Hello {{first_name}} from {{company}},</p><p>This is a test campaign email.</p>",
                "type": "initial",
                "placeholders": ["first_name", "company"]
            }
            
            response = requests.post(f"{self.base_url}/api/templates", json=template_data, headers=self.headers)
            if response.status_code != 200:
                self.log_result("Setup Test Template", False, f"HTTP {response.status_code}", response.text)
                return None, None, None
            
            template = response.json()
            template_id = template['id']
            self.created_resources['templates'].append(template_id)
            self.log_result("Setup Test Template", True, f"Created template: {template_id}")
            
            # Create test prospects
            prospects = []
            for i in range(3):
                unique_timestamp = int(time.time()) + i
                prospect_data = {
                    "email": f"test.prospect.{unique_timestamp}@example.com",
                    "first_name": f"TestUser{i+1}",
                    "last_name": "Campaign",
                    "company": f"TestCorp{i+1}",
                    "job_title": "Test Manager",
                    "industry": "Testing"
                }
                
                response = requests.post(f"{self.base_url}/api/prospects", json=prospect_data, headers=self.headers)
                if response.status_code == 200:
                    prospect = response.json()
                    prospects.append(prospect['id'])
                    self.created_resources['prospects'].append(prospect['id'])
            
            if not prospects:
                self.log_result("Setup Test Prospects", False, "No prospects created")
                return None, None, None
            
            self.log_result("Setup Test Prospects", True, f"Created {len(prospects)} prospects")
            
            # Create a test list and add prospects
            list_data = {
                "name": "Campaign Test List",
                "description": "Test list for campaign functionality testing",
                "color": "#3B82F6",
                "tags": ["test", "campaign"]
            }
            
            response = requests.post(f"{self.base_url}/api/lists", json=list_data, headers=self.headers)
            if response.status_code != 200:
                self.log_result("Setup Test List", False, f"HTTP {response.status_code}", response.text)
                return template_id, prospects, None
            
            list_obj = response.json()
            list_id = list_obj['id']
            self.created_resources['lists'].append(list_id)
            
            # Add prospects to list
            add_request = {"prospect_ids": prospects}
            response = requests.post(f"{self.base_url}/api/lists/{list_id}/prospects", 
                                   json=add_request, headers=self.headers)
            if response.status_code == 200:
                self.log_result("Setup Test List", True, f"Created list with {len(prospects)} prospects: {list_id}")
            else:
                self.log_result("Setup Test List", False, f"Failed to add prospects to list: {response.status_code}")
            
            return template_id, prospects, list_id
            
        except Exception as e:
            self.log_result("Setup Test Data", False, f"Exception: {str(e)}")
            return None, None, None
    
    def test_multiple_campaign_send_prevention(self, template_id, list_id):
        """Test that campaigns cannot be sent multiple times"""
        try:
            # Create a test campaign
            campaign_data = {
                "name": "Multiple Send Prevention Test Campaign",
                "template_id": template_id,
                "list_ids": [list_id] if list_id else [],
                "max_emails": 10,
                "schedule": None
            }
            
            response = requests.post(f"{self.base_url}/api/campaigns", json=campaign_data, headers=self.headers)
            if response.status_code != 200:
                self.log_result("Create Campaign for Send Prevention Test", False, f"HTTP {response.status_code}", response.text)
                return False
            
            campaign = response.json()
            campaign_id = campaign['id']
            self.created_resources['campaigns'].append(campaign_id)
            self.log_result("Create Campaign for Send Prevention Test", True, f"Created campaign: {campaign_id}")
            
            # Verify initial status is 'draft'
            response = requests.get(f"{self.base_url}/api/campaigns/{campaign_id}", headers=self.headers)
            if response.status_code == 200:
                campaign_details = response.json()
                initial_status = campaign_details.get('status', 'unknown')
                if initial_status == 'draft':
                    self.log_result("Verify Initial Campaign Status", True, f"Campaign status is 'draft' as expected")
                else:
                    self.log_result("Verify Initial Campaign Status", False, f"Expected 'draft', got '{initial_status}'")
            
            # Send the campaign for the first time
            send_request = {
                "send_immediately": True,
                "max_emails": 5,
                "schedule_type": "immediate",
                "follow_up_enabled": False
            }
            
            response = requests.post(f"{self.base_url}/api/campaigns/{campaign_id}/send", 
                                   json=send_request, headers=self.headers)
            if response.status_code != 200:
                self.log_result("First Campaign Send", False, f"HTTP {response.status_code}", response.text)
                return False
            
            first_send_result = response.json()
            self.log_result("First Campaign Send", True, 
                           f"Campaign sent successfully: {first_send_result.get('total_sent', 0)} sent, {first_send_result.get('total_failed', 0)} failed")
            
            # Verify campaign status changed to 'sent'
            response = requests.get(f"{self.base_url}/api/campaigns/{campaign_id}", headers=self.headers)
            if response.status_code == 200:
                campaign_details = response.json()
                updated_status = campaign_details.get('status', 'unknown')
                if updated_status in ['sent', 'completed']:
                    self.log_result("Verify Campaign Status After Send", True, f"Campaign status is '{updated_status}' as expected")
                else:
                    self.log_result("Verify Campaign Status After Send", False, f"Expected 'sent' or 'completed', got '{updated_status}'")
            
            # Try to send the campaign again (should fail)
            response = requests.post(f"{self.base_url}/api/campaigns/{campaign_id}/send", 
                                   json=send_request, headers=self.headers)
            
            if response.status_code == 400:
                # Expected behavior - should return 400 with error message
                error_response = response.json()
                error_message = error_response.get('detail', '')
                if 'already been' in error_message.lower() or 'cannot send again' in error_message.lower():
                    self.log_result("Multiple Send Prevention", True, f"Campaign re-send properly prevented: {error_message}")
                else:
                    self.log_result("Multiple Send Prevention", True, f"Campaign re-send prevented with error: {error_message}")
                return True
            elif response.status_code == 200:
                # This should not happen - campaign should not be sent again
                second_send_result = response.json()
                self.log_result("Multiple Send Prevention", False, 
                               f"Campaign was sent again (should be prevented): {second_send_result}")
                return False
            else:
                # Other error codes
                self.log_result("Multiple Send Prevention", False, 
                               f"Unexpected response code {response.status_code}: {response.text}")
                return False
            
        except Exception as e:
            self.log_result("Multiple Campaign Send Prevention", False, f"Exception: {str(e)}")
            return False
    
    def test_campaign_details_functionality(self, template_id, list_id):
        """Test GET /api/campaigns/{id} endpoint for detailed campaign information"""
        try:
            # Create a campaign for testing
            campaign_data = {
                "name": "Campaign Details Test Campaign",
                "template_id": template_id,
                "list_ids": [list_id] if list_id else [],
                "max_emails": 5,
                "schedule": None
            }
            
            response = requests.post(f"{self.base_url}/api/campaigns", json=campaign_data, headers=self.headers)
            if response.status_code != 200:
                self.log_result("Create Campaign for Details Test", False, f"HTTP {response.status_code}", response.text)
                return False
            
            campaign = response.json()
            campaign_id = campaign['id']
            self.created_resources['campaigns'].append(campaign_id)
            self.log_result("Create Campaign for Details Test", True, f"Created campaign: {campaign_id}")
            
            # Send the campaign to generate email records and analytics
            send_request = {
                "send_immediately": True,
                "max_emails": 3,
                "schedule_type": "immediate",
                "follow_up_enabled": False
            }
            
            response = requests.post(f"{self.base_url}/api/campaigns/{campaign_id}/send", 
                                   json=send_request, headers=self.headers)
            if response.status_code == 200:
                self.log_result("Send Campaign for Details Test", True, "Campaign sent to generate data")
            else:
                self.log_result("Send Campaign for Details Test", False, f"HTTP {response.status_code}", response.text)
            
            # Test GET /api/campaigns/{id} with existing campaign
            response = requests.get(f"{self.base_url}/api/campaigns/{campaign_id}", headers=self.headers)
            if response.status_code != 200:
                self.log_result("Get Campaign Details - Existing Campaign", False, f"HTTP {response.status_code}", response.text)
                return False
            
            campaign_details = response.json()
            
            # Verify required fields are present
            required_fields = ['id', 'name', 'status', 'template_id', 'created_at']
            missing_fields = []
            for field in required_fields:
                if field not in campaign_details:
                    missing_fields.append(field)
            
            if missing_fields:
                self.log_result("Campaign Details - Required Fields", False, f"Missing fields: {missing_fields}", campaign_details)
                return False
            else:
                self.log_result("Campaign Details - Required Fields", True, "All required fields present")
            
            # Verify template information is included
            if 'template' in campaign_details and campaign_details['template']:
                template_info = campaign_details['template']
                if 'id' in template_info and 'name' in template_info:
                    self.log_result("Campaign Details - Template Info", True, f"Template info included: {template_info['name']}")
                else:
                    self.log_result("Campaign Details - Template Info", False, "Template info incomplete", template_info)
            else:
                self.log_result("Campaign Details - Template Info", False, "No template info in response")
            
            # Verify list information is included
            if 'lists' in campaign_details and isinstance(campaign_details['lists'], list):
                if len(campaign_details['lists']) > 0:
                    list_info = campaign_details['lists'][0]
                    if 'id' in list_info and 'name' in list_info:
                        self.log_result("Campaign Details - List Info", True, f"List info included: {list_info['name']}")
                    else:
                        self.log_result("Campaign Details - List Info", False, "List info incomplete", list_info)
                else:
                    self.log_result("Campaign Details - List Info", True, "No lists associated (expected for some campaigns)")
            else:
                self.log_result("Campaign Details - List Info", False, "No lists field in response")
            
            # Verify email records are included
            if 'email_records' in campaign_details and isinstance(campaign_details['email_records'], list):
                email_records = campaign_details['email_records']
                self.log_result("Campaign Details - Email Records", True, f"Email records included: {len(email_records)} records")
                
                # Check email record structure if any exist
                if len(email_records) > 0:
                    record = email_records[0]
                    record_fields = ['id', 'campaign_id', 'recipient_email', 'status']
                    missing_record_fields = [f for f in record_fields if f not in record]
                    if missing_record_fields:
                        self.log_result("Campaign Details - Email Record Structure", False, f"Missing fields in email record: {missing_record_fields}")
                    else:
                        self.log_result("Campaign Details - Email Record Structure", True, "Email record structure is correct")
            else:
                self.log_result("Campaign Details - Email Records", False, "No email_records field in response")
            
            # Verify analytics are included
            if 'analytics' in campaign_details and isinstance(campaign_details['analytics'], dict):
                analytics = campaign_details['analytics']
                analytics_fields = ['total_sent', 'total_failed', 'total_emails', 'success_rate']
                missing_analytics_fields = [f for f in analytics_fields if f not in analytics]
                if missing_analytics_fields:
                    self.log_result("Campaign Details - Analytics", False, f"Missing analytics fields: {missing_analytics_fields}")
                else:
                    self.log_result("Campaign Details - Analytics", True, 
                                   f"Analytics included: {analytics['total_sent']} sent, {analytics['total_failed']} failed, {analytics['success_rate']:.1f}% success rate")
            else:
                self.log_result("Campaign Details - Analytics", False, "No analytics field in response")
            
            # Test GET /api/campaigns/{id} with non-existent campaign
            non_existent_id = "non-existent-campaign-id-12345"
            response = requests.get(f"{self.base_url}/api/campaigns/{non_existent_id}", headers=self.headers)
            if response.status_code == 404:
                self.log_result("Get Campaign Details - Non-existent Campaign", True, "404 returned for non-existent campaign")
            else:
                self.log_result("Get Campaign Details - Non-existent Campaign", False, f"Expected 404, got {response.status_code}")
            
            return True
            
        except Exception as e:
            self.log_result("Campaign Details Functionality", False, f"Exception: {str(e)}")
            return False
    
    def test_campaign_status_tracking(self, template_id, list_id):
        """Test campaign status progression and validation"""
        try:
            # Create a campaign for status tracking
            campaign_data = {
                "name": "Status Tracking Test Campaign",
                "template_id": template_id,
                "list_ids": [list_id] if list_id else [],
                "max_emails": 3,
                "schedule": None
            }
            
            response = requests.post(f"{self.base_url}/api/campaigns", json=campaign_data, headers=self.headers)
            if response.status_code != 200:
                self.log_result("Create Campaign for Status Test", False, f"HTTP {response.status_code}", response.text)
                return False
            
            campaign = response.json()
            campaign_id = campaign['id']
            self.created_resources['campaigns'].append(campaign_id)
            self.log_result("Create Campaign for Status Test", True, f"Created campaign: {campaign_id}")
            
            # Verify initial status is 'draft'
            response = requests.get(f"{self.base_url}/api/campaigns/{campaign_id}", headers=self.headers)
            if response.status_code != 200:
                self.log_result("Check Initial Campaign Status", False, f"HTTP {response.status_code}", response.text)
                return False
            
            campaign_details = response.json()
            initial_status = campaign_details.get('status', 'unknown')
            if initial_status == 'draft':
                self.log_result("Initial Campaign Status", True, "Campaign created with 'draft' status")
            else:
                self.log_result("Initial Campaign Status", False, f"Expected 'draft', got '{initial_status}'")
            
            # Test that draft campaigns can be sent
            send_request = {
                "send_immediately": True,
                "max_emails": 2,
                "schedule_type": "immediate",
                "follow_up_enabled": False
            }
            
            response = requests.post(f"{self.base_url}/api/campaigns/{campaign_id}/send", 
                                   json=send_request, headers=self.headers)
            if response.status_code == 200:
                send_result = response.json()
                self.log_result("Send Draft Campaign", True, 
                               f"Draft campaign sent successfully: {send_result.get('total_sent', 0)} sent")
            else:
                self.log_result("Send Draft Campaign", False, f"HTTP {response.status_code}", response.text)
                return False
            
            # Verify status changed after sending
            response = requests.get(f"{self.base_url}/api/campaigns/{campaign_id}", headers=self.headers)
            if response.status_code == 200:
                campaign_details = response.json()
                final_status = campaign_details.get('status', 'unknown')
                if final_status in ['sent', 'completed']:
                    self.log_result("Campaign Status After Send", True, f"Status changed to '{final_status}' after sending")
                else:
                    self.log_result("Campaign Status After Send", False, f"Expected 'sent' or 'completed', got '{final_status}'")
                
                # Verify analytics are calculated correctly
                if 'analytics' in campaign_details:
                    analytics = campaign_details['analytics']
                    total_emails = analytics.get('total_emails', 0)
                    total_sent = analytics.get('total_sent', 0)
                    total_failed = analytics.get('total_failed', 0)
                    success_rate = analytics.get('success_rate', 0)
                    
                    # Basic validation of analytics
                    if total_emails == (total_sent + total_failed):
                        self.log_result("Analytics Calculation", True, 
                                       f"Analytics calculated correctly: {total_sent} sent + {total_failed} failed = {total_emails} total")
                    else:
                        self.log_result("Analytics Calculation", False, 
                                       f"Analytics mismatch: {total_sent} sent + {total_failed} failed ≠ {total_emails} total")
                    
                    # Check success rate calculation
                    if total_emails > 0:
                        expected_success_rate = (total_sent / total_emails) * 100
                        if abs(success_rate - expected_success_rate) < 0.1:  # Allow small floating point differences
                            self.log_result("Success Rate Calculation", True, f"Success rate calculated correctly: {success_rate:.1f}%")
                        else:
                            self.log_result("Success Rate Calculation", False, 
                                           f"Success rate mismatch: expected {expected_success_rate:.1f}%, got {success_rate:.1f}%")
                    else:
                        self.log_result("Success Rate Calculation", True, "Success rate is 0% for campaign with no emails (correct)")
                else:
                    self.log_result("Analytics Calculation", False, "No analytics found in campaign details")
            
            # Create another campaign to test that only draft campaigns can be sent
            campaign_data2 = {
                "name": "Second Status Test Campaign",
                "template_id": template_id,
                "list_ids": [list_id] if list_id else [],
                "max_emails": 2,
                "schedule": None
            }
            
            response = requests.post(f"{self.base_url}/api/campaigns", json=campaign_data2, headers=self.headers)
            if response.status_code == 200:
                campaign2 = response.json()
                campaign2_id = campaign2['id']
                self.created_resources['campaigns'].append(campaign2_id)
                
                # Send this campaign
                response = requests.post(f"{self.base_url}/api/campaigns/{campaign2_id}/send", 
                                       json=send_request, headers=self.headers)
                if response.status_code == 200:
                    # Now try to send it again (should fail)
                    response = requests.post(f"{self.base_url}/api/campaigns/{campaign2_id}/send", 
                                           json=send_request, headers=self.headers)
                    if response.status_code == 400:
                        self.log_result("Non-Draft Campaign Send Prevention", True, "Non-draft campaign send properly prevented")
                    else:
                        self.log_result("Non-Draft Campaign Send Prevention", False, f"Expected 400, got {response.status_code}")
                else:
                    self.log_result("Non-Draft Campaign Send Prevention", False, "Could not send second campaign for test")
            
            return True
            
        except Exception as e:
            self.log_result("Campaign Status Tracking", False, f"Exception: {str(e)}")
            return False
    
    def cleanup_resources(self):
        """Clean up created test resources"""
        print("\n🧹 Cleaning up test resources...")
        
        # Delete campaigns
        for campaign_id in self.created_resources['campaigns']:
            try:
                response = requests.delete(f"{self.base_url}/api/campaigns/{campaign_id}", headers=self.headers)
                if response.status_code == 200:
                    print(f"   ✅ Deleted campaign {campaign_id}")
                else:
                    print(f"   ⚠️ Failed to delete campaign {campaign_id}: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Error deleting campaign {campaign_id}: {str(e)}")
        
        # Delete lists
        for list_id in self.created_resources['lists']:
            try:
                response = requests.delete(f"{self.base_url}/api/lists/{list_id}", headers=self.headers)
                if response.status_code == 200:
                    print(f"   ✅ Deleted list {list_id}")
                else:
                    print(f"   ⚠️ Failed to delete list {list_id}: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Error deleting list {list_id}: {str(e)}")
        
        # Delete templates
        for template_id in self.created_resources['templates']:
            try:
                response = requests.delete(f"{self.base_url}/api/templates/{template_id}", headers=self.headers)
                if response.status_code == 200:
                    print(f"   ✅ Deleted template {template_id}")
                else:
                    print(f"   ⚠️ Failed to delete template {template_id}: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Error deleting template {template_id}: {str(e)}")
        
        # Delete prospects
        for prospect_id in self.created_resources['prospects']:
            try:
                response = requests.delete(f"{self.base_url}/api/prospects/{prospect_id}", headers=self.headers)
                if response.status_code == 200:
                    print(f"   ✅ Deleted prospect {prospect_id}")
                else:
                    print(f"   ⚠️ Failed to delete prospect {prospect_id}: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Error deleting prospect {prospect_id}: {str(e)}")
    
    def run_campaign_functionality_tests(self):
        """Run all campaign functionality tests"""
        print("🚀 Starting Campaign Functionality Tests")
        print("Testing specific requirements from review request:")
        print("1. Multiple Campaign Send Prevention")
        print("2. Campaign Details/View Functionality") 
        print("3. Campaign Status Tracking")
        print("=" * 80)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return self.test_results
        
        # Setup test data
        template_id, prospects, list_id = self.setup_test_data()
        if not template_id:
            print("❌ Test data setup failed. Cannot proceed with tests.")
            return self.test_results
        
        # Run the specific tests
        tests = [
            ("Multiple Campaign Send Prevention", lambda: self.test_multiple_campaign_send_prevention(template_id, list_id)),
            ("Campaign Details/View Functionality", lambda: self.test_campaign_details_functionality(template_id, list_id)),
            ("Campaign Status Tracking", lambda: self.test_campaign_status_tracking(template_id, list_id))
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🧪 Running: {test_name}")
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                self.log_result(test_name, False, f"Test execution failed: {str(e)}")
        
        print("\n" + "=" * 80)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All campaign functionality tests passed!")
        else:
            print(f"⚠️  {total - passed} tests failed")
        
        # Cleanup
        self.cleanup_resources()
        
        return self.test_results

def main():
    """Main test execution"""
    tester = CampaignFunctionalityTester()
    results = tester.run_campaign_functionality_tests()
    
    # Print detailed results
    print("\n" + "=" * 80)
    print("📋 DETAILED TEST RESULTS")
    print("=" * 80)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"{status} {test_name}")
        if result['message']:
            print(f"   Message: {result['message']}")
        if result['details']:
            print(f"   Details: {result['details']}")
        print()
    
    # Summary for test_result.md update
    print("\n" + "=" * 80)
    print("📝 CAMPAIGN FUNCTIONALITY TEST SUMMARY")
    print("=" * 80)
    
    passed_tests = [name for name, result in results.items() if result['success']]
    failed_tests = [name for name, result in results.items() if not result['success']]
    
    print("✅ PASSED TESTS:")
    for test in passed_tests:
        print(f"   - {test}")
    
    if failed_tests:
        print("\n❌ FAILED TESTS:")
        for test in failed_tests:
            print(f"   - {test}")
    
    # Specific findings for the review request
    print("\n🎯 REVIEW REQUEST FINDINGS:")
    print("1. Multiple Campaign Send Prevention:", "✅ WORKING" if any("Multiple Campaign Send Prevention" in name and results[name]['success'] for name in results) else "❌ FAILING")
    print("2. Campaign Details/View Functionality:", "✅ WORKING" if any("Campaign Details" in name and results[name]['success'] for name in results) else "❌ FAILING")
    print("3. Campaign Status Tracking:", "✅ WORKING" if any("Campaign Status Tracking" in name and results[name]['success'] for name in results) else "❌ FAILING")
    
    return results

if __name__ == "__main__":
    main()
"""
Campaign Sending Functionality Testing for AI Email Responder
Tests the specific functionality requested in the review:
1. Campaign API Endpoints Testing
2. Follow-up Functionality Testing  
3. Auto Email Responder Testing
4. Template and Knowledge Base Integration
"""

import requests
import json
import time
from datetime import datetime
import uuid

# Get backend URL from frontend .env file
BACKEND_URL = "https://b5f20154-c131-4ea5-9b47-ef59aae7ea1b.preview.emergentagent.com"

class CampaignFunctionalityTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.test_results = {}
        self.auth_token = None
        self.created_resources = {
            'campaigns': [],
            'templates': [],
            'prospects': [],
            'email_providers': []
        }
    
    def log_result(self, test_name, success, message="", details=None):
        """Log test results"""
        self.test_results[test_name] = {
            'success': success,
            'message': message,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if details:
            print(f"   Details: {details}")
    
    def authenticate(self):
        """Authenticate with the API"""
        try:
            auth_data = {
                "username": "testuser",
                "password": "testpass123"
            }
            
            response = requests.post(f"{self.base_url}/api/auth/login", json=auth_data)
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('access_token')
                self.log_result("Authentication", True, "Successfully authenticated")
                return True
            else:
                self.log_result("Authentication", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Authentication", False, f"Exception: {str(e)}")
            return False
    
    def get_headers(self):
        """Get headers with authentication"""
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers
    
    def test_campaign_api_endpoints(self):
        """Test Campaign API Endpoints"""
        print("\n🎯 TESTING CAMPAIGN API ENDPOINTS")
        print("-" * 50)
        
        try:
            # Test GET /api/campaigns
            response = requests.get(f"{self.base_url}/api/campaigns", headers=self.get_headers())
            if response.status_code != 200:
                self.log_result("GET /api/campaigns", False, f"HTTP {response.status_code}", response.text)
                return False
            
            campaigns = response.json()
            self.log_result("GET /api/campaigns", True, f"Retrieved {len(campaigns)} campaigns")
            
            # Create a test template first (needed for campaign)
            template_data = {
                "name": "Test Campaign Template",
                "subject": "Hello {{first_name}}, let's connect!",
                "content": "<p>Hi {{first_name}},</p><p>I hope this email finds you well at {{company}}.</p><p>Best regards</p>",
                "type": "initial",
                "placeholders": ["first_name", "company"]
            }
            
            response = requests.post(f"{self.base_url}/api/templates", json=template_data, headers=self.get_headers())
            if response.status_code != 200:
                self.log_result("Create Template for Campaign", False, f"HTTP {response.status_code}", response.text)
                return False
            
            template = response.json()
            template_id = template.get('id')
            self.created_resources['templates'].append(template_id)
            self.log_result("Create Template for Campaign", True, f"Created template: {template_id}")
            
            # Create a test prospect
            prospect_data = {
                "email": f"test.prospect.{int(time.time())}@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "company": "Test Company",
                "job_title": "Manager"
            }
            
            response = requests.post(f"{self.base_url}/api/prospects", json=prospect_data, headers=self.get_headers())
            if response.status_code != 200:
                self.log_result("Create Prospect for Campaign", False, f"HTTP {response.status_code}", response.text)
                return False
            
            prospect = response.json()
            prospect_id = prospect.get('id')
            self.created_resources['prospects'].append(prospect_id)
            self.log_result("Create Prospect for Campaign", True, f"Created prospect: {prospect_id}")
            
            # Test POST /api/campaigns
            campaign_data = {
                "name": f"Test Campaign {int(time.time())}",
                "template_id": template_id,
                "list_ids": [],
                "max_emails": 100,
                "schedule": None
            }
            
            response = requests.post(f"{self.base_url}/api/campaigns", json=campaign_data, headers=self.get_headers())
            if response.status_code != 200:
                self.log_result("POST /api/campaigns", False, f"HTTP {response.status_code}", response.text)
                return False
            
            campaign = response.json()
            campaign_id = campaign.get('id')
            self.created_resources['campaigns'].append(campaign_id)
            self.log_result("POST /api/campaigns", True, f"Created campaign: {campaign_id}")
            
            # Test campaign sending - POST /api/campaigns/{id}/send
            send_request = {
                "send_immediately": True,
                "email_provider_id": "",
                "max_emails": 1,
                "schedule_type": "immediate",
                "follow_up_enabled": True,
                "follow_up_intervals": [3, 7, 14],
                "follow_up_templates": []
            }
            
            response = requests.post(f"{self.base_url}/api/campaigns/{campaign_id}/send", 
                                   json=send_request, headers=self.get_headers())
            
            if response.status_code == 200:
                result = response.json()
                self.log_result("POST /api/campaigns/{id}/send", True, 
                               f"Campaign sent: {result.get('total_sent', 0)} emails sent, {result.get('total_failed', 0)} failed")
            else:
                self.log_result("POST /api/campaigns/{id}/send", False, 
                               f"HTTP {response.status_code}", response.text)
            
            return True
            
        except Exception as e:
            self.log_result("Campaign API Endpoints", False, f"Exception: {str(e)}")
            return False
    
    def test_follow_up_functionality(self):
        """Test Follow-up Functionality"""
        print("\n🔄 TESTING FOLLOW-UP FUNCTIONALITY")
        print("-" * 50)
        
        try:
            # Test GET /api/follow-up-rules
            response = requests.get(f"{self.base_url}/api/follow-up-rules", headers=self.get_headers())
            if response.status_code == 200:
                rules = response.json()
                self.log_result("GET /api/follow-up-rules", True, f"Retrieved {len(rules)} follow-up rules")
            else:
                self.log_result("GET /api/follow-up-rules", False, f"HTTP {response.status_code}", response.text)
            
            # Test POST /api/follow-up-engine/start
            response = requests.post(f"{self.base_url}/api/follow-up-engine/start", headers=self.get_headers())
            if response.status_code == 200:
                result = response.json()
                self.log_result("POST /api/follow-up-engine/start", True, 
                               f"Follow-up engine started: {result.get('message', 'Success')}")
            else:
                self.log_result("POST /api/follow-up-engine/start", False, f"HTTP {response.status_code}", response.text)
            
            # Test GET /api/follow-up-engine/status
            response = requests.get(f"{self.base_url}/api/follow-up-engine/status", headers=self.get_headers())
            if response.status_code == 200:
                status = response.json()
                self.log_result("GET /api/follow-up-engine/status", True, 
                               f"Follow-up engine status: {status.get('status', 'unknown')}")
            else:
                self.log_result("GET /api/follow-up-engine/status", False, f"HTTP {response.status_code}", response.text)
            
            return True
            
        except Exception as e:
            self.log_result("Follow-up Functionality", False, f"Exception: {str(e)}")
            return False
    
    def test_auto_email_responder(self):
        """Test Auto Email Responder"""
        print("\n🤖 TESTING AUTO EMAIL RESPONDER")
        print("-" * 50)
        
        try:
            # Test GET /api/email-processing/status
            response = requests.get(f"{self.base_url}/api/email-processing/status", headers=self.get_headers())
            if response.status_code == 200:
                status = response.json()
                self.log_result("GET /api/email-processing/status", True, 
                               f"Email processing status: {status.get('status', 'unknown')}")
            else:
                self.log_result("GET /api/email-processing/status", False, f"HTTP {response.status_code}", response.text)
            
            # Test POST /api/email-processing/start
            response = requests.post(f"{self.base_url}/api/email-processing/start", headers=self.get_headers())
            if response.status_code == 200:
                result = response.json()
                self.log_result("POST /api/email-processing/start", True, 
                               f"Email processing started: {result.get('message', 'Success')}")
            else:
                self.log_result("POST /api/email-processing/start", False, f"HTTP {response.status_code}", response.text)
            
            # Test POST /api/email-processing/test-classification
            test_email = {
                "subject": "Interested in your product",
                "content": "Hi, I received your email and I'm very interested in learning more about your product. Can you send me pricing information?"
            }
            
            response = requests.post(f"{self.base_url}/api/email-processing/test-classification", 
                                   json=test_email, headers=self.get_headers())
            if response.status_code == 200:
                result = response.json()
                self.log_result("POST /api/email-processing/test-classification", True, 
                               f"Email classified successfully: {len(result.get('classified_intents', []))} intents found")
            else:
                self.log_result("POST /api/email-processing/test-classification", False, f"HTTP {response.status_code}", response.text)
            
            # Test POST /api/email-processing/test-response
            test_response_data = {
                "subject": "Interested in your product",
                "content": "Hi, I received your email and I'm very interested in learning more about your product. Can you send me pricing information?",
                "prospect_id": self.created_resources['prospects'][0] if self.created_resources['prospects'] else None
            }
            
            if test_response_data['prospect_id']:
                response = requests.post(f"{self.base_url}/api/email-processing/test-response", 
                                       json=test_response_data, headers=self.get_headers())
                if response.status_code == 200:
                    result = response.json()
                    self.log_result("POST /api/email-processing/test-response", True, 
                                   f"Response generated successfully")
                else:
                    self.log_result("POST /api/email-processing/test-response", False, f"HTTP {response.status_code}", response.text)
            else:
                self.log_result("POST /api/email-processing/test-response", False, "No prospect available for testing")
            
            return True
            
        except Exception as e:
            self.log_result("Auto Email Responder", False, f"Exception: {str(e)}")
            return False
    
    def test_template_and_knowledge_base_integration(self):
        """Test Template and Knowledge Base Integration"""
        print("\n📚 TESTING TEMPLATE AND KNOWLEDGE BASE INTEGRATION")
        print("-" * 50)
        
        try:
            # Test GET /api/templates
            response = requests.get(f"{self.base_url}/api/templates", headers=self.get_headers())
            if response.status_code == 200:
                templates = response.json()
                self.log_result("GET /api/templates", True, f"Retrieved {len(templates)} templates")
                
                # Check if templates have proper structure
                if templates:
                    template = templates[0]
                    required_fields = ['id', 'name', 'subject', 'content']
                    missing_fields = [field for field in required_fields if field not in template]
                    if missing_fields:
                        self.log_result("Template Structure Validation", False, f"Missing fields: {missing_fields}")
                    else:
                        self.log_result("Template Structure Validation", True, "Templates have proper structure")
            else:
                self.log_result("GET /api/templates", False, f"HTTP {response.status_code}", response.text)
            
            # Test GET /api/knowledge-base
            response = requests.get(f"{self.base_url}/api/knowledge-base", headers=self.get_headers())
            if response.status_code == 200:
                kb_articles = response.json()
                self.log_result("GET /api/knowledge-base", True, f"Retrieved {len(kb_articles)} knowledge base articles")
                
                # Check if knowledge base articles have proper structure
                if kb_articles:
                    article = kb_articles[0]
                    required_fields = ['id', 'title', 'content']
                    missing_fields = [field for field in required_fields if field not in article]
                    if missing_fields:
                        self.log_result("Knowledge Base Structure Validation", False, f"Missing fields: {missing_fields}")
                    else:
                        self.log_result("Knowledge Base Structure Validation", True, "Knowledge base articles have proper structure")
            else:
                self.log_result("GET /api/knowledge-base", False, f"HTTP {response.status_code}", response.text)
            
            # Test template personalization with knowledge base
            if self.created_resources['templates'] and self.created_resources['prospects']:
                template_id = self.created_resources['templates'][0]
                prospect_id = self.created_resources['prospects'][0]
                
                # Get template
                response = requests.get(f"{self.base_url}/api/templates/{template_id}", headers=self.get_headers())
                if response.status_code == 200:
                    template = response.json()
                    
                    # Get prospect
                    response = requests.get(f"{self.base_url}/api/prospects/{prospect_id}", headers=self.get_headers())
                    if response.status_code == 200:
                        prospect = response.json()
                        
                        # Check if template contains personalization placeholders
                        content = template.get('content', '')
                        subject = template.get('subject', '')
                        
                        placeholders_found = []
                        common_placeholders = ['{{first_name}}', '{{last_name}}', '{{company}}', '{{job_title}}']
                        
                        for placeholder in common_placeholders:
                            if placeholder in content or placeholder in subject:
                                placeholders_found.append(placeholder)
                        
                        if placeholders_found:
                            self.log_result("Template Personalization Check", True, 
                                           f"Found placeholders: {', '.join(placeholders_found)}")
                        else:
                            self.log_result("Template Personalization Check", False, "No personalization placeholders found")
                    else:
                        self.log_result("Get Prospect for Personalization", False, f"HTTP {response.status_code}")
                else:
                    self.log_result("Get Template for Personalization", False, f"HTTP {response.status_code}")
            
            return True
            
        except Exception as e:
            self.log_result("Template and Knowledge Base Integration", False, f"Exception: {str(e)}")
            return False
    
    def test_email_providers_configuration(self):
        """Test Email Providers Configuration"""
        print("\n📧 TESTING EMAIL PROVIDERS CONFIGURATION")
        print("-" * 50)
        
        try:
            # Test GET /api/email-providers
            response = requests.get(f"{self.base_url}/api/email-providers", headers=self.get_headers())
            if response.status_code == 200:
                providers = response.json()
                self.log_result("GET /api/email-providers", True, f"Retrieved {len(providers)} email providers")
                
                if len(providers) == 0:
                    # Create a test email provider
                    provider_data = {
                        "name": "Test Email Provider",
                        "provider_type": "gmail",
                        "email_address": "test@example.com",
                        "display_name": "Test Sender",
                        "smtp_host": "smtp.gmail.com",
                        "smtp_port": 587,
                        "smtp_username": "test@example.com",
                        "smtp_password": "test_password",
                        "smtp_use_tls": True,
                        "imap_host": "imap.gmail.com",
                        "imap_port": 993,
                        "imap_username": "test@example.com",
                        "imap_password": "test_password",
                        "daily_send_limit": 500,
                        "hourly_send_limit": 50,
                        "is_default": True,
                        "skip_connection_test": True
                    }
                    
                    response = requests.post(f"{self.base_url}/api/email-providers", 
                                           json=provider_data, headers=self.get_headers())
                    if response.status_code == 200:
                        provider = response.json()
                        provider_id = provider.get('id')
                        self.created_resources['email_providers'].append(provider_id)
                        self.log_result("Create Test Email Provider", True, f"Created provider: {provider_id}")
                    else:
                        self.log_result("Create Test Email Provider", False, f"HTTP {response.status_code}", response.text)
                else:
                    self.log_result("Email Providers Available", True, f"Found {len(providers)} configured providers")
            else:
                self.log_result("GET /api/email-providers", False, f"HTTP {response.status_code}", response.text)
            
            return True
            
        except Exception as e:
            self.log_result("Email Providers Configuration", False, f"Exception: {str(e)}")
            return False
    
    def run_comprehensive_tests(self):
        """Run comprehensive campaign functionality tests"""
        print("🚀 Starting Campaign Functionality Tests")
        print("=" * 60)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return self.test_results
        
        # Test order matters - some tests depend on others
        tests = [
            ("Email Providers Configuration", self.test_email_providers_configuration),
            ("Campaign API Endpoints", self.test_campaign_api_endpoints),
            ("Follow-up Functionality", self.test_follow_up_functionality),
            ("Auto Email Responder", self.test_auto_email_responder),
            ("Template and Knowledge Base Integration", self.test_template_and_knowledge_base_integration)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                self.log_result(test_name, False, f"Test execution failed: {str(e)}")
        
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed!")
        else:
            print(f"⚠️  {total - passed} tests failed")
        
        return self.test_results

def main():
    """Main test execution"""
    tester = CampaignFunctionalityTester()
    results = tester.run_comprehensive_tests()
    
    # Print detailed results
    print("\n" + "=" * 60)
    print("📋 DETAILED TEST RESULTS")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"{status} {test_name}")
        if result['message']:
            print(f"   Message: {result['message']}")
        if result['details']:
            print(f"   Details: {result['details']}")
        print()
    
    return results

if __name__ == "__main__":
    main()