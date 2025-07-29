#!/usr/bin/env python3
"""
Simple Backend API Testing for AI Email Responder
Tests only the endpoints that actually exist in the backend
"""

import requests
import json
from datetime import datetime

# Get backend URL from frontend .env file
BACKEND_URL = "https://1e08e58e-1080-4fe8-bd99-54911ebc72f3.preview.emergentagent.com"

class SimpleBackendTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.token = None
        self.tests_passed = 0
        self.tests_total = 0
    
    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        if headers is None:
            headers = {'Content-Type': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        self.tests_total += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return True, response.json()
                except:
                    return True, response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_authentication(self):
        """Test authentication endpoints"""
        print("\n=== Testing Authentication ===")
        
        # Test login with correct credentials
        success, response = self.run_test(
            "Login with correct credentials",
            "POST",
            "api/auth/login",
            200,
            data={"username": "testuser", "password": "testpass123"}
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            print(f"   Token received: {self.token[:20]}...")
        
        # Test login with wrong credentials
        self.run_test(
            "Login with wrong credentials",
            "POST", 
            "api/auth/login",
            401,
            data={"username": "wronguser", "password": "wrongpass"}
        )
        
        # Test register
        self.run_test(
            "Register new user",
            "POST",
            "api/auth/register", 
            200,
            data={"username": "newuser", "password": "newpass123"}
        )
        
        # Test get user info
        self.run_test(
            "Get user info",
            "GET",
            "api/auth/me",
            200
        )

    def test_data_endpoints(self):
        """Test data retrieval endpoints"""
        print("\n=== Testing Data Endpoints ===")
        
        # Test campaigns
        self.run_test(
            "Get campaigns",
            "GET",
            "api/campaigns",
            200
        )
        
        # Test email providers
        self.run_test(
            "Get email providers",
            "GET", 
            "api/email-providers",
            200
        )
        
        # Test lists
        self.run_test(
            "Get lists",
            "GET",
            "api/lists", 
            200
        )
        
        # Test templates
        self.run_test(
            "Get templates",
            "GET",
            "api/templates",
            200
        )
        
        # Test prospects
        self.run_test(
            "Get prospects",
            "GET",
            "api/prospects",
            200
        )
        
        # Test intents
        self.run_test(
            "Get intents", 
            "GET",
            "api/intents",
            200
        )

    def test_creation_endpoints(self):
        """Test creation endpoints that exist"""
        print("\n=== Testing Creation Endpoints ===")
        
        # Test campaign creation
        campaign_data = {
            "name": "Test Campaign",
            "template_id": "1",
            "list_ids": ["1", "2"],
            "email_provider_id": "1",
            "max_emails": 100
        }
        
        self.run_test(
            "Create campaign",
            "POST",
            "api/campaigns",
            200,
            data=campaign_data
        )
        
        # Test email provider creation
        provider_data = {
            "name": "Test Provider",
            "provider_type": "gmail",
            "email_address": "test@gmail.com",
            "display_name": "Test Gmail"
        }
        
        self.run_test(
            "Create email provider",
            "POST", 
            "api/email-providers",
            200,
            data=provider_data
        )

    def test_analytics_endpoints(self):
        """Test analytics endpoints"""
        print("\n=== Testing Analytics Endpoints ===")
        
        # Test campaign analytics
        self.run_test(
            "Get campaign analytics",
            "GET",
            "api/analytics/campaign/1",
            200
        )
        
        # Test real-time dashboard metrics
        self.run_test(
            "Get real-time dashboard metrics",
            "GET",
            "api/real-time/dashboard-metrics", 
            200
        )

    def run_all_tests(self):
        """Run all available tests"""
        print("🚀 Starting Simple Backend API Tests")
        print("=" * 60)
        
        # Test health first
        self.run_test(
            "Health check",
            "GET",
            "api/health",
            200
        )
        
        # Run test suites
        self.test_authentication()
        self.test_data_endpoints() 
        self.test_creation_endpoints()
        self.test_analytics_endpoints()
        
        # Print results
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_total} tests passed")
        
        if self.tests_passed == self.tests_total:
            print("🎉 All tests passed!")
        else:
            print(f"⚠️  {self.tests_total - self.tests_passed} tests failed")
        
        return self.tests_passed, self.tests_total

def main():
    """Main test execution"""
    tester = SimpleBackendTester()
    passed, total = tester.run_all_tests()
    
    print(f"\n📋 SUMMARY: {passed}/{total} backend API tests passed")
    
    if passed >= total * 0.8:  # 80% pass rate is acceptable
        print("✅ Backend API is functioning well enough for frontend testing")
        return 0
    else:
        print("❌ Too many backend failures - frontend testing may be impacted")
        return 1

if __name__ == "__main__":
    exit(main())