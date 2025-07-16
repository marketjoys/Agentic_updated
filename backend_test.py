#!/usr/bin/env python3
"""
Focused Backend API Testing for AI Email Responder
Tests the specific issues that were reported as broken
"""

import requests
import json
import io
import pandas as pd
from datetime import datetime
import time
import os

# Get backend URL from frontend .env file
BACKEND_URL = "https://f1e48876-6c4d-487d-9bfb-9b4e5d78e5b2.preview.emergentagent.com"  # Using the configured backend URL

class BackendTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.test_results = {}
        self.created_resources = {
            'prospects': [],
            'templates': [],
            'lists': [],
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
    
    def test_prospect_management(self):
        """Test prospect management functionality"""
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
            
            self.log_result("Prospect READ", True, f"Retrieved {len(prospects)} prospects")
            
            # Test CSV upload
            csv_data = """email,first_name,last_name,company,phone
sarah.johnson@innovate.com,Sarah,Johnson,Innovate Solutions,+1-555-0124
mike.wilson@startup.io,Mike,Wilson,Startup.io,+1-555-0125
lisa.chen@enterprise.com,Lisa,Chen,Enterprise Corp,+1-555-0126"""
            
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
            self.log_result("Prospect Management", False, f"Exception: {str(e)}")
            return False
    
    def test_list_management(self):
        """Test list management and prospect-to-list association"""
        try:
            # Create a list
            list_data = {
                "name": "Test List",
                "description": "A test list for API testing",
                "color": "#3B82F6",
                "tags": ["test", "api"]
            }
            
            response = requests.post(f"{self.base_url}/api/lists", json=list_data)
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
            
            # Get prospects to add to the list
            response = requests.get(f"{self.base_url}/api/prospects")
            if response.status_code != 200:
                self.log_result("Get Prospects for List", False, f"HTTP {response.status_code}", response.text)
                return False
            
            prospects = response.json()
            if not prospects or len(prospects) == 0:
                self.log_result("Get Prospects for List", False, "No prospects available")
                return False
            
            # Select up to 3 prospects to add to the list
            prospect_ids = [p['id'] for p in prospects[:min(3, len(prospects))]]
            
            # Add prospects to the list
            response = requests.post(f"{self.base_url}/api/lists/{list_id}/prospects", json=prospect_ids)
            if response.status_code != 200:
                self.log_result("Add Prospects to List", False, f"HTTP {response.status_code}", response.text)
                return False
            
            result = response.json()
            self.log_result("Add Prospects to List", True, f"Added prospects to list: {result.get('message', '')}")
            
            # Verify the list now contains the prospects
            response = requests.get(f"{self.base_url}/api/lists/{list_id}")
            if response.status_code != 200:
                self.log_result("Verify List Contents", False, f"HTTP {response.status_code}", response.text)
                return False
            
            updated_list = response.json()
            if 'prospect_count' not in updated_list:
                self.log_result("Verify List Contents", False, "No prospect_count in response", updated_list)
                return False
            
            if updated_list['prospect_count'] == 0:
                self.log_result("Verify List Contents", False, "List shows 0 prospects after adding them")
                return False
            
            self.log_result("Verify List Contents", True, f"List now contains {updated_list['prospect_count']} prospects")
            return True
            
        except Exception as e:
            self.log_result("List Management", False, f"Exception: {str(e)}")
            return False
    
    def test_intent_management(self):
        """Test intent management and template association"""
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
    results = tester.run_focused_tests()
    
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