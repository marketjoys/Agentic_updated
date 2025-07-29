#!/usr/bin/env python3
"""
Comprehensive Email Campaign Functionality Testing for AI Email Responder
Tests the complete email campaign workflow as requested in the review
"""

import requests
import json
import time
from datetime import datetime
import sys

# Get backend URL from frontend .env file
BACKEND_URL = "http://localhost:8001"

class EmailCampaignTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.test_results = {}
        self.auth_token = None
        self.created_resources = {
            'email_providers': [],
            'templates': [],
            'prospects': [],
            'campaigns': []
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
        """Authenticate with the system"""
        try:
            login_data = {
                "username": "testuser",
                "password": "testpass123"
            }
            
            response = requests.post(f"{self.base_url}/api/auth/login", json=login_data, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'access_token' in data:
                    self.auth_token = data['access_token']
                    self.log_result("Authentication", True, "Successfully authenticated")
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
    
    def test_email_provider_management(self):
        """Test CRUD operations for email providers"""
        try:
            # Test READ - Get existing email providers
            response = requests.get(f"{self.base_url}/api/email-providers", timeout=10)
            if response.status_code != 200:
                self.log_result("Email Provider READ", False, f"HTTP {response.status_code}", response.text)
                return False
            
            providers = response.json()
            if not isinstance(providers, list):
                self.log_result("Email Provider READ", False, "Response is not a list", providers)
                return False
            
            self.log_result("Email Provider READ", True, f"Retrieved {len(providers)} email providers")
            
            # Test CREATE - Create new email provider
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
                self.log_result("Email Provider CREATE", False, f"HTTP {response.status_code}", response.text)
                return False
            
            created_provider = response.json()
            if 'id' not in created_provider:
                self.log_result("Email Provider CREATE", False, "No ID in response", created_provider)
                return False
            
            provider_id = created_provider['id']
            self.created_resources['email_providers'].append(provider_id)
            self.log_result("Email Provider CREATE", True, f"Created provider with ID: {provider_id}")
            
            # Test UPDATE - Update email provider
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
                self.log_result("Email Provider UPDATE", False, f"HTTP {response.status_code}", response.text)
                return False
            
            self.log_result("Email Provider UPDATE", True, "Provider updated successfully")
            
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
            
            return True
            
        except Exception as e:
            self.log_result("Email Provider Management", False, f"Exception: {str(e)}")
            return False
    
    def test_template_management(self):
        """Test email template creation and management"""
        try:
            # Test READ - Get existing templates
            response = requests.get(f"{self.base_url}/api/templates", timeout=10)
            if response.status_code != 200:
                self.log_result("Template READ", False, f"HTTP {response.status_code}", response.text)
                return False
            
            templates = response.json()
            if not isinstance(templates, list):
                self.log_result("Template READ", False, "Response is not a list", templates)
                return False
            
            self.log_result("Template READ", True, f"Retrieved {len(templates)} templates")
            
            # Test CREATE - Create new template with personalization
            template_data = {
                "name": "Campaign Welcome Template",
                "subject": "Welcome to our service, {{first_name}}!",
                "content": """
                <html>
                <body>
                    <h2>Hello {{first_name}},</h2>
                    <p>Welcome to our service! We're excited to have {{company}} as part of our community.</p>
                    <p>As a {{job_title}} at {{company}}, we believe you'll find great value in our platform.</p>
                    <p>Best regards,<br>The Team</p>
                </body>
                </html>
                """,
                "type": "initial",
                "placeholders": ["first_name", "last_name", "company", "job_title"]
            }
            
            response = requests.post(f"{self.base_url}/api/templates", json=template_data, timeout=10)
            if response.status_code != 200:
                self.log_result("Template CREATE", False, f"HTTP {response.status_code}", response.text)
                return False
            
            created_template = response.json()
            if 'id' not in created_template:
                self.log_result("Template CREATE", False, "No ID in response", created_template)
                return False
            
            template_id = created_template['id']
            self.created_resources['templates'].append(template_id)
            self.log_result("Template CREATE", True, f"Created template with ID: {template_id}")
            
            # Test CREATE - Follow-up template
            followup_template_data = {
                "name": "Follow-up Day 3",
                "subject": "Quick follow-up for {{company}}",
                "content": """
                <html>
                <body>
                    <p>Hi {{first_name}},</p>
                    <p>I wanted to follow up on my previous email about our service for {{company}}.</p>
                    <p>Have you had a chance to review the information I sent?</p>
                    <p>Best regards,<br>The Team</p>
                </body>
                </html>
                """,
                "type": "follow_up",
                "placeholders": ["first_name", "company"]
            }
            
            response = requests.post(f"{self.base_url}/api/templates", json=followup_template_data, timeout=10)
            if response.status_code != 200:
                self.log_result("Follow-up Template CREATE", False, f"HTTP {response.status_code}", response.text)
                return False
            
            followup_template = response.json()
            followup_template_id = followup_template['id']
            self.created_resources['templates'].append(followup_template_id)
            self.log_result("Follow-up Template CREATE", True, f"Created follow-up template with ID: {followup_template_id}")
            
            return True
            
        except Exception as e:
            self.log_result("Template Management", False, f"Exception: {str(e)}")
            return False
    
    def test_prospect_management(self):
        """Test prospect list management"""
        try:
            # Test READ - Get existing prospects
            response = requests.get(f"{self.base_url}/api/prospects", timeout=10)
            if response.status_code != 200:
                self.log_result("Prospect READ", False, f"HTTP {response.status_code}", response.text)
                return False
            
            prospects = response.json()
            if not isinstance(prospects, list):
                self.log_result("Prospect READ", False, "Response is not a list", prospects)
                return False
            
            self.log_result("Prospect READ", True, f"Retrieved {len(prospects)} prospects")
            
            # Test CREATE - Add new prospects for campaign testing
            prospect_data = [
                {
                    "email": "john.smith@techcorp.com",
                    "first_name": "John",
                    "last_name": "Smith",
                    "company": "TechCorp Solutions",
                    "job_title": "CEO",
                    "industry": "Technology"
                },
                {
                    "email": "sarah.johnson@innovate.com",
                    "first_name": "Sarah",
                    "last_name": "Johnson",
                    "company": "Innovate Inc",
                    "job_title": "CTO",
                    "industry": "Software"
                },
                {
                    "email": "mike.wilson@startup.io",
                    "first_name": "Mike",
                    "last_name": "Wilson",
                    "company": "Startup.io",
                    "job_title": "Founder",
                    "industry": "Startup"
                }
            ]
            
            created_prospect_ids = []
            for prospect in prospect_data:
                response = requests.post(f"{self.base_url}/api/prospects", json=prospect, timeout=10)
                if response.status_code == 200:
                    created_prospect = response.json()
                    if 'id' in created_prospect:
                        created_prospect_ids.append(created_prospect['id'])
                        self.created_resources['prospects'].append(created_prospect['id'])
            
            if len(created_prospect_ids) == len(prospect_data):
                self.log_result("Prospect CREATE", True, f"Created {len(created_prospect_ids)} prospects for campaign testing")
            else:
                self.log_result("Prospect CREATE", False, f"Only created {len(created_prospect_ids)} out of {len(prospect_data)} prospects")
                return False
            
            return True
            
        except Exception as e:
            self.log_result("Prospect Management", False, f"Exception: {str(e)}")
            return False
    
    def test_campaign_creation(self):
        """Test creating new email campaigns"""
        try:
            # Get available templates and prospects
            templates_response = requests.get(f"{self.base_url}/api/templates", timeout=10)
            if templates_response.status_code != 200:
                self.log_result("Campaign Creation - Get Templates", False, "Failed to get templates")
                return False
            
            templates = templates_response.json()
            if not templates:
                self.log_result("Campaign Creation - Get Templates", False, "No templates available")
                return False
            
            prospects_response = requests.get(f"{self.base_url}/api/prospects", timeout=10)
            if prospects_response.status_code != 200:
                self.log_result("Campaign Creation - Get Prospects", False, "Failed to get prospects")
                return False
            
            prospects = prospects_response.json()
            if not prospects:
                self.log_result("Campaign Creation - Get Prospects", False, "No prospects available")
                return False
            
            # Get email providers
            providers_response = requests.get(f"{self.base_url}/api/email-providers", timeout=10)
            if providers_response.status_code != 200:
                self.log_result("Campaign Creation - Get Providers", False, "Failed to get email providers")
                return False
            
            providers = providers_response.json()
            if not providers:
                self.log_result("Campaign Creation - Get Providers", False, "No email providers available")
                return False
            
            # Create campaign
            campaign_data = {
                "name": "Q1 2025 Product Launch Campaign",
                "template_id": templates[0]['id'],
                "list_ids": ["1", "2"],  # Using mock list IDs
                "email_provider_id": providers[0]['id'],
                "max_emails": 1000,
                "schedule_type": "immediate",
                "follow_up_enabled": True,
                "follow_up_intervals": [3, 7, 14],
                "follow_up_templates": [templates[1]['id'] if len(templates) > 1 else templates[0]['id']]
            }
            
            response = requests.post(f"{self.base_url}/api/campaigns", json=campaign_data, timeout=10)
            if response.status_code != 200:
                self.log_result("Campaign CREATE", False, f"HTTP {response.status_code}", response.text)
                return False
            
            created_campaign = response.json()
            if 'id' not in created_campaign:
                self.log_result("Campaign CREATE", False, "No ID in response", created_campaign)
                return False
            
            campaign_id = created_campaign['id']
            self.created_resources['campaigns'].append(campaign_id)
            self.log_result("Campaign CREATE", True, f"Created campaign with ID: {campaign_id}")
            
            # Test campaign validation
            invalid_campaign_data = {
                "name": "",  # Invalid empty name
                "template_id": "invalid_template_id",
                "max_emails": -1  # Invalid negative number
            }
            
            response = requests.post(f"{self.base_url}/api/campaigns", json=invalid_campaign_data, timeout=10)
            if response.status_code == 200:
                self.log_result("Campaign Validation", False, "Invalid campaign data was accepted")
                return False
            else:
                self.log_result("Campaign Validation", True, "Invalid campaign data properly rejected")
            
            return True
            
        except Exception as e:
            self.log_result("Campaign Creation", False, f"Exception: {str(e)}")
            return False
    
    def test_email_sending(self):
        """Test the actual email sending functionality through campaigns"""
        try:
            # Get campaigns
            response = requests.get(f"{self.base_url}/api/campaigns", timeout=10)
            if response.status_code != 200:
                self.log_result("Email Sending - Get Campaigns", False, f"HTTP {response.status_code}", response.text)
                return False
            
            campaigns = response.json()
            if not campaigns:
                self.log_result("Email Sending - Get Campaigns", False, "No campaigns available")
                return False
            
            campaign_id = campaigns[0]['id']
            
            # Test email sending endpoint
            send_data = {
                "campaign_id": campaign_id,
                "test_mode": True,  # Use test mode to avoid actual email sending
                "recipient_limit": 5
            }
            
            response = requests.post(f"{self.base_url}/api/campaigns/{campaign_id}/send", json=send_data, timeout=30)
            if response.status_code != 200:
                self.log_result("Email Sending", False, f"HTTP {response.status_code}", response.text)
                return False
            
            send_result = response.json()
            expected_fields = ['total_sent', 'total_failed', 'campaign_id']
            
            for field in expected_fields:
                if field not in send_result:
                    self.log_result("Email Sending", False, f"Missing field in response: {field}", send_result)
                    return False
            
            self.log_result("Email Sending", True, f"Email sending completed - Sent: {send_result.get('total_sent', 0)}, Failed: {send_result.get('total_failed', 0)}")
            
            # Test email sending status check
            response = requests.get(f"{self.base_url}/api/campaigns/{campaign_id}/status", timeout=10)
            if response.status_code == 200:
                status_data = response.json()
                self.log_result("Email Sending Status", True, f"Campaign status: {status_data.get('status', 'unknown')}")
            else:
                self.log_result("Email Sending Status", False, f"HTTP {response.status_code}", response.text)
            
            return True
            
        except Exception as e:
            self.log_result("Email Sending", False, f"Exception: {str(e)}")
            return False
    
    def test_analytics(self):
        """Test campaign performance tracking"""
        try:
            # Get campaigns for analytics testing
            response = requests.get(f"{self.base_url}/api/campaigns", timeout=10)
            if response.status_code != 200:
                self.log_result("Analytics - Get Campaigns", False, f"HTTP {response.status_code}", response.text)
                return False
            
            campaigns = response.json()
            if not campaigns:
                self.log_result("Analytics - Get Campaigns", False, "No campaigns available")
                return False
            
            campaign_id = campaigns[0]['id']
            
            # Test campaign analytics
            response = requests.get(f"{self.base_url}/api/analytics/campaign/{campaign_id}", timeout=10)
            if response.status_code != 200:
                self.log_result("Campaign Analytics", False, f"HTTP {response.status_code}", response.text)
                return False
            
            analytics_data = response.json()
            expected_fields = ['total_sent', 'total_failed', 'total_opened', 'total_replied', 'open_rate', 'reply_rate']
            
            for field in expected_fields:
                if field not in analytics_data:
                    self.log_result("Campaign Analytics", False, f"Missing field in analytics: {field}", analytics_data)
                    return False
            
            self.log_result("Campaign Analytics", True, f"Analytics retrieved - Open Rate: {analytics_data.get('open_rate', 0)}%, Reply Rate: {analytics_data.get('reply_rate', 0)}%")
            
            # Test overall analytics
            response = requests.get(f"{self.base_url}/api/analytics", timeout=10)
            if response.status_code == 200:
                overall_analytics = response.json()
                self.log_result("Overall Analytics", True, "Overall analytics retrieved successfully")
            else:
                self.log_result("Overall Analytics", False, f"HTTP {response.status_code}", response.text)
            
            return True
            
        except Exception as e:
            self.log_result("Analytics", False, f"Exception: {str(e)}")
            return False
    
    def cleanup_resources(self):
        """Clean up created test resources"""
        try:
            # Delete created campaigns
            for campaign_id in self.created_resources['campaigns']:
                try:
                    requests.delete(f"{self.base_url}/api/campaigns/{campaign_id}", timeout=10)
                except:
                    pass
            
            # Delete created email providers
            for provider_id in self.created_resources['email_providers']:
                try:
                    requests.delete(f"{self.base_url}/api/email-providers/{provider_id}", timeout=10)
                except:
                    pass
            
            # Delete created templates
            for template_id in self.created_resources['templates']:
                try:
                    requests.delete(f"{self.base_url}/api/templates/{template_id}", timeout=10)
                except:
                    pass
            
            # Delete created prospects
            for prospect_id in self.created_resources['prospects']:
                try:
                    requests.delete(f"{self.base_url}/api/prospects/{prospect_id}", timeout=10)
                except:
                    pass
            
            self.log_result("Cleanup", True, "Test resources cleaned up")
            
        except Exception as e:
            self.log_result("Cleanup", False, f"Exception during cleanup: {str(e)}")
    
    def run_email_campaign_tests(self):
        """Run complete email campaign functionality tests"""
        print("🚀 Starting Email Campaign Functionality Tests")
        print("=" * 70)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed with tests")
            return self.test_results
        
        # Test order matters for campaign workflow
        tests = [
            ("Email Provider Management", self.test_email_provider_management),
            ("Template Management", self.test_template_management),
            ("Prospect Management", self.test_prospect_management),
            ("Campaign Creation", self.test_campaign_creation),
            ("Email Sending", self.test_email_sending),
            ("Analytics", self.test_analytics)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🧪 Running: {test_name}")
            print("-" * 50)
            try:
                if test_func():
                    passed += 1
                time.sleep(1)  # Brief pause between tests
            except Exception as e:
                self.log_result(test_name, False, f"Test execution failed: {str(e)}")
        
        # Cleanup resources
        print(f"\n🧹 Cleaning up test resources...")
        self.cleanup_resources()
        
        print("\n" + "=" * 70)
        print(f"📊 Test Results: {passed}/{total} test categories passed")
        
        # Count individual test results
        individual_passed = sum(1 for result in self.test_results.values() if result['success'])
        individual_total = len(self.test_results)
        
        print(f"📋 Individual Tests: {individual_passed}/{individual_total} tests passed")
        
        if passed == total:
            print("🎉 All email campaign functionality tests passed!")
        else:
            print(f"⚠️  {total - passed} test categories had issues")
        
        return self.test_results

def main():
    """Main test execution"""
    tester = EmailCampaignTester()
    results = tester.run_email_campaign_tests()
    
    # Print detailed results
    print("\n" + "=" * 70)
    print("📋 DETAILED TEST RESULTS")
    print("=" * 70)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"{status} {test_name}")
        if result['message']:
            print(f"   Message: {result['message']}")
        if result['details']:
            print(f"   Details: {result['details']}")
        print()
    
    # Summary of failed tests
    failed_tests = [name for name, result in results.items() if not result['success']]
    if failed_tests:
        print("\n❌ FAILED TESTS:")
        for test_name in failed_tests:
            result = results[test_name]
            print(f"  - {test_name}: {result['message']}")
    
    return results

if __name__ == "__main__":
    main()