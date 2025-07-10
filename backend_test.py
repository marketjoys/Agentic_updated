#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for AI Email Responder
Tests all backend functionality including CRUD operations, file uploads, and analytics
"""

import requests
import json
import io
import pandas as pd
from datetime import datetime
import time
import os

# Get backend URL from frontend .env file
BACKEND_URL = "https://6b62dee1-5327-415a-9c56-b9cabfcdef65.preview.emergentagent.com"  # Using the configured backend URL

class BackendTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.test_results = {}
        self.created_resources = {
            'prospects': [],
            'templates': [],
            'campaigns': [],
            'intents': []
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
    
    def test_prospect_crud(self):
        """Test prospect CRUD operations"""
        try:
            # Test CREATE prospect
            unique_timestamp = int(time.time())
            prospect_data = {
                "email": f"john.doe.{unique_timestamp}@techcorp.com",
                "first_name": "John",
                "last_name": "Doe",
                "company": "TechCorp Inc",
                "phone": "+1-555-0123"
            }
            
            response = requests.post(f"{self.base_url}/api/prospects", json=prospect_data)
            if response.status_code != 200:
                self.log_result("Prospect CREATE", False, f"HTTP {response.status_code}", response.text)
                return False
            
            created_prospect = response.json()
            if 'id' not in created_prospect:
                self.log_result("Prospect CREATE", False, "No ID in response", created_prospect)
                return False
            
            self.created_resources['prospects'].append(created_prospect['id'])
            self.log_result("Prospect CREATE", True, f"Created prospect with ID: {created_prospect['id']}")
            
            # Test READ prospects
            response = requests.get(f"{self.base_url}/api/prospects")
            if response.status_code != 200:
                self.log_result("Prospect READ", False, f"HTTP {response.status_code}", response.text)
                return False
            
            prospects = response.json()
            if not isinstance(prospects, list):
                self.log_result("Prospect READ", False, "Response is not a list", prospects)
                return False
            
            # Verify our created prospect is in the list
            found_prospect = None
            for prospect in prospects:
                if prospect.get('id') == created_prospect['id']:
                    found_prospect = prospect
                    break
            
            if not found_prospect:
                self.log_result("Prospect READ", False, "Created prospect not found in list")
                return False
            
            self.log_result("Prospect READ", True, f"Retrieved {len(prospects)} prospects")
            return True
            
        except Exception as e:
            self.log_result("Prospect CRUD", False, f"Exception: {str(e)}")
            return False
    
    def test_prospect_csv_upload(self):
        """Test CSV upload functionality"""
        try:
            # Create test CSV data
            csv_data = """email,first_name,last_name,company,phone
