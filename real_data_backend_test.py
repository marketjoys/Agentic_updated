#!/usr/bin/env python3
"""
Real Data Backend Testing for AI Email Responder
Focus on testing with real Gmail credentials and real prospect data as requested in review
"""

import requests
import json
from datetime import datetime
import time
import os

# Get backend URL from frontend .env file
BACKEND_URL = "https://c7a1ce41-8b78-4aa9-b2bd-0db18addaca3.preview.emergentagent.com"
AUTH_TOKEN = "test_token_12345"

class RealDataTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.auth_token = AUTH_TOKEN
        self.headers = {"Authorization": f"Bearer {self.auth_token}"}
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
    
    def test_real_gmail_provider_integration(self):
        """Test Gmail provider integration with real credentials"""
        try:
            # Check if Gmail provider exists with real credentials
            response = requests.get(f"{self.base_url}/api/email-providers", headers=self.headers)
            if response.status_code != 200:
                self.log_result("Gmail Provider Check", False, f"HTTP {response.status_code}", response.text)
                return False
            
            providers = response.json()
            gmail_provider = None
            
            for provider in providers:
                if provider.get('provider_type') == 'gmail' or 'gmail' in provider.get('email_address', '').lower():
                    gmail_provider = provider
                    break
            
            if not gmail_provider:
                # Create Gmail provider with real credentials
                gmail_data = {
                    "name": "Real Gmail Provider",
                    "provider_type": "gmail",
                    "email_address": "kasargovinda@gmail.com",
                    "display_name": "Govinda Kasar",
                    "smtp_host": "smtp.gmail.com",
                    "smtp_port": 587,
                    "smtp_username": "kasargovinda@gmail.com",
                    "smtp_password": "urvsdfvrzfabvykm",
                    "smtp_use_tls": True,
                    "imap_host": "imap.gmail.com",
                    "imap_port": 993,
                    "imap_username": "kasargovinda@gmail.com",
                    "imap_password": "urvsdfvrzfabvykm",
                    "daily_send_limit": 500,
                    "hourly_send_limit": 50,
                    "is_default": True,
                    "skip_connection_test": True
                }
                
                response = requests.post(f"{self.base_url}/api/email-providers", json=gmail_data, headers=self.headers)
                if response.status_code != 200:
                    self.log_result("Gmail Provider Creation", False, f"HTTP {response.status_code}", response.text)
                    return False
                
                gmail_provider = response.json()
                self.created_resources['email_providers'].append(gmail_provider['id'])
                self.log_result("Gmail Provider Creation", True, f"Created Gmail provider with real credentials")
            else:
                self.log_result("Gmail Provider Check", True, f"Found existing Gmail provider: {gmail_provider['email_address']}")
            
            # Test connection to Gmail provider
            provider_id = gmail_provider['id']
            response = requests.post(f"{self.base_url}/api/email-providers/{provider_id}/test", headers=self.headers)
            if response.status_code == 200:
                self.log_result("Gmail Connection Test", True, "Gmail provider connection successful")
            else:
                self.log_result("Gmail Connection Test", False, f"HTTP {response.status_code}", response.text)
            
            return True
            
        except Exception as e:
            self.log_result("Gmail Provider Integration", False, f"Exception: {str(e)}")
            return False
    
    def test_real_prospect_management(self):
        """Test prospect management with real prospect emails"""
        try:
            # Create real prospects as mentioned in review request
            real_prospects = [
                {
                    "email": "amits.joys@gmail.com",
                    "first_name": "Amit",
                    "last_name": "Singh",
                    "company": "Tech Solutions Inc",
                    "job_title": "Software Engineer",
                    "industry": "Technology",
                    "phone": "+1-555-0101"
                },
                {
                    "email": "ronsmith.joys@gmail.com", 
                    "first_name": "Ron",
                    "last_name": "Smith",
                    "company": "Digital Marketing Pro",
                    "job_title": "Marketing Manager",
                    "industry": "Marketing",
                    "phone": "+1-555-0102"
                }
            ]
            
            created_prospects = []
            
            for prospect_data in real_prospects:
                response = requests.post(f"{self.base_url}/api/prospects", json=prospect_data, headers=self.headers)
                if response.status_code != 200:
                    self.log_result(f"Real Prospect CREATE ({prospect_data['email']})", False, f"HTTP {response.status_code}", response.text)
                    continue
                
                created_prospect = response.json()
                if 'id' not in created_prospect:
                    self.log_result(f"Real Prospect CREATE ({prospect_data['email']})", False, "No ID in response", created_prospect)
                    continue
                
                prospect_id = created_prospect['id']
                self.created_resources['prospects'].append(prospect_id)
                created_prospects.append(created_prospect)
                self.log_result(f"Real Prospect CREATE ({prospect_data['email']})", True, f"Created prospect with ID: {prospect_id}")
            
            if len(created_prospects) == 0:
                self.log_result("Real Prospect Management", False, "No real prospects were created")
                return False
            
            # Verify prospects can be retrieved
            response = requests.get(f"{self.base_url}/api/prospects", headers=self.headers)
            if response.status_code != 200:
                self.log_result("Real Prospect READ", False, f"HTTP {response.status_code}", response.text)
                return False
            
            all_prospects = response.json()
            real_prospect_emails = [p['email'] for p in created_prospects]
            found_real_prospects = [p for p in all_prospects if p['email'] in real_prospect_emails]
            
            self.log_result("Real Prospect READ", True, f"Retrieved {len(found_real_prospects)} real prospects from database")
            
            return True
            
        except Exception as e:
            self.log_result("Real Prospect Management", False, f"Exception: {str(e)}")
            return False
    
    def test_real_campaign_with_gmail_sending(self):
        """Test campaign creation and sending with real Gmail provider and real prospects"""
        try:
            # First create a personalized template for real data
            template_data = {
                "name": "Real Data Welcome Template",
                "subject": "Welcome {{first_name}} from {{company}}!",
                "content": """
                <html>
                <body>
                    <p>Hello {{first_name}},</p>
                    <p>Thank you for your interest in our AI Email Responder service!</p>
                    <p>We noticed you work at {{company}} as a {{job_title}}, and we believe our solution can help streamline your email communications in the {{industry}} industry.</p>
                    <p>This is a test email sent through our real Gmail integration to verify our system is working correctly.</p>
                    <p>Best regards,<br>
                    The AI Email Responder Team</p>
                </body>
                </html>
                """,
                "type": "initial",
                "placeholders": ["first_name", "last_name", "company", "job_title", "industry"]
            }
            
            response = requests.post(f"{self.base_url}/api/templates", json=template_data, headers=self.headers)
            if response.status_code != 200:
                self.log_result("Real Template CREATE", False, f"HTTP {response.status_code}", response.text)
                return False
            
            created_template = response.json()
            template_id = created_template['id']
            self.created_resources['templates'].append(template_id)
            self.log_result("Real Template CREATE", True, f"Created personalized template with ID: {template_id}")
            
            # Get real prospects
            response = requests.get(f"{self.base_url}/api/prospects", headers=self.headers)
            if response.status_code != 200:
                self.log_result("Get Real Prospects", False, f"HTTP {response.status_code}", response.text)
                return False
            
            prospects = response.json()
            real_prospects = [p for p in prospects if p['email'] in ['amits.joys@gmail.com', 'ronsmith.joys@gmail.com']]
            
            if len(real_prospects) == 0:
                self.log_result("Get Real Prospects", False, "No real prospects found for campaign")
                return False
            
            self.log_result("Get Real Prospects", True, f"Found {len(real_prospects)} real prospects for campaign")
            
            # Create campaign with real data
            campaign_data = {
                "name": "Real Data Test Campaign",
                "template_id": template_id,
                "list_ids": [],  # Use all prospects
                "max_emails": 10,
                "schedule": None
            }
            
            response = requests.post(f"{self.base_url}/api/campaigns", json=campaign_data, headers=self.headers)
            if response.status_code != 200:
                self.log_result("Real Campaign CREATE", False, f"HTTP {response.status_code}", response.text)
                return False
            
            created_campaign = response.json()
            campaign_id = created_campaign['id']
            self.created_resources['campaigns'].append(campaign_id)
            self.log_result("Real Campaign CREATE", True, f"Created real data campaign with ID: {campaign_id}")
            
            # Send campaign with Gmail provider
            send_request = {
                "send_immediately": True,
                "max_emails": 2,  # Limit to 2 for testing
                "schedule_type": "immediate",
                "follow_up_enabled": False,
                "email_provider_id": ""  # Use default Gmail provider
            }
            
            response = requests.post(f"{self.base_url}/api/campaigns/{campaign_id}/send", 
                                   json=send_request, headers=self.headers)
            if response.status_code != 200:
                self.log_result("Real Campaign SEND", False, f"HTTP {response.status_code}", response.text)
                return False
            
            send_result = response.json()
            if 'total_sent' not in send_result:
                self.log_result("Real Campaign SEND", False, "Invalid send result format", send_result)
                return False
            
            total_sent = send_result.get('total_sent', 0)
            total_failed = send_result.get('total_failed', 0)
            
            if total_sent > 0:
                self.log_result("Real Campaign SEND", True, f"Successfully sent {total_sent} emails via Gmail, {total_failed} failed")
            else:
                self.log_result("Real Campaign SEND", False, f"No emails sent: {total_sent} sent, {total_failed} failed", send_result)
            
            # Verify template personalization worked
            if 'email_results' in send_result:
                for email_result in send_result['email_results']:
                    if 'subject' in email_result:
                        if '{{' not in email_result['subject']:
                            self.log_result("Template Personalization", True, f"Template personalized correctly: {email_result['subject']}")
                        else:
                            self.log_result("Template Personalization", False, f"Template not personalized: {email_result['subject']}")
                        break
            
            return True
            
        except Exception as e:
            self.log_result("Real Campaign with Gmail Sending", False, f"Exception: {str(e)}")
            return False
    
    def test_real_time_data_updates(self):
        """Test real-time data updates in database"""
        try:
            # Get initial campaign count
            response = requests.get(f"{self.base_url}/api/campaigns", headers=self.headers)
            if response.status_code != 200:
                self.log_result("Initial Campaign Count", False, f"HTTP {response.status_code}", response.text)
                return False
            
            initial_campaigns = response.json()
            initial_count = len(initial_campaigns)
            
            # Create a new campaign
            template_response = requests.get(f"{self.base_url}/api/templates", headers=self.headers)
            if template_response.status_code != 200 or not template_response.json():
                self.log_result("Get Template for Real-time Test", False, "No templates available")
                return False
            
            template_id = template_response.json()[0]['id']
            
            campaign_data = {
                "name": "Real-time Update Test Campaign",
                "template_id": template_id,
                "list_ids": [],
                "max_emails": 50,
                "schedule": None
            }
            
            response = requests.post(f"{self.base_url}/api/campaigns", json=campaign_data, headers=self.headers)
            if response.status_code != 200:
                self.log_result("Real-time Campaign CREATE", False, f"HTTP {response.status_code}", response.text)
                return False
            
            created_campaign = response.json()
            campaign_id = created_campaign['id']
            self.created_resources['campaigns'].append(campaign_id)
            
            # Immediately check if the campaign appears in the list
            response = requests.get(f"{self.base_url}/api/campaigns", headers=self.headers)
            if response.status_code != 200:
                self.log_result("Real-time Campaign READ", False, f"HTTP {response.status_code}", response.text)
                return False
            
            updated_campaigns = response.json()
            updated_count = len(updated_campaigns)
            
            if updated_count == initial_count + 1:
                self.log_result("Real-time Data Updates", True, f"Campaign count updated immediately: {initial_count} -> {updated_count}")
            else:
                self.log_result("Real-time Data Updates", False, f"Campaign count not updated: {initial_count} -> {updated_count}")
            
            # Test campaign status update after sending
            send_request = {
                "send_immediately": True,
                "max_emails": 1,
                "schedule_type": "immediate",
                "follow_up_enabled": False
            }
            
            response = requests.post(f"{self.base_url}/api/campaigns/{campaign_id}/send", 
                                   json=send_request, headers=self.headers)
            if response.status_code == 200:
                # Check if campaign status was updated
                response = requests.get(f"{self.base_url}/api/campaigns", headers=self.headers)
                if response.status_code == 200:
                    campaigns = response.json()
                    test_campaign = next((c for c in campaigns if c['id'] == campaign_id), None)
                    if test_campaign and test_campaign.get('status') == 'sent':
                        self.log_result("Real-time Status Updates", True, "Campaign status updated to 'sent' after sending")
                    else:
                        self.log_result("Real-time Status Updates", False, f"Campaign status not updated: {test_campaign.get('status') if test_campaign else 'not found'}")
            
            return True
            
        except Exception as e:
            self.log_result("Real-time Data Updates", False, f"Exception: {str(e)}")
            return False
    
    def test_analytics_with_real_data(self):
        """Test analytics tracking with real sent emails"""
        try:
            # Get overall analytics
            response = requests.get(f"{self.base_url}/api/analytics", headers=self.headers)
            if response.status_code != 200:
                self.log_result("Overall Analytics", False, f"HTTP {response.status_code}", response.text)
                return False
            
            analytics = response.json()
            required_fields = ['total_campaigns', 'total_emails_sent', 'total_prospects']
            
            for field in required_fields:
                if field not in analytics:
                    self.log_result("Analytics Data Structure", False, f"Missing field: {field}", analytics)
                    return False
            
            self.log_result("Overall Analytics", True, f"Analytics retrieved: {analytics['total_campaigns']} campaigns, {analytics['total_emails_sent']} emails sent")
            
            # Get campaign-specific analytics
            response = requests.get(f"{self.base_url}/api/campaigns", headers=self.headers)
            if response.status_code == 200:
                campaigns = response.json()
                if campaigns:
                    campaign_id = campaigns[0]['id']
                    
                    response = requests.get(f"{self.base_url}/api/analytics/campaign/{campaign_id}", headers=self.headers)
                    if response.status_code == 200:
                        campaign_analytics = response.json()
                        if 'total_sent' in campaign_analytics:
                            self.log_result("Campaign Analytics", True, f"Campaign analytics retrieved: {campaign_analytics['total_sent']} sent")
                        else:
                            self.log_result("Campaign Analytics", False, "Missing total_sent in campaign analytics", campaign_analytics)
                    else:
                        self.log_result("Campaign Analytics", False, f"HTTP {response.status_code}", response.text)
            
            # Test real-time dashboard metrics
            response = requests.get(f"{self.base_url}/api/real-time/dashboard-metrics", headers=self.headers)
            if response.status_code == 200:
                metrics = response.json()
                if 'metrics' in metrics and 'overview' in metrics['metrics']:
                    overview = metrics['metrics']['overview']
                    self.log_result("Real-time Dashboard Metrics", True, f"Dashboard metrics: {overview.get('total_emails_sent', 0)} emails sent today")
                else:
                    self.log_result("Real-time Dashboard Metrics", False, "Invalid metrics structure", metrics)
            else:
                self.log_result("Real-time Dashboard Metrics", False, f"HTTP {response.status_code}", response.text)
            
            return True
            
        except Exception as e:
            self.log_result("Analytics with Real Data", False, f"Exception: {str(e)}")
            return False
    
    def cleanup_resources(self):
        """Clean up created test resources"""
        print("\n🧹 Cleaning up real data test resources...")
        
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
        
        # Delete prospects (real prospect emails - be careful)
        for prospect_id in self.created_resources['prospects']:
            try:
                response = requests.delete(f"{self.base_url}/api/prospects/{prospect_id}", headers=self.headers)
                if response.status_code == 200:
                    print(f"   ✅ Deleted prospect {prospect_id}")
                else:
                    print(f"   ⚠️ Failed to delete prospect {prospect_id}: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Error deleting prospect {prospect_id}: {str(e)}")
    
    def run_real_data_tests(self):
        """Run comprehensive real data tests as requested in review"""
        print("🚀 Starting AI Email Responder Real Data Tests")
        print("Focus: Gmail Integration, Real Prospects, Campaign Sending, Real-time Updates, Analytics")
        print("=" * 90)
        
        tests = [
            ("Gmail Provider Integration", self.test_real_gmail_provider_integration),
            ("Real Prospect Management", self.test_real_prospect_management),
            ("Real Campaign with Gmail Sending", self.test_real_campaign_with_gmail_sending),
            ("Real-time Data Updates", self.test_real_time_data_updates),
            ("Analytics with Real Data", self.test_analytics_with_real_data)
        ]
        
        passed = 0
        total = len(tests)
        critical_failures = []
        
        for test_name, test_func in tests:
            print(f"\n🧪 Running: {test_name}")
            try:
                if test_func():
                    passed += 1
                else:
                    critical_failures.append(test_name)
            except Exception as e:
                self.log_result(test_name, False, f"Test execution failed: {str(e)}")
                critical_failures.append(test_name)
        
        print("\n" + "=" * 90)
        print(f"📊 Real Data Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All real data tests passed!")
        else:
            print(f"⚠️  {total - passed} tests failed")
            if critical_failures:
                print(f"🚨 Critical failures in: {', '.join(critical_failures)}")
        
        # Cleanup
        self.cleanup_resources()
        
        return self.test_results, critical_failures

def main():
    """Main test execution for real data testing"""
    tester = RealDataTester()
    results, critical_failures = tester.run_real_data_tests()
    
    # Print detailed results
    print("\n" + "=" * 90)
    print("📋 DETAILED REAL DATA TEST RESULTS")
    print("=" * 90)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"{status} {test_name}")
        if result['message']:
            print(f"   Message: {result['message']}")
        if result['details']:
            print(f"   Details: {result['details']}")
        print()
    
    return results, critical_failures

if __name__ == "__main__":
    main()