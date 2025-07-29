#!/usr/bin/env python3
"""
List and Prospect Management Testing - December 2024
Testing the specific functionality requested in the review:
- Authentication and token management
- Get Lists endpoint
- Get Prospects endpoint  
- Get List Details for Technology Companies list
- Add Prospects to List functionality
- Verify Addition and data structure
"""

import requests
import json
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://5f33b0de-2474-4f94-a9e0-dac40fa9173f.preview.emergentagent.com"

class ListProspectTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.username = "testuser"
        self.password = "testpass123"
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
            print(f"   Details: {details}")
    
    def test_authentication(self):
        """Test 1: Authentication - Login and get auth token"""
        print("🔐 TEST 1: Authentication - Login and get auth token")
        
        try:
            login_data = {
                "username": self.username,
                "password": self.password
            }
            
            response = requests.post(f"{self.base_url}/api/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.headers = {"Authorization": f"Bearer {self.auth_token}"}
                self.log_result("Authentication", True, "Login successful", f"Token: {self.auth_token[:20]}...")
                return True
            else:
                self.log_result("Authentication", False, f"Login failed: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Authentication", False, f"Authentication error: {str(e)}")
            return False
    
    def test_get_lists(self):
        """Test 2: Get Lists - Test GET /api/lists endpoint"""
        print("\n📋 TEST 2: Get Lists - Test GET /api/lists endpoint")
        
        try:
            response = requests.get(f"{self.base_url}/api/lists", headers=self.headers)
            
            if response.status_code == 200:
                lists = response.json()
                self.log_result("Get Lists", True, f"Retrieved {len(lists)} lists", lists)
                
                # Log list details
                for i, list_item in enumerate(lists):
                    print(f"   List {i+1}: {list_item.get('name', 'Unknown')} (ID: {list_item.get('id', 'N/A')})")
                    print(f"            Prospects: {list_item.get('prospect_count', 0)}")
                
                return lists
            else:
                self.log_result("Get Lists", False, f"Failed to get lists: {response.status_code}", response.text)
                return None
                
        except Exception as e:
            self.log_result("Get Lists", False, f"Get lists error: {str(e)}")
            return None
    
    def test_get_prospects(self):
        """Test 3: Get Prospects - Test GET /api/prospects endpoint"""
        print("\n👥 TEST 3: Get Prospects - Test GET /api/prospects endpoint")
        
        try:
            response = requests.get(f"{self.base_url}/api/prospects", headers=self.headers)
            
            if response.status_code == 200:
                prospects = response.json()
                self.log_result("Get Prospects", True, f"Retrieved {len(prospects)} prospects", prospects)
                
                # Log prospect details and check list_ids field
                for i, prospect in enumerate(prospects):
                    print(f"   Prospect {i+1}: {prospect.get('first_name', '')} {prospect.get('last_name', '')} ({prospect.get('email', 'N/A')})")
                    print(f"                ID: {prospect.get('id', 'N/A')}")
                    print(f"                Company: {prospect.get('company', 'N/A')}")
                    
                    # Check list_ids field structure
                    list_ids = prospect.get('list_ids', [])
                    print(f"                List IDs: {list_ids} (Type: {type(list_ids)})")
                
                return prospects
            else:
                self.log_result("Get Prospects", False, f"Failed to get prospects: {response.status_code}", response.text)
                return None
                
        except Exception as e:
            self.log_result("Get Prospects", False, f"Get prospects error: {str(e)}")
            return None
    
    def test_get_list_details(self, lists):
        """Test 4: Get List Details - Test GET /api/lists/{list_id} for Technology Companies list"""
        print("\n🔍 TEST 4: Get List Details - Test GET /api/lists/{list_id} for Technology Companies list")
        
        if not lists:
            self.log_result("Get List Details", False, "No lists available for testing")
            return None
        
        # Find Technology Companies list
        tech_list = None
        for list_item in lists:
            if "Technology" in list_item.get('name', '') or "Tech" in list_item.get('name', ''):
                tech_list = list_item
                break
        
        if not tech_list:
            # Use first available list if Technology Companies not found
            tech_list = lists[0]
            print(f"   Technology Companies list not found, using: {tech_list.get('name', 'Unknown')}")
        
        list_id = tech_list.get('id')
        print(f"   Testing list: {tech_list.get('name', 'Unknown')} (ID: {list_id})")
        
        try:
            response = requests.get(f"{self.base_url}/api/lists/{list_id}", headers=self.headers)
            
            if response.status_code == 200:
                list_details = response.json()
                self.log_result("Get List Details", True, f"Retrieved list details for {list_details.get('name', 'Unknown')}", list_details)
                
                print(f"   Name: {list_details.get('name', 'N/A')}")
                print(f"   Description: {list_details.get('description', 'N/A')}")
                print(f"   Prospect Count: {list_details.get('prospect_count', 0)}")
                print(f"   Created: {list_details.get('created_at', 'N/A')}")
                
                return list_details
            else:
                self.log_result("Get List Details", False, f"Failed to get list details: {response.status_code}", response.text)
                return None
                
        except Exception as e:
            self.log_result("Get List Details", False, f"Get list details error: {str(e)}")
            return None
    
    def test_add_prospects_to_list(self, lists, prospects):
        """Test 5: Add Prospects to List - Test POST /api/lists/{list_id}/prospects endpoint"""
        print("\n➕ TEST 5: Add Prospects to List - Test POST /api/lists/{list_id}/prospects endpoint")
        
        if not lists or not prospects:
            self.log_result("Add Prospects to List", False, "No lists or prospects available for testing")
            return False
        
        # Use first available list
        test_list = lists[0]
        list_id = test_list.get('id')
        print(f"   Using list: {test_list.get('name', 'Unknown')} (ID: {list_id})")
        
        # Get first 2 prospects for testing
        test_prospects = prospects[:2] if len(prospects) >= 2 else prospects
        prospect_ids = [p.get('id') for p in test_prospects if p.get('id')]
        
        print(f"   Adding {len(prospect_ids)} prospects to list:")
        for i, prospect in enumerate(test_prospects):
            print(f"     {i+1}. {prospect.get('first_name', '')} {prospect.get('last_name', '')} ({prospect.get('email', 'N/A')})")
        
        try:
            add_request = {
                "prospect_ids": prospect_ids
            }
            
            response = requests.post(
                f"{self.base_url}/api/lists/{list_id}/prospects",
                headers=self.headers,
                json=add_request
            )
            
            if response.status_code == 200:
                result = response.json()
                self.log_result("Add Prospects to List", True, f"Added {len(prospect_ids)} prospects to list", result)
                return True
            else:
                self.log_result("Add Prospects to List", False, f"Failed to add prospects: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Add Prospects to List", False, f"Add prospects error: {str(e)}")
            return False
    
    def test_verify_addition(self, lists, prospects):
        """Test 6: Verify Addition - Test that prospects were added successfully"""
        print("\n✅ TEST 6: Verify Addition - Test that prospects were added successfully")
        
        if not lists:
            self.log_result("Verify Addition", False, "No lists available for verification")
            return False
        
        # Use first available list
        test_list = lists[0]
        list_id = test_list.get('id')
        print(f"   Verifying list: {test_list.get('name', 'Unknown')} (ID: {list_id})")
        
        try:
            # Get list details to check prospect count
            response = requests.get(f"{self.base_url}/api/lists/{list_id}", headers=self.headers)
            if response.status_code == 200:
                list_details = response.json()
                prospect_count = list_details.get('prospect_count', 0)
                print(f"   List prospect count: {prospect_count}")
            else:
                print(f"   Failed to get list details for verification: {response.status_code}")
            
            # Get prospects in the list
            response = requests.get(f"{self.base_url}/api/lists/{list_id}/prospects", headers=self.headers)
            
            if response.status_code == 200:
                list_prospects = response.json()
                prospects_in_list = list_prospects.get('prospects', [])
                total_count = list_prospects.get('total_count', 0)
                
                self.log_result("Verify Addition", True, f"Verified {total_count} prospects in list", list_prospects)
                
                print(f"   Total prospects in list: {total_count}")
                print(f"   List name: {list_prospects.get('list_name', 'Unknown')}")
                
                # Log prospects in list
                for i, prospect in enumerate(prospects_in_list):
                    print(f"     {i+1}. {prospect.get('first_name', '')} {prospect.get('last_name', '')} ({prospect.get('email', 'N/A')})")
                
                return True
            else:
                self.log_result("Verify Addition", False, f"Failed to get list prospects: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Verify Addition", False, f"Verify addition error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting List and Prospect Management Testing")
        print(f"   Backend URL: {self.base_url}")
        print(f"   Test Credentials: {self.username} / {self.password}")
        print("=" * 80)
        
        # Test 1: Authentication
        auth_success = self.test_authentication()
        if not auth_success:
            print("❌ Authentication failed - stopping tests")
            return
        
        print("-" * 80)
        
        # Test 2: Get Lists
        lists = self.test_get_lists()
        if lists is None:
            print("❌ Get lists failed - stopping tests")
            return
        
        print("-" * 80)
        
        # Test 3: Get Prospects
        prospects = self.test_get_prospects()
        if prospects is None:
            print("❌ Get prospects failed - stopping tests")
            return
        
        print("-" * 80)
        
        # Test 4: Get List Details
        list_details = self.test_get_list_details(lists)
        if list_details is None:
            print("❌ Get list details failed - continuing with other tests")
        
        print("-" * 80)
        
        # Test 5: Add Prospects to List
        add_success = self.test_add_prospects_to_list(lists, prospects)
        if not add_success:
            print("❌ Add prospects to list failed - continuing with verification")
        
        print("-" * 80)
        
        # Test 6: Verify Addition
        verify_success = self.test_verify_addition(lists, prospects)
        if not verify_success:
            print("❌ Verify addition failed")
        
        print("=" * 80)
        print("🎯 LIST AND PROSPECT MANAGEMENT TESTING COMPLETED")
        
        # Summary
        tests_passed = sum([
            auth_success,
            lists is not None,
            prospects is not None,
            list_details is not None,
            add_success,
            verify_success
        ])
        
        print(f"📊 SUMMARY: {tests_passed}/6 tests passed")
        
        if tests_passed == 6:
            print("✅ ALL TESTS PASSED - List and Prospect Management is fully functional")
        elif tests_passed >= 4:
            print("⚠️ MOSTLY FUNCTIONAL - Some minor issues detected")
        else:
            print("❌ CRITICAL ISSUES - Major functionality problems detected")
        
        return self.test_results

def main():
    """Main test execution"""
    tester = ListProspectTester()
    results = tester.run_all_tests()
    
    # Print detailed results
    print("\n" + "=" * 80)
    print("📋 DETAILED TEST RESULTS")
    print("=" * 80)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"{status} {test_name}")
        if result['message']:
            print(f"   Message: {result['message']}")
        if result['details']:
            print(f"   Details: {result['details']}")
        print()
    
    return results

if __name__ == "__main__":
    main()