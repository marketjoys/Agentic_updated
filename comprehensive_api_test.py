#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for AI Email Responder
Tests all CRUD operations and email sending functionality as requested
"""

import requests
import json
import time
from datetime import datetime
import sys

# Backend URL from the review request
BACKEND_URL = "https://b9312b09-0291-4341-83e9-28393511b75a.preview.emergentagent.com"

class ComprehensiveAPITester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.auth_token = None
        self.test_results = {}
        self.created_resources = {
            'templates': [],
            'prospects': [],
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
        if details and not success:
            print(f"   Details: {details}")
    
    def authenticate(self):
        """Authenticate with the API"""
        try:
            login_data = {
                "username": "testuser",
                "password": "testpass123"
            }
            
            response = requests.post(f"{self.base_url}/api/auth/login", json=login_data)
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
    
    def test_template_crud(self):
        """Test Template Management CRUD Operations"""
        print("\n🧪 Testing Template Management CRUD Operations")
        
        # 1. CREATE Template
        template_data = {
            "name": "Test Welcome Template",
            "subject": "Welcome to our service, {{first_name}}!",
            "content": "<p>Hello {{first_name}},</p><p>Welcome to our service! We're excited to work with {{company}}.</p><p>Best regards,<br>The Team</p>",
            "type": "initial",
            "placeholders": ["first_name", "last_name", "company"]
        }
        
        try:
            response = requests.post(f"{self.base_url}/api/templates", 
                                   json=template_data, 
                                   headers=self.get_headers())
            
            if response.status_code == 200:
                created_template = response.json()
                if 'id' in created_template:
                    template_id = created_template['id']
                    self.created_resources['templates'].append(template_id)
                    self.log_result("Template CREATE", True, f"Created template with ID: {template_id}")
                else:
                    self.log_result("Template CREATE", False, "No ID in response", created_template)
                    return False
            else:
                self.log_result("Template CREATE", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Template CREATE", False, f"Exception: {str(e)}")
            return False
        
        # 2. READ Templates
        try:
            response = requests.get(f"{self.base_url}/api/templates", headers=self.get_headers())
            if response.status_code == 200:
                templates = response.json()
                if isinstance(templates, list):
                    self.log_result("Template READ", True, f"Retrieved {len(templates)} templates")
                else:
                    self.log_result("Template READ", False, "Response is not a list", templates)
                    return False
            else:
                self.log_result("Template READ", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Template READ", False, f"Exception: {str(e)}")
            return False
        
        # 3. UPDATE Template
        try:
            update_data = {
                "name": "Updated Welcome Template",
                "subject": "Updated: Welcome to our service, {{first_name}}!",
                "content": template_data["content"],
                "type": "initial",
                "placeholders": ["first_name", "last_name", "company"]
            }
            
            response = requests.put(f"{self.base_url}/api/templates/{template_id}", 
                                  json=update_data, 
                                  headers=self.get_headers())
            
            if response.status_code == 200:
                self.log_result("Template UPDATE", True, "Template updated successfully")
            else:
                self.log_result("Template UPDATE", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Template UPDATE", False, f"Exception: {str(e)}")
            return False
        
        # 4. DELETE Template
        try:
            response = requests.delete(f"{self.base_url}/api/templates/{template_id}", 
                                     headers=self.get_headers())
            
            if response.status_code == 200:
                self.log_result("Template DELETE", True, "Template deleted successfully")
                self.created_resources['templates'].remove(template_id)
            else:
                self.log_result("Template DELETE", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Template DELETE", False, f"Exception: {str(e)}")
            return False
        
        return True
    
    def test_prospect_crud(self):
        """Test Prospect Management CRUD Operations"""
        print("\n🧪 Testing Prospect Management CRUD Operations")
        
        # 1. CREATE Prospect
        unique_timestamp = int(time.time())
        prospect_data = {
            "email": f"john.doe.{unique_timestamp}@techcorp.com",
            "first_name": "John",
            "last_name": "Doe",
            "company": "TechCorp Inc",
            "job_title": "CEO",
            "industry": "Technology",
            "phone": "+1-555-0123"
        }
        
        try:
            response = requests.post(f"{self.base_url}/api/prospects", 
                                   json=prospect_data, 
                                   headers=self.get_headers())
            
            if response.status_code == 200:
                created_prospect = response.json()
                if 'id' in created_prospect:
                    prospect_id = created_prospect['id']
                    self.created_resources['prospects'].append(prospect_id)
                    self.log_result("Prospect CREATE", True, f"Created prospect with ID: {prospect_id}")
                else:
                    self.log_result("Prospect CREATE", False, "No ID in response", created_prospect)
                    return False
            else:
                self.log_result("Prospect CREATE", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Prospect CREATE", False, f"Exception: {str(e)}")
            return False
        
        # 2. READ Prospects
        try:
            response = requests.get(f"{self.base_url}/api/prospects", headers=self.get_headers())
            if response.status_code == 200:
                prospects = response.json()
                if isinstance(prospects, list):
                    self.log_result("Prospect READ", True, f"Retrieved {len(prospects)} prospects")
                else:
                    self.log_result("Prospect READ", False, "Response is not a list", prospects)
                    return False
            else:
                self.log_result("Prospect READ", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Prospect READ", False, f"Exception: {str(e)}")
            return False
        
        # 3. UPDATE Prospect
        try:
            update_data = {
                "email": prospect_data["email"],
                "first_name": "John Updated",
                "last_name": "Doe",
                "company": "TechCorp Inc Updated",
                "job_title": "Senior CEO",
                "industry": "Technology",
                "phone": "+1-555-0123"
            }
            
            response = requests.put(f"{self.base_url}/api/prospects/{prospect_id}", 
                                  json=update_data, 
                                  headers=self.get_headers())
            
            if response.status_code == 200:
                self.log_result("Prospect UPDATE", True, "Prospect updated successfully")
            else:
                self.log_result("Prospect UPDATE", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Prospect UPDATE", False, f"Exception: {str(e)}")
            return False
        
        # 4. CSV Upload
        try:
            csv_content = f"""email,first_name,last_name,company,job_title,industry
