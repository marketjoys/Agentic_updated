#!/usr/bin/env python3
"""
Duplicate Prevention Testing - January 2025
Testing duplicate prevention functionality specifically to verify that:

1. Creating a duplicate email provider (with the same email address) now returns HTTP 400 instead of 500
2. Creating a duplicate email provider (with the same provider name) now returns HTTP 400 instead of 500  
3. Creating a duplicate prospect (with the same email address) now returns HTTP 400 instead of 500
4. Verify that the error messages are meaningful and indicate the duplicate issue
5. Test that normal creation still works without issues

URL: https://6464b8e1-a5e1-4bb7-b2f5-42bbc07856fb.preview.emergentagent.com
Login: testuser / testpass123
"""

import requests
import json
import sys
from datetime import datetime
import uuid

# Configuration
BASE_URL = "https://6464b8e1-a5e1-4bb7-b2f5-42bbc07856fb.preview.emergentagent.com/api"
USERNAME = "testuser"
PASSWORD = "testpass123"

class DuplicatePreventionTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.test_results = []
        
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
                print(f"❌ Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False

    def log_test_result(self, test_name, passed, details):
        """Log test result"""
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })

    def test_email_provider_duplicate_prevention(self):
        """Test duplicate prevention for email providers"""
        print("\n🧪 TESTING EMAIL PROVIDER DUPLICATE PREVENTION")
        
        # Generate unique test data
        unique_id = str(uuid.uuid4())[:8]
        test_email = f"test-provider-{unique_id}@example.com"
        test_name = f"Test Provider {unique_id}"
        
        # Test data for email provider
        provider_data = {
            "name": test_name,
            "provider_type": "gmail",
            "email_address": test_email,
            "display_name": f"Test Display {unique_id}",
            "smtp_host": "smtp.gmail.com",
            "smtp_port": 587,
            "smtp_username": test_email,
            "smtp_password": "test_password",
            "smtp_use_tls": True,
            "imap_host": "imap.gmail.com",
            "imap_port": 993,
            "imap_username": test_email,
            "imap_password": "test_password",
            "daily_send_limit": 500,
            "hourly_send_limit": 50,
            "is_default": False,
            "skip_connection_test": True
        }
        
        # Test 1: Create initial email provider (should succeed)
        try:
            response = self.session.post(f"{BASE_URL}/email-providers", json=provider_data)
            
            if response.status_code == 200:
                self.log_test_result(
                    "Create initial email provider",
                    True,
                    f"Successfully created provider with email {test_email}"
                )
                first_provider_id = response.json().get("id")
            else:
                self.log_test_result(
                    "Create initial email provider",
                    False,
                    f"Failed to create initial provider: {response.status_code} - {response.text}"
                )
                return
                
        except Exception as e:
            self.log_test_result(
                "Create initial email provider",
                False,
                f"Exception: {str(e)}"
            )
            return

        # Test 2: Try to create duplicate email provider with same email address (should return 400)
        try:
            duplicate_provider_data = provider_data.copy()
            duplicate_provider_data["name"] = f"Different Name {unique_id}"
            
            response = self.session.post(f"{BASE_URL}/email-providers", json=duplicate_provider_data)
            
            if response.status_code == 400:
                error_message = response.text
                if "duplicate" in error_message.lower() or "already exists" in error_message.lower() or "email" in error_message.lower():
                    self.log_test_result(
                        "Duplicate email address prevention (HTTP 400)",
                        True,
                        f"Correctly returned 400 with meaningful error: {error_message}"
                    )
                else:
                    self.log_test_result(
                        "Duplicate email address prevention (HTTP 400)",
                        False,
                        f"Returned 400 but error message not meaningful: {error_message}"
                    )
            elif response.status_code == 500:
                self.log_test_result(
                    "Duplicate email address prevention (HTTP 400)",
                    False,
                    f"Still returning 500 instead of 400: {response.text}"
                )
            else:
                self.log_test_result(
                    "Duplicate email address prevention (HTTP 400)",
                    False,
                    f"Unexpected status code {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test_result(
                "Duplicate email address prevention (HTTP 400)",
                False,
                f"Exception: {str(e)}"
            )

        # Test 3: Try to create duplicate email provider with same name (should return 400)
        try:
            duplicate_name_data = provider_data.copy()
            duplicate_name_data["email_address"] = f"different-{unique_id}@example.com"
            duplicate_name_data["smtp_username"] = duplicate_name_data["email_address"]
            duplicate_name_data["imap_username"] = duplicate_name_data["email_address"]
            
            response = self.session.post(f"{BASE_URL}/email-providers", json=duplicate_name_data)
            
            if response.status_code == 400:
                error_message = response.text
                if "duplicate" in error_message.lower() or "already exists" in error_message.lower() or "name" in error_message.lower():
                    self.log_test_result(
                        "Duplicate provider name prevention (HTTP 400)",
                        True,
                        f"Correctly returned 400 with meaningful error: {error_message}"
                    )
                else:
                    self.log_test_result(
                        "Duplicate provider name prevention (HTTP 400)",
                        False,
                        f"Returned 400 but error message not meaningful: {error_message}"
                    )
            elif response.status_code == 500:
                self.log_test_result(
                    "Duplicate provider name prevention (HTTP 400)",
                    False,
                    f"Still returning 500 instead of 400: {response.text}"
                )
            else:
                self.log_test_result(
                    "Duplicate provider name prevention (HTTP 400)",
                    False,
                    f"Unexpected status code {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test_result(
                "Duplicate provider name prevention (HTTP 400)",
                False,
                f"Exception: {str(e)}"
            )

        # Cleanup: Delete the created provider
        try:
            if 'first_provider_id' in locals():
                cleanup_response = self.session.delete(f"{BASE_URL}/email-providers/{first_provider_id}")
                if cleanup_response.status_code == 200:
                    print(f"✅ Cleaned up test provider {first_provider_id}")
                else:
                    print(f"⚠️ Failed to cleanup test provider: {cleanup_response.status_code}")
        except Exception as e:
            print(f"⚠️ Cleanup error: {str(e)}")

    def test_prospect_duplicate_prevention(self):
        """Test duplicate prevention for prospects"""
        print("\n🧪 TESTING PROSPECT DUPLICATE PREVENTION")
        
        # Generate unique test data
        unique_id = str(uuid.uuid4())[:8]
        test_email = f"test-prospect-{unique_id}@example.com"
        
        # Test data for prospect
        prospect_data = {
            "first_name": f"Test{unique_id}",
            "last_name": "Prospect",
            "email": test_email,
            "company": f"Test Company {unique_id}",
            "job_title": "Test Manager",
            "industry": "Technology",
            "phone": "+1234567890",
            "website": "https://example.com",
            "notes": "Test prospect for duplicate prevention"
        }
        
        # Test 1: Create initial prospect (should succeed)
        try:
            response = self.session.post(f"{BASE_URL}/prospects", json=prospect_data)
            
            if response.status_code == 200:
                self.log_test_result(
                    "Create initial prospect",
                    True,
                    f"Successfully created prospect with email {test_email}"
                )
                first_prospect_id = response.json().get("id")
            else:
                self.log_test_result(
                    "Create initial prospect",
                    False,
                    f"Failed to create initial prospect: {response.status_code} - {response.text}"
                )
                return
                
        except Exception as e:
            self.log_test_result(
                "Create initial prospect",
                False,
                f"Exception: {str(e)}"
            )
            return

        # Test 2: Try to create duplicate prospect with same email address (should return 400)
        try:
            duplicate_prospect_data = prospect_data.copy()
            duplicate_prospect_data["first_name"] = f"Different{unique_id}"
            duplicate_prospect_data["company"] = f"Different Company {unique_id}"
            
            response = self.session.post(f"{BASE_URL}/prospects", json=duplicate_prospect_data)
            
            if response.status_code == 400:
                error_message = response.text
                if "duplicate" in error_message.lower() or "already exists" in error_message.lower() or "email" in error_message.lower():
                    self.log_test_result(
                        "Duplicate prospect email prevention (HTTP 400)",
                        True,
                        f"Correctly returned 400 with meaningful error: {error_message}"
                    )
                else:
                    self.log_test_result(
                        "Duplicate prospect email prevention (HTTP 400)",
                        False,
                        f"Returned 400 but error message not meaningful: {error_message}"
                    )
            elif response.status_code == 500:
                self.log_test_result(
                    "Duplicate prospect email prevention (HTTP 400)",
                    False,
                    f"Still returning 500 instead of 400: {response.text}"
                )
            else:
                self.log_test_result(
                    "Duplicate prospect email prevention (HTTP 400)",
                    False,
                    f"Unexpected status code {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test_result(
                "Duplicate prospect email prevention (HTTP 400)",
                False,
                f"Exception: {str(e)}"
            )

        # Cleanup: Delete the created prospect
        try:
            if 'first_prospect_id' in locals():
                cleanup_response = self.session.delete(f"{BASE_URL}/prospects/{first_prospect_id}")
                if cleanup_response.status_code == 200:
                    print(f"✅ Cleaned up test prospect {first_prospect_id}")
                else:
                    print(f"⚠️ Failed to cleanup test prospect: {cleanup_response.status_code}")
        except Exception as e:
            print(f"⚠️ Cleanup error: {str(e)}")

    def test_normal_creation_still_works(self):
        """Test that normal creation without duplicates still works"""
        print("\n🧪 TESTING NORMAL CREATION FUNCTIONALITY")
        
        # Generate unique test data
        unique_id = str(uuid.uuid4())[:8]
        
        # Test normal email provider creation
        try:
            provider_data = {
                "name": f"Normal Provider {unique_id}",
                "provider_type": "gmail",
                "email_address": f"normal-provider-{unique_id}@example.com",
                "display_name": f"Normal Display {unique_id}",
                "smtp_host": "smtp.gmail.com",
                "smtp_port": 587,
                "smtp_username": f"normal-provider-{unique_id}@example.com",
                "smtp_password": "test_password",
                "smtp_use_tls": True,
                "daily_send_limit": 500,
                "hourly_send_limit": 50,
                "is_default": False,
                "skip_connection_test": True
            }
            
            response = self.session.post(f"{BASE_URL}/email-providers", json=provider_data)
            
            if response.status_code == 200:
                self.log_test_result(
                    "Normal email provider creation",
                    True,
                    f"Successfully created normal provider"
                )
                provider_id = response.json().get("id")
                
                # Cleanup
                cleanup_response = self.session.delete(f"{BASE_URL}/email-providers/{provider_id}")
                if cleanup_response.status_code == 200:
                    print(f"✅ Cleaned up normal provider {provider_id}")
            else:
                self.log_test_result(
                    "Normal email provider creation",
                    False,
                    f"Failed to create normal provider: {response.status_code} - {response.text}"
                )
                
        except Exception as e:
            self.log_test_result(
                "Normal email provider creation",
                False,
                f"Exception: {str(e)}"
            )

        # Test normal prospect creation
        try:
            prospect_data = {
                "first_name": f"Normal{unique_id}",
                "last_name": "Prospect",
                "email": f"normal-prospect-{unique_id}@example.com",
                "company": f"Normal Company {unique_id}",
                "job_title": "Normal Manager",
                "industry": "Technology"
            }
            
            response = self.session.post(f"{BASE_URL}/prospects", json=prospect_data)
            
            if response.status_code == 200:
                self.log_test_result(
                    "Normal prospect creation",
                    True,
                    f"Successfully created normal prospect"
                )
                prospect_id = response.json().get("id")
                
                # Cleanup
                cleanup_response = self.session.delete(f"{BASE_URL}/prospects/{prospect_id}")
                if cleanup_response.status_code == 200:
                    print(f"✅ Cleaned up normal prospect {prospect_id}")
            else:
                self.log_test_result(
                    "Normal prospect creation",
                    False,
                    f"Failed to create normal prospect: {response.status_code} - {response.text}"
                )
                
        except Exception as e:
            self.log_test_result(
                "Normal prospect creation",
                False,
                f"Exception: {str(e)}"
            )

    def run_all_tests(self):
        """Run all duplicate prevention tests"""
        print("🚀 STARTING DUPLICATE PREVENTION TESTING")
        print("=" * 60)
        
        if not self.authenticate():
            return False
        
        # Run all tests
        self.test_email_provider_duplicate_prevention()
        self.test_prospect_duplicate_prevention()
        self.test_normal_creation_still_works()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["passed"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["passed"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        return failed_tests == 0

def main():
    """Main function"""
    tester = DuplicatePreventionTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 ALL DUPLICATE PREVENTION TESTS PASSED!")
        sys.exit(0)
    else:
        print("\n💥 SOME DUPLICATE PREVENTION TESTS FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    main()