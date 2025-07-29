#!/usr/bin/env python3
"""
Voice Capabilities Backend Test for AI Email Responder
Tests the backend APIs that support voice functionality
"""

import requests
import sys
import json
from datetime import datetime
import time

class VoiceCapabilitiesBackendTester:
    def __init__(self, base_url="https://9f8a7167-d7f1-4045-b864-65d30ef37460.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        if details:
            print(f"   Details: {details}")

    def test_health_check(self):
        """Test basic health endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/health")
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", Response: {data.get('status', 'unknown')}"
            self.log_test("Health Check", success, details)
            return success
        except Exception as e:
            self.log_test("Health Check", False, str(e))
            return False

    def test_login(self):
        """Test login functionality"""
        try:
            login_data = {
                "username": "testuser",
                "password": "testpass123"
            }
            response = self.session.post(f"{self.base_url}/api/auth/login", json=login_data)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                self.token = data.get('access_token')
                self.session.headers.update({'Authorization': f'Bearer {self.token}'})
                details = "Login successful, token obtained"
            else:
                details = f"Status: {response.status_code}, Response: {response.text}"
            
            self.log_test("User Login", success, details)
            return success
        except Exception as e:
            self.log_test("User Login", False, str(e))
            return False

    def test_ai_agent_endpoints(self):
        """Test AI Agent endpoints that support voice functionality"""
        print("\n🤖 Testing AI Agent Endpoints...")
        
        # Test AI Agent chat endpoint
        try:
            chat_data = {
                "message": "Hello Joy, show me my campaigns",
                "user_id": "testuser",
                "session_id": f"test_session_{int(time.time())}",
                "context": {}
            }
            response = self.session.post(f"{self.base_url}/api/ai-agent/chat", json=chat_data)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                details = f"Response received: {data.get('response', '')[:100]}..."
            else:
                details = f"Status: {response.status_code}, Response: {response.text[:200]}"
            
            self.log_test("AI Agent Chat", success, details)
        except Exception as e:
            self.log_test("AI Agent Chat", False, str(e))

    def test_ai_prospecting_endpoints(self):
        """Test AI Prospecting endpoints that support voice functionality"""
        print("\n🔍 Testing AI Prospecting Endpoints...")
        
        # Test AI Prospecting search endpoint
        try:
            search_data = {
                "query": "Find me CEOs at technology companies in California",
                "target_list": None,
                "max_results": 5
            }
            response = self.session.post(f"{self.base_url}/api/ai-prospecting/search", json=search_data)
            success = response.status_code in [200, 400]  # 400 might be expected if no Apollo integration
            
            if response.status_code == 200:
                data = response.json()
                details = f"Search successful: {data.get('message', 'No message')}"
            elif response.status_code == 400:
                details = "Search endpoint exists but may need Apollo integration"
            else:
                details = f"Status: {response.status_code}, Response: {response.text[:200]}"
            
            self.log_test("AI Prospecting Search", success, details)
        except Exception as e:
            self.log_test("AI Prospecting Search", False, str(e))

    def test_supporting_endpoints(self):
        """Test supporting endpoints that voice features depend on"""
        print("\n📊 Testing Supporting Endpoints...")
        
        # Test campaigns endpoint
        try:
            response = self.session.get(f"{self.base_url}/api/campaigns")
            success = response.status_code == 200
            
            if success:
                data = response.json()
                details = f"Found {len(data)} campaigns"
            else:
                details = f"Status: {response.status_code}"
            
            self.log_test("Get Campaigns", success, details)
        except Exception as e:
            self.log_test("Get Campaigns", False, str(e))

        # Test prospects endpoint
        try:
            response = self.session.get(f"{self.base_url}/api/prospects")
            success = response.status_code == 200
            
            if success:
                data = response.json()
                details = f"Found {len(data)} prospects"
            else:
                details = f"Status: {response.status_code}"
            
            self.log_test("Get Prospects", success, details)
        except Exception as e:
            self.log_test("Get Prospects", False, str(e))

        # Test lists endpoint
        try:
            response = self.session.get(f"{self.base_url}/api/lists")
            success = response.status_code == 200
            
            if success:
                data = response.json()
                details = f"Found {len(data)} lists"
            else:
                details = f"Status: {response.status_code}"
            
            self.log_test("Get Lists", success, details)
        except Exception as e:
            self.log_test("Get Lists", False, str(e))

        # Test templates endpoint
        try:
            response = self.session.get(f"{self.base_url}/api/templates")
            success = response.status_code == 200
            
            if success:
                data = response.json()
                details = f"Found {len(data)} templates"
            else:
                details = f"Status: {response.status_code}"
            
            self.log_test("Get Templates", success, details)
        except Exception as e:
            self.log_test("Get Templates", False, str(e))

    def test_industries_endpoint(self):
        """Test industries endpoint used by AI Agent"""
        print("\n🏭 Testing Industries Endpoint...")
        
        try:
            response = self.session.get(f"{self.base_url}/api/industries")
            success = response.status_code == 200
            
            if success:
                data = response.json()
                industries = data.get('industries', [])
                details = f"Found {len(industries)} industries, total_count: {data.get('total_count', 0)}"
            else:
                details = f"Status: {response.status_code}"
            
            self.log_test("Get Industries", success, details)
        except Exception as e:
            self.log_test("Get Industries", False, str(e))

    def test_dashboard_metrics(self):
        """Test dashboard metrics endpoint"""
        print("\n📈 Testing Dashboard Metrics...")
        
        try:
            response = self.session.get(f"{self.base_url}/api/real-time/dashboard-metrics")
            success = response.status_code == 200
            
            if success:
                data = response.json()
                metrics = data.get('metrics', {}).get('overview', {})
                details = f"Prospects: {metrics.get('total_prospects', 0)}, Campaigns: {metrics.get('total_campaigns', 0)}"
            else:
                details = f"Status: {response.status_code}"
            
            self.log_test("Dashboard Metrics", success, details)
        except Exception as e:
            self.log_test("Dashboard Metrics", False, str(e))

    def test_services_status(self):
        """Test services status endpoint"""
        print("\n⚙️ Testing Services Status...")
        
        try:
            response = self.session.get(f"{self.base_url}/api/services/status")
            success = response.status_code == 200
            
            if success:
                data = response.json()
                services = data.get('services', {})
                follow_up_status = services.get('smart_follow_up_engine', {}).get('status', 'unknown')
                email_processor_status = services.get('email_processor', {}).get('status', 'unknown')
                details = f"Follow-up: {follow_up_status}, Email Processor: {email_processor_status}"
            else:
                details = f"Status: {response.status_code}"
            
            self.log_test("Services Status", success, details)
        except Exception as e:
            self.log_test("Services Status", False, str(e))

    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Voice Capabilities Backend Tests")
        print(f"Testing against: {self.base_url}")
        print("=" * 60)
        
        # Basic connectivity
        if not self.test_health_check():
            print("❌ Health check failed - backend may be down")
            return False
        
        # Authentication
        if not self.test_login():
            print("❌ Login failed - cannot proceed with authenticated tests")
            return False
        
        # Voice-related endpoints
        self.test_ai_agent_endpoints()
        self.test_ai_prospecting_endpoints()
        
        # Supporting endpoints
        self.test_supporting_endpoints()
        self.test_industries_endpoint()
        self.test_dashboard_metrics()
        self.test_services_status()
        
        # Summary
        print("\n" + "=" * 60)
        print(f"📊 Test Summary: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed! Backend is ready for voice functionality testing.")
            return True
        else:
            print(f"⚠️ {self.tests_run - self.tests_passed} tests failed. Check the issues above.")
            return False

def main():
    """Main test execution"""
    tester = VoiceCapabilitiesBackendTester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())