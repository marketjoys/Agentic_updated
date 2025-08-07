#!/usr/bin/env python3
"""
Comprehensive Backend Testing for FIXED Email Campaign System
Tests the critical fixes for follow-up stopping and auto-responder functionality
"""

import requests
import sys
import json
from datetime import datetime
from typing import Dict, Any

class FixedEmailSystemTester:
    def __init__(self, base_url="https://0479aeb2-d819-46be-a97f-9c1af66e157c.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.critical_failures = []

    def log_result(self, test_name: str, success: bool, details: str = ""):
        """Log test result with details"""
        self.tests_run += 1
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"\n{status} - {test_name}")
        if details:
            print(f"   Details: {details}")
        if success:
            self.tests_passed += 1
        else:
            self.critical_failures.append(f"{test_name}: {details}")

    def run_test(self, name: str, method: str, endpoint: str, expected_status: int, data: Dict = None, headers: Dict = None) -> tuple:
        """Run a single API test and return success status and response"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        # Default headers
        test_headers = {'Content-Type': 'application/json'}
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        if headers:
            test_headers.update(headers)

        try:
            print(f"\n🔍 Testing {name}...")
            print(f"   URL: {url}")
            
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=10)

            success = response.status_code == expected_status
            response_data = {}
            
            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text[:200]}

            details = f"Status: {response.status_code}"
            if not success:
                details += f", Expected: {expected_status}, Response: {response.text[:100]}"

            self.log_result(name, success, details)
            return success, response_data

        except requests.exceptions.Timeout:
            self.log_result(name, False, "Request timeout (10s)")
            return False, {"error": "timeout"}
        except requests.exceptions.ConnectionError:
            self.log_result(name, False, "Connection error - service may be down")
            return False, {"error": "connection_error"}
        except Exception as e:
            self.log_result(name, False, f"Exception: {str(e)}")
            return False, {"error": str(e)}

    def test_health_check(self):
        """Test basic health endpoint"""
        success, response = self.run_test(
            "Health Check",
            "GET",
            "/api/health",
            200
        )
        return success

    def test_authentication(self):
        """Test authentication system"""
        # Test login
        success, response = self.run_test(
            "User Login",
            "POST",
            "/api/auth/login",
            200,
            data={"username": "testuser", "password": "testpass123"}
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            print(f"   ✅ Token obtained: {self.token[:20]}...")
            
            # Test token validation
            success2, _ = self.run_test(
                "Token Validation (/api/auth/me)",
                "GET",
                "/api/auth/me",
                200
            )
            return success and success2
        
        return False

    def test_fixed_services_status(self):
        """Test the CRITICAL FIXED services status endpoint"""
        print("\n" + "="*60)
        print("🔧 TESTING FIXED SERVICES STATUS - CRITICAL TEST")
        print("="*60)
        
        success, response = self.run_test(
            "FIXED Services Status",
            "GET",
            "/api/services/status",
            200
        )
        
        if success and response:
            print("\n📊 FIXED SERVICES ANALYSIS:")
            
            # Check services structure
            services = response.get('services', {})
            
            # Check Smart Follow-up Engine (FIXED)
            follow_up = services.get('smart_follow_up_engine', {})
            follow_up_status = follow_up.get('status', 'unknown')
            follow_up_desc = follow_up.get('description', '')
            
            print(f"   📧 Smart Follow-up Engine: {follow_up_status.upper()}")
            print(f"      Description: {follow_up_desc}")
            
            # Check Email Processor (FIXED)
            processor = services.get('email_processor', {})
            processor_status = processor.get('status', 'unknown')
            processor_desc = processor.get('description', '')
            monitored_count = processor.get('monitored_providers_count', 0)
            
            print(f"   🤖 Email Processor: {processor_status.upper()}")
            print(f"      Description: {processor_desc}")
            print(f"      Monitored Providers: {monitored_count}")
            
            # Check overall status
            overall_status = response.get('overall_status', 'unknown')
            print(f"   🎯 Overall Status: {overall_status.upper()}")
            
            # Check fixes applied
            fixes = response.get('fixes_applied', [])
            print(f"\n✅ FIXES APPLIED ({len(fixes)}):")
            for fix in fixes:
                print(f"      {fix}")
            
            # Validate critical fixes
            critical_checks = {
                'follow_up_running': follow_up_status == 'running',
                'processor_running': processor_status == 'running',
                'overall_healthy': overall_status in ['healthy', 'degraded'],
                'fixes_present': len(fixes) >= 4,
                'follow_up_fix': any('STOP immediately' in fix for fix in fixes),
                'responder_fix': any('RESPONDS to ALL' in fix for fix in fixes)
            }
            
            print(f"\n🔍 CRITICAL VALIDATION:")
            all_critical_passed = True
            for check, passed in critical_checks.items():
                status = "✅" if passed else "❌"
                print(f"      {status} {check}: {passed}")
                if not passed:
                    all_critical_passed = False
            
            if all_critical_passed:
                print(f"\n🎉 ALL CRITICAL FIXES VALIDATED SUCCESSFULLY!")
            else:
                print(f"\n⚠️  SOME CRITICAL FIXES MAY NOT BE WORKING!")
                self.critical_failures.append("FIXED services validation failed")
            
            return all_critical_passed
        
        return False

    def test_service_management(self):
        """Test service start/stop functionality"""
        # Test starting all services
        success1, response1 = self.run_test(
            "Start All FIXED Services",
            "POST",
            "/api/services/start-all",
            200
        )
        
        if success1:
            print(f"   Service start results: {response1.get('results', {})}")
        
        return success1

    def test_core_endpoints(self):
        """Test core application endpoints"""
        endpoints = [
            ("Campaigns List", "GET", "/api/campaigns", 200),
            ("Email Providers List", "GET", "/api/email-providers", 200),
            ("Lists", "GET", "/api/lists", 200),
            ("Templates", "GET", "/api/templates", 200),
            ("Prospects", "GET", "/api/prospects", 200),
            ("Dashboard Metrics", "GET", "/api/real-time/dashboard-metrics", 200),
        ]
        
        all_passed = True
        for name, method, endpoint, expected_status in endpoints:
            success, _ = self.run_test(name, method, endpoint, expected_status)
            if not success:
                all_passed = False
        
        return all_passed

    def test_industries_endpoint(self):
        """Test industries endpoint for AI Agent"""
        success, response = self.run_test(
            "Industries for AI Agent",
            "GET",
            "/api/industries",
            200
        )
        
        if success and response:
            industries = response.get('industries', [])
            total_count = response.get('total_count', 0)
            print(f"   Found {total_count} industries available for AI Agent")
        
        return success

    def run_comprehensive_test(self):
        """Run all tests in sequence"""
        print("🚀 STARTING COMPREHENSIVE FIXED EMAIL SYSTEM TESTING")
        print("="*70)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)

        # Critical tests first
        health_ok = self.test_health_check()
        if not health_ok:
            print("\n❌ CRITICAL: Health check failed - backend may be down!")
            return self.generate_report()

        auth_ok = self.test_authentication()
        if not auth_ok:
            print("\n❌ CRITICAL: Authentication failed - cannot proceed with authenticated tests!")
            return self.generate_report()

        # Test FIXED services - MOST IMPORTANT
        fixed_services_ok = self.test_fixed_services_status()
        
        # Test service management
        service_mgmt_ok = self.test_service_management()
        
        # Test core functionality
        core_ok = self.test_core_endpoints()
        
        # Test AI Agent endpoints
        ai_ok = self.test_industries_endpoint()

        return self.generate_report()

    def generate_report(self):
        """Generate final test report"""
        print("\n" + "="*70)
        print("📊 FINAL TEST REPORT")
        print("="*70)
        
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if self.critical_failures:
            print(f"\n❌ CRITICAL FAILURES ({len(self.critical_failures)}):")
            for failure in self.critical_failures:
                print(f"   • {failure}")
        
        if success_rate >= 80 and not self.critical_failures:
            print(f"\n🎉 SYSTEM STATUS: HEALTHY - FIXED services are working!")
            return 0
        elif success_rate >= 60:
            print(f"\n⚠️  SYSTEM STATUS: DEGRADED - Some issues found")
            return 1
        else:
            print(f"\n❌ SYSTEM STATUS: CRITICAL ISSUES - Major problems detected")
            return 2

def main():
    """Main test execution"""
    tester = FixedEmailSystemTester()
    return tester.run_comprehensive_test()

if __name__ == "__main__":
    sys.exit(main())