#!/usr/bin/env python3
"""
Simple Backend Test for AI Email Responder System
Tests all critical endpoints mentioned in the review request
"""

import requests
import json
from datetime import datetime
import sys
import time

# Backend URL
BACKEND_URL = "http://localhost:8001/api"

class AIEmailResponderTester:
    def __init__(self):
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.results = {}

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")

    def test_endpoint(self, name, method, endpoint, expected_status, data=None):
        """Test a single endpoint"""
        url = f"{BACKEND_URL}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        try:
            print(f"\n🔍 Testing {name}...")
            print(f"   URL: {url}")
            
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)

            success = response.status_code == expected_status
            details = f"Status: {response.status_code}"
            
            if not success:
                details += f" (Expected: {expected_status})"
                try:
                    error_data = response.json()
                    details += f" - {error_data.get('detail', 'No error details')}"
                except:
                    details += f" - {response.text[:200]}"

            self.log_test(name, success, details)
            
            if success:
                try:
                    return True, response.json()
                except:
                    return True, response.text
            else:
                return False, details

        except Exception as e:
            self.log_test(name, False, f"Exception: {str(e)}")
            return False, str(e)

    def run_comprehensive_test(self):
        """Run all critical tests"""
        print("=" * 80)
        print("🚀 AI EMAIL RESPONDER BACKEND TEST")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        
        start_time = time.time()
        
        # 1. Health Check
        print("\n🔍 Testing Health Check...")
        success, response = self.test_endpoint("Health Check", "GET", "health", 200)
        if not success:
            print("❌ CRITICAL: Backend health check failed!")
            return False
        
        # 2. Authentication
        print("\n🔍 Testing Authentication...")
        success, response = self.test_endpoint(
            "Login with valid credentials",
            "POST",
            "auth/login",
            200,
            data={"username": "testuser", "password": "testpass123"}
        )
        
        if success and isinstance(response, dict) and 'access_token' in response:
            self.token = response['access_token']
            print(f"   Token obtained: {self.token[:20]}...")
        else:
            print("❌ Authentication failed - stopping tests")
            return False
        
        # Test user info
        self.test_endpoint("Get user info", "GET", "auth/me", 200)
        
        # 3. Core Data Endpoints
        print("\n🔍 Testing Core Data Endpoints...")
        
        # Campaigns
        success, campaigns = self.test_endpoint("Get campaigns", "GET", "campaigns", 200)
        if success:
            print(f"   Found {len(campaigns)} campaigns")
            self.results['campaigns'] = campaigns
        
        # Prospects
        success, prospects = self.test_endpoint("Get prospects", "GET", "prospects", 200)
        if success:
            print(f"   Found {len(prospects)} prospects")
            self.results['prospects'] = prospects
        
        # Templates
        success, templates = self.test_endpoint("Get templates", "GET", "templates", 200)
        if success:
            print(f"   Found {len(templates)} templates")
            self.results['templates'] = templates
        
        # Intents
        success, intents = self.test_endpoint("Get intents", "GET", "intents", 200)
        if success:
            print(f"   Found {len(intents)} intents")
            self.results['intents'] = intents
        
        # Email Providers
        success, providers = self.test_endpoint("Get email providers", "GET", "email-providers", 200)
        if success:
            print(f"   Found {len(providers)} email providers")
            self.results['email_providers'] = providers
        
        # Lists
        success, lists = self.test_endpoint("Get lists", "GET", "lists", 200)
        if success:
            print(f"   Found {len(lists)} lists")
            self.results['lists'] = lists
        
        # 4. AI Features
        print("\n🔍 Testing AI Features...")
        
        # AI Agent Chat
        chat_data = {
            "message": "Hello, test message",
            "conversation_id": "test_conversation"
        }
        self.test_endpoint("AI Agent chat", "POST", "ai-agent/chat", 200, data=chat_data)
        
        # AI Prospecting
        search_data = {
            "query": "Find CTOs at software companies",
            "limit": 10
        }
        self.test_endpoint("AI Prospecting search", "POST", "ai-prospecting/search", 200, data=search_data)
        
        # Industries
        self.test_endpoint("Get industries", "GET", "industries", 200)
        
        # 5. Services Status
        print("\n🔍 Testing Services Status...")
        success, services = self.test_endpoint("Get services status", "GET", "services/status", 200)
        if success:
            self.results['services'] = services
            if 'services' in services:
                for service_name, service_info in services['services'].items():
                    status = service_info.get('status', 'unknown')
                    print(f"   {service_name}: {status}")
        
        # 6. Dashboard Metrics
        self.test_endpoint("Get dashboard metrics", "GET", "real-time/dashboard-metrics", 200)
        
        # 7. Test CRUD Operations
        print("\n🔍 Testing CRUD Operations...")
        
        # Create a test campaign
        campaign_data = {
            "name": f"Test Campaign {datetime.now().strftime('%H%M%S')}",
            "template_id": "test_template_id",
            "list_ids": [],
            "max_emails": 100,
            "follow_up_enabled": True,
            "follow_up_intervals": [3, 7, 14]
        }
        
        success, create_response = self.test_endpoint(
            "Create campaign",
            "POST",
            "campaigns",
            200,
            data=campaign_data
        )
        
        campaign_id = None
        if success and isinstance(create_response, dict):
            campaign_id = create_response.get('id')
            print(f"   Created campaign with ID: {campaign_id}")
        
        # Create a test list
        list_data = {
            "name": f"Test List {datetime.now().strftime('%H%M%S')}",
            "description": "Test list for API testing",
            "color": "#3B82F6",
            "tags": ["test", "api"]
        }
        
        self.test_endpoint("Create list", "POST", "lists", 200, data=list_data)
        
        # Create a test email provider
        provider_data = {
            "name": f"Test Provider {datetime.now().strftime('%H%M%S')}",
            "provider_type": "gmail",
            "email_address": "test@example.com",
            "display_name": "Test Provider",
            "smtp_host": "smtp.gmail.com",
            "smtp_port": 587,
            "smtp_username": "test@example.com",
            "smtp_password": "test_password",
            "skip_connection_test": True
        }
        
        self.test_endpoint("Create email provider", "POST", "email-providers", 200, data=provider_data)
        
        end_time = time.time()
        
        print("\n" + "=" * 80)
        print(f"🏁 Testing completed in {end_time - start_time:.2f} seconds")
        self.print_summary()
        
        return self.tests_passed >= (self.tests_run * 0.8)  # 80% pass rate

    def print_summary(self):
        """Print test summary"""
        print(f"\n📊 Test Summary:")
        print(f"   Total Tests: {self.tests_run}")
        print(f"   Passed: {self.tests_passed}")
        print(f"   Failed: {self.tests_run - self.tests_passed}")
        print(f"   Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "   Success Rate: 0%")
        
        # Data Summary
        if self.results:
            print(f"\n📋 Data Summary:")
            for key, value in self.results.items():
                if isinstance(value, list):
                    print(f"   {key}: {len(value)} items")
                elif isinstance(value, dict) and 'services' in value:
                    print(f"   Services Status: {value.get('overall_status', 'unknown')}")

def main():
    """Main function"""
    tester = AIEmailResponderTester()
    success = tester.run_comprehensive_test()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())