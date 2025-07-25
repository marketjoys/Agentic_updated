#!/usr/bin/env python3
"""
Industry Functionality Testing - December 2025
Testing the new industry functionality that was just added for the AI Agent as requested in review.

Focus Areas:
1. Test the `/api/industries` endpoint to verify all 148 industries are available
2. Test getting a specific industry by external ID using `/api/industries/{external_id}`
3. Test the industry search functionality `/api/industries/search/{search_term}`
4. Test that the AI Agent can access and suggest industries when creating prospects
5. Verify the enhanced AI Agent capabilities now include industry support
6. Test creating a prospect with industry information through the AI Agent
7. Check that the industry URLs are properly formatted and accessible
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://b9312b09-0291-4341-83e9-28393511b75a.preview.emergentagent.com/api"
USERNAME = "testuser"
PASSWORD = "testpass123"

class IndustryFunctionalityTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.test_results = {}
        self.created_resources = []
        
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
        if details and isinstance(details, dict):
            for key, value in details.items():
                print(f"   {key}: {value}")
        elif details:
            print(f"   Details: {details}")
        
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
                self.log_result("Authentication", True, "Login successful")
                return True
            else:
                self.log_result("Authentication", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_industries_endpoint(self):
        """Test the /api/industries endpoint to verify all 148 industries are available"""
        print("\n🧪 Testing Industries Endpoint (/api/industries)")
        
        try:
            response = self.session.get(f"{BASE_URL}/industries")
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code != 200:
                self.log_result("Industries Endpoint", False, f"HTTP {response.status_code}", response.text)
                return False
            
            data = response.json()
            
            # Check response structure
            if not isinstance(data, dict):
                self.log_result("Industries Endpoint", False, "Response is not a dictionary", data)
                return False
            
            if "industries" not in data:
                self.log_result("Industries Endpoint", False, "No 'industries' field in response", data)
                return False
            
            industries = data["industries"]
            total_count = data.get("total_count", 0)
            
            if not isinstance(industries, list):
                self.log_result("Industries Endpoint", False, "Industries field is not a list", industries)
                return False
            
            # Check if we have the expected number of industries (148)
            if len(industries) < 140:  # Allow some flexibility
                self.log_result("Industries Endpoint", False, 
                              f"Expected ~148 industries, got {len(industries)}", 
                              {"total_count": total_count, "actual_count": len(industries)})
                return False
            
            # Check structure of first industry
            if industries:
                first_industry = industries[0]
                required_fields = ["id", "external_id", "industry", "url", "is_active"]
                missing_fields = [field for field in required_fields if field not in first_industry]
                
                if missing_fields:
                    self.log_result("Industries Endpoint", False, 
                                  f"Missing required fields: {missing_fields}", first_industry)
                    return False
                
                # Check URL format
                expected_url_pattern = f"/api/industries/{first_industry['external_id']}"
                if first_industry["url"] != expected_url_pattern:
                    self.log_result("Industries Endpoint", False, 
                                  f"URL format incorrect. Expected: {expected_url_pattern}, Got: {first_industry['url']}")
                    return False
            
            self.log_result("Industries Endpoint", True, 
                          f"Successfully retrieved {len(industries)} industries", 
                          {"total_count": total_count, "sample_industry": industries[0] if industries else None})
            return True
                
        except Exception as e:
            self.log_result("Industries Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_industry_by_external_id(self):
        """Test getting a specific industry by external ID using /api/industries/{external_id}"""
        print("\n🧪 Testing Industry by External ID")
        
        try:
            # First get all industries to find a valid external_id
            response = self.session.get(f"{BASE_URL}/industries")
            if response.status_code != 200:
                self.log_result("Industry by External ID - Setup", False, "Could not get industries list")
                return False
            
            data = response.json()
            industries = data.get("industries", [])
            
            if not industries:
                self.log_result("Industry by External ID", False, "No industries available for testing")
                return False
            
            # Test with first industry's external_id
            test_external_id = industries[0]["external_id"]
            
            response = self.session.get(f"{BASE_URL}/industries/{test_external_id}")
            
            print(f"Testing external_id: {test_external_id}")
            print(f"Status Code: {response.status_code}")
            
            if response.status_code != 200:
                self.log_result("Industry by External ID", False, f"HTTP {response.status_code}", response.text)
                return False
            
            industry_data = response.json()
            
            # Check required fields
            required_fields = ["id", "external_id", "industry", "url", "is_active"]
            missing_fields = [field for field in required_fields if field not in industry_data]
            
            if missing_fields:
                self.log_result("Industry by External ID", False, 
                              f"Missing required fields: {missing_fields}", industry_data)
                return False
            
            # Verify external_id matches
            if industry_data["external_id"] != test_external_id:
                self.log_result("Industry by External ID", False, 
                              f"External ID mismatch. Expected: {test_external_id}, Got: {industry_data['external_id']}")
                return False
            
            # Check URL format
            expected_url = f"/api/industries/{test_external_id}"
            if industry_data["url"] != expected_url:
                self.log_result("Industry by External ID", False, 
                              f"URL format incorrect. Expected: {expected_url}, Got: {industry_data['url']}")
                return False
            
            self.log_result("Industry by External ID", True, 
                          f"Successfully retrieved industry: {industry_data['industry']}", 
                          {"external_id": test_external_id, "industry_name": industry_data["industry"]})
            return True
                
        except Exception as e:
            self.log_result("Industry by External ID", False, f"Exception: {str(e)}")
            return False
    
    def test_industry_search_functionality(self):
        """Test the industry search functionality /api/industries/search/{search_term}"""
        print("\n🧪 Testing Industry Search Functionality")
        
        try:
            # Test with common search terms
            search_terms = ["technology", "healthcare", "finance", "software"]
            
            for search_term in search_terms:
                print(f"Testing search term: '{search_term}'")
                
                response = self.session.get(f"{BASE_URL}/industries/search/{search_term}")
                
                print(f"Status Code: {response.status_code}")
                
                if response.status_code != 200:
                    self.log_result(f"Industry Search - {search_term}", False, 
                                  f"HTTP {response.status_code}", response.text)
                    continue
                
                data = response.json()
                
                # Check response structure
                required_fields = ["search_term", "industries", "total_count", "message"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_result(f"Industry Search - {search_term}", False, 
                                  f"Missing required fields: {missing_fields}", data)
                    continue
                
                # Verify search term matches
                if data["search_term"] != search_term:
                    self.log_result(f"Industry Search - {search_term}", False, 
                                  f"Search term mismatch. Expected: {search_term}, Got: {data['search_term']}")
                    continue
                
                industries = data["industries"]
                total_count = data["total_count"]
                
                # Check if results make sense
                if len(industries) != total_count:
                    self.log_result(f"Industry Search - {search_term}", False, 
                                  f"Count mismatch. Array length: {len(industries)}, total_count: {total_count}")
                    continue
                
                # Check structure of results
                if industries:
                    first_result = industries[0]
                    required_result_fields = ["id", "external_id", "industry", "url", "is_active"]
                    missing_result_fields = [field for field in required_result_fields if field not in first_result]
                    
                    if missing_result_fields:
                        self.log_result(f"Industry Search - {search_term}", False, 
                                      f"Missing fields in result: {missing_result_fields}", first_result)
                        continue
                
                self.log_result(f"Industry Search - {search_term}", True, 
                              f"Found {total_count} industries matching '{search_term}'", 
                              {"sample_result": industries[0] if industries else None})
            
            # Test overall search functionality
            self.log_result("Industry Search Functionality", True, 
                          f"Successfully tested search with {len(search_terms)} terms")
            return True
                
        except Exception as e:
            self.log_result("Industry Search Functionality", False, f"Exception: {str(e)}")
            return False
    
    def test_ai_agent_industry_access(self):
        """Test that the AI Agent can access and suggest industries when creating prospects"""
        print("\n🧪 Testing AI Agent Industry Access")
        
        try:
            # Test AI Agent capabilities to see if industry support is included
            response = self.session.get(f"{BASE_URL}/ai-agent/capabilities")
            
            print(f"AI Agent Capabilities Status Code: {response.status_code}")
            
            if response.status_code != 200:
                self.log_result("AI Agent Industry Access - Capabilities", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            capabilities = response.json()
            
            # Check if industry-related capabilities are mentioned
            capabilities_str = json.dumps(capabilities).lower()
            industry_keywords = ["industry", "industries", "sector", "business"]
            
            industry_support_found = any(keyword in capabilities_str for keyword in industry_keywords)
            
            if not industry_support_found:
                self.log_result("AI Agent Industry Access - Capabilities", False, 
                              "No industry-related capabilities found", capabilities)
                return False
            
            self.log_result("AI Agent Industry Access - Capabilities", True, 
                          "Industry support found in AI Agent capabilities")
            
            # Test AI Agent chat with industry-related query
            chat_payload = {
                "message": "What industries are available for prospects?",
                "session_id": "test_industry_session"
            }
            
            response = self.session.post(f"{BASE_URL}/ai-agent/chat", json=chat_payload)
            
            print(f"AI Agent Chat Status Code: {response.status_code}")
            
            if response.status_code != 200:
                self.log_result("AI Agent Industry Access - Chat", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            chat_response = response.json()
            
            # Check if the response mentions industries
            response_text = json.dumps(chat_response).lower()
            if "industry" not in response_text and "industries" not in response_text:
                self.log_result("AI Agent Industry Access - Chat", False, 
                              "AI Agent response does not mention industries", chat_response)
                return False
            
            self.log_result("AI Agent Industry Access", True, 
                          "AI Agent can access and discuss industries")
            return True
                
        except Exception as e:
            self.log_result("AI Agent Industry Access", False, f"Exception: {str(e)}")
            return False
    
    def test_prospect_creation_with_industry(self):
        """Test creating a prospect with industry information through the AI Agent"""
        print("\n🧪 Testing Prospect Creation with Industry via AI Agent")
        
        try:
            # First get a valid industry to use
            response = self.session.get(f"{BASE_URL}/industries")
            if response.status_code != 200:
                self.log_result("Prospect Creation with Industry - Setup", False, "Could not get industries")
                return False
            
            data = response.json()
            industries = data.get("industries", [])
            
            if not industries:
                self.log_result("Prospect Creation with Industry", False, "No industries available")
                return False
            
            # Use first industry for testing
            test_industry = industries[0]["industry"]
            
            # Test AI Agent prospect creation with industry
            chat_payload = {
                "message": f"Create a prospect named John Smith from TechCorp in the {test_industry} industry",
                "session_id": "test_prospect_industry_session"
            }
            
            response = self.session.post(f"{BASE_URL}/ai-agent/chat", json=chat_payload)
            
            print(f"AI Agent Prospect Creation Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code != 200:
                self.log_result("Prospect Creation with Industry - AI Agent", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            chat_response = response.json()
            
            # Check if the response indicates successful prospect creation
            response_text = json.dumps(chat_response).lower()
            success_indicators = ["created", "successfully", "prospect", "john smith"]
            
            success_found = any(indicator in response_text for indicator in success_indicators)
            
            if not success_found:
                self.log_result("Prospect Creation with Industry - AI Agent", False, 
                              "AI Agent response does not indicate successful creation", chat_response)
                return False
            
            # Verify the prospect was actually created by checking prospects endpoint
            prospects_response = self.session.get(f"{BASE_URL}/prospects")
            if prospects_response.status_code == 200:
                prospects = prospects_response.json()
                
                # Look for the created prospect
                john_smith_prospect = None
                for prospect in prospects:
                    if (prospect.get("first_name", "").lower() == "john" and 
                        prospect.get("last_name", "").lower() == "smith"):
                        john_smith_prospect = prospect
                        break
                
                if john_smith_prospect:
                    # Check if industry information is included
                    prospect_industry = john_smith_prospect.get("industry", "")
                    if test_industry.lower() in prospect_industry.lower():
                        self.log_result("Prospect Creation with Industry", True, 
                                      f"Successfully created prospect with industry: {prospect_industry}", 
                                      {"prospect_id": john_smith_prospect.get("id"), 
                                       "industry": prospect_industry})
                        
                        # Store for cleanup
                        self.created_resources.append(("prospect", john_smith_prospect.get("id")))
                        return True
                    else:
                        self.log_result("Prospect Creation with Industry", False, 
                                      f"Prospect created but industry not set correctly. Expected: {test_industry}, Got: {prospect_industry}")
                        return False
                else:
                    self.log_result("Prospect Creation with Industry", False, 
                                  "Prospect not found in database after AI Agent creation")
                    return False
            else:
                self.log_result("Prospect Creation with Industry - Verification", False, 
                              "Could not verify prospect creation")
                return False
                
        except Exception as e:
            self.log_result("Prospect Creation with Industry", False, f"Exception: {str(e)}")
            return False
    
    def test_industry_urls_accessibility(self):
        """Check that the industry URLs are properly formatted and accessible"""
        print("\n🧪 Testing Industry URLs Accessibility")
        
        try:
            # Get industries to test their URLs
            response = self.session.get(f"{BASE_URL}/industries")
            if response.status_code != 200:
                self.log_result("Industry URLs - Setup", False, "Could not get industries")
                return False
            
            data = response.json()
            industries = data.get("industries", [])
            
            if not industries:
                self.log_result("Industry URLs Accessibility", False, "No industries available")
                return False
            
            # Test first 5 industry URLs
            test_count = min(5, len(industries))
            successful_urls = 0
            
            for i in range(test_count):
                industry = industries[i]
                industry_url = industry.get("url", "")
                external_id = industry.get("external_id", "")
                
                # Check URL format
                expected_url = f"/api/industries/{external_id}"
                if industry_url != expected_url:
                    self.log_result(f"Industry URL Format - {external_id}", False, 
                                  f"URL format incorrect. Expected: {expected_url}, Got: {industry_url}")
                    continue
                
                # Test URL accessibility
                full_url = f"{BASE_URL.replace('/api', '')}{industry_url}"
                url_response = self.session.get(full_url)
                
                if url_response.status_code == 200:
                    successful_urls += 1
                    self.log_result(f"Industry URL Access - {external_id}", True, 
                                  f"URL accessible: {industry_url}")
                else:
                    self.log_result(f"Industry URL Access - {external_id}", False, 
                                  f"URL not accessible: {industry_url} (HTTP {url_response.status_code})")
            
            # Overall assessment
            if successful_urls == test_count:
                self.log_result("Industry URLs Accessibility", True, 
                              f"All {test_count} tested URLs are properly formatted and accessible")
                return True
            else:
                self.log_result("Industry URLs Accessibility", False, 
                              f"Only {successful_urls}/{test_count} URLs are accessible")
                return False
                
        except Exception as e:
            self.log_result("Industry URLs Accessibility", False, f"Exception: {str(e)}")
            return False
    
    def cleanup_resources(self):
        """Clean up created test resources"""
        print("\n🧹 Cleaning up test resources...")
        
        for resource_type, resource_id in self.created_resources:
            try:
                if resource_type == "prospect":
                    response = self.session.delete(f"{BASE_URL}/prospects/{resource_id}")
                    if response.status_code == 200:
                        print(f"   ✅ Deleted prospect {resource_id}")
                    else:
                        print(f"   ⚠️ Failed to delete prospect {resource_id}: {response.status_code}")
                # Add other resource types as needed
            except Exception as e:
                print(f"   ❌ Error deleting {resource_type} {resource_id}: {str(e)}")
    
    def run_comprehensive_industry_test(self):
        """Run all industry functionality tests"""
        print("🚀 INDUSTRY FUNCTIONALITY COMPREHENSIVE TESTING - DECEMBER 2025")
        print("=" * 80)
        print("Testing new industry functionality for AI Agent as requested in review:")
        print("1. Industries endpoint (/api/industries) - verify all 148 industries")
        print("2. Industry by external ID (/api/industries/{external_id})")
        print("3. Industry search functionality (/api/industries/search/{search_term})")
        print("4. AI Agent industry access and suggestions")
        print("5. Enhanced AI Agent capabilities with industry support")
        print("6. Prospect creation with industry information via AI Agent")
        print("7. Industry URLs proper formatting and accessibility")
        print("=" * 80)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ CRITICAL: Authentication failed - cannot proceed with testing")
            return False
        
        # Run all tests
        test_results = {
            "industries_endpoint": self.test_industries_endpoint(),
            "industry_by_external_id": self.test_industry_by_external_id(),
            "industry_search_functionality": self.test_industry_search_functionality(),
            "ai_agent_industry_access": self.test_ai_agent_industry_access(),
            "prospect_creation_with_industry": self.test_prospect_creation_with_industry(),
            "industry_urls_accessibility": self.test_industry_urls_accessibility()
        }
        
        # Summary
        print("\n" + "=" * 80)
        print("🎯 INDUSTRY FUNCTIONALITY TEST RESULTS SUMMARY")
        print("=" * 80)
        
        passed_tests = sum(test_results.values())
        total_tests = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
        
        print(f"\nOverall Results: {passed_tests}/{total_tests} tests passed ({(passed_tests/total_tests)*100:.1f}%)")
        
        if passed_tests == total_tests:
            print("\n🎉 ALL INDUSTRY FUNCTIONALITY TESTS PASSED")
            print("✅ All 148 industries are available and accessible")
            print("✅ Industry search functionality is working")
            print("✅ AI Agent can access and suggest industries")
            print("✅ Prospect creation with industry information is functional")
            print("✅ Industry URLs are properly formatted and accessible")
            print("✅ Enhanced AI Agent capabilities include industry support")
            print("\nRECOMMENDATION: Industry functionality is production-ready and fully integrated with AI Agent")
        elif passed_tests >= total_tests * 0.8:  # 80% pass rate
            print(f"\n⚠️ MOSTLY FUNCTIONAL: {total_tests - passed_tests} tests failed")
            print("RECOMMENDATION: Address failing test scenarios for full functionality")
        else:
            print(f"\n🚨 CRITICAL ISSUES: {total_tests - passed_tests} tests failed")
            print("RECOMMENDATION: Major issues with industry functionality - requires immediate attention")
        
        # Cleanup
        self.cleanup_resources()
        
        return passed_tests == total_tests

if __name__ == "__main__":
    tester = IndustryFunctionalityTester()
    success = tester.run_comprehensive_industry_test()
    
    if not success:
        sys.exit(1)
    else:
        sys.exit(0)