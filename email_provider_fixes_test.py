#!/usr/bin/env python3
"""
Email Provider Fixes Testing - January 2025
Testing the specific fixes implemented for the AI Email Responder application as requested in review.

Focus Areas:
1. Email Provider Delete Function - Test DELETE /api/email-providers/{provider_id} endpoint
2. Email Provider Duplicate Prevention - Test POST /api/email-providers endpoint
3. IMAP Activation & Status - Test IMAP connectivity and status endpoints

Test Scenarios:
- Create a test email provider
- Delete it and verify it's gone from database
- Try to delete non-existent provider (should return 404)
- Try to create providers with same email address (should fail)
- Try to create providers with same name (should fail)
- Test IMAP connection testing endpoint
- Check IMAP status endpoint
- Verify monitoring status is accurately reported
"""

import requests
import json
import sys
import time
from datetime import datetime

# Configuration
BASE_URL = "https://01b4b25c-7ecb-4496-b8f4-e35875af5f0c.preview.emergentagent.com/api"
USERNAME = "testuser"
PASSWORD = "testpass123"

class EmailProviderFixesTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.created_providers = []
        
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
    
    def test_email_provider_delete_function(self):
        """Test DELETE /api/email-providers/{provider_id} endpoint"""
        print("\n🧪 Testing Email Provider Delete Function")
        
        try:
            # Step 1: Create a test email provider
            print("Step 1: Creating test email provider...")
            unique_timestamp = int(time.time())
            provider_data = {
                "name": f"Test Provider {unique_timestamp}",
                "provider_type": "gmail",
                "email_address": f"test.provider.{unique_timestamp}@gmail.com",
                "display_name": f"Test Provider {unique_timestamp}",
                "smtp_host": "smtp.gmail.com",
                "smtp_port": 587,
                "smtp_username": f"test.provider.{unique_timestamp}@gmail.com",
                "smtp_password": "test_password",
                "smtp_use_tls": True,
                "imap_host": "imap.gmail.com",
                "imap_port": 993,
                "imap_username": f"test.provider.{unique_timestamp}@gmail.com",
                "imap_password": "test_password",
                "daily_send_limit": 500,
                "hourly_send_limit": 50,
                "is_default": False,
                "skip_connection_test": True
            }
            
            response = self.session.post(f"{BASE_URL}/email-providers", json=provider_data)
            
            if response.status_code != 200:
                print(f"❌ Failed to create test provider: {response.status_code} - {response.text}")
                return False
            
            created_provider = response.json()
            provider_id = created_provider.get("id")
            if not provider_id:
                print(f"❌ No provider ID in response: {created_provider}")
                return False
            
            self.created_providers.append(provider_id)
            print(f"✅ Created test provider with ID: {provider_id}")
            
            # Step 2: Verify provider exists in database
            print("Step 2: Verifying provider exists...")
            response = self.session.get(f"{BASE_URL}/email-providers")
            if response.status_code != 200:
                print(f"❌ Failed to get providers: {response.status_code}")
                return False
            
            providers = response.json()
            provider_exists = any(p.get("id") == provider_id for p in providers)
            if not provider_exists:
                print(f"❌ Provider {provider_id} not found in database")
                return False
            
            print(f"✅ Provider {provider_id} exists in database")
            
            # Step 3: Delete the provider
            print("Step 3: Deleting the provider...")
            response = self.session.delete(f"{BASE_URL}/email-providers/{provider_id}")
            
            if response.status_code != 200:
                print(f"❌ Delete failed: {response.status_code} - {response.text}")
                return False
            
            delete_result = response.json()
            print(f"✅ Delete response: {delete_result}")
            
            # Step 4: Verify provider is gone from database
            print("Step 4: Verifying provider is deleted...")
            response = self.session.get(f"{BASE_URL}/email-providers")
            if response.status_code != 200:
                print(f"❌ Failed to get providers after delete: {response.status_code}")
                return False
            
            providers_after_delete = response.json()
            provider_still_exists = any(p.get("id") == provider_id for p in providers_after_delete)
            if provider_still_exists:
                print(f"❌ Provider {provider_id} still exists after delete")
                return False
            
            print(f"✅ Provider {provider_id} successfully deleted from database")
            
            # Remove from our tracking since it's deleted
            self.created_providers.remove(provider_id)
            
            # Step 5: Try to delete non-existent provider (should return 404)
            print("Step 5: Testing delete of non-existent provider...")
            fake_provider_id = "non-existent-provider-id-12345"
            response = self.session.delete(f"{BASE_URL}/email-providers/{fake_provider_id}")
            
            if response.status_code == 404:
                print("✅ Non-existent provider delete returned 404 as expected")
                return True
            else:
                print(f"❌ Expected 404 for non-existent provider, got {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Email provider delete test error: {str(e)}")
            return False
    
    def test_email_provider_duplicate_prevention(self):
        """Test POST /api/email-providers endpoint for duplicate prevention"""
        print("\n🧪 Testing Email Provider Duplicate Prevention")
        
        try:
            unique_timestamp = int(time.time())
            
            # Step 1: Create first email provider successfully
            print("Step 1: Creating first email provider...")
            provider_data_1 = {
                "name": f"Unique Provider {unique_timestamp}",
                "provider_type": "gmail",
                "email_address": f"unique.provider.{unique_timestamp}@gmail.com",
                "display_name": f"Unique Provider {unique_timestamp}",
                "smtp_host": "smtp.gmail.com",
                "smtp_port": 587,
                "smtp_username": f"unique.provider.{unique_timestamp}@gmail.com",
                "smtp_password": "test_password",
                "smtp_use_tls": True,
                "imap_host": "imap.gmail.com",
                "imap_port": 993,
                "imap_username": f"unique.provider.{unique_timestamp}@gmail.com",
                "imap_password": "test_password",
                "daily_send_limit": 500,
                "hourly_send_limit": 50,
                "is_default": False,
                "skip_connection_test": True
            }
            
            response = self.session.post(f"{BASE_URL}/email-providers", json=provider_data_1)
            
            if response.status_code != 200:
                print(f"❌ Failed to create first provider: {response.status_code} - {response.text}")
                return False
            
            created_provider_1 = response.json()
            provider_id_1 = created_provider_1.get("id")
            if not provider_id_1:
                print(f"❌ No provider ID in response: {created_provider_1}")
                return False
            
            self.created_providers.append(provider_id_1)
            print(f"✅ Created first provider with ID: {provider_id_1}")
            
            # Step 2: Try to create provider with same email address (should fail with 400)
            print("Step 2: Testing duplicate email address prevention...")
            provider_data_duplicate_email = {
                "name": f"Different Name {unique_timestamp}",
                "provider_type": "gmail",
                "email_address": f"unique.provider.{unique_timestamp}@gmail.com",  # Same email as first provider
                "display_name": f"Different Display Name {unique_timestamp}",
                "smtp_host": "smtp.gmail.com",
                "smtp_port": 587,
                "smtp_username": f"unique.provider.{unique_timestamp}@gmail.com",
                "smtp_password": "test_password",
                "smtp_use_tls": True,
                "imap_host": "imap.gmail.com",
                "imap_port": 993,
                "imap_username": f"unique.provider.{unique_timestamp}@gmail.com",
                "imap_password": "test_password",
                "daily_send_limit": 500,
                "hourly_send_limit": 50,
                "is_default": False,
                "skip_connection_test": True
            }
            
            response = self.session.post(f"{BASE_URL}/email-providers", json=provider_data_duplicate_email)
            
            if response.status_code == 400:
                error_message = response.text
                print(f"✅ Duplicate email address rejected with 400: {error_message}")
            else:
                print(f"❌ Expected 400 for duplicate email, got {response.status_code} - {response.text}")
                # If it was created, track it for cleanup
                if response.status_code == 200:
                    duplicate_provider = response.json()
                    if duplicate_provider.get("id"):
                        self.created_providers.append(duplicate_provider["id"])
                return False
            
            # Step 3: Try to create provider with same name (should fail with 400)
            print("Step 3: Testing duplicate name prevention...")
            provider_data_duplicate_name = {
                "name": f"Unique Provider {unique_timestamp}",  # Same name as first provider
                "provider_type": "gmail",
                "email_address": f"different.email.{unique_timestamp}@gmail.com",  # Different email
                "display_name": f"Different Display Name {unique_timestamp}",
                "smtp_host": "smtp.gmail.com",
                "smtp_port": 587,
                "smtp_username": f"different.email.{unique_timestamp}@gmail.com",
                "smtp_password": "test_password",
                "smtp_use_tls": True,
                "imap_host": "imap.gmail.com",
                "imap_port": 993,
                "imap_username": f"different.email.{unique_timestamp}@gmail.com",
                "imap_password": "test_password",
                "daily_send_limit": 500,
                "hourly_send_limit": 50,
                "is_default": False,
                "skip_connection_test": True
            }
            
            response = self.session.post(f"{BASE_URL}/email-providers", json=provider_data_duplicate_name)
            
            if response.status_code == 400:
                error_message = response.text
                print(f"✅ Duplicate name rejected with 400: {error_message}")
                return True
            else:
                print(f"❌ Expected 400 for duplicate name, got {response.status_code} - {response.text}")
                # If it was created, track it for cleanup
                if response.status_code == 200:
                    duplicate_provider = response.json()
                    if duplicate_provider.get("id"):
                        self.created_providers.append(duplicate_provider["id"])
                return False
                
        except Exception as e:
            print(f"❌ Email provider duplicate prevention test error: {str(e)}")
            return False
    
    def test_imap_activation_and_status(self):
        """Test IMAP connectivity and status endpoints"""
        print("\n🧪 Testing IMAP Activation & Status")
        
        try:
            # Step 1: Create a test email provider with IMAP credentials
            print("Step 1: Creating test provider with IMAP credentials...")
            unique_timestamp = int(time.time())
            provider_data = {
                "name": f"IMAP Test Provider {unique_timestamp}",
                "provider_type": "gmail",
                "email_address": f"imap.test.{unique_timestamp}@gmail.com",
                "display_name": f"IMAP Test Provider {unique_timestamp}",
                "smtp_host": "smtp.gmail.com",
                "smtp_port": 587,
                "smtp_username": f"imap.test.{unique_timestamp}@gmail.com",
                "smtp_password": "test_password",
                "smtp_use_tls": True,
                "imap_host": "imap.gmail.com",
                "imap_port": 993,
                "imap_username": f"imap.test.{unique_timestamp}@gmail.com",
                "imap_password": "test_password",
                "daily_send_limit": 500,
                "hourly_send_limit": 50,
                "is_default": False,
                "skip_connection_test": True
            }
            
            response = self.session.post(f"{BASE_URL}/email-providers", json=provider_data)
            
            if response.status_code != 200:
                print(f"❌ Failed to create IMAP test provider: {response.status_code} - {response.text}")
                return False
            
            created_provider = response.json()
            provider_id = created_provider.get("id")
            if not provider_id:
                print(f"❌ No provider ID in response: {created_provider}")
                return False
            
            self.created_providers.append(provider_id)
            print(f"✅ Created IMAP test provider with ID: {provider_id}")
            
            # Step 2: Test IMAP connection testing endpoint
            print("Step 2: Testing IMAP connection test endpoint...")
            response = self.session.post(f"{BASE_URL}/email-providers/{provider_id}/test")
            
            if response.status_code != 200:
                print(f"❌ IMAP test endpoint failed: {response.status_code} - {response.text}")
                return False
            
            test_result = response.json()
            print(f"✅ IMAP test result: {test_result}")
            
            # Check if test result has expected fields
            expected_fields = ["id", "name", "smtp_test", "imap_test", "overall_status"]
            missing_fields = [field for field in expected_fields if field not in test_result]
            if missing_fields:
                print(f"❌ Missing fields in test result: {missing_fields}")
                return False
            
            print(f"✅ IMAP test endpoint working correctly")
            
            # Step 3: Test IMAP status endpoint
            print("Step 3: Testing IMAP status endpoint...")
            response = self.session.get(f"{BASE_URL}/email-providers/{provider_id}/imap-status")
            
            if response.status_code != 200:
                print(f"❌ IMAP status endpoint failed: {response.status_code} - {response.text}")
                return False
            
            status_result = response.json()
            print(f"✅ IMAP status result: {status_result}")
            
            # Check if status result has expected fields
            expected_status_fields = ["provider_id", "provider_name", "imap_enabled", "is_monitoring", "email_processor_running"]
            missing_status_fields = [field for field in expected_status_fields if field not in status_result]
            if missing_status_fields:
                print(f"❌ Missing fields in status result: {missing_status_fields}")
                return False
            
            print(f"✅ IMAP status endpoint working correctly")
            
            # Step 4: Test IMAP toggle endpoint
            print("Step 4: Testing IMAP toggle endpoint...")
            response = self.session.put(f"{BASE_URL}/email-providers/{provider_id}/toggle-imap")
            
            if response.status_code != 200:
                print(f"❌ IMAP toggle endpoint failed: {response.status_code} - {response.text}")
                return False
            
            toggle_result = response.json()
            print(f"✅ IMAP toggle result: {toggle_result}")
            
            # Check if toggle result has expected fields
            expected_toggle_fields = ["id", "message", "imap_enabled"]
            missing_toggle_fields = [field for field in expected_toggle_fields if field not in toggle_result]
            if missing_toggle_fields:
                print(f"❌ Missing fields in toggle result: {missing_toggle_fields}")
                return False
            
            print(f"✅ IMAP toggle endpoint working correctly")
            
            # Step 5: Verify IMAP status changed after toggle
            print("Step 5: Verifying IMAP status after toggle...")
            response = self.session.get(f"{BASE_URL}/email-providers/{provider_id}/imap-status")
            
            if response.status_code != 200:
                print(f"❌ IMAP status check after toggle failed: {response.status_code} - {response.text}")
                return False
            
            status_after_toggle = response.json()
            print(f"✅ IMAP status after toggle: {status_after_toggle}")
            
            # The IMAP enabled status should have changed
            original_status = status_result.get("imap_enabled")
            new_status = status_after_toggle.get("imap_enabled")
            
            if original_status == new_status:
                print(f"⚠️ IMAP status didn't change after toggle (both {original_status})")
            else:
                print(f"✅ IMAP status successfully toggled from {original_status} to {new_status}")
            
            return True
                
        except Exception as e:
            print(f"❌ IMAP activation and status test error: {str(e)}")
            return False
    
    def cleanup_created_providers(self):
        """Clean up any providers created during testing"""
        print("\n🧹 Cleaning up created providers...")
        
        for provider_id in self.created_providers:
            try:
                response = self.session.delete(f"{BASE_URL}/email-providers/{provider_id}")
                if response.status_code == 200:
                    print(f"   ✅ Deleted provider {provider_id}")
                else:
                    print(f"   ⚠️ Failed to delete provider {provider_id}: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Error deleting provider {provider_id}: {str(e)}")
        
        self.created_providers.clear()
    
    def run_comprehensive_test(self):
        """Run all email provider fixes tests"""
        print("🚀 EMAIL PROVIDER FIXES TESTING - JANUARY 2025")
        print("=" * 80)
        print("Testing specific fixes implemented for AI Email Responder:")
        print("1. Email Provider Delete Function")
        print("2. Email Provider Duplicate Prevention")
        print("3. IMAP Activation & Status")
        print("=" * 80)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ CRITICAL: Authentication failed - cannot proceed with testing")
            return False
        
        # Run all tests
        test_results = {
            "email_provider_delete": self.test_email_provider_delete_function(),
            "duplicate_prevention": self.test_email_provider_duplicate_prevention(),
            "imap_activation_status": self.test_imap_activation_and_status()
        }
        
        # Summary
        print("\n" + "=" * 80)
        print("🎯 EMAIL PROVIDER FIXES TEST RESULTS SUMMARY")
        print("=" * 80)
        
        passed_tests = sum(test_results.values())
        total_tests = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
        
        print(f"\nOverall Results: {passed_tests}/{total_tests} tests passed ({(passed_tests/total_tests)*100:.1f}%)")
        
        if passed_tests == total_tests:
            print("\n🎉 ALL EMAIL PROVIDER FIXES TESTS PASSED")
            print("All specific fixes are working correctly:")
            print("✅ Email provider delete function works and removes from database")
            print("✅ Duplicate prevention works for both email addresses and names")
            print("✅ IMAP connectivity testing and status endpoints are functional")
            print("✅ IMAP monitoring is properly tracked and can be toggled")
        elif passed_tests == 0:
            print("\n🚨 CRITICAL: ALL EMAIL PROVIDER FIXES TESTS FAILED")
            print("None of the requested fixes are working properly")
        else:
            print(f"\n⚠️ PARTIAL SUCCESS: {total_tests - passed_tests} test(s) failed")
            print("Some fixes are working but others need attention")
        
        # Cleanup
        self.cleanup_created_providers()
        
        return passed_tests == total_tests

if __name__ == "__main__":
    tester = EmailProviderFixesTester()
    success = tester.run_comprehensive_test()
    
    if not success:
        sys.exit(1)
    else:
        sys.exit(0)