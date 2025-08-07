#!/usr/bin/env python3
"""
Follow-up Scheduling System Backend Test
Tests the specific follow-up engine endpoints and functionality
"""

import requests
import sys
import json
from datetime import datetime

class FollowUpSystemTester:
    def __init__(self, base_url="https://0479aeb2-d819-46be-a97f-9c1af66e157c.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0

    def log_test(self, name: str, success: bool, details: str = "", response_data=None):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}: PASSED")
        else:
            print(f"❌ {name}: FAILED - {details}")
        
        if response_data:
            print(f"   Response: {json.dumps(response_data, indent=2)[:300]}...")

    def run_test(self, name: str, method: str, endpoint: str, expected_status: int, data=None):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)

            success = response.status_code == expected_status
            response_data = {}
            
            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text[:200]}

            self.log_test(name, success, f"Expected {expected_status}, got {response.status_code}", response_data)
            return success, response_data

        except Exception as e:
            self.log_test(name, False, f"Exception: {str(e)}")
            return False, {"error": str(e)}

    def test_authentication(self):
        """Test login functionality"""
        print("\n" + "="*60)
        print("TESTING AUTHENTICATION")
        print("="*60)
        
        success, response = self.run_test(
            "User Login",
            "POST",
            "auth/login",
            200,
            data={"username": "testuser", "password": "testpass123"}
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            return True
        return False

    def test_follow_up_engine_status(self):
        """Test follow-up engine status endpoint"""
        print("\n" + "="*60)
        print("TESTING FOLLOW-UP ENGINE STATUS")
        print("="*60)
        
        success, response = self.run_test(
            "Follow-up Engine Status",
            "GET",
            "follow-up-engine/status",
            200
        )
        
        if success:
            status = response.get('status', 'unknown')
            print(f"   Engine Status: {status}")
            return status == 'running'
        return False

    def test_follow_up_statistics(self):
        """Test follow-up engine statistics"""
        print("\n" + "="*60)
        print("TESTING FOLLOW-UP STATISTICS")
        print("="*60)
        
        success, response = self.run_test(
            "Follow-up Statistics",
            "GET",
            "follow-up-engine/statistics",
            200
        )
        
        if success:
            print(f"   Total Prospects: {response.get('total_prospects', 'N/A')}")
            print(f"   Active Follow-ups: {response.get('active_follow_ups', 'N/A')}")
            print(f"   Stopped Follow-ups: {response.get('stopped_follow_ups', 'N/A')}")
            print(f"   Completed Follow-ups: {response.get('completed_follow_ups', 'N/A')}")
            print(f"   Response Rate: {response.get('response_rate', 'N/A')}%")
            
            # Check if we have active prospects
            active_prospects = response.get('active_follow_ups', 0)
            if active_prospects >= 3:
                print("   ✅ Expected 3 active prospects found")
                return True
            else:
                print(f"   ⚠️  Expected 3 active prospects, found {active_prospects}")
                return False
        return False

    def test_services_status(self):
        """Test services status"""
        print("\n" + "="*60)
        print("TESTING SERVICES STATUS")
        print("="*60)
        
        success, response = self.run_test(
            "Services Status",
            "GET",
            "services/status",
            200
        )
        
        if success:
            services = response.get('services', {})
            follow_up_status = services.get('smart_follow_up_engine', {}).get('status')
            email_processor_status = services.get('email_processor', {}).get('status')
            
            print(f"   Smart Follow-up Engine: {follow_up_status}")
            print(f"   Email Processor: {email_processor_status}")
            
            both_running = (follow_up_status == 'running' and email_processor_status == 'running')
            if both_running:
                print("   ✅ Both services are running")
            else:
                print("   ⚠️  Not all services are running")
            
            return both_running
        return False

    def test_campaigns_with_followup(self):
        """Test campaigns with follow-up configuration"""
        print("\n" + "="*60)
        print("TESTING CAMPAIGNS WITH FOLLOW-UP")
        print("="*60)
        
        success, response = self.run_test(
            "Get Campaigns",
            "GET",
            "campaigns",
            200
        )
        
        if success:
            campaigns = response if isinstance(response, list) else []
            follow_up_campaigns = [c for c in campaigns if c.get('follow_up_enabled')]
            
            print(f"   Total Campaigns: {len(campaigns)}")
            print(f"   Follow-up Enabled Campaigns: {len(follow_up_campaigns)}")
            
            for campaign in follow_up_campaigns:
                name = campaign.get('name', 'Unknown')
                intervals = campaign.get('follow_up_intervals', [])
                print(f"   - {name}: {intervals} day intervals")
            
            # Check if we have test campaign with follow-ups
            test_campaign = next((c for c in campaigns if 'Test' in c.get('name', '')), None)
            if test_campaign and test_campaign.get('follow_up_enabled'):
                print("   ✅ Test campaign with follow-up found")
                return True
            else:
                print("   ⚠️  Test campaign with follow-up not found")
                return False
        return False

    def test_email_providers(self):
        """Test email providers"""
        print("\n" + "="*60)
        print("TESTING EMAIL PROVIDERS")
        print("="*60)
        
        success, response = self.run_test(
            "Get Email Providers",
            "GET",
            "email-providers",
            200
        )
        
        if success:
            providers = response if isinstance(response, list) else []
            active_providers = [p for p in providers if p.get('is_active')]
            
            print(f"   Total Providers: {len(providers)}")
            print(f"   Active Providers: {len(active_providers)}")
            
            for provider in active_providers:
                name = provider.get('name', 'Unknown')
                provider_type = provider.get('provider_type', 'Unknown')
                email = provider.get('email_address', 'N/A')
                print(f"   - {name} ({provider_type}): {email}")
            
            if len(active_providers) > 0:
                print("   ✅ Email providers configured")
                return True
            else:
                print("   ❌ No active email providers found")
                return False
        return False

    def test_start_services(self):
        """Test starting all services"""
        print("\n" + "="*60)
        print("TESTING SERVICE START")
        print("="*60)
        
        success, response = self.run_test(
            "Start All Services",
            "POST",
            "services/start-all",
            200
        )
        
        if success:
            results = response.get('results', {})
            follow_up_result = results.get('smart_follow_up_engine', {})
            email_result = results.get('email_processor', {})
            
            print(f"   Follow-up Engine Start: {follow_up_result.get('status', 'unknown')}")
            print(f"   Email Processor Start: {email_result.get('status', 'unknown')}")
            
            return True
        return False

    def run_comprehensive_test(self):
        """Run all follow-up system tests"""
        print("🚀 Starting Follow-up Scheduling System Backend Tests")
        print(f"🌐 Testing against: {self.base_url}")
        print("="*80)
        
        # Test authentication first
        if not self.test_authentication():
            print("\n❌ Authentication failed - cannot proceed")
            return False
        
        # Run all tests
        results = []
        results.append(self.test_services_status())
        results.append(self.test_follow_up_engine_status())
        results.append(self.test_follow_up_statistics())
        results.append(self.test_campaigns_with_followup())
        results.append(self.test_email_providers())
        
        # Try to start services if they're not running
        self.test_start_services()
        
        # Wait a moment and test again
        import time
        time.sleep(3)
        
        print("\n" + "="*60)
        print("RE-TESTING AFTER SERVICE START")
        print("="*60)
        
        results.append(self.test_services_status())
        results.append(self.test_follow_up_engine_status())
        
        # Print final results
        self.print_final_results(results)
        
        return all(results)

    def print_final_results(self, results):
        """Print comprehensive test results"""
        print("\n" + "="*80)
        print("FOLLOW-UP SYSTEM TEST RESULTS")
        print("="*80)
        
        print(f"📊 Tests Run: {self.tests_run}")
        print(f"✅ Tests Passed: {self.tests_passed}")
        print(f"❌ Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"📈 Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        passed_tests = sum(1 for r in results if r)
        total_tests = len(results)
        
        print(f"\n🎯 FOLLOW-UP SYSTEM HEALTH: {passed_tests}/{total_tests} components working")
        
        if passed_tests == total_tests:
            print("\n🎉 ALL FOLLOW-UP SYSTEM TESTS PASSED!")
            print("✅ Follow-up scheduling system is healthy and operational")
        elif passed_tests >= total_tests * 0.7:
            print(f"\n⚠️  FOLLOW-UP SYSTEM PARTIALLY WORKING ({passed_tests}/{total_tests})")
            print("🔧 Some components need attention but core functionality is available")
        else:
            print(f"\n❌ FOLLOW-UP SYSTEM NEEDS ATTENTION ({passed_tests}/{total_tests})")
            print("🚨 Multiple components are not working properly")
        
        print("\n" + "="*80)

def main():
    """Main test execution"""
    tester = FollowUpSystemTester()
    
    try:
        success = tester.run_comprehensive_test()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n\n💥 Unexpected error during testing: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())