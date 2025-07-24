#!/usr/bin/env python3
"""
Simple Backend API Testing for AI Email Responder
Tests the actual endpoints that exist in the backend
"""

import requests
import json
import sys
from datetime import datetime

class SimpleBackendTester:
    def __init__(self, base_url="https://57e8cdec-8da4-4e0b-bab5-4b707f4b9e38.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            self.failed_tests.append(f"{name}: {details}")
            print(f"❌ {name} - FAILED: {details}")

    def make_request(self, method, endpoint, data=None, expected_status=200):
        """Make HTTP request with proper headers"""
        url = f"{self.base_url}/api/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)
            
            success = response.status_code == expected_status
            return success, response.status_code, response.json() if response.content else {}
            
        except requests.exceptions.RequestException as e:
            return False, 0, {"error": str(e)}
        except json.JSONDecodeError:
            return False, response.status_code, {"error": "Invalid JSON response"}

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting AI Email Responder API Tests")
        print(f"📡 Testing against: {self.base_url}")
        print("=" * 60)

        # Test health check
        print("\n🏥 Testing Health Check...")
        success, status, response = self.make_request('GET', 'health')
        if success and 'status' in response:
            self.log_test("Health Check", True)
        else:
            self.log_test("Health Check", False, f"Status: {status}, Response: {response}")

        # Test authentication
        print("\n🔐 Testing Authentication...")
        login_data = {"username": "testuser", "password": "testpass123"}
        success, status, response = self.make_request('POST', 'auth/login', login_data)
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.log_test("Login with valid credentials", True)
            
            # Test get user info
            success, status, response = self.make_request('GET', 'auth/me')
            if success and 'username' in response:
                self.log_test("Get user info", True)
            else:
                self.log_test("Get user info", False, f"Status: {status}")
        else:
            self.log_test("Login with valid credentials", False, f"Status: {status}")

        # Test invalid login
        login_data = {"username": "wronguser", "password": "wrongpass"}
        success, status, response = self.make_request('POST', 'auth/login', login_data, expected_status=401)
        if success:
            self.log_test("Login with invalid credentials (should fail)", True)
        else:
            self.log_test("Login with invalid credentials (should fail)", False, f"Expected 401, got {status}")

        # Test email providers
        print("\n📧 Testing Email Providers...")
        success, status, response = self.make_request('GET', 'email-providers')
        if success and isinstance(response, list):
            self.log_test("Get email providers", True)
            print(f"   Found {len(response)} email providers")
        else:
            self.log_test("Get email providers", False, f"Status: {status}")

        # Test create email provider
        new_provider = {
            "name": "Test Provider",
            "provider_type": "gmail",
            "email_address": "test@gmail.com",
            "display_name": "Test Display",
            "smtp_host": "smtp.gmail.com",
            "smtp_port": 587,
            "smtp_username": "test@gmail.com",
            "smtp_password": "testpass",
            "smtp_use_tls": True,
            "imap_host": "imap.gmail.com",
            "imap_port": 993,
            "imap_username": "test@gmail.com",
            "imap_password": "testpass",
            "daily_send_limit": 500,
            "hourly_send_limit": 50,
            "is_default": False,
            "skip_connection_test": True
        }
        
        success, status, response = self.make_request('POST', 'email-providers', new_provider)
        if success and 'id' in response:
            provider_id = response['id']
            self.log_test("Create email provider", True)
            
            # Test update email provider
            updated_provider = new_provider.copy()
            updated_provider['name'] = "Updated Test Provider"
            success, status, response = self.make_request('PUT', f'email-providers/{provider_id}', updated_provider)
            if success:
                self.log_test("Update email provider", True)
            else:
                self.log_test("Update email provider", False, f"Status: {status}")
            
            # Test connection test
            success, status, response = self.make_request('POST', f'email-providers/{provider_id}/test')
            if success and 'message' in response:
                self.log_test("Test email provider connection", True)
            else:
                self.log_test("Test email provider connection", False, f"Status: {status}")
            
            # Test set default provider
            success, status, response = self.make_request('POST', f'email-providers/{provider_id}/set-default')
            if success and 'message' in response:
                self.log_test("Set default email provider", True)
            else:
                self.log_test("Set default email provider", False, f"Status: {status}")
            
            # Test delete email provider
            success, status, response = self.make_request('DELETE', f'email-providers/{provider_id}')
            if success and 'message' in response:
                self.log_test("Delete email provider", True)
            else:
                self.log_test("Delete email provider", False, f"Status: {status}")
        else:
            self.log_test("Create email provider", False, f"Status: {status}")

        # Test campaigns
        print("\n📋 Testing Campaigns...")
        success, status, response = self.make_request('GET', 'campaigns')
        if success and isinstance(response, list):
            self.log_test("Get campaigns", True)
            print(f"   Found {len(response)} campaigns")
        else:
            self.log_test("Get campaigns", False, f"Status: {status}")

        # Test create campaign
        new_campaign = {
            "name": "Test Campaign",
            "template_id": "1",
            "list_ids": ["1", "2"],
            "email_provider_id": "1",
            "max_emails": 1000,
            "schedule_type": "immediate",
            "follow_up_enabled": True,
            "follow_up_intervals": [3, 7, 14],
            "follow_up_templates": ["2", "3"]
        }
        
        success, status, response = self.make_request('POST', 'campaigns', new_campaign)
        if success and 'id' in response:
            self.log_test("Create campaign", True)
        else:
            self.log_test("Create campaign", False, f"Status: {status}")

        # Test supporting endpoints
        print("\n🔧 Testing Supporting Endpoints...")
        
        # Templates
        success, status, response = self.make_request('GET', 'templates')
        if success and isinstance(response, list):
            self.log_test("Get templates", True)
            print(f"   Found {len(response)} templates")
        else:
            self.log_test("Get templates", False, f"Status: {status}")

        # Lists
        success, status, response = self.make_request('GET', 'lists')
        if success and isinstance(response, list):
            self.log_test("Get lists", True)
            print(f"   Found {len(response)} lists")
        else:
            self.log_test("Get lists", False, f"Status: {status}")

        # Prospects
        success, status, response = self.make_request('GET', 'prospects')
        if success and isinstance(response, list):
            self.log_test("Get prospects", True)
            print(f"   Found {len(response)} prospects")
        else:
            self.log_test("Get prospects", False, f"Status: {status}")

        # Intents
        success, status, response = self.make_request('GET', 'intents')
        if success and isinstance(response, list):
            self.log_test("Get intents", True)
            print(f"   Found {len(response)} intents")
        else:
            self.log_test("Get intents", False, f"Status: {status}")

        # Test analytics
        print("\n📊 Testing Analytics...")
        success, status, response = self.make_request('GET', 'analytics/campaign/1')
        if success and 'total_sent' in response:
            self.log_test("Get campaign analytics", True)
        else:
            self.log_test("Get campaign analytics", False, f"Status: {status}")

        # Test real-time dashboard
        success, status, response = self.make_request('GET', 'real-time/dashboard-metrics')
        if success and 'metrics' in response:
            self.log_test("Get real-time dashboard metrics", True)
        else:
            self.log_test("Get real-time dashboard metrics", False, f"Status: {status}")

        return True

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {len(self.failed_tests)}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.failed_tests:
            print("\n❌ FAILED TESTS:")
            for failure in self.failed_tests:
                print(f"   • {failure}")
        
        print(f"\n🕒 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    tester = SimpleBackendTester()
    
    try:
        tester.run_all_tests()
        tester.print_summary()
        
        # Return appropriate exit code
        return 0 if len(tester.failed_tests) == 0 else 1
        
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())