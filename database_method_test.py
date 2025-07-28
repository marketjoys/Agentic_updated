#!/usr/bin/env python3
"""
Database Method Testing - January 2025
Testing the specific database method mentioned in the review request:
- get_last_imap_scan_for_provider method
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://6aa35d2d-1224-4abb-b5c1-ebe60774a6f1.preview.emergentagent.com/api"
USERNAME = "testuser"
PASSWORD = "testpass123"
PROVIDER_ID = "544fe9dd-3b65-4e23-8509-82f1ad0db1e5"

class DatabaseMethodTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        
    def authenticate(self):
        """Authenticate and get access token"""
        try:
            response = self.session.post(f"{BASE_URL}/auth/login", json={
                "username": USERNAME,
                "password": PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                print("✅ Authentication successful")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def test_get_last_imap_scan_method(self):
        """Test the get_last_imap_scan_for_provider method"""
        print("\n🧪 Testing get_last_imap_scan_for_provider method")
        
        try:
            # This method should be called when getting IMAP status
            response = self.session.get(f"{BASE_URL}/email-providers/{PROVIDER_ID}/imap-status")
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 500:
                print("❌ CRITICAL: HTTP 500 error - likely missing database method")
                print("Response:", response.text)
                
                # Check if the error mentions the missing method
                if "get_last_imap_scan_for_provider" in response.text:
                    print("🔍 CONFIRMED: Missing get_last_imap_scan_for_provider method in database service")
                    return False
                else:
                    print("🔍 Different 500 error - not the expected missing method")
                    return False
                    
            elif response.status_code == 200:
                data = response.json()
                print("✅ IMAP status endpoint working correctly")
                
                # Check if last_scan field is present
                if "last_scan" in data:
                    last_scan = data["last_scan"]
                    if last_scan:
                        print(f"✅ Last scan timestamp: {last_scan}")
                    else:
                        print("✅ Last scan is null (no scans yet)")
                    return True
                else:
                    print("❌ Missing last_scan field in response")
                    return False
            else:
                print(f"❌ Unexpected status code: {response.status_code}")
                print("Response:", response.text)
                return False
                
        except Exception as e:
            print(f"❌ Exception testing database method: {str(e)}")
            return False
    
    def test_email_processor_monitoring(self):
        """Test if email processor is actively monitoring"""
        print("\n🧪 Testing Email Processor Monitoring")
        
        try:
            # Check services status
            response = self.session.get(f"{BASE_URL}/services/status")
            
            if response.status_code != 200:
                print(f"❌ Services status error: {response.status_code}")
                return False
            
            data = response.json()
            services = data.get("services", {})
            email_processor = services.get("email_processor", {})
            
            status = email_processor.get("status")
            monitored_count = email_processor.get("monitored_providers_count", 0)
            monitored_providers = email_processor.get("monitored_providers", [])
            
            print(f"Email Processor Status: {status}")
            print(f"Monitored Providers Count: {monitored_count}")
            
            # Check if our specific provider is being monitored
            target_provider_monitored = False
            for provider in monitored_providers:
                if provider.get("id") == PROVIDER_ID:
                    target_provider_monitored = True
                    print(f"✅ Target provider '{provider.get('name')}' is being monitored")
                    print(f"   Last scan: {provider.get('last_scan')}")
                    break
            
            if not target_provider_monitored:
                print(f"❌ Target provider {PROVIDER_ID} is not being monitored")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Exception testing email processor monitoring: {str(e)}")
            return False
    
    def run_database_tests(self):
        """Run database-specific tests"""
        print("🚀 DATABASE METHOD TESTING - JANUARY 2025")
        print("=" * 60)
        print("Testing specific database methods mentioned in review request")
        print("=" * 60)
        
        if not self.authenticate():
            print("❌ CRITICAL: Authentication failed")
            return False
        
        tests_passed = 0
        total_tests = 2
        
        # Test 1: get_last_imap_scan_for_provider method
        if self.test_get_last_imap_scan_method():
            tests_passed += 1
        
        # Test 2: Email processor monitoring
        if self.test_email_processor_monitoring():
            tests_passed += 1
        
        print("\n" + "=" * 60)
        print("🎯 DATABASE METHOD TEST RESULTS")
        print("=" * 60)
        print(f"Tests Passed: {tests_passed}/{total_tests}")
        
        if tests_passed == total_tests:
            print("✅ All database methods working correctly")
            return True
        else:
            print("❌ Some database methods have issues")
            return False

if __name__ == "__main__":
    tester = DatabaseMethodTester()
    success = tester.run_database_tests()
    
    if not success:
        sys.exit(1)
    else:
        sys.exit(0)