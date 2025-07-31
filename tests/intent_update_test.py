#!/usr/bin/env python3
"""
Intent Update Functionality Testing - January 2025
Testing the specific intent update functionality as requested in review.

Focus Areas:
1. Get all intents (GET /api/intents)
2. Test updating an intent (PUT /api/intents/{id}) with partial data
3. Verify the update worked by getting the specific intent
4. Test updating multiple fields at once
5. Test error handling for non-existent intents
6. Ensure all intent CRUD operations work properly

The issue was that intent updates were failing, but the backend endpoint has been 
fixed to accept dict instead of IntentConfig model.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://6b79b9a6-93ed-4a33-b1a5-f766f54ddce0.preview.emergentagent.com/api"
USERNAME = "testuser"
PASSWORD = "testpass123"

class IntentUpdateTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.created_intents = []
        
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
    
    def test_get_all_intents(self):
        """Test GET /api/intents - Get all intents"""
        print("\n🧪 Testing GET /api/intents - Get all intents")
        
        try:
            response = self.session.get(f"{BASE_URL}/intents")
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                intents = response.json()
                
                if isinstance(intents, list):
                    print(f"✅ Successfully retrieved {len(intents)} intents")
                    
                    # Show some details about existing intents
                    for i, intent in enumerate(intents[:3]):  # Show first 3
                        print(f"   Intent {i+1}: {intent.get('name', 'Unknown')} (ID: {intent.get('id', 'No ID')[:8]}...)")
                    
                    return True, intents
                else:
                    print(f"❌ Expected list, got: {type(intents)}")
                    return False, []
            else:
                print(f"❌ Failed to get intents: {response.status_code} - {response.text}")
                return False, []
                
        except Exception as e:
            print(f"❌ Get intents test error: {str(e)}")
            return False, []
    
    def create_test_intent(self):
        """Create a test intent for update testing"""
        print("\n🧪 Creating test intent for update testing")
        
        try:
            intent_data = {
                "name": "Test Intent for Updates",
                "description": "This is a test intent for testing updates",
                "keywords": ["test", "update", "original"],
                "confidence_threshold": 0.7,
                "auto_respond": True
            }
            
            response = self.session.post(f"{BASE_URL}/intents", json=intent_data)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                created_intent = response.json()
                intent_id = created_intent.get("id")
                
                if intent_id:
                    self.created_intents.append(intent_id)
                    print(f"✅ Successfully created test intent with ID: {intent_id[:8]}...")
                    return True, intent_id, created_intent
                else:
                    print(f"❌ No ID in created intent response: {created_intent}")
                    return False, None, None
            else:
                print(f"❌ Failed to create test intent: {response.status_code} - {response.text}")
                return False, None, None
                
        except Exception as e:
            print(f"❌ Create test intent error: {str(e)}")
            return False, None, None
    
    def test_update_intent_partial_data(self, intent_id):
        """Test updating an intent with partial data"""
        print(f"\n🧪 Testing PUT /api/intents/{intent_id[:8]}... - Update with partial data")
        
        try:
            # Test 1: Update only the name
            partial_update = {
                "name": "Updated Test Intent Name"
            }
            
            response = self.session.put(f"{BASE_URL}/intents/{intent_id}", json=partial_update)
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("message") == "Intent updated successfully":
                    print("✅ Partial update (name only) successful")
                    return True
                else:
                    print(f"❌ Unexpected response format: {result}")
                    return False
            else:
                print(f"❌ Partial update failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Partial update test error: {str(e)}")
            return False
    
    def test_get_specific_intent(self, intent_id):
        """Test getting a specific intent to verify update worked"""
        print(f"\n🧪 Testing GET /api/intents/{intent_id[:8]}... - Verify update worked")
        
        try:
            response = self.session.get(f"{BASE_URL}/intents/{intent_id}")
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                intent = response.json()
                
                # Check if the name was updated
                if intent.get("name") == "Updated Test Intent Name":
                    print("✅ Intent update verified - name was successfully updated")
                    print(f"   Current name: {intent.get('name')}")
                    print(f"   Description: {intent.get('description', 'No description')}")
                    print(f"   Keywords: {intent.get('keywords', [])}")
                    print(f"   Auto-respond: {intent.get('auto_respond', False)}")
                    return True, intent
                else:
                    print(f"❌ Intent update not reflected. Current name: {intent.get('name')}")
                    return False, intent
            else:
                print(f"❌ Failed to get specific intent: {response.status_code} - {response.text}")
                return False, None
                
        except Exception as e:
            print(f"❌ Get specific intent test error: {str(e)}")
            return False, None
    
    def test_update_multiple_fields(self, intent_id):
        """Test updating multiple fields at once"""
        print(f"\n🧪 Testing PUT /api/intents/{intent_id[:8]}... - Update multiple fields")
        
        try:
            # Update multiple fields at once
            multi_field_update = {
                "name": "Multi-Field Updated Intent",
                "description": "Updated description with multiple fields",
                "keywords": ["updated", "multiple", "fields", "test"],
                "confidence_threshold": 0.8,
                "auto_respond": False
            }
            
            response = self.session.put(f"{BASE_URL}/intents/{intent_id}", json=multi_field_update)
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("message") == "Intent updated successfully":
                    print("✅ Multiple fields update successful")
                    
                    # Verify the update by getting the intent
                    verify_response = self.session.get(f"{BASE_URL}/intents/{intent_id}")
                    if verify_response.status_code == 200:
                        updated_intent = verify_response.json()
                        
                        # Check all updated fields
                        checks = [
                            ("name", "Multi-Field Updated Intent"),
                            ("description", "Updated description with multiple fields"),
                            ("confidence_threshold", 0.8),
                            ("auto_respond", False)
                        ]
                        
                        all_correct = True
                        for field, expected_value in checks:
                            actual_value = updated_intent.get(field)
                            if actual_value == expected_value:
                                print(f"   ✅ {field}: {actual_value}")
                            else:
                                print(f"   ❌ {field}: expected {expected_value}, got {actual_value}")
                                all_correct = False
                        
                        # Check keywords separately (list comparison)
                        expected_keywords = ["updated", "multiple", "fields", "test"]
                        actual_keywords = updated_intent.get("keywords", [])
                        if set(actual_keywords) == set(expected_keywords):
                            print(f"   ✅ keywords: {actual_keywords}")
                        else:
                            print(f"   ❌ keywords: expected {expected_keywords}, got {actual_keywords}")
                            all_correct = False
                        
                        return all_correct
                    else:
                        print("❌ Could not verify multiple field update")
                        return False
                else:
                    print(f"❌ Unexpected response format: {result}")
                    return False
            else:
                print(f"❌ Multiple fields update failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Multiple fields update test error: {str(e)}")
            return False
    
    def test_error_handling_nonexistent_intent(self):
        """Test error handling for non-existent intents"""
        print("\n🧪 Testing error handling for non-existent intents")
        
        try:
            fake_intent_id = "non-existent-intent-id-12345"
            
            # Test 1: Update non-existent intent
            update_data = {
                "name": "This should fail"
            }
            
            response = self.session.put(f"{BASE_URL}/intents/{fake_intent_id}", json=update_data)
            
            print(f"Update non-existent intent - Status Code: {response.status_code}")
            
            if response.status_code == 404:
                print("✅ Correctly returned 404 for non-existent intent update")
                update_test_passed = True
            else:
                print(f"❌ Expected 404, got {response.status_code} - {response.text}")
                update_test_passed = False
            
            # Test 2: Get non-existent intent
            response = self.session.get(f"{BASE_URL}/intents/{fake_intent_id}")
            
            print(f"Get non-existent intent - Status Code: {response.status_code}")
            
            if response.status_code == 404:
                print("✅ Correctly returned 404 for non-existent intent get")
                get_test_passed = True
            else:
                print(f"❌ Expected 404, got {response.status_code} - {response.text}")
                get_test_passed = False
            
            # Test 3: Delete non-existent intent
            response = self.session.delete(f"{BASE_URL}/intents/{fake_intent_id}")
            
            print(f"Delete non-existent intent - Status Code: {response.status_code}")
            
            if response.status_code == 404:
                print("✅ Correctly returned 404 for non-existent intent delete")
                delete_test_passed = True
            else:
                print(f"❌ Expected 404, got {response.status_code} - {response.text}")
                delete_test_passed = False
            
            return update_test_passed and get_test_passed and delete_test_passed
                
        except Exception as e:
            print(f"❌ Error handling test error: {str(e)}")
            return False
    
    def test_intent_crud_operations(self):
        """Test all intent CRUD operations work properly"""
        print("\n🧪 Testing complete intent CRUD operations")
        
        try:
            # CREATE
            create_data = {
                "name": "CRUD Test Intent",
                "description": "Testing all CRUD operations",
                "keywords": ["crud", "test", "operations"],
                "confidence_threshold": 0.75,
                "auto_respond": True
            }
            
            response = self.session.post(f"{BASE_URL}/intents", json=create_data)
            
            if response.status_code != 200:
                print(f"❌ CREATE failed: {response.status_code} - {response.text}")
                return False
            
            created_intent = response.json()
            intent_id = created_intent.get("id")
            
            if not intent_id:
                print("❌ CREATE failed: No ID in response")
                return False
            
            self.created_intents.append(intent_id)
            print(f"✅ CREATE successful: {intent_id[:8]}...")
            
            # READ (specific)
            response = self.session.get(f"{BASE_URL}/intents/{intent_id}")
            
            if response.status_code != 200:
                print(f"❌ READ (specific) failed: {response.status_code} - {response.text}")
                return False
            
            read_intent = response.json()
            if read_intent.get("name") != "CRUD Test Intent":
                print(f"❌ READ (specific) failed: Wrong name {read_intent.get('name')}")
                return False
            
            print("✅ READ (specific) successful")
            
            # UPDATE
            update_data = {
                "name": "Updated CRUD Test Intent",
                "description": "Updated description"
            }
            
            response = self.session.put(f"{BASE_URL}/intents/{intent_id}", json=update_data)
            
            if response.status_code != 200:
                print(f"❌ UPDATE failed: {response.status_code} - {response.text}")
                return False
            
            print("✅ UPDATE successful")
            
            # Verify UPDATE
            response = self.session.get(f"{BASE_URL}/intents/{intent_id}")
            if response.status_code == 200:
                updated_intent = response.json()
                if updated_intent.get("name") == "Updated CRUD Test Intent":
                    print("✅ UPDATE verification successful")
                else:
                    print(f"❌ UPDATE verification failed: {updated_intent.get('name')}")
                    return False
            else:
                print("❌ UPDATE verification failed: Could not retrieve updated intent")
                return False
            
            # DELETE
            response = self.session.delete(f"{BASE_URL}/intents/{intent_id}")
            
            if response.status_code != 200:
                print(f"❌ DELETE failed: {response.status_code} - {response.text}")
                return False
            
            print("✅ DELETE successful")
            
            # Verify DELETE
            response = self.session.get(f"{BASE_URL}/intents/{intent_id}")
            if response.status_code == 404:
                print("✅ DELETE verification successful (intent not found)")
                # Remove from cleanup list since it's already deleted
                if intent_id in self.created_intents:
                    self.created_intents.remove(intent_id)
            else:
                print(f"❌ DELETE verification failed: {response.status_code}")
                return False
            
            return True
                
        except Exception as e:
            print(f"❌ CRUD operations test error: {str(e)}")
            return False
    
    def cleanup_test_intents(self):
        """Clean up created test intents"""
        print("\n🧹 Cleaning up test intents...")
        
        for intent_id in self.created_intents:
            try:
                response = self.session.delete(f"{BASE_URL}/intents/{intent_id}")
                if response.status_code == 200:
                    print(f"   ✅ Deleted intent {intent_id[:8]}...")
                else:
                    print(f"   ⚠️ Failed to delete intent {intent_id[:8]}...: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Error deleting intent {intent_id[:8]}...: {str(e)}")
    
    def run_comprehensive_intent_update_test(self):
        """Run comprehensive intent update functionality tests"""
        print("🚀 INTENT UPDATE FUNCTIONALITY TESTING - JANUARY 2025")
        print("=" * 80)
        print("Testing intent update functionality as requested in review:")
        print("1. Get all intents (GET /api/intents)")
        print("2. Test updating an intent (PUT /api/intents/{id}) with partial data")
        print("3. Verify the update worked by getting the specific intent")
        print("4. Test updating multiple fields at once")
        print("5. Test error handling for non-existent intents")
        print("6. Ensure all intent CRUD operations work properly")
        print("=" * 80)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ CRITICAL: Authentication failed - cannot proceed with testing")
            return False
        
        # Run all tests
        test_results = {}
        
        # Test 1: Get all intents
        success, existing_intents = self.test_get_all_intents()
        test_results["get_all_intents"] = success
        
        # Create a test intent for update testing
        success, test_intent_id, created_intent = self.create_test_intent()
        if not success:
            print("❌ CRITICAL: Could not create test intent - cannot proceed with update tests")
            return False
        
        # Test 2: Update intent with partial data
        test_results["update_partial_data"] = self.test_update_intent_partial_data(test_intent_id)
        
        # Test 3: Verify update worked
        success, updated_intent = self.test_get_specific_intent(test_intent_id)
        test_results["verify_update"] = success
        
        # Test 4: Update multiple fields at once
        test_results["update_multiple_fields"] = self.test_update_multiple_fields(test_intent_id)
        
        # Test 5: Error handling for non-existent intents
        test_results["error_handling"] = self.test_error_handling_nonexistent_intent()
        
        # Test 6: Complete CRUD operations
        test_results["crud_operations"] = self.test_intent_crud_operations()
        
        # Cleanup
        self.cleanup_test_intents()
        
        # Summary
        print("\n" + "=" * 80)
        print("🎯 INTENT UPDATE FUNCTIONALITY TEST RESULTS SUMMARY")
        print("=" * 80)
        
        passed_tests = sum(test_results.values())
        total_tests = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
        
        print(f"\nOverall Results: {passed_tests}/{total_tests} tests passed ({(passed_tests/total_tests)*100:.1f}%)")
        
        if passed_tests == total_tests:
            print("\n🎉 ALL INTENT UPDATE TESTS PASSED")
            print("Intent update functionality is fully operational!")
            print("✅ The fix to accept dict instead of IntentConfig model is working correctly")
        elif passed_tests >= total_tests * 0.8:  # 80% or more
            print(f"\n✅ MOSTLY FUNCTIONAL: {passed_tests}/{total_tests} tests passed")
            print("Intent update functionality is mostly working with minor issues")
        else:
            print(f"\n❌ SIGNIFICANT ISSUES: Only {passed_tests}/{total_tests} tests passed")
            print("Intent update functionality has significant problems")
        
        # Specific findings
        if test_results.get("update_partial_data") and test_results.get("verify_update"):
            print("\n🔧 KEY FINDING: PUT /api/intents/{id} endpoint is working correctly")
            print("✅ Partial data updates are functional")
            print("✅ Updates are persisted and retrievable")
        
        if test_results.get("update_multiple_fields"):
            print("✅ Multiple field updates work correctly")
        
        if test_results.get("error_handling"):
            print("✅ Error handling for non-existent intents is proper")
        
        if test_results.get("crud_operations"):
            print("✅ All CRUD operations are functional")
        
        return passed_tests == total_tests

if __name__ == "__main__":
    tester = IntentUpdateTester()
    success = tester.run_comprehensive_intent_update_test()
    
    if not success:
        sys.exit(1)
    else:
        sys.exit(0)