sarah.johnson.{unique_timestamp}@innovate.com,Sarah,Johnson,Innovate Solutions,CTO,Technology
mike.wilson.{unique_timestamp}@startup.io,Mike,Wilson,Startup.io,Founder,Technology
lisa.chen.{unique_timestamp}@enterprise.com,Lisa,Chen,Enterprise Corp,VP Sales,Enterprise"""
            
            response = requests.post(f"{self.base_url}/api/prospects/upload", 
                                   params={"file_content": csv_content},
                                   headers=self.get_headers())
            
            if response.status_code == 200:
                result = response.json()
                self.log_result("CSV Upload", True, f"Uploaded prospects: {result.get('message', 'Success')}")
            else:
                self.log_result("CSV Upload", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("CSV Upload", False, f"Exception: {str(e)}")
            return False
        
        # 5. DELETE Prospect
        try:
            response = requests.delete(f"{self.base_url}/api/prospects/{prospect_id}", 
                                     headers=self.get_headers())
            
            if response.status_code == 200:
                self.log_result("Prospect DELETE", True, "Prospect deleted successfully")
                self.created_resources['prospects'].remove(prospect_id)
            else:
                self.log_result("Prospect DELETE", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Prospect DELETE", False, f"Exception: {str(e)}")
            return False
        
        return True
    
    def test_campaign_crud(self):
        """Test Campaign Management CRUD Operations"""
        print("\n🧪 Testing Campaign Management CRUD Operations")
        
        # First, get a template ID for the campaign
        try:
            response = requests.get(f"{self.base_url}/api/templates", headers=self.get_headers())
            if response.status_code == 200:
                templates = response.json()
                if templates and len(templates) > 0:
                    template_id = templates[0]['id']
                else:
                    self.log_result("Campaign CRUD Setup", False, "No templates available for campaign")
                    return False
            else:
                self.log_result("Campaign CRUD Setup", False, f"Failed to get templates: HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Campaign CRUD Setup", False, f"Exception getting templates: {str(e)}")
            return False
        
        # 1. CREATE Campaign
        campaign_data = {
            "name": "Test Email Campaign",
            "template_id": template_id,
            "list_ids": [],
            "max_emails": 100,
            "schedule": None
        }
        
        try:
            response = requests.post(f"{self.base_url}/api/campaigns", 
                                   json=campaign_data, 
                                   headers=self.get_headers())
            
            if response.status_code == 200:
                created_campaign = response.json()
                if 'id' in created_campaign:
                    campaign_id = created_campaign['id']
                    self.created_resources['campaigns'].append(campaign_id)
                    self.log_result("Campaign CREATE", True, f"Created campaign with ID: {campaign_id}")
                else:
                    self.log_result("Campaign CREATE", False, "No ID in response", created_campaign)
                    return False
            else:
                self.log_result("Campaign CREATE", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Campaign CREATE", False, f"Exception: {str(e)}")
            return False
        
        # 2. READ Campaigns
        try:
            response = requests.get(f"{self.base_url}/api/campaigns", headers=self.get_headers())
            if response.status_code == 200:
                campaigns = response.json()
                if isinstance(campaigns, list):
                    self.log_result("Campaign READ", True, f"Retrieved {len(campaigns)} campaigns")
                else:
                    self.log_result("Campaign READ", False, "Response is not a list", campaigns)
                    return False
            else:
                self.log_result("Campaign READ", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Campaign READ", False, f"Exception: {str(e)}")
            return False
        
        # 3. UPDATE Campaign
        try:
            update_data = {
                "name": "Updated Test Email Campaign",
                "template_id": template_id,
                "list_ids": [],
                "max_emails": 200,
                "schedule": None
            }
            
            response = requests.put(f"{self.base_url}/api/campaigns/{campaign_id}", 
                                  json=update_data, 
                                  headers=self.get_headers())
            
            if response.status_code == 200:
                self.log_result("Campaign UPDATE", True, "Campaign updated successfully")
            else:
                self.log_result("Campaign UPDATE", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Campaign UPDATE", False, f"Exception: {str(e)}")
            return False
        
        # 4. EMAIL SENDING (CRITICAL TEST)
        try:
            send_request = {
                "send_immediately": True,
                "email_provider_id": "",  # Use default provider
                "max_emails": 5,
                "schedule_type": "immediate",
                "start_time": None,
                "follow_up_enabled": False,
                "follow_up_intervals": [],
                "follow_up_templates": []
            }
            
            response = requests.post(f"{self.base_url}/api/campaigns/{campaign_id}/send", 
                                   json=send_request, 
                                   headers=self.get_headers())
            
            if response.status_code == 200:
                result = response.json()
                if 'total_sent' in result or 'status' in result:
                    self.log_result("Campaign EMAIL SENDING", True, f"Email sending completed: {result.get('message', 'Success')}")
                else:
                    self.log_result("Campaign EMAIL SENDING", False, "Invalid response format", result)
                    return False
            else:
                self.log_result("Campaign EMAIL SENDING", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Campaign EMAIL SENDING", False, f"Exception: {str(e)}")
            return False
        
        # 5. DELETE Campaign
        try:
            response = requests.delete(f"{self.base_url}/api/campaigns/{campaign_id}", 
                                     headers=self.get_headers())
            
            if response.status_code == 200:
                self.log_result("Campaign DELETE", True, "Campaign deleted successfully")
                self.created_resources['campaigns'].remove(campaign_id)
            else:
                self.log_result("Campaign DELETE", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Campaign DELETE", False, f"Exception: {str(e)}")
            return False
        
        return True
    
    def test_analytics_system(self):
        """Test Analytics System"""
        print("\n🧪 Testing Analytics System")
        
        # 1. Overall Analytics Dashboard
        try:
            response = requests.get(f"{self.base_url}/api/analytics", headers=self.get_headers())
            if response.status_code == 200:
                analytics = response.json()
                expected_fields = ['total_campaigns', 'total_emails_sent', 'total_prospects']
                
                missing_fields = [field for field in expected_fields if field not in analytics]
                if missing_fields:
                    self.log_result("Analytics Dashboard", False, f"Missing fields: {missing_fields}", analytics)
                    return False
                else:
                    self.log_result("Analytics Dashboard", True, "Analytics dashboard data retrieved successfully")
            else:
                self.log_result("Analytics Dashboard", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Analytics Dashboard", False, f"Exception: {str(e)}")
            return False
        
        # 2. Campaign-specific Analytics
        try:
            # Get a campaign ID first
            response = requests.get(f"{self.base_url}/api/campaigns", headers=self.get_headers())
            if response.status_code == 200:
                campaigns = response.json()
                if campaigns and len(campaigns) > 0:
                    campaign_id = campaigns[0]['id']
                    
                    # Test campaign analytics
                    response = requests.get(f"{self.base_url}/api/analytics/campaign/{campaign_id}", 
                                          headers=self.get_headers())
                    
                    if response.status_code == 200:
                        campaign_analytics = response.json()
                        expected_fields = ['total_sent', 'total_opened', 'total_replied', 'open_rate', 'reply_rate']
                        
                        missing_fields = [field for field in expected_fields if field not in campaign_analytics]
                        if missing_fields:
                            self.log_result("Campaign Analytics", False, f"Missing fields: {missing_fields}", campaign_analytics)
                            return False
                        else:
                            self.log_result("Campaign Analytics", True, f"Campaign analytics retrieved for campaign {campaign_id}")
                    else:
                        self.log_result("Campaign Analytics", False, f"HTTP {response.status_code}", response.text)
                        return False
                else:
                    self.log_result("Campaign Analytics", False, "No campaigns available for analytics test")
                    return False
            else:
                self.log_result("Campaign Analytics Setup", False, f"Failed to get campaigns: HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Campaign Analytics", False, f"Exception: {str(e)}")
            return False
        
        return True
    
    def test_email_providers(self):
        """Test Email Provider Management (should still work)"""
        print("\n🧪 Testing Email Provider Management")
        
        # 1. READ Email Providers
        try:
            response = requests.get(f"{self.base_url}/api/email-providers", headers=self.get_headers())
            if response.status_code == 200:
                providers = response.json()
                if isinstance(providers, list):
                    self.log_result("Email Providers READ", True, f"Retrieved {len(providers)} email providers")
                else:
                    self.log_result("Email Providers READ", False, "Response is not a list", providers)
                    return False
            else:
                self.log_result("Email Providers READ", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Email Providers READ", False, f"Exception: {str(e)}")
            return False
        
        return True
    
    def run_comprehensive_tests(self):
        """Run all comprehensive tests"""
        print("🚀 Starting Comprehensive AI Email Responder API Tests")
        print("=" * 70)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return self.test_results
        
        # Test order matters for dependencies
        tests = [
            ("Template Management CRUD", self.test_template_crud),
            ("Prospect Management CRUD", self.test_prospect_crud),
            ("Campaign Management CRUD", self.test_campaign_crud),
            ("Analytics System", self.test_analytics_system),
            ("Email Providers", self.test_email_providers)
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
        
        print("\n" + "=" * 70)
        print(f"📊 Test Results: {passed}/{total} test suites passed")
        
        if passed == total:
            print("🎉 All test suites passed!")
        else:
            print(f"⚠️  {total - passed} test suites failed")
        
        return self.test_results

def main():
    """Main test execution"""
    tester = ComprehensiveAPITester()
    results = tester.run_comprehensive_tests()
    
    # Print detailed results
    print("\n" + "=" * 70)
    print("📋 DETAILED TEST RESULTS")
    print("=" * 70)
    
    passed_tests = 0
    failed_tests = 0
    
    for test_name, result in results.items():
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"{status} {test_name}")
        if result['message']:
            print(f"   Message: {result['message']}")
        if result['details'] and not result['success']:
            print(f"   Details: {result['details']}")
        
        if result['success']:
            passed_tests += 1
        else:
            failed_tests += 1
        print()
    
    print(f"📊 FINAL SUMMARY: {passed_tests} passed, {failed_tests} failed")
    
    return results

if __name__ == "__main__":
    main()