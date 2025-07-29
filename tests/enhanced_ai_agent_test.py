#!/usr/bin/env python3
"""
Enhanced AI Agent Functionality Testing - December 2024
Testing the ENHANCED AI Agent functionality with improvements made to:

1. List Creation Commands:
   - "Create a new list called Test Marketing List"
   - "Make a new list named VIP Customers"
   - "Add a list called Technology Companies"

2. Prospect Creation Commands:
   - "Add a prospect named John Smith from TechCorp"
   - "Create a new prospect called Sarah Johnson from InnovateSoft"
   - "Add prospect Mike Davis at DataScience AI"

3. Show Commands:
   - "Show me all my campaigns"
   - "Show me all my lists"
   - "Show me all my prospects"

Focus: Verify the AI Agent can now:
- Parse natural language correctly
- Extract parameters (names, companies) from commands
- Execute the intended actions via action router
- Return successful responses with actual data
"""

import requests
import json
import time
from datetime import datetime

# Get backend URL from frontend .env file
BACKEND_URL = "https://5f33b0de-2474-4f94-a9e0-dac40fa9173f.preview.emergentagent.com"

class EnhancedAIAgentTester:
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
            self.log_result("Authentication", True, "Login successful with testuser/testpass123")
            return True
            
        except Exception as e:
            self.log_result("Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_list_creation_command_1(self):
        """Test: 'Create a new list called Test Marketing List'"""
        try:
            chat_request = {
                "message": "Create a new list called Test Marketing List",
                "context": {
                    "user_id": "testuser",
                    "session_id": "test_session_list_1"
                }
            }
            
            response = requests.post(f"{self.base_url}/api/ai-agent/chat", json=chat_request, headers=self.headers)
            
            if response.status_code != 200:
                self.log_result("List Creation Command 1", False, f"HTTP {response.status_code}", response.text)
                return False
            
            chat_response = response.json()
            
            # Check if response indicates successful action
            if 'response' not in chat_response:
                self.log_result("List Creation Command 1", False, "No response field", chat_response)
                return False
            
            response_text = chat_response['response']
            
            # Check if the response indicates success (not a help message)
            if any(word in response_text.lower() for word in ['help', 'assist', 'can help', 'what can']):
                self.log_result("List Creation Command 1", False, "AI Agent returned help message instead of creating list", chat_response)
                return False
            
            # Check if action was taken
            action_taken = chat_response.get('action_taken')
            if not action_taken or action_taken == 'help':
                self.log_result("List Creation Command 1", False, f"No proper action taken: {action_taken}", chat_response)
                return False
            
            # Check if data was returned (indicating successful creation)
            if 'data' in chat_response and chat_response['data']:
                data = chat_response['data']
                if 'id' in data:
                    list_id = data['id']
                    self.created_resources['lists'].append(list_id)
                    
                    # Verify the list name was extracted correctly
                    if 'Test Marketing List' in data.get('name', ''):
                        self.log_result("List Creation Command 1", True, f"Successfully created list: {data['name']}")
                        return True
                    else:
                        self.log_result("List Creation Command 1", False, f"List name not extracted correctly: {data.get('name')}")
                        return False
                else:
                    self.log_result("List Creation Command 1", False, "No ID in created list data", data)
                    return False
            else:
                self.log_result("List Creation Command 1", False, "No data returned from list creation", chat_response)
                return False
            
        except Exception as e:
            self.log_result("List Creation Command 1", False, f"Exception: {str(e)}")
            return False
    
    def test_list_creation_command_2(self):
        """Test: 'Make a new list named VIP Customers'"""
        try:
            chat_request = {
                "message": "Make a new list named VIP Customers",
                "context": {
                    "user_id": "testuser",
                    "session_id": "test_session_list_2"
                }
            }
            
            response = requests.post(f"{self.base_url}/api/ai-agent/chat", json=chat_request, headers=self.headers)
            
            if response.status_code != 200:
                self.log_result("List Creation Command 2", False, f"HTTP {response.status_code}", response.text)
                return False
            
            chat_response = response.json()
            response_text = chat_response.get('response', '')
            
            # Check if the response indicates success (not a help message)
            if any(word in response_text.lower() for word in ['help', 'assist', 'can help', 'what can']):
                self.log_result("List Creation Command 2", False, "AI Agent returned help message instead of creating list", chat_response)
                return False
            
            # Check if action was taken
            action_taken = chat_response.get('action_taken')
            if not action_taken or action_taken == 'help':
                self.log_result("List Creation Command 2", False, f"No proper action taken: {action_taken}", chat_response)
                return False
            
            # Check if data was returned
            if 'data' in chat_response and chat_response['data']:
                data = chat_response['data']
                if 'id' in data:
                    list_id = data['id']
                    self.created_resources['lists'].append(list_id)
                    
                    # Verify the list name was extracted correctly
                    if 'VIP Customers' in data.get('name', ''):
                        self.log_result("List Creation Command 2", True, f"Successfully created list: {data['name']}")
                        return True
                    else:
                        self.log_result("List Creation Command 2", False, f"List name not extracted correctly: {data.get('name')}")
                        return False
                else:
                    self.log_result("List Creation Command 2", False, "No ID in created list data", data)
                    return False
            else:
                self.log_result("List Creation Command 2", False, "No data returned from list creation", chat_response)
                return False
            
        except Exception as e:
            self.log_result("List Creation Command 2", False, f"Exception: {str(e)}")
            return False
    
    def test_list_creation_command_3(self):
        """Test: 'Add a list called Technology Companies'"""
        try:
            chat_request = {
                "message": "Add a list called Technology Companies",
                "context": {
                    "user_id": "testuser",
                    "session_id": "test_session_list_3"
                }
            }
            
            response = requests.post(f"{self.base_url}/api/ai-agent/chat", json=chat_request, headers=self.headers)
            
            if response.status_code != 200:
                self.log_result("List Creation Command 3", False, f"HTTP {response.status_code}", response.text)
                return False
            
            chat_response = response.json()
            response_text = chat_response.get('response', '')
            
            # Check if the response indicates success (not a help message)
            if any(word in response_text.lower() for word in ['help', 'assist', 'can help', 'what can']):
                self.log_result("List Creation Command 3", False, "AI Agent returned help message instead of creating list", chat_response)
                return False
            
            # Check if action was taken
            action_taken = chat_response.get('action_taken')
            if not action_taken or action_taken == 'help':
                self.log_result("List Creation Command 3", False, f"No proper action taken: {action_taken}", chat_response)
                return False
            
            # Check if data was returned
            if 'data' in chat_response and chat_response['data']:
                data = chat_response['data']
                if 'id' in data:
                    list_id = data['id']
                    self.created_resources['lists'].append(list_id)
                    
                    # Verify the list name was extracted correctly
                    if 'Technology Companies' in data.get('name', ''):
                        self.log_result("List Creation Command 3", True, f"Successfully created list: {data['name']}")
                        return True
                    else:
                        self.log_result("List Creation Command 3", False, f"List name not extracted correctly: {data.get('name')}")
                        return False
                else:
                    self.log_result("List Creation Command 3", False, "No ID in created list data", data)
                    return False
            else:
                self.log_result("List Creation Command 3", False, "No data returned from list creation", chat_response)
                return False
            
        except Exception as e:
            self.log_result("List Creation Command 3", False, f"Exception: {str(e)}")
            return False
    
    def test_prospect_creation_command_1(self):
        """Test: 'Add a prospect named John Smith from TechCorp'"""
        try:
            chat_request = {
                "message": "Add a prospect named John Smith from TechCorp",
                "context": {
                    "user_id": "testuser",
                    "session_id": "test_session_prospect_1"
                }
            }
            
            response = requests.post(f"{self.base_url}/api/ai-agent/chat", json=chat_request, headers=self.headers)
            
            if response.status_code != 200:
                self.log_result("Prospect Creation Command 1", False, f"HTTP {response.status_code}", response.text)
                return False
            
            chat_response = response.json()
            response_text = chat_response.get('response', '')
            
            # Check if the response indicates success (not a help message)
            if any(word in response_text.lower() for word in ['help', 'assist', 'can help', 'what can']):
                self.log_result("Prospect Creation Command 1", False, "AI Agent returned help message instead of creating prospect", chat_response)
                return False
            
            # Check if action was taken
            action_taken = chat_response.get('action_taken')
            if not action_taken or action_taken == 'help':
                self.log_result("Prospect Creation Command 1", False, f"No proper action taken: {action_taken}", chat_response)
                return False
            
            # Check if data was returned
            if 'data' in chat_response and chat_response['data']:
                data = chat_response['data']
                if 'id' in data:
                    prospect_id = data['id']
                    self.created_resources['prospects'].append(prospect_id)
                    
                    # Verify the prospect details were extracted correctly
                    first_name = data.get('first_name', '')
                    last_name = data.get('last_name', '')
                    company = data.get('company', '')
                    
                    if 'John' in first_name and 'Smith' in last_name and 'TechCorp' in company:
                        self.log_result("Prospect Creation Command 1", True, f"Successfully created prospect: {first_name} {last_name} from {company}")
                        return True
                    else:
                        self.log_result("Prospect Creation Command 1", False, f"Prospect details not extracted correctly: {first_name} {last_name} from {company}")
                        return False
                else:
                    self.log_result("Prospect Creation Command 1", False, "No ID in created prospect data", data)
                    return False
            else:
                self.log_result("Prospect Creation Command 1", False, "No data returned from prospect creation", chat_response)
                return False
            
        except Exception as e:
            self.log_result("Prospect Creation Command 1", False, f"Exception: {str(e)}")
            return False
    
    def test_prospect_creation_command_2(self):
        """Test: 'Create a new prospect called Sarah Johnson from InnovateSoft'"""
        try:
            chat_request = {
                "message": "Create a new prospect called Sarah Johnson from InnovateSoft",
                "context": {
                    "user_id": "testuser",
                    "session_id": "test_session_prospect_2"
                }
            }
            
            response = requests.post(f"{self.base_url}/api/ai-agent/chat", json=chat_request, headers=self.headers)
            
            if response.status_code != 200:
                self.log_result("Prospect Creation Command 2", False, f"HTTP {response.status_code}", response.text)
                return False
            
            chat_response = response.json()
            response_text = chat_response.get('response', '')
            
            # Check if the response indicates success (not a help message)
            if any(word in response_text.lower() for word in ['help', 'assist', 'can help', 'what can']):
                self.log_result("Prospect Creation Command 2", False, "AI Agent returned help message instead of creating prospect", chat_response)
                return False
            
            # Check if action was taken
            action_taken = chat_response.get('action_taken')
            if not action_taken or action_taken == 'help':
                self.log_result("Prospect Creation Command 2", False, f"No proper action taken: {action_taken}", chat_response)
                return False
            
            # Check if data was returned
            if 'data' in chat_response and chat_response['data']:
                data = chat_response['data']
                if 'id' in data:
                    prospect_id = data['id']
                    self.created_resources['prospects'].append(prospect_id)
                    
                    # Verify the prospect details were extracted correctly
                    first_name = data.get('first_name', '')
                    last_name = data.get('last_name', '')
                    company = data.get('company', '')
                    
                    if 'Sarah' in first_name and 'Johnson' in last_name and 'InnovateSoft' in company:
                        self.log_result("Prospect Creation Command 2", True, f"Successfully created prospect: {first_name} {last_name} from {company}")
                        return True
                    else:
                        self.log_result("Prospect Creation Command 2", False, f"Prospect details not extracted correctly: {first_name} {last_name} from {company}")
                        return False
                else:
                    self.log_result("Prospect Creation Command 2", False, "No ID in created prospect data", data)
                    return False
            else:
                self.log_result("Prospect Creation Command 2", False, "No data returned from prospect creation", chat_response)
                return False
            
        except Exception as e:
            self.log_result("Prospect Creation Command 2", False, f"Exception: {str(e)}")
            return False
    
    def test_prospect_creation_command_3(self):
        """Test: 'Add prospect Mike Davis at DataScience AI'"""
        try:
            chat_request = {
                "message": "Add prospect Mike Davis at DataScience AI",
                "context": {
                    "user_id": "testuser",
                    "session_id": "test_session_prospect_3"
                }
            }
            
            response = requests.post(f"{self.base_url}/api/ai-agent/chat", json=chat_request, headers=self.headers)
            
            if response.status_code != 200:
                self.log_result("Prospect Creation Command 3", False, f"HTTP {response.status_code}", response.text)
                return False
            
            chat_response = response.json()
            response_text = chat_response.get('response', '')
            
            # Check if the response indicates success (not a help message)
            if any(word in response_text.lower() for word in ['help', 'assist', 'can help', 'what can']):
                self.log_result("Prospect Creation Command 3", False, "AI Agent returned help message instead of creating prospect", chat_response)
                return False
            
            # Check if action was taken
            action_taken = chat_response.get('action_taken')
            if not action_taken or action_taken == 'help':
                self.log_result("Prospect Creation Command 3", False, f"No proper action taken: {action_taken}", chat_response)
                return False
            
            # Check if data was returned
            if 'data' in chat_response and chat_response['data']:
                data = chat_response['data']
                if 'id' in data:
                    prospect_id = data['id']
                    self.created_resources['prospects'].append(prospect_id)
                    
                    # Verify the prospect details were extracted correctly
                    first_name = data.get('first_name', '')
                    last_name = data.get('last_name', '')
                    company = data.get('company', '')
                    
                    if 'Mike' in first_name and 'Davis' in last_name and 'DataScience AI' in company:
                        self.log_result("Prospect Creation Command 3", True, f"Successfully created prospect: {first_name} {last_name} from {company}")
                        return True
                    else:
                        self.log_result("Prospect Creation Command 3", False, f"Prospect details not extracted correctly: {first_name} {last_name} from {company}")
                        return False
                else:
                    self.log_result("Prospect Creation Command 3", False, "No ID in created prospect data", data)
                    return False
            else:
                self.log_result("Prospect Creation Command 3", False, "No data returned from prospect creation", chat_response)
                return False
            
        except Exception as e:
            self.log_result("Prospect Creation Command 3", False, f"Exception: {str(e)}")
            return False
    
    def test_show_campaigns_command(self):
        """Test: 'Show me all my campaigns'"""
        try:
            chat_request = {
                "message": "Show me all my campaigns",
                "context": {
                    "user_id": "testuser",
                    "session_id": "test_session_show_campaigns"
                }
            }
            
            response = requests.post(f"{self.base_url}/api/ai-agent/chat", json=chat_request, headers=self.headers)
            
            if response.status_code != 200:
                self.log_result("Show Campaigns Command", False, f"HTTP {response.status_code}", response.text)
                return False
            
            chat_response = response.json()
            response_text = chat_response.get('response', '')
            
            # Check if the response indicates success (not a help message)
            if any(word in response_text.lower() for word in ['help', 'assist', 'can help', 'what can']):
                self.log_result("Show Campaigns Command", False, "AI Agent returned help message instead of showing campaigns", chat_response)
                return False
            
            # Check if action was taken
            action_taken = chat_response.get('action_taken')
            if not action_taken or action_taken == 'help':
                self.log_result("Show Campaigns Command", False, f"No proper action taken: {action_taken}", chat_response)
                return False
            
            # Check if the response mentions campaigns
            if 'campaign' not in response_text.lower():
                self.log_result("Show Campaigns Command", False, "Response doesn't mention campaigns", chat_response)
                return False
            
            # Check if data was retrieved (even if empty, it should be present)
            if 'data' in chat_response:
                campaigns_data = chat_response['data']
                if isinstance(campaigns_data, list):
                    self.log_result("Show Campaigns Command", True, f"Successfully retrieved {len(campaigns_data)} campaigns")
                    return True
                else:
                    self.log_result("Show Campaigns Command", True, "Successfully processed campaigns query")
                    return True
            else:
                # Even if no data field, if response is appropriate, it's working
                if any(word in response_text.lower() for word in ['campaign', 'don\'t have', 'no campaigns', 'create']):
                    self.log_result("Show Campaigns Command", True, "Appropriate response for campaigns query")
                    return True
                else:
                    self.log_result("Show Campaigns Command", False, "No appropriate campaigns response", chat_response)
                    return False
            
        except Exception as e:
            self.log_result("Show Campaigns Command", False, f"Exception: {str(e)}")
            return False
    
    def test_show_lists_command(self):
        """Test: 'Show me all my lists'"""
        try:
            chat_request = {
                "message": "Show me all my lists",
                "context": {
                    "user_id": "testuser",
                    "session_id": "test_session_show_lists"
                }
            }
            
            response = requests.post(f"{self.base_url}/api/ai-agent/chat", json=chat_request, headers=self.headers)
            
            if response.status_code != 200:
                self.log_result("Show Lists Command", False, f"HTTP {response.status_code}", response.text)
                return False
            
            chat_response = response.json()
            response_text = chat_response.get('response', '')
            
            # Check if the response indicates success (not a help message)
            if any(word in response_text.lower() for word in ['help', 'assist', 'can help', 'what can']):
                self.log_result("Show Lists Command", False, "AI Agent returned help message instead of showing lists", chat_response)
                return False
            
            # Check if action was taken
            action_taken = chat_response.get('action_taken')
            if not action_taken or action_taken == 'help':
                self.log_result("Show Lists Command", False, f"No proper action taken: {action_taken}", chat_response)
                return False
            
            # Check if the response mentions lists
            if 'list' not in response_text.lower():
                self.log_result("Show Lists Command", False, "Response doesn't mention lists", chat_response)
                return False
            
            # Check if data was retrieved (even if empty, it should be present)
            if 'data' in chat_response:
                lists_data = chat_response['data']
                if isinstance(lists_data, list):
                    self.log_result("Show Lists Command", True, f"Successfully retrieved {len(lists_data)} lists")
                    return True
                else:
                    self.log_result("Show Lists Command", True, "Successfully processed lists query")
                    return True
            else:
                # Even if no data field, if response is appropriate, it's working
                if any(word in response_text.lower() for word in ['list', 'don\'t have', 'no lists', 'create']):
                    self.log_result("Show Lists Command", True, "Appropriate response for lists query")
                    return True
                else:
                    self.log_result("Show Lists Command", False, "No appropriate lists response", chat_response)
                    return False
            
        except Exception as e:
            self.log_result("Show Lists Command", False, f"Exception: {str(e)}")
            return False
    
    def test_show_prospects_command(self):
        """Test: 'Show me all my prospects'"""
        try:
            chat_request = {
                "message": "Show me all my prospects",
                "context": {
                    "user_id": "testuser",
                    "session_id": "test_session_show_prospects"
                }
            }
            
            response = requests.post(f"{self.base_url}/api/ai-agent/chat", json=chat_request, headers=self.headers)
            
            if response.status_code != 200:
                self.log_result("Show Prospects Command", False, f"HTTP {response.status_code}", response.text)
                return False
            
            chat_response = response.json()
            response_text = chat_response.get('response', '')
            
            # Check if the response indicates success (not a help message)
            if any(word in response_text.lower() for word in ['help', 'assist', 'can help', 'what can']):
                self.log_result("Show Prospects Command", False, "AI Agent returned help message instead of showing prospects", chat_response)
                return False
            
            # Check if action was taken
            action_taken = chat_response.get('action_taken')
            if not action_taken or action_taken == 'help':
                self.log_result("Show Prospects Command", False, f"No proper action taken: {action_taken}", chat_response)
                return False
            
            # Check if the response mentions prospects
            if not any(word in response_text.lower() for word in ['prospect', 'contact', 'lead']):
                self.log_result("Show Prospects Command", False, "Response doesn't mention prospects", chat_response)
                return False
            
            # Check if data was retrieved (even if empty, it should be present)
            if 'data' in chat_response:
                prospects_data = chat_response['data']
                if isinstance(prospects_data, list):
                    self.log_result("Show Prospects Command", True, f"Successfully retrieved {len(prospects_data)} prospects")
                    return True
                else:
                    self.log_result("Show Prospects Command", True, "Successfully processed prospects query")
                    return True
            else:
                # Even if no data field, if response is appropriate, it's working
                if any(word in response_text.lower() for word in ['prospect', 'contact', 'don\'t have', 'no prospects', 'create']):
                    self.log_result("Show Prospects Command", True, "Appropriate response for prospects query")
                    return True
                else:
                    self.log_result("Show Prospects Command", False, "No appropriate prospects response", chat_response)
                    return False
            
        except Exception as e:
            self.log_result("Show Prospects Command", False, f"Exception: {str(e)}")
            return False
    
    def cleanup_resources(self):
        """Clean up created test resources"""
        print("\n🧹 Cleaning up Enhanced AI Agent test resources...")
        
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
    
    def run_enhanced_ai_agent_tests(self):
        """Run comprehensive Enhanced AI Agent functionality tests"""
        print("🤖 Starting Enhanced AI Agent Functionality Tests")
        print("Focus: Testing improved natural language processing and parameter extraction")
        print("=" * 80)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return self.test_results
        
        # Test order matters - test creation commands first, then show commands
        tests = [
            ("List Creation Command 1", self.test_list_creation_command_1),
            ("List Creation Command 2", self.test_list_creation_command_2),
            ("List Creation Command 3", self.test_list_creation_command_3),
            ("Prospect Creation Command 1", self.test_prospect_creation_command_1),
            ("Prospect Creation Command 2", self.test_prospect_creation_command_2),
            ("Prospect Creation Command 3", self.test_prospect_creation_command_3),
            ("Show Campaigns Command", self.test_show_campaigns_command),
            ("Show Lists Command", self.test_show_lists_command),
            ("Show Prospects Command", self.test_show_prospects_command)
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
                    # All tests are critical for this enhanced functionality
                    critical_failures.append(test_name)
            except Exception as e:
                self.log_result(test_name, False, f"Test execution failed: {str(e)}")
                critical_failures.append(test_name)
        
        print("\n" + "=" * 80)
        print(f"📊 Enhanced AI Agent Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All Enhanced AI Agent tests passed!")
        else:
            print(f"⚠️  {total - passed} Enhanced AI Agent tests failed")
            if critical_failures:
                print(f"🚨 Critical failures in: {', '.join(critical_failures)}")
        
        # Cleanup
        self.cleanup_resources()
        
        return self.test_results, critical_failures

def main():
    """Main test execution"""
    tester = EnhancedAIAgentTester()
    results, critical_failures = tester.run_enhanced_ai_agent_tests()
    
    # Print detailed results
    print("\n" + "=" * 80)
    print("📋 DETAILED ENHANCED AI AGENT TEST RESULTS")
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
    print("📝 ENHANCED AI AGENT TESTING SUMMARY")
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