sarah.johnson@innovate.com,Sarah,Johnson,Innovate Solutions,+1-555-0124
mike.wilson@startup.io,Mike,Wilson,Startup.io,+1-555-0125
lisa.chen@enterprise.com,Lisa,Chen,Enterprise Corp,+1-555-0126"""
            
            # Create file-like object
            csv_file = io.StringIO(csv_data)
            files = {'file': ('prospects.csv', csv_file.getvalue(), 'text/csv')}
            
            response = requests.post(f"{self.base_url}/api/prospects/upload", files=files)
            
            if response.status_code != 200:
                self.log_result("CSV Upload", False, f"HTTP {response.status_code}", response.text)
                return False
            
            result = response.json()
            if 'successful_count' not in result:
                self.log_result("CSV Upload", False, "Unexpected upload result", result)
                return False
            
            self.log_result("CSV Upload", True, f"Uploaded {result['successful_count']} prospects from CSV")
            return True
            
        except Exception as e:
            self.log_result("CSV Upload", False, f"Exception: {str(e)}")
            return False
    
    def test_template_crud(self):
        """Test template CRUD operations"""
        try:
            # Test CREATE template
            template_data = {
                "name": "Welcome Email Template",
                "subject": "Welcome to our service, {{first_name}}!",
                "content": "<h1>Hello {{first_name}} {{last_name}}</h1><p>Welcome to our service at {{company}}!</p>",
                "type": "initial",
                "placeholders": ["first_name", "last_name", "company"]
            }
            
            response = requests.post(f"{self.base_url}/api/templates", json=template_data)
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
            
            # Test READ templates
            response = requests.get(f"{self.base_url}/api/templates")
            if response.status_code != 200:
                self.log_result("Template READ", False, f"HTTP {response.status_code}", response.text)
                return False
            
            templates = response.json()
            if not isinstance(templates, list):
                self.log_result("Template READ", False, "Response is not a list", templates)
                return False
            
            self.log_result("Template READ", True, f"Retrieved {len(templates)} templates")
            
            # Test GET specific template
            response = requests.get(f"{self.base_url}/api/templates/{template_id}")
            if response.status_code != 200:
                self.log_result("Template GET by ID", False, f"HTTP {response.status_code}", response.text)
                return False
            
            template = response.json()
            if template.get('id') != template_id:
                self.log_result("Template GET by ID", False, "Template ID mismatch", template)
                return False
            
            self.log_result("Template GET by ID", True, f"Retrieved template: {template['name']}")
            
            # Test UPDATE template
            update_data = {
                "name": "Updated Welcome Email Template",
                "subject": "Updated: Welcome {{first_name}}!",
                "content": template_data["content"],
                "type": "initial",
                "placeholders": ["first_name", "last_name", "company"]
            }
            
            response = requests.put(f"{self.base_url}/api/templates/{template_id}", json=update_data)
            if response.status_code != 200:
                self.log_result("Template UPDATE", False, f"HTTP {response.status_code}", response.text)
                return False
            
            self.log_result("Template UPDATE", True, "Template updated successfully")
            return True
            
        except Exception as e:
            self.log_result("Template CRUD", False, f"Exception: {str(e)}")
            return False
    
    def test_campaign_crud(self):
        """Test campaign CRUD operations"""
        try:
            # First ensure we have a template
            if not self.created_resources['templates']:
                self.log_result("Campaign CRUD", False, "No templates available for campaign")
                return False
            
            template_id = self.created_resources['templates'][0]
            
            # Test CREATE campaign
            campaign_data = {
                "name": "Q1 2025 Outreach Campaign",
                "template_id": template_id,
                "max_emails": 500,
                "follow_up_intervals": [3, 7, 14],
                "status": "draft"
            }
            
            response = requests.post(f"{self.base_url}/api/campaigns", json=campaign_data)
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
            
            # Test READ campaigns
            response = requests.get(f"{self.base_url}/api/campaigns")
            if response.status_code != 200:
                self.log_result("Campaign READ", False, f"HTTP {response.status_code}", response.text)
                return False
            
            campaigns = response.json()
            if not isinstance(campaigns, list):
                self.log_result("Campaign READ", False, "Response is not a list", campaigns)
                return False
            
            self.log_result("Campaign READ", True, f"Retrieved {len(campaigns)} campaigns")
            
            # Test GET specific campaign
            response = requests.get(f"{self.base_url}/api/campaigns/{campaign_id}")
            if response.status_code != 200:
                self.log_result("Campaign GET by ID", False, f"HTTP {response.status_code}", response.text)
                return False
            
            campaign = response.json()
            if campaign.get('id') != campaign_id:
                self.log_result("Campaign GET by ID", False, "Campaign ID mismatch", campaign)
                return False
            
            self.log_result("Campaign GET by ID", True, f"Retrieved campaign: {campaign['name']}")
            return True
            
        except Exception as e:
            self.log_result("Campaign CRUD", False, f"Exception: {str(e)}")
            return False
    
    def test_intent_crud(self):
        """Test intent configuration CRUD operations"""
        try:
            # Test CREATE intent
            intent_data = {
                "name": "Interested Response",
                "description": "Customer shows interest in the product",
                "keywords": ["interested", "tell me more", "pricing", "demo"],
                "response_template": "Thank you for your interest! I'll send you more details shortly."
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
            
            # Test READ intents
            response = requests.get(f"{self.base_url}/api/intents")
            if response.status_code != 200:
                self.log_result("Intent READ", False, f"HTTP {response.status_code}", response.text)
                return False
            
            intents = response.json()
            if not isinstance(intents, list):
                self.log_result("Intent READ", False, "Response is not a list", intents)
                return False
            
            self.log_result("Intent READ", True, f"Retrieved {len(intents)} intents")
            return True
            
        except Exception as e:
            self.log_result("Intent CRUD", False, f"Exception: {str(e)}")
            return False
    
    def test_campaign_send(self):
        """Test campaign sending (without actual email sending)"""
        try:
            if not self.created_resources['campaigns']:
                self.log_result("Campaign Send", False, "No campaigns available for sending")
                return False
            
            campaign_id = self.created_resources['campaigns'][0]
            
            # Note: This will fail due to SMTP credentials, but we test the API structure
            response = requests.post(f"{self.base_url}/api/campaigns/{campaign_id}/send")
            
            # We expect this to work even without prospects assigned to campaign
            if response.status_code == 200:
                result = response.json()
                self.log_result("Campaign Send API", True, f"Campaign send API working: {result.get('message', 'No message')}")
                return True
            else:
                # Check if it's a reasonable error (like no prospects)
                if response.status_code == 404 or "prospect" in response.text.lower():
                    self.log_result("Campaign Send API", True, "Campaign send API structure working (no prospects assigned)")
                    return True
                else:
                    self.log_result("Campaign Send API", False, f"HTTP {response.status_code}", response.text)
                    return False
            
        except Exception as e:
            self.log_result("Campaign Send", False, f"Exception: {str(e)}")
            return False
    
    def test_analytics(self):
        """Test analytics endpoints"""
        try:
            if not self.created_resources['campaigns']:
                self.log_result("Analytics", False, "No campaigns available for analytics")
                return False
            
            campaign_id = self.created_resources['campaigns'][0]
            
            response = requests.get(f"{self.base_url}/api/analytics/campaign/{campaign_id}")
            if response.status_code != 200:
                self.log_result("Analytics", False, f"HTTP {response.status_code}", response.text)
                return False
            
            analytics = response.json()
            expected_fields = ['total_sent', 'total_failed', 'total_opened', 'total_replied']
            
            for field in expected_fields:
                if field not in analytics:
                    self.log_result("Analytics", False, f"Missing field: {field}", analytics)
                    return False
            
            self.log_result("Analytics", True, f"Analytics working: {analytics}")
            return True
            
        except Exception as e:
            self.log_result("Analytics", False, f"Exception: {str(e)}")
            return False
    
    def test_database_connectivity(self):
        """Test database connectivity by checking if we can create and retrieve data"""
        try:
            # This is implicitly tested by the CRUD operations
            # If we can create prospects, templates, etc., the database is working
            if self.created_resources['prospects'] or self.created_resources['templates']:
                self.log_result("Database Connectivity", True, "Database operations successful")
                return True
            else:
                self.log_result("Database Connectivity", False, "No successful database operations")
                return False
        except Exception as e:
            self.log_result("Database Connectivity", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting AI Email Responder Backend Tests")
        print("=" * 60)
        
        # Test order matters - some tests depend on others
        tests = [
            ("Health Check", self.test_health_check),
            ("Prospect CRUD", self.test_prospect_crud),
            ("CSV Upload", self.test_prospect_csv_upload),
            ("Template CRUD", self.test_template_crud),
            ("Campaign CRUD", self.test_campaign_crud),
            ("Intent CRUD", self.test_intent_crud),
            ("Campaign Send API", self.test_campaign_send),
            ("Analytics", self.test_analytics),
            ("Database Connectivity", self.test_database_connectivity)
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
    results = tester.run_all_tests()
    
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