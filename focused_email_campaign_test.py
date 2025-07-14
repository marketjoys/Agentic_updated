#!/usr/bin/env python3
"""
Focused Email Campaign Backend Testing - Tests Only Implemented Endpoints
Tests the actual backend implementation as it exists
"""

import requests
import json
import time
from datetime import datetime

# Get backend URL from frontend .env file
BACKEND_URL = "http://localhost:8001"

class FocusedEmailCampaignTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.test_results = {}
        self.auth_token = None
    
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
    
    def test_health_check(self):
        """Test API health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'status' in data and data['status'] == 'healthy':
                    self.log_result("Health Check", True, "API is healthy", data)
                    return True
                else:
                    self.log_result("Health Check", False, "Invalid health response", data)
                    return False
            else:
                self.log_result("Health Check", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Health Check", False, f"Connection failed: {str(e)}")
            return False
    
    def test_authentication(self):
        """Test authentication with provided credentials"""
        try:
            # Test login with correct credentials
            login_data = {
                "username": "testuser",
                "password": "testpass123"
            }
            
            response = requests.post(f"{self.base_url}/api/auth/login", json=login_data, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'access_token' in data:
                    self.auth_token = data['access_token']
                    self.log_result("Authentication Login", True, "Successfully authenticated with provided credentials")
                else:
                    self.log_result("Authentication Login", False, "No access token in response", data)
                    return False
            else:
                self.log_result("Authentication Login", False, f"HTTP {response.status_code}", response.text)
                return False
            
            # Test user profile
            response = requests.get(f"{self.base_url}/api/auth/me", timeout=10)
            if response.status_code == 200:
                profile_data = response.json()
                self.log_result("Authentication Profile", True, f"User profile retrieved: {profile_data.get('username', 'unknown')}")
            else:
                self.log_result("Authentication Profile", False, f"HTTP {response.status_code}", response.text)
            
            # Test token refresh
            response = requests.post(f"{self.base_url}/api/auth/refresh", timeout=10)
            if response.status_code == 200:
                self.log_result("Authentication Refresh", True, "Token refresh successful")
            else:
                self.log_result("Authentication Refresh", False, f"HTTP {response.status_code}", response.text)
            
            return True
            
        except Exception as e:
            self.log_result("Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_email_provider_endpoints(self):
        """Test email provider CRUD operations (implemented endpoints)"""
        try:
            # Test GET email providers
            response = requests.get(f"{self.base_url}/api/email-providers", timeout=10)
            if response.status_code != 200:
                self.log_result("Email Providers GET", False, f"HTTP {response.status_code}", response.text)
                return False
            
            providers = response.json()
            if not isinstance(providers, list):
                self.log_result("Email Providers GET", False, "Response is not a list", providers)
                return False
            
            self.log_result("Email Providers GET", True, f"Retrieved {len(providers)} email providers")
            
            # Test POST - Create email provider
            provider_data = {
                "name": "Test Gmail Provider",
                "provider_type": "gmail",
                "email_address": "test@gmail.com",
                "display_name": "Test Gmail Account",
                "smtp_host": "smtp.gmail.com",
                "smtp_port": 587,
                "smtp_username": "test@gmail.com",
                "smtp_password": "test_app_password",
                "smtp_use_tls": True,
                "imap_host": "imap.gmail.com",
                "imap_port": 993,
                "imap_username": "test@gmail.com",
                "imap_password": "test_app_password",
                "daily_send_limit": 500,
                "hourly_send_limit": 50,
                "is_default": False,
                "skip_connection_test": True
            }
            
            response = requests.post(f"{self.base_url}/api/email-providers", json=provider_data, timeout=10)
            if response.status_code != 200:
                self.log_result("Email Providers POST", False, f"HTTP {response.status_code}", response.text)
                return False
            
            created_provider = response.json()
            if 'id' not in created_provider:
                self.log_result("Email Providers POST", False, "No ID in response", created_provider)
                return False
            
            provider_id = created_provider['id']
            self.log_result("Email Providers POST", True, f"Created provider with ID: {provider_id}")
            
            # Test PUT - Update email provider
            update_data = {
                "name": "Updated Test Gmail Provider",
                "provider_type": "gmail",
                "email_address": "test@gmail.com",
                "display_name": "Updated Test Gmail Account",
                "smtp_host": "smtp.gmail.com",
                "smtp_port": 587,
                "smtp_username": "test@gmail.com",
                "smtp_password": "updated_password",
                "smtp_use_tls": True,
                "imap_host": "imap.gmail.com",
                "imap_port": 993,
                "imap_username": "test@gmail.com",
                "imap_password": "updated_password",
                "daily_send_limit": 600,
                "hourly_send_limit": 60,
                "is_default": False,
                "skip_connection_test": True
            }
            
            response = requests.put(f"{self.base_url}/api/email-providers/{provider_id}", json=update_data, timeout=10)
            if response.status_code != 200:
                self.log_result("Email Providers PUT", False, f"HTTP {response.status_code}", response.text)
                return False
            
            self.log_result("Email Providers PUT", True, "Provider updated successfully")
            
            # Test connection test
            response = requests.post(f"{self.base_url}/api/email-providers/{provider_id}/test", timeout=10)
            if response.status_code != 200:
                self.log_result("Email Provider Connection Test", False, f"HTTP {response.status_code}", response.text)
                return False
            
            test_result = response.json()
            self.log_result("Email Provider Connection Test", True, "Connection test completed", test_result)
            
            # Test set as default
            response = requests.post(f"{self.base_url}/api/email-providers/{provider_id}/set-default", timeout=10)
            if response.status_code != 200:
                self.log_result("Email Provider Set Default", False, f"HTTP {response.status_code}", response.text)
                return False
            
            self.log_result("Email Provider Set Default", True, "Provider set as default successfully")
            
            # Test DELETE
            response = requests.delete(f"{self.base_url}/api/email-providers/{provider_id}", timeout=10)
            if response.status_code != 200:
                self.log_result("Email Providers DELETE", False, f"HTTP {response.status_code}", response.text)
                return False
            
            self.log_result("Email Providers DELETE", True, "Provider deleted successfully")
            
            return True
            
        except Exception as e:
            self.log_result("Email Provider Endpoints", False, f"Exception: {str(e)}")
            return False
    
    def test_template_endpoints(self):
        """Test template management endpoints (GET only implemented)"""
        try:
            # Test GET templates
            response = requests.get(f"{self.base_url}/api/templates", timeout=10)
            if response.status_code != 200:
                self.log_result("Templates GET", False, f"HTTP {response.status_code}", response.text)
                return False
            
            templates = response.json()
            if not isinstance(templates, list):
                self.log_result("Templates GET", False, "Response is not a list", templates)
                return False
            
            self.log_result("Templates GET", True, f"Retrieved {len(templates)} templates")
            
            # Verify template structure and personalization placeholders
            if templates:
                template = templates[0]
                required_fields = ['id', 'name', 'subject', 'content', 'type']
                missing_fields = [field for field in required_fields if field not in template]
                
                if missing_fields:
                    self.log_result("Template Structure", False, f"Missing fields: {missing_fields}", template)
                    return False
                
                # Check for personalization placeholders
                has_placeholders = '{{' in template.get('subject', '') or '{{' in template.get('content', '')
                if has_placeholders:
                    self.log_result("Template Personalization", True, "Templates contain personalization placeholders")
                else:
                    self.log_result("Template Personalization", False, "No personalization placeholders found")
                
                self.log_result("Template Structure", True, "Template structure is valid")
            
            return True
            
        except Exception as e:
            self.log_result("Template Endpoints", False, f"Exception: {str(e)}")
            return False
    
    def test_prospect_endpoints(self):
        """Test prospect management endpoints (GET only implemented)"""
        try:
            # Test GET prospects
            response = requests.get(f"{self.base_url}/api/prospects", timeout=10)
            if response.status_code != 200:
                self.log_result("Prospects GET", False, f"HTTP {response.status_code}", response.text)
                return False
            
            prospects = response.json()
            if not isinstance(prospects, list):
                self.log_result("Prospects GET", False, "Response is not a list", prospects)
                return False
            
            self.log_result("Prospects GET", True, f"Retrieved {len(prospects)} prospects")
            
            # Verify prospect structure
            if prospects:
                prospect = prospects[0]
                required_fields = ['id', 'email', 'first_name', 'last_name', 'company']
                missing_fields = [field for field in required_fields if field not in prospect]
                
                if missing_fields:
                    self.log_result("Prospect Structure", False, f"Missing fields: {missing_fields}", prospect)
                    return False
                
                self.log_result("Prospect Structure", True, "Prospect structure is valid")
            
            # Test with pagination parameters
            response = requests.get(f"{self.base_url}/api/prospects?skip=0&limit=10", timeout=10)
            if response.status_code == 200:
                self.log_result("Prospects Pagination", True, "Pagination parameters accepted")
            else:
                self.log_result("Prospects Pagination", False, f"HTTP {response.status_code}", response.text)
            
            return True
            
        except Exception as e:
            self.log_result("Prospect Endpoints", False, f"Exception: {str(e)}")
            return False
    
    def test_campaign_endpoints(self):
        """Test campaign management endpoints"""
        try:
            # Test GET campaigns
            response = requests.get(f"{self.base_url}/api/campaigns", timeout=10)
            if response.status_code != 200:
                self.log_result("Campaigns GET", False, f"HTTP {response.status_code}", response.text)
                return False
            
            campaigns = response.json()
            if not isinstance(campaigns, list):
                self.log_result("Campaigns GET", False, "Response is not a list", campaigns)
                return False
            
            self.log_result("Campaigns GET", True, f"Retrieved {len(campaigns)} campaigns")
            
            # Test POST - Create campaign
            campaign_data = {
                "name": "Test Email Campaign",
                "template_id": "1",
                "list_ids": ["1", "2"],
                "email_provider_id": "1",
                "max_emails": 1000,
                "schedule_type": "immediate",
                "follow_up_enabled": True,
                "follow_up_intervals": [3, 7, 14],
                "follow_up_templates": ["2", "3"]
            }
            
            response = requests.post(f"{self.base_url}/api/campaigns", json=campaign_data, timeout=10)
            if response.status_code != 200:
                self.log_result("Campaigns POST", False, f"HTTP {response.status_code}", response.text)
                return False
            
            created_campaign = response.json()
            if 'id' not in created_campaign:
                self.log_result("Campaigns POST", False, "No ID in response", created_campaign)
                return False
            
            self.log_result("Campaigns POST", True, f"Created campaign with ID: {created_campaign['id']}")
            
            # Verify campaign structure
            required_fields = ['id', 'name', 'status', 'prospect_count', 'max_emails']
            missing_fields = [field for field in required_fields if field not in created_campaign]
            
            if missing_fields:
                self.log_result("Campaign Structure", False, f"Missing fields: {missing_fields}", created_campaign)
                return False
            
            self.log_result("Campaign Structure", True, "Campaign structure is valid")
            
            return True
            
        except Exception as e:
            self.log_result("Campaign Endpoints", False, f"Exception: {str(e)}")
            return False
    
    def test_analytics_endpoints(self):
        """Test analytics endpoints"""
        try:
            # Test campaign analytics
            campaign_id = "1"  # Using mock campaign ID
            response = requests.get(f"{self.base_url}/api/analytics/campaign/{campaign_id}", timeout=10)
            if response.status_code != 200:
                self.log_result("Campaign Analytics", False, f"HTTP {response.status_code}", response.text)
                return False
            
            analytics_data = response.json()
            required_fields = ['total_sent', 'total_failed', 'total_opened', 'total_replied', 'open_rate', 'reply_rate']
            missing_fields = [field for field in required_fields if field not in analytics_data]
            
            if missing_fields:
                self.log_result("Campaign Analytics", False, f"Missing fields: {missing_fields}", analytics_data)
                return False
            
            self.log_result("Campaign Analytics", True, f"Analytics retrieved - Open Rate: {analytics_data.get('open_rate', 0)}%, Reply Rate: {analytics_data.get('reply_rate', 0)}%")
            
            # Test real-time dashboard metrics
            response = requests.get(f"{self.base_url}/api/real-time/dashboard-metrics", timeout=10)
            if response.status_code != 200:
                self.log_result("Dashboard Metrics", False, f"HTTP {response.status_code}", response.text)
                return False
            
            metrics_data = response.json()
            if 'metrics' not in metrics_data:
                self.log_result("Dashboard Metrics", False, "No metrics in response", metrics_data)
                return False
            
            self.log_result("Dashboard Metrics", True, "Real-time dashboard metrics retrieved successfully")
            
            return True
            
        except Exception as e:
            self.log_result("Analytics Endpoints", False, f"Exception: {str(e)}")
            return False
    
    def test_additional_endpoints(self):
        """Test additional endpoints like lists and intents"""
        try:
            # Test GET lists
            response = requests.get(f"{self.base_url}/api/lists", timeout=10)
            if response.status_code != 200:
                self.log_result("Lists GET", False, f"HTTP {response.status_code}", response.text)
                return False
            
            lists = response.json()
            if not isinstance(lists, list):
                self.log_result("Lists GET", False, "Response is not a list", lists)
                return False
            
            self.log_result("Lists GET", True, f"Retrieved {len(lists)} lists")
            
            # Test GET intents
            response = requests.get(f"{self.base_url}/api/intents", timeout=10)
            if response.status_code != 200:
                self.log_result("Intents GET", False, f"HTTP {response.status_code}", response.text)
                return False
            
            intents = response.json()
            if not isinstance(intents, list):
                self.log_result("Intents GET", False, "Response is not a list", intents)
                return False
            
            self.log_result("Intents GET", True, f"Retrieved {len(intents)} intents")
            
            return True
            
        except Exception as e:
            self.log_result("Additional Endpoints", False, f"Exception: {str(e)}")
            return False
    
    def run_focused_tests(self):
        """Run focused tests on implemented endpoints only"""
        print("🚀 Starting Focused Email Campaign Backend Tests")
        print("Testing only the endpoints that are actually implemented")
        print("=" * 70)
        
        # Test order
        tests = [
            ("Health Check", self.test_health_check),
            ("Authentication", self.test_authentication),
            ("Email Provider Endpoints", self.test_email_provider_endpoints),
            ("Template Endpoints", self.test_template_endpoints),
            ("Prospect Endpoints", self.test_prospect_endpoints),
            ("Campaign Endpoints", self.test_campaign_endpoints),
            ("Analytics Endpoints", self.test_analytics_endpoints),
            ("Additional Endpoints", self.test_additional_endpoints)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🧪 Running: {test_name}")
            print("-" * 50)
            try:
                if test_func():
                    passed += 1
                time.sleep(0.5)  # Brief pause between tests
            except Exception as e:
                self.log_result(test_name, False, f"Test execution failed: {str(e)}")
        
        print("\n" + "=" * 70)
        print(f"📊 Test Results: {passed}/{total} test categories passed")
        
        # Count individual test results
        individual_passed = sum(1 for result in self.test_results.values() if result['success'])
        individual_total = len(self.test_results)
        
        print(f"📋 Individual Tests: {individual_passed}/{individual_total} tests passed")
        
        if passed == total:
            print("🎉 All implemented backend functionality tests passed!")
        else:
            print(f"⚠️  {total - passed} test categories had issues")
        
        return self.test_results

def main():
    """Main test execution"""
    tester = FocusedEmailCampaignTester()
    results = tester.run_focused_tests()
    
    # Print summary
    print("\n" + "=" * 70)
    print("📋 SUMMARY OF BACKEND EMAIL CAMPAIGN FUNCTIONALITY")
    print("=" * 70)
    
    # Categorize results
    passed_tests = []
    failed_tests = []
    
    for test_name, result in results.items():
        if result['success']:
            passed_tests.append(test_name)
        else:
            failed_tests.append((test_name, result['message']))
    
    print(f"\n✅ WORKING FUNCTIONALITY ({len(passed_tests)} tests):")
    for test in passed_tests:
        print(f"  - {test}")
    
    if failed_tests:
        print(f"\n❌ ISSUES FOUND ({len(failed_tests)} tests):")
        for test_name, message in failed_tests:
            print(f"  - {test_name}: {message}")
    
    # Overall assessment
    success_rate = len(passed_tests) / len(results) * 100
    print(f"\n📊 Overall Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("✅ Backend email campaign functionality is working well")
        return 0
    else:
        print("⚠️  Backend has significant issues that need attention")
        return 1

if __name__ == "__main__":
    exit(main())