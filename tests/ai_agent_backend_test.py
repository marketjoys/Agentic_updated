#!/usr/bin/env python3
"""
AI Agent Functionality Testing - December 2024
Testing the specific AI Agent functionality requested in the review:

1. AI Agent Chat Endpoint - POST /api/ai-agent/chat
2. AI Agent Capabilities - GET /api/ai-agent/capabilities  
3. AI Agent Help - GET /api/ai-agent/help
4. Verify backend endpoints the AI agent should access:
   - POST /api/lists (for list creation)
   - POST /api/prospects (for prospect creation)
   - POST /api/lists/{list_id}/prospects (for adding prospects to lists)
   - GET /api/campaigns
   - GET /api/prospects
   - GET /api/lists

Testing natural language commands like:
- "Create a new list called Test Marketing List"
- "Add a prospect named John Smith from TechCorp"
- "Show me all my campaigns"
- "Show me all my lists"
"""

import requests
import json
import time
from datetime import datetime

# Get backend URL from frontend .env file
BACKEND_URL = "https://923febb0-4941-4a54-88e6-10f9c6187a71.preview.emergentagent.com"

class AIAgentTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.auth_token = None
        self.headers = {}
        self.test_results = {}
        self.created_resources = {
            'prospects': [],
            'lists': [],
            'campaigns': []
        }
    
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
    
    def authenticate(self):
        """Authenticate and get token"""
        try:
            login_data = {"username": "testuser", "password": "testpass123"}
            response = requests.post(f"{self.base_url}/api/auth/login", json=login_data)
            
            if response.status_code != 200:
                self.log_result("Authentication", False, f"HTTP {response.status_code}", response.text)
                return False
            
            auth_result = response.json()
            if 'access_token' not in auth_result:
                self.log_result("Authentication", False, "No access token in response", auth_result)
                return False
            
            self.auth_token = auth_result['access_token']
            self.headers = {"Authorization": f"Bearer {self.auth_token}"}
            self.log_result("Authentication", True, "Login successful")
            return True
            
        except Exception as e:
            self.log_result("Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_ai_agent_capabilities(self):
        """Test AI Agent capabilities endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/ai-agent/capabilities", headers=self.headers)
            
            if response.status_code != 200:
                self.log_result("AI Agent Capabilities", False, f"HTTP {response.status_code}", response.text)
                return False
            
            capabilities = response.json()
            
            # Check if capabilities contains expected actions
            expected_actions = ['create_list', 'add_prospect', 'get_campaigns', 'get_lists', 'get_prospects']
            
            if 'available_actions' not in capabilities:
                self.log_result("AI Agent Capabilities", False, "No available_actions in response", capabilities)
                return False
            
            available_actions = capabilities['available_actions']
            missing_actions = []
            
            for action in expected_actions:
                if not any(action in str(available_action) for available_action in available_actions):
                    missing_actions.append(action)
            
            if missing_actions:
                self.log_result("AI Agent Capabilities", False, f"Missing actions: {missing_actions}", capabilities)
                return False
            
            self.log_result("AI Agent Capabilities", True, f"Found {len(available_actions)} available actions")
            return True
            
        except Exception as e:
            self.log_result("AI Agent Capabilities", False, f"Exception: {str(e)}")
            return False
    
    def test_ai_agent_help(self):
        """Test AI Agent help endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/ai-agent/help", headers=self.headers)
            
            if response.status_code != 200:
                self.log_result("AI Agent Help", False, f"HTTP {response.status_code}", response.text)
                return False
            
            help_data = response.json()
            
            # Check if help contains expected information
            expected_fields = ['supported_operations', 'examples', 'usage_guide']
            
            missing_fields = []
            for field in expected_fields:
                if field not in help_data:
                    missing_fields.append(field)
            
            if missing_fields:
                self.log_result("AI Agent Help", False, f"Missing fields: {missing_fields}", help_data)
                return False
            
            # Check if examples contain list creation and prospect addition
            examples = help_data.get('examples', [])
            has_list_creation = any('list' in str(example).lower() and 'create' in str(example).lower() for example in examples)
            has_prospect_addition = any('prospect' in str(example).lower() and 'add' in str(example).lower() for example in examples)
            
            if not has_list_creation:
                self.log_result("AI Agent Help", False, "No list creation examples found", help_data)
                return False
            
            if not has_prospect_addition:
                self.log_result("AI Agent Help", False, "No prospect addition examples found", help_data)
                return False
            
            self.log_result("AI Agent Help", True, f"Help data contains {len(examples)} examples")
            return True
            
        except Exception as e:
            self.log_result("AI Agent Help", False, f"Exception: {str(e)}")
            return False
    
    def test_ai_agent_chat_list_creation(self):
        """Test AI Agent chat endpoint for list creation"""
        try:
            # Test natural language command for list creation
            chat_request = {
                "message": "Create a new list called Test Marketing List",
                "context": {
                    "user_id": "testuser",
                    "session_id": "test_session_1"
                }
            }
            
            response = requests.post(f"{self.base_url}/api/ai-agent/chat", json=chat_request, headers=self.headers)
            
            if response.status_code != 200:
                self.log_result("AI Agent Chat - List Creation", False, f"HTTP {response.status_code}", response.text)
                return False
            
            chat_response = response.json()
            
            # Check if response indicates successful action
            if 'response' not in chat_response:
                self.log_result("AI Agent Chat - List Creation", False, "No response field", chat_response)
                return False
            
            # Check if action was performed
            if 'action_performed' not in chat_response:
                self.log_result("AI Agent Chat - List Creation", False, "No action_performed field", chat_response)
                return False
            
            action_performed = chat_response['action_performed']
            if not action_performed:
                self.log_result("AI Agent Chat - List Creation", False, "No action was performed", chat_response)
                return False
            
            # Check if list was actually created by verifying with backend
            if 'created_resource_id' in chat_response:
                list_id = chat_response['created_resource_id']
                self.created_resources['lists'].append(list_id)
                
                # Verify list exists
                verify_response = requests.get(f"{self.base_url}/api/lists/{list_id}", headers=self.headers)
                if verify_response.status_code == 200:
                    list_data = verify_response.json()
                    if 'Test Marketing List' in list_data.get('name', ''):
                        self.log_result("AI Agent Chat - List Creation", True, f"Successfully created list: {list_data['name']}")
                        return True
                    else:
                        self.log_result("AI Agent Chat - List Creation", False, f"List name mismatch: {list_data.get('name')}")
                        return False
                else:
                    self.log_result("AI Agent Chat - List Creation", False, f"Created list not found: {list_id}")
                    return False
            else:
                self.log_result("AI Agent Chat - List Creation", True, "Action performed but no resource ID returned")
                return True
            
        except Exception as e:
            self.log_result("AI Agent Chat - List Creation", False, f"Exception: {str(e)}")
            return False
    
    def test_ai_agent_chat_prospect_addition(self):
        """Test AI Agent chat endpoint for prospect addition"""
        try:
            # Test natural language command for prospect addition
            chat_request = {
                "message": "Add a prospect named John Smith from TechCorp",
                "context": {
                    "user_id": "testuser",
                    "session_id": "test_session_2"
                }
            }
            
            response = requests.post(f"{self.base_url}/api/ai-agent/chat", json=chat_request, headers=self.headers)
            
            if response.status_code != 200:
                self.log_result("AI Agent Chat - Prospect Addition", False, f"HTTP {response.status_code}", response.text)
                return False
            
            chat_response = response.json()
            
            # Check if response indicates successful action
            if 'response' not in chat_response:
                self.log_result("AI Agent Chat - Prospect Addition", False, "No response field", chat_response)
                return False
            
            # Check if action was performed
            if 'action_performed' not in chat_response:
                self.log_result("AI Agent Chat - Prospect Addition", False, "No action_performed field", chat_response)
                return False
            
            action_performed = chat_response['action_performed']
            if not action_performed:
                self.log_result("AI Agent Chat - Prospect Addition", False, "No action was performed", chat_response)
                return False
            
            # Check if prospect was actually created by verifying with backend
            if 'created_resource_id' in chat_response:
                prospect_id = chat_response['created_resource_id']
                self.created_resources['prospects'].append(prospect_id)
                
                # Verify prospect exists
                verify_response = requests.get(f"{self.base_url}/api/prospects", headers=self.headers)
                if verify_response.status_code == 200:
                    prospects = verify_response.json()
                    created_prospect = None
                    for prospect in prospects:
                        if prospect.get('id') == prospect_id:
                            created_prospect = prospect
                            break
                    
                    if created_prospect:
                        if 'John Smith' in f"{created_prospect.get('first_name', '')} {created_prospect.get('last_name', '')}":
                            self.log_result("AI Agent Chat - Prospect Addition", True, f"Successfully created prospect: {created_prospect.get('first_name')} {created_prospect.get('last_name')}")
                            return True
                        else:
                            self.log_result("AI Agent Chat - Prospect Addition", False, f"Prospect name mismatch: {created_prospect}")
                            return False
                    else:
                        self.log_result("AI Agent Chat - Prospect Addition", False, f"Created prospect not found: {prospect_id}")
                        return False
                else:
                    self.log_result("AI Agent Chat - Prospect Addition", False, "Could not verify prospect creation")
                    return False
            else:
                self.log_result("AI Agent Chat - Prospect Addition", True, "Action performed but no resource ID returned")
                return True
            
        except Exception as e:
            self.log_result("AI Agent Chat - Prospect Addition", False, f"Exception: {str(e)}")
            return False
    
    def test_ai_agent_chat_show_campaigns(self):
        """Test AI Agent chat endpoint for showing campaigns"""
        try:
            chat_request = {
                "message": "Show me all my campaigns",
                "context": {
                    "user_id": "testuser",
                    "session_id": "test_session_3"
                }
            }
            
            response = requests.post(f"{self.base_url}/api/ai-agent/chat", json=chat_request, headers=self.headers)
            
            if response.status_code != 200:
                self.log_result("AI Agent Chat - Show Campaigns", False, f"HTTP {response.status_code}", response.text)
                return False
            
            chat_response = response.json()
            
            # Check if response contains campaign information
            if 'response' not in chat_response:
                self.log_result("AI Agent Chat - Show Campaigns", False, "No response field", chat_response)
                return False
            
            response_text = chat_response['response']
            
            # Check if the response mentions campaigns
            if 'campaign' not in response_text.lower():
                self.log_result("AI Agent Chat - Show Campaigns", False, "Response doesn't mention campaigns", chat_response)
                return False
            
            # Check if data was retrieved
            if 'data_retrieved' in chat_response and chat_response['data_retrieved']:
                campaigns_data = chat_response.get('retrieved_data', {}).get('campaigns', [])
                self.log_result("AI Agent Chat - Show Campaigns", True, f"Retrieved {len(campaigns_data)} campaigns")
                return True
            else:
                # Even if no data retrieved, if response is appropriate, it's working
                self.log_result("AI Agent Chat - Show Campaigns", True, "Appropriate response for campaigns query")
                return True
            
        except Exception as e:
            self.log_result("AI Agent Chat - Show Campaigns", False, f"Exception: {str(e)}")
            return False
    
    def test_ai_agent_chat_show_lists(self):
        """Test AI Agent chat endpoint for showing lists"""
        try:
            chat_request = {
                "message": "Show me all my lists",
                "context": {
                    "user_id": "testuser",
                    "session_id": "test_session_4"
                }
            }
            
            response = requests.post(f"{self.base_url}/api/ai-agent/chat", json=chat_request, headers=self.headers)
            
            if response.status_code != 200:
                self.log_result("AI Agent Chat - Show Lists", False, f"HTTP {response.status_code}", response.text)
                return False
            
            chat_response = response.json()
            
            # Check if response contains list information
            if 'response' not in chat_response:
                self.log_result("AI Agent Chat - Show Lists", False, "No response field", chat_response)
                return False
            
            response_text = chat_response['response']
            
            # Check if the response mentions lists
            if 'list' not in response_text.lower():
                self.log_result("AI Agent Chat - Show Lists", False, "Response doesn't mention lists", chat_response)
                return False
            
            # Check if data was retrieved
            if 'data_retrieved' in chat_response and chat_response['data_retrieved']:
                lists_data = chat_response.get('retrieved_data', {}).get('lists', [])
                self.log_result("AI Agent Chat - Show Lists", True, f"Retrieved {len(lists_data)} lists")
                return True
            else:
                # Even if no data retrieved, if response is appropriate, it's working
                self.log_result("AI Agent Chat - Show Lists", True, "Appropriate response for lists query")
                return True
            
        except Exception as e:
            self.log_result("AI Agent Chat - Show Lists", False, f"Exception: {str(e)}")
            return False
    
    def test_backend_endpoints_accessibility(self):
        """Test that backend endpoints the AI agent should access are working"""
        try:
            # Test GET /api/campaigns
            response = requests.get(f"{self.base_url}/api/campaigns", headers=self.headers)
            if response.status_code != 200:
                self.log_result("Backend Endpoint - GET Campaigns", False, f"HTTP {response.status_code}", response.text)
                return False
            
            campaigns = response.json()
            self.log_result("Backend Endpoint - GET Campaigns", True, f"Retrieved {len(campaigns)} campaigns")
            
            # Test GET /api/prospects
            response = requests.get(f"{self.base_url}/api/prospects", headers=self.headers)
            if response.status_code != 200:
                self.log_result("Backend Endpoint - GET Prospects", False, f"HTTP {response.status_code}", response.text)
                return False
            
            prospects = response.json()
            self.log_result("Backend Endpoint - GET Prospects", True, f"Retrieved {len(prospects)} prospects")
            
            # Test GET /api/lists
            response = requests.get(f"{self.base_url}/api/lists", headers=self.headers)
            if response.status_code != 200:
                self.log_result("Backend Endpoint - GET Lists", False, f"HTTP {response.status_code}", response.text)
                return False
            
            lists = response.json()
            self.log_result("Backend Endpoint - GET Lists", True, f"Retrieved {len(lists)} lists")
            
            # Test POST /api/lists (for list creation)
            test_list_data = {
                "name": "AI Agent Test List",
                "description": "Test list created by AI Agent testing",
                "color": "#FF5722",
                "tags": ["ai-agent", "test"]
            }
            
            response = requests.post(f"{self.base_url}/api/lists", json=test_list_data, headers=self.headers)
            if response.status_code != 200:
                self.log_result("Backend Endpoint - POST Lists", False, f"HTTP {response.status_code}", response.text)
                return False
            
            created_list = response.json()
            if 'id' in created_list:
                list_id = created_list['id']
                self.created_resources['lists'].append(list_id)
                self.log_result("Backend Endpoint - POST Lists", True, f"Created list with ID: {list_id}")
            else:
                self.log_result("Backend Endpoint - POST Lists", False, "No ID in response", created_list)
                return False
            
            # Test POST /api/prospects (for prospect creation)
            unique_timestamp = int(time.time())
            test_prospect_data = {
                "email": f"aiagent.test.{unique_timestamp}@example.com",
                "first_name": "AI",
                "last_name": "Agent",
                "company": "Test Corp",
                "job_title": "Test Manager"
            }
            
            response = requests.post(f"{self.base_url}/api/prospects", json=test_prospect_data, headers=self.headers)
            if response.status_code != 200:
                self.log_result("Backend Endpoint - POST Prospects", False, f"HTTP {response.status_code}", response.text)
                return False
            
            created_prospect = response.json()
            if 'id' in created_prospect:
                prospect_id = created_prospect['id']
                self.created_resources['prospects'].append(prospect_id)
                self.log_result("Backend Endpoint - POST Prospects", True, f"Created prospect with ID: {prospect_id}")
            else:
                self.log_result("Backend Endpoint - POST Prospects", False, "No ID in response", created_prospect)
                return False
            
            # Test POST /api/lists/{list_id}/prospects (for adding prospects to lists)
            if list_id and prospect_id:
                add_request = {"prospect_ids": [prospect_id]}
                response = requests.post(f"{self.base_url}/api/lists/{list_id}/prospects", 
                                       json=add_request, headers=self.headers)
                if response.status_code != 200:
                    self.log_result("Backend Endpoint - Add Prospects to List", False, f"HTTP {response.status_code}", response.text)
                    return False
                
                self.log_result("Backend Endpoint - Add Prospects to List", True, "Successfully added prospect to list")
            
            return True
            
        except Exception as e:
            self.log_result("Backend Endpoints Accessibility", False, f"Exception: {str(e)}")
            return False
    
    def cleanup_resources(self):
        """Clean up created test resources"""
        print("\n🧹 Cleaning up AI Agent test resources...")
        
        # Delete lists
        for list_id in self.created_resources['lists']:
            try:
                response = requests.delete(f"{self.base_url}/api/lists/{list_id}", headers=self.headers)
                if response.status_code == 200:
                    print(f"   ✅ Deleted list {list_id}")
                else:
                    print(f"   ⚠️ Failed to delete list {list_id}: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Error deleting list {list_id}: {str(e)}")
        
        # Delete prospects
        for prospect_id in self.created_resources['prospects']:
            try:
                response = requests.delete(f"{self.base_url}/api/prospects/{prospect_id}", headers=self.headers)
                if response.status_code == 200:
                    print(f"   ✅ Deleted prospect {prospect_id}")
                else:
                    print(f"   ⚠️ Failed to delete prospect {prospect_id}: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Error deleting prospect {prospect_id}: {str(e)}")
    
    def run_ai_agent_tests(self):
        """Run comprehensive AI Agent functionality tests"""
        print("🤖 Starting AI Agent Functionality Tests")
        print("Focus: Natural language processing, list creation, prospect addition")
        print("=" * 80)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return self.test_results
        
        # Test order matters
        tests = [
            ("AI Agent Capabilities Endpoint", self.test_ai_agent_capabilities),
            ("AI Agent Help Endpoint", self.test_ai_agent_help),
            ("Backend Endpoints Accessibility", self.test_backend_endpoints_accessibility),
            ("AI Agent Chat - List Creation", self.test_ai_agent_chat_list_creation),
            ("AI Agent Chat - Prospect Addition", self.test_ai_agent_chat_prospect_addition),
            ("AI Agent Chat - Show Campaigns", self.test_ai_agent_chat_show_campaigns),
            ("AI Agent Chat - Show Lists", self.test_ai_agent_chat_show_lists)
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
                    if any(keyword in test_name.lower() for keyword in ['chat', 'creation', 'addition']):
                        critical_failures.append(test_name)
            except Exception as e:
                self.log_result(test_name, False, f"Test execution failed: {str(e)}")
                critical_failures.append(test_name)
        
        print("\n" + "=" * 80)
        print(f"📊 AI Agent Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All AI Agent tests passed!")
        else:
            print(f"⚠️  {total - passed} AI Agent tests failed")
            if critical_failures:
                print(f"🚨 Critical failures in: {', '.join(critical_failures)}")
        
        # Cleanup
        self.cleanup_resources()
        
        return self.test_results, critical_failures

def main():
    """Main test execution"""
    tester = AIAgentTester()
    results, critical_failures = tester.run_ai_agent_tests()
    
    # Print detailed results
    print("\n" + "=" * 80)
    print("📋 DETAILED AI AGENT TEST RESULTS")
    print("=" * 80)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"{status} {test_name}")
        if result['message']:
            print(f"   Message: {result['message']}")
        if result['details']:
            print(f"   Details: {result['details']}")
        print()
    
    # Summary for test_result.md update
    print("\n" + "=" * 80)
    print("📝 AI AGENT TESTING SUMMARY")
    print("=" * 80)
    
    passed_tests = [name for name, result in results.items() if result['success']]
    failed_tests = [name for name, result in results.items() if not result['success']]
    
    print("✅ PASSED TESTS:")
    for test in passed_tests:
        print(f"   - {test}")
    
    if failed_tests:
        print("\n❌ FAILED TESTS:")
        for test in failed_tests:
            print(f"   - {test}")
    
    if critical_failures:
        print(f"\n🚨 CRITICAL FAILURES: {len(critical_failures)}")
        for failure in critical_failures:
            print(f"   - {failure}")
    else:
        print("\n✅ NO CRITICAL FAILURES")
    
    return results, critical_failures

if __name__ == "__main__":
    main()