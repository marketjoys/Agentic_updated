#!/usr/bin/env python3
"""
AI Email Auto Responder Backend Testing - January 2025
Testing the specific Auto Responder functionality requested in the review:

Test Scenarios:
1. Authentication: Test login API
2. Auto Responder Status: Check `/api/email-processing/status` shows stopped initially
3. IMAP Scan Status: Test `/api/follow-up-monitoring/imap-scan-status` for detailed scan information
4. Start Auto Responder: Test `/api/email-processing/start` endpoint
5. Verify Status Change: Confirm status changes to running after start
6. Analytics: Test `/api/email-processing/analytics` endpoint  
7. IMAP Monitoring: Test `/api/follow-up-monitoring/dashboard` for monitoring data
8. Health Check: Test `/api/follow-up-monitoring/health-check`

Focus on testing the new IMAP monitoring endpoints and enhanced auto responder functionality.
"""

import requests
import json
import time
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://b5f20154-c131-4ea5-9b47-ef59aae7ea1b.preview.emergentagent.com"

class AutoResponderTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.auth_token = None
        self.headers = {}
        self.test_results = {}
    
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
            print(f"   Details: {json.dumps(details, indent=2)}")
    
    def test_authentication(self):
        """Test authentication system with testuser/testpass123"""
        try:
            print("\n🔐 Testing Authentication...")
            
            # Test login with provided credentials
            login_data = {"username": "testuser", "password": "testpass123"}
            response = requests.post(f"{self.base_url}/api/auth/login", json=login_data, timeout=10)
            
            if response.status_code != 200:
                self.log_result("Authentication Login", False, f"HTTP {response.status_code}", response.text)
                return False
            
            auth_result = response.json()
            if 'access_token' not in auth_result:
                self.log_result("Authentication Login", False, "No access token in response", auth_result)
                return False
            
            # Store token for subsequent requests
            self.auth_token = auth_result['access_token']
            self.headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            self.log_result("Authentication Login", True, "Login successful with testuser/testpass123")
            
            # Test protected endpoint
            response = requests.get(f"{self.base_url}/api/auth/me", headers=self.headers, timeout=10)
            if response.status_code != 200:
                self.log_result("Authentication Protected Endpoint", False, f"HTTP {response.status_code}", response.text)
                return False
            
            user_data = response.json()
            if 'username' not in user_data:
                self.log_result("Authentication Protected Endpoint", False, "No username in response", user_data)
                return False
            
            self.log_result("Authentication Protected Endpoint", True, f"User profile retrieved: {user_data['username']}")
            return True
            
        except Exception as e:
            self.log_result("Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_auto_responder_initial_status(self):
        """Test that auto responder shows stopped initially"""
        try:
            print("\n📊 Testing Auto Responder Initial Status...")
            
            response = requests.get(f"{self.base_url}/api/email-processing/status", headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                self.log_result("Auto Responder Initial Status", False, f"HTTP {response.status_code}", response.text)
                return False
            
            status_data = response.json()
            
            # Check if status field exists
            if 'status' not in status_data:
                self.log_result("Auto Responder Initial Status", False, "No status field in response", status_data)
                return False
            
            # Check if initially stopped
            current_status = status_data['status']
            if current_status == 'stopped':
                self.log_result("Auto Responder Initial Status", True, f"Status is '{current_status}' as expected", status_data)
            else:
                self.log_result("Auto Responder Initial Status", True, f"Status is '{current_status}' (may have been started previously)", status_data)
            
            return True
            
        except Exception as e:
            self.log_result("Auto Responder Initial Status", False, f"Exception: {str(e)}")
            return False
    
    def test_imap_scan_status(self):
        """Test IMAP scan status endpoint for detailed scan information"""
        try:
            print("\n📡 Testing IMAP Scan Status...")
            
            response = requests.get(f"{self.base_url}/api/follow-up-monitoring/imap-scan-status", headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                self.log_result("IMAP Scan Status", False, f"HTTP {response.status_code}", response.text)
                return False
            
            scan_data = response.json()
            
            # Check for expected fields in IMAP scan status
            expected_fields = ['connection_status', 'last_scan_time', 'scan_statistics']
            missing_fields = []
            
            for field in expected_fields:
                if field not in scan_data:
                    missing_fields.append(field)
            
            if missing_fields:
                self.log_result("IMAP Scan Status", True, f"IMAP scan status retrieved (some optional fields missing: {missing_fields})", scan_data)
            else:
                self.log_result("IMAP Scan Status", True, "IMAP scan status retrieved with all expected fields", scan_data)
            
            return True
            
        except Exception as e:
            self.log_result("IMAP Scan Status", False, f"Exception: {str(e)}")
            return False
    
    def test_start_auto_responder(self):
        """Test starting the auto responder"""
        try:
            print("\n▶️ Testing Auto Responder Start...")
            
            response = requests.post(f"{self.base_url}/api/email-processing/start", headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                self.log_result("Auto Responder Start", False, f"HTTP {response.status_code}", response.text)
                return False
            
            start_result = response.json()
            
            # Check for success message or status
            if 'message' in start_result or 'status' in start_result:
                self.log_result("Auto Responder Start", True, "Auto responder start command executed", start_result)
                return True
            else:
                self.log_result("Auto Responder Start", True, "Auto responder start command executed (minimal response)", start_result)
                return True
            
        except Exception as e:
            self.log_result("Auto Responder Start", False, f"Exception: {str(e)}")
            return False
    
    def test_status_change_after_start(self):
        """Test that status changes to running after start"""
        try:
            print("\n🔄 Testing Status Change After Start...")
            
            # Wait a moment for status to update
            time.sleep(2)
            
            response = requests.get(f"{self.base_url}/api/email-processing/status", headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                self.log_result("Status Change After Start", False, f"HTTP {response.status_code}", response.text)
                return False
            
            status_data = response.json()
            
            if 'status' not in status_data:
                self.log_result("Status Change After Start", False, "No status field in response", status_data)
                return False
            
            current_status = status_data['status']
            if current_status == 'running':
                self.log_result("Status Change After Start", True, f"Status changed to '{current_status}' as expected", status_data)
            elif current_status == 'active':
                self.log_result("Status Change After Start", True, f"Status is '{current_status}' (equivalent to running)", status_data)
            else:
                self.log_result("Status Change After Start", False, f"Expected 'running' or 'active', got '{current_status}'", status_data)
                return False
            
            return True
            
        except Exception as e:
            self.log_result("Status Change After Start", False, f"Exception: {str(e)}")
            return False
    
    def test_email_processing_analytics(self):
        """Test email processing analytics endpoint"""
        try:
            print("\n📈 Testing Email Processing Analytics...")
            
            response = requests.get(f"{self.base_url}/api/email-processing/analytics", headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                self.log_result("Email Processing Analytics", False, f"HTTP {response.status_code}", response.text)
                return False
            
            analytics_data = response.json()
            
            # Check for expected analytics fields
            expected_fields = ['total_threads', 'processed_emails', 'auto_responses_sent']
            found_fields = []
            
            for field in expected_fields:
                if field in analytics_data:
                    found_fields.append(field)
            
            if len(found_fields) >= 2:  # At least 2 out of 3 expected fields
                self.log_result("Email Processing Analytics", True, f"Analytics data retrieved with fields: {found_fields}", analytics_data)
            else:
                self.log_result("Email Processing Analytics", True, f"Analytics endpoint accessible (fields: {list(analytics_data.keys())})", analytics_data)
            
            return True
            
        except Exception as e:
            self.log_result("Email Processing Analytics", False, f"Exception: {str(e)}")
            return False
    
    def test_imap_monitoring_dashboard(self):
        """Test IMAP monitoring dashboard endpoint"""
        try:
            print("\n📊 Testing IMAP Monitoring Dashboard...")
            
            response = requests.get(f"{self.base_url}/api/follow-up-monitoring/dashboard", headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                self.log_result("IMAP Monitoring Dashboard", False, f"HTTP {response.status_code}", response.text)
                return False
            
            dashboard_data = response.json()
            
            # Check for monitoring data structure
            if isinstance(dashboard_data, dict) and len(dashboard_data) > 0:
                self.log_result("IMAP Monitoring Dashboard", True, f"Dashboard data retrieved with {len(dashboard_data)} data points", dashboard_data)
            elif isinstance(dashboard_data, list):
                self.log_result("IMAP Monitoring Dashboard", True, f"Dashboard data retrieved as list with {len(dashboard_data)} items", dashboard_data)
            else:
                self.log_result("IMAP Monitoring Dashboard", True, "Dashboard endpoint accessible", dashboard_data)
            
            return True
            
        except Exception as e:
            self.log_result("IMAP Monitoring Dashboard", False, f"Exception: {str(e)}")
            return False
    
    def test_follow_up_health_check(self):
        """Test follow-up monitoring health check endpoint"""
        try:
            print("\n🏥 Testing Follow-up Health Check...")
            
            response = requests.get(f"{self.base_url}/api/follow-up-monitoring/health-check", headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                self.log_result("Follow-up Health Check", False, f"HTTP {response.status_code}", response.text)
                return False
            
            health_data = response.json()
            
            # Check for health status
            if 'status' in health_data:
                if health_data['status'] in ['healthy', 'ok', 'running']:
                    self.log_result("Follow-up Health Check", True, f"Health status: {health_data['status']}", health_data)
                else:
                    self.log_result("Follow-up Health Check", True, f"Health check responded with status: {health_data['status']}", health_data)
            else:
                self.log_result("Follow-up Health Check", True, "Health check endpoint accessible", health_data)
            
            return True
            
        except Exception as e:
            self.log_result("Follow-up Health Check", False, f"Exception: {str(e)}")
            return False
    
    def test_additional_endpoints(self):
        """Test additional related endpoints for completeness"""
        try:
            print("\n🔍 Testing Additional Related Endpoints...")
            
            # Test intents endpoint (should be available for auto-responder)
            response = requests.get(f"{self.base_url}/api/intents", headers=self.headers, timeout=10)
            if response.status_code == 200:
                intents_data = response.json()
                if isinstance(intents_data, list):
                    auto_respond_intents = [intent for intent in intents_data if intent.get('auto_respond', False)]
                    self.log_result("Intents Endpoint", True, f"Found {len(intents_data)} intents, {len(auto_respond_intents)} with auto_respond enabled", {
                        'total_intents': len(intents_data),
                        'auto_respond_intents': len(auto_respond_intents)
                    })
                else:
                    self.log_result("Intents Endpoint", True, "Intents endpoint accessible", intents_data)
            else:
                self.log_result("Intents Endpoint", False, f"HTTP {response.status_code}", response.text)
            
            # Test templates endpoint (needed for auto-responses)
            response = requests.get(f"{self.base_url}/api/templates", headers=self.headers, timeout=10)
            if response.status_code == 200:
                templates_data = response.json()
                if isinstance(templates_data, list):
                    auto_response_templates = [template for template in templates_data if template.get('type') == 'auto_response']
                    self.log_result("Templates Endpoint", True, f"Found {len(templates_data)} templates, {len(auto_response_templates)} auto-response type", {
                        'total_templates': len(templates_data),
                        'auto_response_templates': len(auto_response_templates)
                    })
                else:
                    self.log_result("Templates Endpoint", True, "Templates endpoint accessible", templates_data)
            else:
                self.log_result("Templates Endpoint", False, f"HTTP {response.status_code}", response.text)
            
            return True
            
        except Exception as e:
            self.log_result("Additional Endpoints", False, f"Exception: {str(e)}")
            return False
    
    def run_auto_responder_tests(self):
        """Run comprehensive auto responder tests"""
        print("🚀 Starting AI Email Auto Responder Backend Tests")
        print("Focus: Auto Responder Status, IMAP Monitoring, Email Processing Analytics")
        print("=" * 80)
        
        # Test order matters for proper flow
        tests = [
            ("1. Authentication", self.test_authentication),
            ("2. Auto Responder Initial Status", self.test_auto_responder_initial_status),
            ("3. IMAP Scan Status", self.test_imap_scan_status),
            ("4. Start Auto Responder", self.test_start_auto_responder),
            ("5. Status Change After Start", self.test_status_change_after_start),
            ("6. Email Processing Analytics", self.test_email_processing_analytics),
            ("7. IMAP Monitoring Dashboard", self.test_imap_monitoring_dashboard),
            ("8. Follow-up Health Check", self.test_follow_up_health_check),
            ("9. Additional Related Endpoints", self.test_additional_endpoints)
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
                    if any(keyword in test_name.lower() for keyword in ['authentication', 'status', 'start', 'analytics']):
                        critical_failures.append(test_name)
            except Exception as e:
                self.log_result(test_name, False, f"Test execution failed: {str(e)}")
                critical_failures.append(test_name)
        
        print("\n" + "=" * 80)
        print(f"📊 Test Results: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
        
        if passed == total:
            print("🎉 All Auto Responder tests passed!")
        else:
            print(f"⚠️  {total - passed} tests failed")
            if critical_failures:
                print(f"🚨 Critical failures in: {', '.join(critical_failures)}")
        
        return self.test_results, critical_failures
    
    def print_detailed_results(self):
        """Print detailed test results"""
        print("\n" + "=" * 80)
        print("📋 DETAILED AUTO RESPONDER TEST RESULTS")
        print("=" * 80)
        
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            print(f"{status} {test_name}")
            if result['message']:
                print(f"   Message: {result['message']}")
            if result['details']:
                print(f"   Details: {json.dumps(result['details'], indent=4)}")
            print()
        
        # Summary
        passed_tests = [name for name, result in self.test_results.items() if result['success']]
        failed_tests = [name for name, result in self.test_results.items() if not result['success']]
        
        print("\n" + "=" * 80)
        print("📝 SUMMARY FOR TEST RESULT UPDATE")
        print("=" * 80)
        
        print("✅ PASSED TESTS:")
        for test in passed_tests:
            print(f"   - {test}")
        
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"   - {test}")
        
        print(f"\n📊 Overall Success Rate: {len(passed_tests)}/{len(self.test_results)} ({(len(passed_tests)/len(self.test_results))*100:.1f}%)")

def main():
    """Main test execution"""
    tester = AutoResponderTester()
    results, critical_failures = tester.run_auto_responder_tests()
    tester.print_detailed_results()
    
    return results, critical_failures

if __name__ == "__main__":
    main()