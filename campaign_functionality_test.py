#!/usr/bin/env python3
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
BACKEND_URL = "https://0267b990-fd14-417f-9297-46270e013278.preview.emergentagent.com"

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