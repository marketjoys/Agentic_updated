#!/usr/bin/env python3
"""
Email Sending Functionality Testing for AI Email Responder
Tests the newly implemented email sending features as requested
"""

import requests
import json
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "http://localhost:8001"

class EmailSendingTester:
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
    
    def authenticate(self):
        """Authenticate with the backend"""
        try:
            auth_data = {
                "username": "testuser",
                "password": "testpass123"
            }
            
            response = requests.post(f"{self.base_url}/api/auth/login", json=auth_data)
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
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
    
    def test_campaign_email_sending(self):
        """Test POST /api/campaigns/{id}/send endpoint"""
        try:
            # First get available campaigns
            response = requests.get(f"{self.base_url}/api/campaigns", headers=self.get_headers())
            if response.status_code != 200:
                self.log_result("Get Campaigns for Sending", False, f"HTTP {response.status_code}", response.text)
                return False
            
            campaigns = response.json()
            if not campaigns:
                self.log_result("Get Campaigns for Sending", False, "No campaigns available")
                return False
            
            campaign_id = campaigns[0]["id"]
            
            # Test email sending
            send_request = {
                "campaign_id": campaign_id,
                "send_immediately": True,
                "email_provider_id": "1",
                "max_emails": 100,
                "schedule_type": "immediate",
                "follow_up_enabled": True,
                "follow_up_intervals": [3, 7, 14],
                "follow_up_templates": []
            }
            
            response = requests.post(f"{self.base_url}/api/campaigns/{campaign_id}/send", 
                                   json=send_request, headers=self.get_headers())
            
            if response.status_code != 200:
                self.log_result("Campaign Email Sending", False, f"HTTP {response.status_code}", response.text)
                return False
            
            result = response.json()
            
            # Verify response structure
            required_fields = ["campaign_id", "status", "total_sent", "total_failed", "total_prospects", "email_results"]
            for field in required_fields:
                if field not in result:
                    self.log_result("Campaign Email Sending", False, f"Missing field: {field}", result)
                    return False
            
            # Verify email results contain personalization
            if result["email_results"]:
                first_result = result["email_results"][0]
                if "personalized_subject" not in first_result:
                    self.log_result("Campaign Email Sending", False, "No personalized_subject in email results", first_result)
                    return False
                
                # Check if personalization worked (should not contain {{}} placeholders)
                if "{{" in first_result["personalized_subject"]:
                    self.log_result("Campaign Email Sending", False, "Personalization failed - placeholders still present", first_result["personalized_subject"])
                    return False
            
            self.log_result("Campaign Email Sending", True, 
                           f"Campaign sent successfully: {result['total_sent']} sent, {result['total_failed']} failed")
            return True
            
        except Exception as e:
            self.log_result("Campaign Email Sending", False, f"Exception: {str(e)}")
            return False
    
    def test_campaign_status(self):
        """Test GET /api/campaigns/{id}/status endpoint"""
        try:
            # Get available campaigns
            response = requests.get(f"{self.base_url}/api/campaigns", headers=self.get_headers())
            if response.status_code != 200:
                self.log_result("Get Campaigns for Status", False, f"HTTP {response.status_code}", response.text)
                return False
            
            campaigns = response.json()
            if not campaigns:
                self.log_result("Get Campaigns for Status", False, "No campaigns available")
                return False
            
            campaign_id = campaigns[0]["id"]
            
            # Test campaign status
            response = requests.get(f"{self.base_url}/api/campaigns/{campaign_id}/status", headers=self.get_headers())
            
            if response.status_code != 200:
                self.log_result("Campaign Status", False, f"HTTP {response.status_code}", response.text)
                return False
            
            status_data = response.json()
            
            # Verify response structure
            required_fields = ["campaign_id", "status", "total_sent", "total_failed", "total_prospects"]
            for field in required_fields:
                if field not in status_data:
                    self.log_result("Campaign Status", False, f"Missing field: {field}", status_data)
                    return False
            
            self.log_result("Campaign Status", True, 
                           f"Status retrieved: {status_data['status']}, {status_data['total_sent']} sent")
            return True
            
        except Exception as e:
            self.log_result("Campaign Status", False, f"Exception: {str(e)}")
            return False
    
    def test_template_crud(self):
        """Test POST, PUT, DELETE /api/templates endpoints"""
        try:
            # Test CREATE template
            template_data = {
                "name": "Test Email Template",
                "subject": "Hello {{first_name}} from {{company}}!",
                "content": """
                <html>
                <body>
                    <h2>Hello {{first_name}},</h2>
                    <p>We're excited to connect with {{company}}!</p>
                    <p>As a {{job_title}}, you might be interested in our solution.</p>
                    <p>Best regards,<br>The Team</p>
                </body>
                </html>
                """,
                "type": "initial",
                "placeholders": ["first_name", "company", "job_title"]
            }
            
            response = requests.post(f"{self.base_url}/api/templates", json=template_data, headers=self.get_headers())
            if response.status_code != 200:
                self.log_result("Template CREATE", False, f"HTTP {response.status_code}", response.text)
                return False
            
            created_template = response.json()
            if "id" not in created_template:
                self.log_result("Template CREATE", False, "No ID in response", created_template)
                return False
            
            template_id = created_template["id"]
            self.log_result("Template CREATE", True, f"Template created with ID: {template_id}")
            
            # Test UPDATE template
            updated_data = {
                "name": "Updated Test Template",
                "subject": "Updated: Hello {{first_name}} from {{company}}!",
                "content": template_data["content"],
                "type": "follow_up",
                "placeholders": ["first_name", "company", "job_title"]
            }
            
            response = requests.put(f"{self.base_url}/api/templates/{template_id}", 
                                  json=updated_data, headers=self.get_headers())
            if response.status_code != 200:
                self.log_result("Template UPDATE", False, f"HTTP {response.status_code}", response.text)
                return False
            
            self.log_result("Template UPDATE", True, "Template updated successfully")
            
            # Test DELETE template
            response = requests.delete(f"{self.base_url}/api/templates/{template_id}", headers=self.get_headers())
            if response.status_code != 200:
                self.log_result("Template DELETE", False, f"HTTP {response.status_code}", response.text)
                return False
            
            self.log_result("Template DELETE", True, "Template deleted successfully")
            return True
            
        except Exception as e:
            self.log_result("Template CRUD", False, f"Exception: {str(e)}")
            return False
    
    def test_prospect_crud(self):
        """Test POST, PUT, DELETE /api/prospects endpoints"""
        try:
            # Test CREATE prospect
            unique_timestamp = int(time.time())
            prospect_data = {
                "email": f"sarah.wilson.{unique_timestamp}@techcorp.com",
                "first_name": "Sarah",
                "last_name": "Wilson",
                "company": "TechCorp Solutions",
                "job_title": "Marketing Director",
                "industry": "Technology",
                "phone": "+1-555-0199"
            }
            
            response = requests.post(f"{self.base_url}/api/prospects", json=prospect_data, headers=self.get_headers())
            if response.status_code != 200:
                self.log_result("Prospect CREATE", False, f"HTTP {response.status_code}", response.text)
                return False
            
            created_prospect = response.json()
            if "id" not in created_prospect:
                self.log_result("Prospect CREATE", False, "No ID in response", created_prospect)
                return False
            
            prospect_id = created_prospect["id"]
            self.log_result("Prospect CREATE", True, f"Prospect created with ID: {prospect_id}")
            
            # Test UPDATE prospect
            updated_data = {
                "email": prospect_data["email"],
                "first_name": "Sarah",
                "last_name": "Wilson-Smith",
                "company": "TechCorp Solutions Inc",
                "job_title": "Senior Marketing Director",
                "industry": "Technology",
                "phone": "+1-555-0199"
            }
            
            response = requests.put(f"{self.base_url}/api/prospects/{prospect_id}", 
                                  json=updated_data, headers=self.get_headers())
            if response.status_code != 200:
                self.log_result("Prospect UPDATE", False, f"HTTP {response.status_code}", response.text)
                return False
            
            self.log_result("Prospect UPDATE", True, "Prospect updated successfully")
            
            # Test DELETE prospect
            response = requests.delete(f"{self.base_url}/api/prospects/{prospect_id}", headers=self.get_headers())
            if response.status_code != 200:
                self.log_result("Prospect DELETE", False, f"HTTP {response.status_code}", response.text)
                return False
            
            self.log_result("Prospect DELETE", True, "Prospect deleted successfully")
            return True
            
        except Exception as e:
            self.log_result("Prospect CRUD", False, f"Exception: {str(e)}")
            return False
    
    def test_csv_upload(self):
        """Test POST /api/prospects/upload endpoint"""
        try:
            # Create CSV data
            csv_content = """email,first_name,last_name,company,job_title,industry,phone
david.brown@startup.io,David,Brown,Startup.io,CTO,Technology,+1-555-0200
emma.davis@finance.com,Emma,Davis,Finance Corp,VP Finance,Finance,+1-555-0201
alex.johnson@health.org,Alex,Johnson,Health Organization,Director,Healthcare,+1-555-0202"""
            
            # Test CSV upload with query parameter
            response = requests.post(f"{self.base_url}/api/prospects/upload?file_content={csv_content}", 
                                   headers=self.get_headers())
            
            if response.status_code != 200:
                self.log_result("CSV Upload", False, f"HTTP {response.status_code}", response.text)
                return False
            
            result = response.json()
            
            # Verify response structure
            expected_fields = ["message", "prospects_added", "prospects_updated", "total_prospects"]
            for field in expected_fields:
                if field not in result:
                    self.log_result("CSV Upload", False, f"Missing field: {field}", result)
                    return False
            
            self.log_result("CSV Upload", True, 
                           f"CSV uploaded: {result['prospects_added']} added, {result['prospects_updated']} updated")
            return True
            
        except Exception as e:
            self.log_result("CSV Upload", False, f"Exception: {str(e)}")
            return False
    
    def test_overall_analytics(self):
        """Test GET /api/analytics endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/analytics", headers=self.get_headers())
            
            if response.status_code != 200:
                self.log_result("Overall Analytics", False, f"HTTP {response.status_code}", response.text)
                return False
            
            analytics = response.json()
            
            # Verify response structure
            expected_fields = ["total_campaigns", "total_emails_sent", "total_prospects", 
                             "average_open_rate", "average_reply_rate", "top_performing_campaigns"]
            for field in expected_fields:
                if field not in analytics:
                    self.log_result("Overall Analytics", False, f"Missing field: {field}", analytics)
                    return False
            
            # Verify top_performing_campaigns structure
            if analytics["top_performing_campaigns"]:
                campaign = analytics["top_performing_campaigns"][0]
                required_campaign_fields = ["name", "open_rate", "reply_rate"]
                for field in required_campaign_fields:
                    if field not in campaign:
                        self.log_result("Overall Analytics", False, f"Missing campaign field: {field}", campaign)
                        return False
            
            self.log_result("Overall Analytics", True, 
                           f"Analytics retrieved: {analytics['total_campaigns']} campaigns, {analytics['total_emails_sent']} emails sent")
            return True
            
        except Exception as e:
            self.log_result("Overall Analytics", False, f"Exception: {str(e)}")
            return False
    
    def test_template_personalization(self):
        """Test template personalization with placeholders"""
        try:
            # Get templates to test personalization
            response = requests.get(f"{self.base_url}/api/templates", headers=self.get_headers())
            if response.status_code != 200:
                self.log_result("Get Templates for Personalization", False, f"HTTP {response.status_code}", response.text)
                return False
            
            templates = response.json()
            if not templates:
                self.log_result("Get Templates for Personalization", False, "No templates available")
                return False
            
            # Find a template with personalization placeholders
            personalized_template = None
            for template in templates:
                if "{{" in template.get("subject", "") or "{{" in template.get("content", ""):
                    personalized_template = template
                    break
            
            if not personalized_template:
                self.log_result("Template Personalization", False, "No templates with personalization placeholders found")
                return False
            
            # Check for common placeholders
            expected_placeholders = ["{{first_name}}", "{{company}}", "{{job_title}}"]
            found_placeholders = []
            
            content_to_check = personalized_template.get("subject", "") + " " + personalized_template.get("content", "")
            
            for placeholder in expected_placeholders:
                if placeholder in content_to_check:
                    found_placeholders.append(placeholder)
            
            if not found_placeholders:
                self.log_result("Template Personalization", False, "No expected placeholders found in templates")
                return False
            
            self.log_result("Template Personalization", True, 
                           f"Found personalization placeholders: {', '.join(found_placeholders)}")
            return True
            
        except Exception as e:
            self.log_result("Template Personalization", False, f"Exception: {str(e)}")
            return False
    
    def test_complete_email_workflow(self):
        """Test the complete email workflow from creation to sending"""
        try:
            # Step 1: Create a prospect
            unique_timestamp = int(time.time())
            prospect_data = {
                "email": f"workflow.test.{unique_timestamp}@example.com",
                "first_name": "Workflow",
                "last_name": "Test",
                "company": "Test Company Inc",
                "job_title": "Test Manager",
                "industry": "Testing"
            }
            
            response = requests.post(f"{self.base_url}/api/prospects", json=prospect_data, headers=self.get_headers())
            if response.status_code != 200:
                self.log_result("Workflow Step 1 - Create Prospect", False, f"HTTP {response.status_code}", response.text)
                return False
            
            # Step 2: Create a template
            template_data = {
                "name": "Workflow Test Template",
                "subject": "Hello {{first_name}} from {{company}}!",
                "content": "<p>Hi {{first_name}}, we'd love to work with {{company}}!</p>",
                "type": "initial"
            }
            
            response = requests.post(f"{self.base_url}/api/templates", json=template_data, headers=self.get_headers())
            if response.status_code != 200:
                self.log_result("Workflow Step 2 - Create Template", False, f"HTTP {response.status_code}", response.text)
                return False
            
            template_id = response.json()["id"]
            
            # Step 3: Create a campaign
            campaign_data = {
                "name": "Workflow Test Campaign",
                "template_id": template_id,
                "list_ids": [],
                "max_emails": 100
            }
            
            response = requests.post(f"{self.base_url}/api/campaigns", json=campaign_data, headers=self.get_headers())
            if response.status_code != 200:
                self.log_result("Workflow Step 3 - Create Campaign", False, f"HTTP {response.status_code}", response.text)
                return False
            
            campaign_id = response.json()["id"]
            
            # Step 4: Send the campaign
            send_request = {
                "campaign_id": campaign_id,
                "send_immediately": True,
                "max_emails": 10
            }
            
            response = requests.post(f"{self.base_url}/api/campaigns/{campaign_id}/send", 
                                   json=send_request, headers=self.get_headers())
            if response.status_code != 200:
                self.log_result("Workflow Step 4 - Send Campaign", False, f"HTTP {response.status_code}", response.text)
                return False
            
            # Step 5: Check campaign status
            response = requests.get(f"{self.base_url}/api/campaigns/{campaign_id}/status", headers=self.get_headers())
            if response.status_code != 200:
                self.log_result("Workflow Step 5 - Check Status", False, f"HTTP {response.status_code}", response.text)
                return False
            
            self.log_result("Complete Email Workflow", True, "All workflow steps completed successfully")
            return True
            
        except Exception as e:
            self.log_result("Complete Email Workflow", False, f"Exception: {str(e)}")
            return False
    
    def run_email_sending_tests(self):
        """Run all email sending functionality tests"""
        print("🚀 Starting Email Sending Functionality Tests")
        print("=" * 60)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed with tests")
            return self.test_results
        
        # Test order matters for workflow
        tests = [
            ("Campaign Email Sending", self.test_campaign_email_sending),
            ("Campaign Status", self.test_campaign_status),
            ("Template CRUD", self.test_template_crud),
            ("Prospect CRUD", self.test_prospect_crud),
            ("CSV Upload", self.test_csv_upload),
            ("Overall Analytics", self.test_overall_analytics),
            ("Template Personalization", self.test_template_personalization),
            ("Complete Email Workflow", self.test_complete_email_workflow)
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
        
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All email sending tests passed!")
        else:
            print(f"⚠️  {total - passed} tests failed")
        
        return self.test_results

def main():
    """Main test execution"""
    tester = EmailSendingTester()
    results = tester.run_email_sending_tests()
    
    # Print detailed results
    print("\n" + "=" * 60)
    print("📋 DETAILED EMAIL SENDING TEST RESULTS")
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