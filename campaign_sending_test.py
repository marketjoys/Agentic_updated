#!/usr/bin/env python3
"""
Email Campaign Sending Functionality Test for AI Email Responder
Tests the specific campaign sending functionality as requested
"""

import requests
import json
from datetime import datetime
import time

# Backend URL from environment
BACKEND_URL = "https://d91c1d61-d849-44ea-aabf-3847cd5b2bcc.preview.emergentagent.com"

class CampaignSendingTester:
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
    
    def test_authentication(self):
        """Test authentication with provided credentials"""
        try:
            login_data = {
                "username": "testuser",
                "password": "testpass123"
            }
            
            response = requests.post(f"{self.base_url}/api/auth/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                if 'access_token' in data:
                    self.auth_token = data['access_token']
                    self.log_result("Authentication", True, "Login successful")
                    return True
                else:
                    self.log_result("Authentication", False, "No access token in response", data)
                    return False
            else:
                self.log_result("Authentication", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_email_providers(self):
        """Test email provider configuration"""
        try:
            response = requests.get(f"{self.base_url}/api/email-providers")
            if response.status_code == 200:
                providers = response.json()
                if isinstance(providers, list) and len(providers) > 0:
                    # Check if providers have skip_connection_test flag
                    test_providers = [p for p in providers if p.get('skip_connection_test', False)]
                    self.log_result("Email Providers", True, 
                                  f"Found {len(providers)} providers, {len(test_providers)} with skip_connection_test")
                    return True
                else:
                    self.log_result("Email Providers", False, "No email providers found", providers)
                    return False
            else:
                self.log_result("Email Providers", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Email Providers", False, f"Exception: {str(e)}")
            return False
    
    def test_templates_retrieval(self):
        """Test template retrieval for campaigns"""
        try:
            response = requests.get(f"{self.base_url}/api/templates")
            if response.status_code == 200:
                templates = response.json()
                if isinstance(templates, list) and len(templates) > 0:
                    # Check template structure
                    template = templates[0]
                    required_fields = ['id', 'name', 'subject', 'content']
                    missing_fields = [field for field in required_fields if field not in template]
                    
                    if not missing_fields:
                        self.log_result("Templates Retrieval", True, 
                                      f"Found {len(templates)} templates with proper structure")
                        return True
                    else:
                        self.log_result("Templates Retrieval", False, 
                                      f"Templates missing fields: {missing_fields}", template)
                        return False
                else:
                    self.log_result("Templates Retrieval", False, "No templates found", templates)
                    return False
            else:
                self.log_result("Templates Retrieval", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Templates Retrieval", False, f"Exception: {str(e)}")
            return False
    
    def test_prospects_retrieval(self):
        """Test prospect retrieval for campaigns"""
        try:
            response = requests.get(f"{self.base_url}/api/prospects")
            if response.status_code == 200:
                prospects = response.json()
                if isinstance(prospects, list) and len(prospects) > 0:
                    # Check prospect structure
                    prospect = prospects[0]
                    required_fields = ['id', 'email', 'first_name']
                    missing_fields = [field for field in required_fields if field not in prospect]
                    
                    if not missing_fields:
                        self.log_result("Prospects Retrieval", True, 
                                      f"Found {len(prospects)} prospects with proper structure")
                        return True
                    else:
                        self.log_result("Prospects Retrieval", False, 
                                      f"Prospects missing fields: {missing_fields}", prospect)
                        return False
                else:
                    self.log_result("Prospects Retrieval", False, "No prospects found", prospects)
                    return False
            else:
                self.log_result("Prospects Retrieval", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Prospects Retrieval", False, f"Exception: {str(e)}")
            return False
    
    def test_campaign_creation(self):
        """Test campaign creation"""
        try:
            # Get templates first
            templates_response = requests.get(f"{self.base_url}/api/templates")
            if templates_response.status_code != 200:
                self.log_result("Campaign Creation", False, "Cannot get templates for campaign")
                return False
            
            templates = templates_response.json()
            if not templates:
                self.log_result("Campaign Creation", False, "No templates available for campaign")
                return False
            
            template_id = templates[0]['id']
            
            # Create campaign
            campaign_data = {
                "name": f"Test Campaign {int(time.time())}",
                "template_id": template_id,
                "list_ids": [],
                "max_emails": 100,
                "schedule": None
            }
            
            response = requests.post(f"{self.base_url}/api/campaigns", json=campaign_data)
            if response.status_code == 200:
                campaign = response.json()
                if 'id' in campaign:
                    self.campaign_id = campaign['id']
                    self.log_result("Campaign Creation", True, f"Created campaign with ID: {campaign['id']}")
                    return True
                else:
                    self.log_result("Campaign Creation", False, "No ID in campaign response", campaign)
                    return False
            else:
                self.log_result("Campaign Creation", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Campaign Creation", False, f"Exception: {str(e)}")
            return False
    
    def test_campaign_sending(self):
        """Test the critical campaign sending functionality"""
        try:
            if not hasattr(self, 'campaign_id'):
                self.log_result("Campaign Sending", False, "No campaign ID available for sending")
                return False
            
            # Prepare send request
            send_request = {
                "send_immediately": True,
                "email_provider_id": "",  # Use default provider
                "max_emails": 10,
                "schedule_type": "immediate",
                "start_time": None,
                "follow_up_enabled": True,
                "follow_up_intervals": [3, 7, 14],
                "follow_up_templates": []
            }
            
            response = requests.post(f"{self.base_url}/api/campaigns/{self.campaign_id}/send", 
                                   json=send_request)
            
            if response.status_code == 200:
                result = response.json()
                
                # Check response structure
                required_fields = ['campaign_id', 'status', 'total_sent', 'total_failed', 'email_results']
                missing_fields = [field for field in required_fields if field not in result]
                
                if missing_fields:
                    self.log_result("Campaign Sending", False, 
                                  f"Response missing fields: {missing_fields}", result)
                    return False
                
                # Check if emails were sent
                total_sent = result.get('total_sent', 0)
                total_failed = result.get('total_failed', 0)
                
                if total_sent > 0:
                    self.log_result("Campaign Sending", True, 
                                  f"Campaign sent successfully: {total_sent} emails sent, {total_failed} failed")
                    
                    # Check email results structure
                    if 'email_results' in result and len(result['email_results']) > 0:
                        email_result = result['email_results'][0]
                        email_fields = ['recipient', 'status', 'message', 'subject']
                        missing_email_fields = [field for field in email_fields if field not in email_result]
                        
                        if not missing_email_fields:
                            self.log_result("Email Results Structure", True, 
                                          "Email results have proper structure")
                        else:
                            self.log_result("Email Results Structure", False, 
                                          f"Email results missing fields: {missing_email_fields}")
                    
                    return True
                else:
                    self.log_result("Campaign Sending", False, 
                                  f"No emails sent: {total_sent} sent, {total_failed} failed", result)
                    return False
            else:
                self.log_result("Campaign Sending", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Campaign Sending", False, f"Exception: {str(e)}")
            return False
    
    def test_campaign_status(self):
        """Test campaign status after sending"""
        try:
            if not hasattr(self, 'campaign_id'):
                self.log_result("Campaign Status", False, "No campaign ID available for status check")
                return False
            
            response = requests.get(f"{self.base_url}/api/campaigns/{self.campaign_id}/status")
            if response.status_code == 200:
                status = response.json()
                
                required_fields = ['campaign_id', 'status', 'total_sent', 'total_failed']
                missing_fields = [field for field in required_fields if field not in status]
                
                if not missing_fields:
                    self.log_result("Campaign Status", True, 
                                  f"Campaign status: {status.get('status')}, sent: {status.get('total_sent')}")
                    return True
                else:
                    self.log_result("Campaign Status", False, 
                                  f"Status response missing fields: {missing_fields}", status)
                    return False
            else:
                self.log_result("Campaign Status", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Campaign Status", False, f"Exception: {str(e)}")
            return False
    
    def test_analytics_after_sending(self):
        """Test analytics endpoints after campaign sending"""
        try:
            # Test overall analytics
            response = requests.get(f"{self.base_url}/api/analytics")
            if response.status_code == 200:
                analytics = response.json()
                self.log_result("Overall Analytics", True, 
                              f"Analytics retrieved: {analytics.get('total_campaigns', 0)} campaigns")
            else:
                self.log_result("Overall Analytics", False, f"HTTP {response.status_code}", response.text)
                return False
            
            # Test campaign-specific analytics
            if hasattr(self, 'campaign_id'):
                response = requests.get(f"{self.base_url}/api/analytics/campaign/{self.campaign_id}")
                if response.status_code == 200:
                    campaign_analytics = response.json()
                    
                    analytics_fields = ['total_sent', 'total_failed', 'open_rate', 'reply_rate']
                    missing_fields = [field for field in analytics_fields if field not in campaign_analytics]
                    
                    if not missing_fields:
                        self.log_result("Campaign Analytics", True, 
                                      f"Campaign analytics: {campaign_analytics.get('total_sent')} sent, "
                                      f"{campaign_analytics.get('open_rate')}% open rate")
                        return True
                    else:
                        self.log_result("Campaign Analytics", False, 
                                      f"Analytics missing fields: {missing_fields}", campaign_analytics)
                        return False
                else:
                    self.log_result("Campaign Analytics", False, f"HTTP {response.status_code}", response.text)
                    return False
            else:
                self.log_result("Campaign Analytics", False, "No campaign ID for analytics test")
                return False
                
        except Exception as e:
            self.log_result("Analytics After Sending", False, f"Exception: {str(e)}")
            return False
    
    def test_database_operations(self):
        """Test database operations related to campaigns"""
        try:
            # Test campaigns retrieval
            response = requests.get(f"{self.base_url}/api/campaigns")
            if response.status_code == 200:
                campaigns = response.json()
                if isinstance(campaigns, list):
                    self.log_result("Database - Campaigns", True, f"Retrieved {len(campaigns)} campaigns")
                else:
                    self.log_result("Database - Campaigns", False, "Campaigns response not a list", campaigns)
                    return False
            else:
                self.log_result("Database - Campaigns", False, f"HTTP {response.status_code}", response.text)
                return False
            
            # Test real-time dashboard metrics
            response = requests.get(f"{self.base_url}/api/real-time/dashboard-metrics")
            if response.status_code == 200:
                metrics = response.json()
                if 'metrics' in metrics:
                    self.log_result("Database - Real-time Metrics", True, "Real-time metrics retrieved")
                    return True
                else:
                    self.log_result("Database - Real-time Metrics", False, "No metrics in response", metrics)
                    return False
            else:
                self.log_result("Database - Real-time Metrics", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Database Operations", False, f"Exception: {str(e)}")
            return False
    
    def run_campaign_sending_tests(self):
        """Run comprehensive campaign sending tests"""
        print("🚀 Starting Email Campaign Sending Functionality Tests")
        print("=" * 70)
        
        # Test order is important for campaign sending workflow
        tests = [
            ("Authentication", self.test_authentication),
            ("Email Providers Configuration", self.test_email_providers),
            ("Templates Retrieval", self.test_templates_retrieval),
            ("Prospects Retrieval", self.test_prospects_retrieval),
            ("Campaign Creation", self.test_campaign_creation),
            ("Campaign Sending (CRITICAL)", self.test_campaign_sending),
            ("Campaign Status", self.test_campaign_status),
            ("Analytics After Sending", self.test_analytics_after_sending),
            ("Database Operations", self.test_database_operations)
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
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All campaign sending tests passed!")
        else:
            print(f"⚠️  {total - passed} tests failed")
        
        return self.test_results

def main():
    """Main test execution"""
    tester = CampaignSendingTester()
    results = tester.run_campaign_sending_tests()
    
    # Print detailed results
    print("\n" + "=" * 70)
    print("📋 DETAILED CAMPAIGN SENDING TEST RESULTS")
    print("=" * 70)
    
    critical_tests = []
    other_tests = []
    
    for test_name, result in results.items():
        if "CRITICAL" in test_name or "Campaign Sending" in test_name:
            critical_tests.append((test_name, result))
        else:
            other_tests.append((test_name, result))
    
    # Show critical tests first
    if critical_tests:
        print("🔥 CRITICAL FUNCTIONALITY:")
        for test_name, result in critical_tests:
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            print(f"{status} {test_name}")
            if result['message']:
                print(f"   Message: {result['message']}")
            if result['details']:
                print(f"   Details: {result['details']}")
            print()
    
    # Show other tests
    if other_tests:
        print("📋 SUPPORTING FUNCTIONALITY:")
        for test_name, result in other_tests:
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