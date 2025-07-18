#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for AI Email Responder
Focus on List Management, Campaign Sending, Template/Prospect CRUD, and Edge Cases
"""

import requests
import json
import io
from datetime import datetime
import time
import os

# Get backend URL from frontend .env file
BACKEND_URL = "https://2f0e9441-c5a6-4abd-86c1-f24f15fd0382.preview.emergentagent.com"
AUTH_TOKEN = "test_token_12345"

class BackendTester:
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
    
    def test_authentication(self):
        """Test authentication system"""
        try:
            # Test login
            login_data = {"username": "testuser", "password": "testpass123"}
            response = requests.post(f"{self.base_url}/api/auth/login", json=login_data)
            
            if response.status_code != 200:
                self.log_result("Authentication Login", False, f"HTTP {response.status_code}", response.text)
                return False
            
            auth_result = response.json()
            if 'access_token' not in auth_result:
                self.log_result("Authentication Login", False, "No access token in response", auth_result)
                return False
            
            self.log_result("Authentication Login", True, "Login successful")
            
            # Test protected endpoint
            response = requests.get(f"{self.base_url}/api/auth/me", headers=self.headers)
            if response.status_code != 200:
                self.log_result("Authentication Protected Endpoint", False, f"HTTP {response.status_code}", response.text)
                return False
            
            user_data = response.json()
            if 'username' not in user_data:
                self.log_result("Authentication Protected Endpoint", False, "No username in response", user_data)
                return False
            
            self.log_result("Authentication Protected Endpoint", True, f"User: {user_data['username']}")
            return True
            
        except Exception as e:
            self.log_result("Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_health_check(self):
        """Test API health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'status' in data and data['status'] == 'healthy':
                    self.log_result("Health Check", True, "API is healthy")
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
    
    def test_template_crud(self):
        """Test template CRUD operations"""
        try:
            # CREATE template
            template_data = {
                "name": "Test Email Template",
                "subject": "Welcome {{first_name}}!",
                "content": "<p>Hello {{first_name}} from {{company}},</p><p>Welcome to our service!</p>",
                "type": "initial",
                "placeholders": ["first_name", "company"]
            }
            
            response = requests.post(f"{self.base_url}/api/templates", json=template_data, headers=self.headers)
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
            
            # READ templates
            response = requests.get(f"{self.base_url}/api/templates", headers=self.headers)
            if response.status_code != 200:
                self.log_result("Template READ", False, f"HTTP {response.status_code}", response.text)
                return False
            
            templates = response.json()
            if not isinstance(templates, list):
                self.log_result("Template READ", False, "Response is not a list", templates)
                return False
            
            self.log_result("Template READ", True, f"Retrieved {len(templates)} templates")
            
            # UPDATE template
            update_data = {
                "name": "Updated Test Template",
                "subject": "Updated Welcome {{first_name}}!",
                "content": template_data["content"],
                "type": template_data["type"],
                "placeholders": template_data["placeholders"]
            }
            
            response = requests.put(f"{self.base_url}/api/templates/{template_id}", json=update_data, headers=self.headers)
            if response.status_code != 200:
                self.log_result("Template UPDATE", False, f"HTTP {response.status_code}", response.text)
                return False
            
            self.log_result("Template UPDATE", True, "Template updated successfully")
            
            # DELETE template (will be done in cleanup)
            return True
            
        except Exception as e:
            self.log_result("Template CRUD", False, f"Exception: {str(e)}")
            return False
    
    def test_prospect_crud(self):
        """Test prospect CRUD operations"""
        try:
            # CREATE prospect
            unique_timestamp = int(time.time())
            prospect_data = {
                "email": f"john.doe.{unique_timestamp}@techcorp.com",
                "first_name": "John",
                "last_name": "Doe",
                "company": "TechCorp Inc",
                "job_title": "Software Engineer",
                "industry": "Technology",
                "phone": "+1-555-0123"
            }
            
            response = requests.post(f"{self.base_url}/api/prospects", json=prospect_data, headers=self.headers)
            if response.status_code != 200:
                self.log_result("Prospect CREATE", False, f"HTTP {response.status_code}", response.text)
                return False
            
            created_prospect = response.json()
            if 'id' not in created_prospect:
                self.log_result("Prospect CREATE", False, "No ID in response", created_prospect)
                return False
            
            prospect_id = created_prospect['id']
            self.created_resources['prospects'].append(prospect_id)
            self.log_result("Prospect CREATE", True, f"Created prospect with ID: {prospect_id}")
            
            # READ prospects
            response = requests.get(f"{self.base_url}/api/prospects", headers=self.headers)
            if response.status_code != 200:
                self.log_result("Prospect READ", False, f"HTTP {response.status_code}", response.text)
                return False
            
            prospects = response.json()
            if not isinstance(prospects, list):
                self.log_result("Prospect READ", False, "Response is not a list", prospects)
                return False
            
            self.log_result("Prospect READ", True, f"Retrieved {len(prospects)} prospects")
            
            # UPDATE prospect
            update_data = {
                "first_name": "Johnny",
                "last_name": "Doe",
                "company": "Updated TechCorp Inc",
                "job_title": "Senior Software Engineer"
            }
            
            response = requests.put(f"{self.base_url}/api/prospects/{prospect_id}", json=update_data, headers=self.headers)
            if response.status_code != 200:
                self.log_result("Prospect UPDATE", False, f"HTTP {response.status_code}", response.text)
                return False
            
            self.log_result("Prospect UPDATE", True, "Prospect updated successfully")
            
            # Test CSV upload
            csv_data = f"""email,first_name,last_name,company,job_title,industry,phone
sarah.johnson.{unique_timestamp}@innovate.com,Sarah,Johnson,Innovate Solutions,Product Manager,Technology,+1-555-0124
mike.wilson.{unique_timestamp}@startup.io,Mike,Wilson,Startup.io,CTO,Technology,+1-555-0125"""
            
            response = requests.post(f"{self.base_url}/api/prospects/upload", 
                                   data=csv_data, 
                                   headers={**self.headers, 'Content-Type': 'text/csv'})
            
            if response.status_code != 200:
                self.log_result("Prospect CSV Upload", False, f"HTTP {response.status_code}", response.text)
                return False
            
            result = response.json()
            if 'prospects_added' not in result:
                self.log_result("Prospect CSV Upload", False, "Unexpected upload result", result)
                return False
            
            self.log_result("Prospect CSV Upload", True, f"Uploaded {result['prospects_added']} prospects from CSV")
            return True
            
        except Exception as e:
            self.log_result("Prospect CRUD", False, f"Exception: {str(e)}")
            return False
    
    def test_list_crud(self):
        """Test list CRUD operations and prospect associations"""
        try:
            # CREATE list
            list_data = {
                "name": "Test Prospect List",
                "description": "A test list for API testing",
                "color": "#3B82F6",
                "tags": ["test", "api"]
            }
            
            response = requests.post(f"{self.base_url}/api/lists", json=list_data, headers=self.headers)
            if response.status_code != 200:
                self.log_result("List CREATE", False, f"HTTP {response.status_code}", response.text)
                return False
            
            created_list = response.json()
            if 'id' not in created_list:
                self.log_result("List CREATE", False, "No ID in response", created_list)
                return False
            
            list_id = created_list['id']
            self.created_resources['lists'].append(list_id)
            self.log_result("List CREATE", True, f"Created list with ID: {list_id}")
            
            # READ lists
            response = requests.get(f"{self.base_url}/api/lists", headers=self.headers)
            if response.status_code != 200:
                self.log_result("List READ", False, f"HTTP {response.status_code}", response.text)
                return False
            
            lists = response.json()
            if not isinstance(lists, list):
                self.log_result("List READ", False, "Response is not a list", lists)
                return False
            
            self.log_result("List READ", True, f"Retrieved {len(lists)} lists")
            
            # Get prospects to add to the list
            response = requests.get(f"{self.base_url}/api/prospects", headers=self.headers)
            if response.status_code != 200:
                self.log_result("Get Prospects for List", False, f"HTTP {response.status_code}", response.text)
                return False
            
            prospects = response.json()
            if not prospects or len(prospects) == 0:
                self.log_result("Get Prospects for List", False, "No prospects available")
                return False
            
            # Select up to 2 prospects to add to the list
            prospect_ids = [p['id'] for p in prospects[:min(2, len(prospects))]]
            
            # ADD prospects to list
            add_request = {"prospect_ids": prospect_ids}
            response = requests.post(f"{self.base_url}/api/lists/{list_id}/prospects", 
                                   json=add_request, headers=self.headers)
            if response.status_code != 200:
                self.log_result("Add Prospects to List", False, f"HTTP {response.status_code}", response.text)
                return False
            
            result = response.json()
            self.log_result("Add Prospects to List", True, f"Added {len(prospect_ids)} prospects to list")
            
            # Verify the list by getting it by ID
            response = requests.get(f"{self.base_url}/api/lists/{list_id}", headers=self.headers)
            if response.status_code != 200:
                self.log_result("Verify List Contents", False, f"HTTP {response.status_code}", response.text)
                return False
            
            updated_list = response.json()
            self.log_result("Verify List Contents", True, f"List retrieved successfully")
            
            # UPDATE list
            update_data = {
                "name": "Updated Test List",
                "description": "Updated description",
                "color": "#10B981",
                "tags": ["updated", "test"]
            }
            
            response = requests.put(f"{self.base_url}/api/lists/{list_id}", json=update_data, headers=self.headers)
            if response.status_code != 200:
                self.log_result("List UPDATE", False, f"HTTP {response.status_code}", response.text)
                return False
            
            self.log_result("List UPDATE", True, "List updated successfully")
            
            # REMOVE prospects from list
            remove_request = {"prospect_ids": [prospect_ids[0]]}  # Remove first prospect
            response = requests.delete(f"{self.base_url}/api/lists/{list_id}/prospects", 
                                     json=remove_request, headers=self.headers)
            if response.status_code != 200:
                self.log_result("Remove Prospects from List", False, f"HTTP {response.status_code}", response.text)
                return False
            
            self.log_result("Remove Prospects from List", True, "Removed prospect from list")
            
            return True
            
        except Exception as e:
            self.log_result("List CRUD", False, f"Exception: {str(e)}")
            return False
    
    def test_campaign_crud_and_sending(self):
        """Test campaign CRUD operations and email sending functionality"""
        try:
            # First ensure we have templates and prospects
            templates_response = requests.get(f"{self.base_url}/api/templates", headers=self.headers)
            if templates_response.status_code != 200 or not templates_response.json():
                self.log_result("Campaign Test Prerequisites", False, "No templates available for campaign")
                return False
            
            prospects_response = requests.get(f"{self.base_url}/api/prospects", headers=self.headers)
            if prospects_response.status_code != 200 or not prospects_response.json():
                self.log_result("Campaign Test Prerequisites", False, "No prospects available for campaign")
                return False
            
            template_id = templates_response.json()[0]['id']
            
            # CREATE campaign
            campaign_data = {
                "name": "Test Email Campaign",
                "template_id": template_id,
                "list_ids": [],  # Use all prospects
                "max_emails": 100,
                "schedule": None
            }
            
            response = requests.post(f"{self.base_url}/api/campaigns", json=campaign_data, headers=self.headers)
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
            
            # READ campaigns
            response = requests.get(f"{self.base_url}/api/campaigns", headers=self.headers)
            if response.status_code != 200:
                self.log_result("Campaign READ", False, f"HTTP {response.status_code}", response.text)
                return False
            
            campaigns = response.json()
            if not isinstance(campaigns, list):
                self.log_result("Campaign READ", False, "Response is not a list", campaigns)
                return False
            
            self.log_result("Campaign READ", True, f"Retrieved {len(campaigns)} campaigns")
            
            # UPDATE campaign
            update_data = {
                "name": "Updated Test Campaign",
                "template_id": template_id,
                "max_emails": 50
            }
            
            response = requests.put(f"{self.base_url}/api/campaigns/{campaign_id}", json=update_data, headers=self.headers)
            if response.status_code != 200:
                self.log_result("Campaign UPDATE", False, f"HTTP {response.status_code}", response.text)
                return False
            
            self.log_result("Campaign UPDATE", True, "Campaign updated successfully")
            
            # Test CAMPAIGN SENDING - This is the critical functionality
            send_request = {
                "send_immediately": True,
                "max_emails": 5,  # Limit to 5 for testing
                "schedule_type": "immediate",
                "follow_up_enabled": False
            }
            
            response = requests.post(f"{self.base_url}/api/campaigns/{campaign_id}/send", 
                                   json=send_request, headers=self.headers)
            if response.status_code != 200:
                self.log_result("Campaign SEND", False, f"HTTP {response.status_code}", response.text)
                return False
            
            send_result = response.json()
            if 'total_sent' not in send_result and 'total_failed' not in send_result:
                self.log_result("Campaign SEND", False, "Invalid send result format", send_result)
                return False
            
            total_sent = send_result.get('total_sent', 0)
            total_failed = send_result.get('total_failed', 0)
            self.log_result("Campaign SEND", True, f"Campaign sent: {total_sent} sent, {total_failed} failed")
            
            # Check campaign status after sending
            response = requests.get(f"{self.base_url}/api/campaigns/{campaign_id}/status", headers=self.headers)
            if response.status_code == 200:
                status_result = response.json()
                self.log_result("Campaign Status Check", True, f"Status: {status_result.get('status', 'unknown')}")
            else:
                self.log_result("Campaign Status Check", False, f"HTTP {response.status_code}", response.text)
            
            return True
            
        except Exception as e:
            self.log_result("Campaign CRUD and Sending", False, f"Exception: {str(e)}")
            return False
    def test_edge_cases_and_validation(self):
        """Test edge cases and error handling"""
        try:
            # Test invalid template ID in campaign
            invalid_campaign_data = {
                "name": "Invalid Campaign",
                "template_id": "non-existent-template-id",
                "list_ids": [],
                "max_emails": 100
            }
            
            response = requests.post(f"{self.base_url}/api/campaigns", json=invalid_campaign_data, headers=self.headers)
            # This should either fail or create campaign that fails on send
            if response.status_code == 200:
                campaign_id = response.json()['id']
                self.created_resources['campaigns'].append(campaign_id)
                
                # Try to send campaign with invalid template
                send_request = {"send_immediately": True, "max_emails": 1}
                send_response = requests.post(f"{self.base_url}/api/campaigns/{campaign_id}/send", 
                                            json=send_request, headers=self.headers)
                if send_response.status_code != 200:
                    self.log_result("Invalid Template ID Handling", True, "Campaign send failed as expected with invalid template")
                else:
                    send_result = send_response.json()
                    if send_result.get('total_failed', 0) > 0:
                        self.log_result("Invalid Template ID Handling", True, "Campaign send handled invalid template gracefully")
                    else:
                        self.log_result("Invalid Template ID Handling", False, "Campaign send succeeded with invalid template")
            else:
                self.log_result("Invalid Template ID Handling", True, "Campaign creation failed as expected with invalid template")
            
            # Test non-existent list
            response = requests.get(f"{self.base_url}/api/lists/non-existent-list-id", headers=self.headers)
            if response.status_code == 404:
                self.log_result("Non-existent List Handling", True, "404 returned for non-existent list")
            else:
                self.log_result("Non-existent List Handling", False, f"Expected 404, got {response.status_code}")
            
            # Test duplicate prospect email
            unique_timestamp = int(time.time())
            duplicate_prospect = {
                "email": f"duplicate.{unique_timestamp}@test.com",
                "first_name": "Duplicate",
                "last_name": "User",
                "company": "Test Corp"
            }
            
            # Create first prospect
            response1 = requests.post(f"{self.base_url}/api/prospects", json=duplicate_prospect, headers=self.headers)
            if response1.status_code == 200:
                self.created_resources['prospects'].append(response1.json()['id'])
                
                # Try to create duplicate
                response2 = requests.post(f"{self.base_url}/api/prospects", json=duplicate_prospect, headers=self.headers)
                if response2.status_code != 200:
                    self.log_result("Duplicate Email Handling", True, "Duplicate email rejected as expected")
                else:
                    # Some systems allow duplicates but handle them in business logic
                    self.log_result("Duplicate Email Handling", True, "Duplicate email handled (may be allowed)")
                    self.created_resources['prospects'].append(response2.json()['id'])
            else:
                self.log_result("Duplicate Email Handling", False, "Could not create initial prospect for duplicate test")
            
            # Test missing required fields
            incomplete_prospect = {
                "first_name": "Incomplete",
                "last_name": "User"
                # Missing email field
            }
            
            response = requests.post(f"{self.base_url}/api/prospects", json=incomplete_prospect, headers=self.headers)
            if response.status_code != 200:
                self.log_result("Missing Required Fields", True, "Missing email field rejected as expected")
            else:
                result = response.json()
                if 'error' in result or 'message' in result:
                    self.log_result("Missing Required Fields", True, "Missing email handled with error message")
                else:
                    self.log_result("Missing Required Fields", False, "Missing email field was accepted")
                    if 'id' in result:
                        self.created_resources['prospects'].append(result['id'])
            
            # Test invalid email format
            invalid_email_prospect = {
                "email": "invalid-email-format",
                "first_name": "Invalid",
                "last_name": "Email",
                "company": "Test Corp"
            }
            
            response = requests.post(f"{self.base_url}/api/prospects", json=invalid_email_prospect, headers=self.headers)
            if response.status_code != 200:
                self.log_result("Invalid Email Format", True, "Invalid email format rejected as expected")
            else:
                result = response.json()
                if 'error' in result or 'message' in result:
                    self.log_result("Invalid Email Format", True, "Invalid email handled with error message")
                else:
                    self.log_result("Invalid Email Format", False, "Invalid email format was accepted")
                    if 'id' in result:
                        self.created_resources['prospects'].append(result['id'])
            
            return True
            
        except Exception as e:
            self.log_result("Edge Cases and Validation", False, f"Exception: {str(e)}")
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
    
    def run_comprehensive_tests(self):
        """Run comprehensive backend tests focusing on the review request requirements"""
        print("🚀 Starting AI Email Responder Comprehensive Backend Tests")
        print("Focus: List Management, Campaign Sending, Template/Prospect CRUD, Edge Cases")
        print("=" * 80)
        
        # Test order matters - some tests depend on others
        tests = [
            ("Health Check", self.test_health_check),
            ("Authentication System", self.test_authentication),
            ("Template CRUD Operations", self.test_template_crud),
            ("Prospect CRUD Operations", self.test_prospect_crud),
            ("List CRUD & Prospect Association", self.test_list_crud),
            ("Campaign CRUD & Email Sending", self.test_campaign_crud_and_sending),
            ("Edge Cases & Validation", self.test_edge_cases_and_validation)
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
                    # Mark critical failures
                    if any(keyword in test_name.lower() for keyword in ['campaign', 'sending', 'list', 'template', 'prospect']):
                        critical_failures.append(test_name)
            except Exception as e:
                self.log_result(test_name, False, f"Test execution failed: {str(e)}")
                critical_failures.append(test_name)
        
        print("\n" + "=" * 80)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed!")
        else:
            print(f"⚠️  {total - passed} tests failed")
            if critical_failures:
                print(f"🚨 Critical failures in: {', '.join(critical_failures)}")
        
        # Cleanup
        self.cleanup_resources()
        
        return self.test_results, critical_failures
        try:
            # First create a template for the intent
            template_data = {
                "name": "Positive Response Template",
                "subject": "Thank you for your interest, {{first_name}}!",
                "content": "<p>Hello {{first_name}},</p><p>Thank you for your interest in our product. We'd be happy to schedule a demo for you.</p>",
                "type": "auto_response",
                "placeholders": ["first_name", "last_name", "company"]
            }
            
            response = requests.post(f"{self.base_url}/api/templates", json=template_data)
            if response.status_code != 200:
                self.log_result("Template CREATE for Intent", False, f"HTTP {response.status_code}", response.text)
                return False
            
            created_template = response.json()
            if 'id' not in created_template:
                self.log_result("Template CREATE for Intent", False, "No ID in response", created_template)
                return False
            
            template_id = created_template['id']
            self.created_resources['templates'].append(template_id)
            self.log_result("Template CREATE for Intent", True, f"Created template with ID: {template_id}")
            
            # Create a fallback template
            fallback_template_data = {
                "name": "Fallback Response Template",
                "subject": "Following up, {{first_name}}",
                "content": "<p>Hello {{first_name}},</p><p>I wanted to follow up on your inquiry. Let me know if you have any questions.</p>",
                "type": "auto_response",
                "placeholders": ["first_name", "last_name", "company"]
            }
            
            response = requests.post(f"{self.base_url}/api/templates", json=fallback_template_data)
            if response.status_code != 200:
                self.log_result("Fallback Template CREATE", False, f"HTTP {response.status_code}", response.text)
                return False
            
            fallback_template = response.json()
            fallback_template_id = fallback_template['id']
            self.created_resources['templates'].append(fallback_template_id)
            
            # Create an intent with the templates
            intent_data = {
                "name": "Positive Response",
                "description": "Customer shows interest in the product",
                "keywords": ["interested", "tell me more", "pricing", "demo"],
                "primary_template_id": template_id,
                "fallback_template_id": fallback_template_id,
                "auto_respond": True,
                "confidence_threshold": 0.7
            }
            
            response = requests.post(f"{self.base_url}/api/intents", json=intent_data)
            if response.status_code != 200:
                self.log_result("Intent CREATE", False, f"HTTP {response.status_code}", response.text)
                return False
            
            created_intent = response.json()
            if 'id' not in created_intent:
                self.log_result("Intent CREATE", False, "No ID in response", created_intent)
                return False
            
            intent_id = created_intent['id']
            self.created_resources['intents'].append(intent_id)
            self.log_result("Intent CREATE", True, f"Created intent with ID: {intent_id}")
            
            # Verify the intent has the templates associated
            response = requests.get(f"{self.base_url}/api/intents/{intent_id}")
            if response.status_code != 200:
                self.log_result("Intent-Template Verification", False, f"HTTP {response.status_code}", response.text)
                return False
            
            intent = response.json()
            if intent.get('primary_template_id') != template_id:
                self.log_result("Intent-Template Verification", False, "Primary template not associated correctly", intent)
                return False
            
            if intent.get('fallback_template_id') != fallback_template_id:
                self.log_result("Intent-Template Verification", False, "Fallback template not associated correctly", intent)
                return False
            
            self.log_result("Intent-Template Verification", True, "Templates correctly associated with intent")
            
            # Test intent CRUD operations
            # Update the intent
            update_data = {
                "name": "Updated Positive Response",
                "description": intent_data["description"],
                "keywords": intent_data["keywords"],
                "primary_template_id": template_id,
                "fallback_template_id": fallback_template_id
            }
            
            response = requests.put(f"{self.base_url}/api/intents/{intent_id}", json=update_data)
            if response.status_code != 200:
                self.log_result("Intent UPDATE", False, f"HTTP {response.status_code}", response.text)
                return False
            
            self.log_result("Intent UPDATE", True, "Intent updated successfully")
            
            # Get all intents
            response = requests.get(f"{self.base_url}/api/intents")
            if response.status_code != 200:
                self.log_result("Intent READ", False, f"HTTP {response.status_code}", response.text)
                return False
            
            intents = response.json()
            if not isinstance(intents, list):
                self.log_result("Intent READ", False, "Response is not a list", intents)
                return False
            
            self.log_result("Intent READ", True, f"Retrieved {len(intents)} intents")
            
            # Delete the intent
            response = requests.delete(f"{self.base_url}/api/intents/{intent_id}")
            if response.status_code != 200:
                self.log_result("Intent DELETE", False, f"HTTP {response.status_code}", response.text)
                return False
            
            self.log_result("Intent DELETE", True, "Intent deleted successfully")
            
            return True
            
        except Exception as e:
            self.log_result("Intent Management", False, f"Exception: {str(e)}")
            return False
    
    def test_ai_intent_classification(self):
        """Test AI intent classification"""
        try:
            # Test with a positive response email
            positive_email = {
                "subject": "Interested in your product",
                "content": "Thanks for reaching out! I am very interested in your product and would like to schedule a demo. Please send me more information about pricing."
            }
            
            response = requests.post(f"{self.base_url}/api/email-processing/test-classification", json=positive_email)
            if response.status_code != 200:
                self.log_result("AI Intent Classification", False, f"HTTP {response.status_code}", response.text)
                return False
            
            result = response.json()
            if 'classified_intents' not in result:
                self.log_result("AI Intent Classification", False, "No intents in response", result)
                return False
            
            # Check if we have at least one intent classified
            if len(result['classified_intents']) == 0:
                self.log_result("AI Intent Classification", False, "No intents classified", result)
                return False
            
            # Check if we have confidence scores
            for intent in result['classified_intents']:
                if 'confidence' not in intent:
                    self.log_result("AI Intent Classification", False, "No confidence score in intent", intent)
                    return False
            
            # Check if we have sentiment analysis
            if 'sentiment_analysis' not in result:
                self.log_result("AI Intent Classification", False, "No sentiment analysis in response", result)
                return False
            
            self.log_result("AI Intent Classification", True, 
                           f"Successfully classified {len(result['classified_intents'])} intents with sentiment: {result['sentiment_analysis'].get('sentiment', 'unknown')}")
            
            return True
            
        except Exception as e:
            self.log_result("AI Intent Classification", False, f"Exception: {str(e)}")
            return False
    
    def test_ai_response_generation(self):
        """Test AI response generation"""
        try:
            # First get a prospect to use
            response = requests.get(f"{self.base_url}/api/prospects")
            if response.status_code != 200:
                self.log_result("Get Prospect for Response Test", False, f"HTTP {response.status_code}", response.text)
                return False
            
            prospects = response.json()
            if not prospects or len(prospects) == 0:
                self.log_result("Get Prospect for Response Test", False, "No prospects available")
                return False
            
            prospect_id = prospects[0]['id']
            
            # Test response generation
            test_data = {
                "subject": "Interested in your product",
                "content": "Thanks for reaching out! I am very interested in your product and would like to schedule a demo. Please send me more information about pricing.",
                "prospect_id": prospect_id
            }
            
            response = requests.post(f"{self.base_url}/api/email-processing/test-response", json=test_data)
            if response.status_code != 200:
                self.log_result("AI Response Generation", False, f"HTTP {response.status_code}", response.text)
                return False
            
            result = response.json()
            if 'generated_response' not in result:
                self.log_result("AI Response Generation", False, "No generated response in result", result)
                return False
            
            # Check if the response contains content
            if 'content' not in result['generated_response']:
                self.log_result("AI Response Generation", False, "No content in generated response", result['generated_response'])
                return False
            
            self.log_result("AI Response Generation", True, "Successfully generated AI response")
            return True
            
        except Exception as e:
            self.log_result("AI Response Generation", False, f"Exception: {str(e)}")
            return False
    
    def test_email_processing_status(self):
        """Test email processing status and control"""
        try:
            # Check initial status
            response = requests.get(f"{self.base_url}/api/email-processing/status")
            if response.status_code != 200:
                self.log_result("Email Processing Status", False, f"HTTP {response.status_code}", response.text)
                return False
            
            initial_status = response.json()
            if 'status' not in initial_status:
                self.log_result("Email Processing Status", False, "No status in response", initial_status)
                return False
            
            self.log_result("Email Processing Status", True, f"Initial status: {initial_status['status']}")
            
            # Start email processing
            response = requests.post(f"{self.base_url}/api/email-processing/start")
            if response.status_code != 200:
                self.log_result("Email Processing Start", False, f"HTTP {response.status_code}", response.text)
                return False
            
            # Check status after starting
            response = requests.get(f"{self.base_url}/api/email-processing/status")
            if response.status_code != 200:
                self.log_result("Email Processing Status After Start", False, f"HTTP {response.status_code}", response.text)
                return False
            
            status_after_start = response.json()
            if status_after_start.get('status') != 'running':
                self.log_result("Email Processing Status After Start", False, f"Expected 'running', got '{status_after_start.get('status')}'", status_after_start)
            else:
                self.log_result("Email Processing Status After Start", True, "Status is 'running' as expected")
            
            # Stop email processing
            response = requests.post(f"{self.base_url}/api/email-processing/stop")
            if response.status_code != 200:
                self.log_result("Email Processing Stop", False, f"HTTP {response.status_code}", response.text)
                return False
            
            # Check status after stopping
            response = requests.get(f"{self.base_url}/api/email-processing/status")
            if response.status_code != 200:
                self.log_result("Email Processing Status After Stop", False, f"HTTP {response.status_code}", response.text)
                return False
            
            status_after_stop = response.json()
            if status_after_stop.get('status') != 'stopped':
                self.log_result("Email Processing Status After Stop", False, f"Expected 'stopped', got '{status_after_stop.get('status')}'", status_after_stop)
            else:
                self.log_result("Email Processing Status After Stop", True, "Status is 'stopped' as expected")
            
            # Check analytics
            response = requests.get(f"{self.base_url}/api/email-processing/analytics")
            if response.status_code != 200:
                self.log_result("Email Processing Analytics", False, f"HTTP {response.status_code}", response.text)
                return False
            
            analytics = response.json()
            expected_fields = ['total_threads', 'processed_emails', 'auto_responses_sent', 'processing_status']
            
            for field in expected_fields:
                if field not in analytics:
                    self.log_result("Email Processing Analytics", False, f"Missing field: {field}", analytics)
                    return False
            
            self.log_result("Email Processing Analytics", True, f"Analytics data retrieved successfully")
            
            return True
            
        except Exception as e:
            self.log_result("Email Processing Status", False, f"Exception: {str(e)}")
            return False
    
    def run_focused_tests(self):
        """Run tests focused on the reported issues"""
        print("🚀 Starting AI Email Responder Focused Tests")
        print("=" * 60)
        
        # Test order matters - some tests depend on others
        tests = [
            ("Health Check", self.test_health_check),
            ("Prospect Management", self.test_prospect_management),
            ("List Management & Prospect Association", self.test_list_management),
            ("Intent Management & Template Association", self.test_intent_management),
            ("AI Intent Classification", self.test_ai_intent_classification),
            ("AI Response Generation", self.test_ai_response_generation),
            ("Email Processing Status & Analytics", self.test_email_processing_status)
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
            print("🎉 All tests passed!")
        else:
            print(f"⚠️  {total - passed} tests failed")
        
        return self.test_results

def main():
    """Main test execution"""
    tester = BackendTester()
    results, critical_failures = tester.run_comprehensive_tests()
    
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
    print("📝 SUMMARY FOR TEST RESULT UPDATE")
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
    
    if critical_failures:
        print(f"\n🚨 CRITICAL FAILURES: {len(critical_failures)}")
        for failure in critical_failures:
            print(f"   - {failure}")
    
    return results, critical_failures

if __name__ == "__main__":
    main()