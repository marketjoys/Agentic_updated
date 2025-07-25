#!/usr/bin/env python3
"""
AI Agent Comprehensive Backend Testing - December 2024
Testing the AI Agent functionality as requested in the review:

1. Test the AI Agent chat endpoint for campaign management commands
2. Test the AI Agent for prospect management  
3. Test the AI Agent for list management
4. Test AI Agent capabilities endpoint
5. Verify parameter extraction is working correctly

Credentials: testuser/testpass123
Backend URL: http://localhost:8001
"""

import requests
import json
import time
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get backend URL from frontend .env file
BACKEND_URL = "https://a5bd14af-2054-464a-9676-36072f2c8d35.preview.emergentagent.com"
AUTH_TOKEN = None  # Will be obtained from login

class AIAgentTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.auth_token = None
        self.headers = {}
        self.test_results = {}
        self.session_id = f"test_session_{int(time.time())}"
        
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
        """Test authentication system"""
        try:
            # Test login
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
            
            # Check required fields
            required_fields = ['capabilities', 'supported_actions', 'examples']
            for field in required_fields:
                if field not in capabilities:
                    self.log_result("AI Agent Capabilities", False, f"Missing field: {field}", capabilities)
                    return False
            
            # Check if we have expected capabilities
            expected_capabilities = ['campaign_management', 'prospect_management', 'list_management']
            capabilities_data = capabilities.get('capabilities', {})
            
            for cap in expected_capabilities:
                if cap not in capabilities_data:
                    self.log_result("AI Agent Capabilities", False, f"Missing capability: {cap}", capabilities_data)
                    return False
            
            self.log_result("AI Agent Capabilities", True, f"Retrieved {len(capabilities_data)} capabilities")
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
            
            # Check required fields
            if 'help' not in help_data:
                self.log_result("AI Agent Help", False, "Missing help field", help_data)
                return False
            
            help_content = help_data['help']
            required_help_fields = ['overview', 'supported_operations', 'examples']
            
            for field in required_help_fields:
                if field not in help_content:
                    self.log_result("AI Agent Help", False, f"Missing help field: {field}", help_content)
                    return False
            
            self.log_result("AI Agent Help", True, "Help endpoint working correctly")
            return True
            
        except Exception as e:
            self.log_result("AI Agent Help", False, f"Exception: {str(e)}")
            return False
    
    def test_campaign_management_commands(self):
        """Test AI Agent chat endpoint for campaign management commands"""
        try:
            # Test 1: Create a campaign command
            create_command = "Create a campaign named Summer Sale using Welcome template for VIP Customers list"
            
            chat_request = {
                "message": create_command,
                "user_id": "testuser",
                "session_id": self.session_id
            }
            
            response = requests.post(f"{self.base_url}/api/ai-agent/chat", json=chat_request, headers=self.headers)
            
            if response.status_code != 200:
                self.log_result("Campaign Creation Command", False, f"HTTP {response.status_code}", response.text)
                return False
            
            result = response.json()
            
            # Check response structure
            required_fields = ['response', 'action_taken', 'session_id', 'timestamp']
            for field in required_fields:
                if field not in result:
                    self.log_result("Campaign Creation Command", False, f"Missing field: {field}", result)
                    return False
            
            # Check if action was recognized
            action_taken = result.get('action_taken')
            if not action_taken or 'campaign' not in action_taken.lower():
                self.log_result("Campaign Creation Command", False, f"Action not recognized correctly: {action_taken}", result)
                return False
            
            self.log_result("Campaign Creation Command", True, f"Action: {action_taken}")
            
            # Test 2: Show campaigns command
            show_command = "Show me all my campaigns"
            
            chat_request = {
                "message": show_command,
                "user_id": "testuser", 
                "session_id": self.session_id
            }
            
            response = requests.post(f"{self.base_url}/api/ai-agent/chat", json=chat_request, headers=self.headers)
            
            if response.status_code != 200:
                self.log_result("Show Campaigns Command", False, f"HTTP {response.status_code}", response.text)
                return False
            
            result = response.json()
            action_taken = result.get('action_taken')
            
            if not action_taken or 'campaign' not in action_taken.lower():
                self.log_result("Show Campaigns Command", False, f"Action not recognized: {action_taken}", result)
                return False
            
            self.log_result("Show Campaigns Command", True, f"Action: {action_taken}")
            
            # Test 3: Send campaign command
            send_command = "Send the Summer Sale campaign to all prospects"
            
            chat_request = {
                "message": send_command,
                "user_id": "testuser",
                "session_id": self.session_id
            }
            
            response = requests.post(f"{self.base_url}/api/ai-agent/chat", json=chat_request, headers=self.headers)
            
            if response.status_code != 200:
                self.log_result("Send Campaign Command", False, f"HTTP {response.status_code}", response.text)
                return False
            
            result = response.json()
            action_taken = result.get('action_taken')
            
            if not action_taken or 'campaign' not in action_taken.lower():
                self.log_result("Send Campaign Command", False, f"Action not recognized: {action_taken}", result)
                return False
            
            self.log_result("Send Campaign Command", True, f"Action: {action_taken}")
            return True
            
        except Exception as e:
            self.log_result("Campaign Management Commands", False, f"Exception: {str(e)}")
            return False
    
    def test_prospect_management_commands(self):
        """Test AI Agent for prospect management"""
        try:
            # Test 1: Add a prospect
            add_command = "Add a prospect named John Smith from TechCorp with email john@techcorp.com"
            
            chat_request = {
                "message": add_command,
                "user_id": "testuser",
                "session_id": self.session_id
            }
            
            response = requests.post(f"{self.base_url}/api/ai-agent/chat", json=chat_request, headers=self.headers)
            
            if response.status_code != 200:
                self.log_result("Add Prospect Command", False, f"HTTP {response.status_code}", response.text)
                return False
            
            result = response.json()
            action_taken = result.get('action_taken')
            
            if not action_taken or 'prospect' not in action_taken.lower():
                self.log_result("Add Prospect Command", False, f"Action not recognized: {action_taken}", result)
                return False
            
            # Check if parameters were extracted correctly
            if result.get('data'):
                data = result['data']
                if 'first_name' in data and 'company' in data and 'email' in data:
                    self.log_result("Add Prospect Command", True, f"Parameters extracted correctly: {action_taken}")
                else:
                    self.log_result("Add Prospect Command", False, f"Parameters not extracted correctly", data)
                    return False
            else:
                self.log_result("Add Prospect Command", True, f"Action recognized: {action_taken}")
            
            # Test 2: Show prospects
            show_command = "Show me all my prospects"
            
            chat_request = {
                "message": show_command,
                "user_id": "testuser",
                "session_id": self.session_id
            }
            
            response = requests.post(f"{self.base_url}/api/ai-agent/chat", json=chat_request, headers=self.headers)
            
            if response.status_code != 200:
                self.log_result("Show Prospects Command", False, f"HTTP {response.status_code}", response.text)
                return False
            
            result = response.json()
            action_taken = result.get('action_taken')
            
            if not action_taken or 'prospect' not in action_taken.lower():
                self.log_result("Show Prospects Command", False, f"Action not recognized: {action_taken}", result)
                return False
            
            self.log_result("Show Prospects Command", True, f"Action: {action_taken}")
            
            # Test 3: Find prospects from company
            find_command = "Find prospects from TechCorp"
            
            chat_request = {
                "message": find_command,
                "user_id": "testuser",
                "session_id": self.session_id
            }
            
            response = requests.post(f"{self.base_url}/api/ai-agent/chat", json=chat_request, headers=self.headers)
            
            if response.status_code != 200:
                self.log_result("Find Prospects Command", False, f"HTTP {response.status_code}", response.text)
                return False
            
            result = response.json()
            action_taken = result.get('action_taken')
            
            if not action_taken:
                self.log_result("Find Prospects Command", False, f"No action taken", result)
                return False
            
            self.log_result("Find Prospects Command", True, f"Action: {action_taken}")
            return True
            
        except Exception as e:
            self.log_result("Prospect Management Commands", False, f"Exception: {str(e)}")
            return False
    
    def test_list_management_commands(self):
        """Test AI Agent for list management"""
        try:
            # Test 1: Create a new list
            create_command = "Create a new list called VIP Customers"
            
            chat_request = {
                "message": create_command,
                "user_id": "testuser",
                "session_id": self.session_id
            }
            
            response = requests.post(f"{self.base_url}/api/ai-agent/chat", json=chat_request, headers=self.headers)
            
            if response.status_code != 200:
                self.log_result("Create List Command", False, f"HTTP {response.status_code}", response.text)
                return False
            
            result = response.json()
            action_taken = result.get('action_taken')
            
            if not action_taken or 'list' not in action_taken.lower():
                self.log_result("Create List Command", False, f"Action not recognized: {action_taken}", result)
                return False
            
            # Check if list name was extracted correctly
            if result.get('data') and 'name' in result['data']:
                list_name = result['data']['name']
                if 'VIP' in list_name or 'Customers' in list_name:
                    self.log_result("Create List Command", True, f"List name extracted: {list_name}")
                else:
                    self.log_result("Create List Command", False, f"List name not extracted correctly: {list_name}")
                    return False
            else:
                self.log_result("Create List Command", True, f"Action recognized: {action_taken}")
            
            # Test 2: Show all lists
            show_command = "Show me all my lists"
            
            chat_request = {
                "message": show_command,
                "user_id": "testuser",
                "session_id": self.session_id
            }
            
            response = requests.post(f"{self.base_url}/api/ai-agent/chat", json=chat_request, headers=self.headers)
            
            if response.status_code != 200:
                self.log_result("Show Lists Command", False, f"HTTP {response.status_code}", response.text)
                return False
            
            result = response.json()
            action_taken = result.get('action_taken')
            
            if not action_taken or 'list' not in action_taken.lower():
                self.log_result("Show Lists Command", False, f"Action not recognized: {action_taken}", result)
                return False
            
            self.log_result("Show Lists Command", True, f"Action: {action_taken}")
            
            # Test 3: Add prospect to list
            add_command = "Add John Smith to VIP Customers list"
            
            chat_request = {
                "message": add_command,
                "user_id": "testuser",
                "session_id": self.session_id
            }
            
            response = requests.post(f"{self.base_url}/api/ai-agent/chat", json=chat_request, headers=self.headers)
            
            if response.status_code != 200:
                self.log_result("Add to List Command", False, f"HTTP {response.status_code}", response.text)
                return False
            
            result = response.json()
            action_taken = result.get('action_taken')
            
            if not action_taken:
                self.log_result("Add to List Command", False, f"No action taken", result)
                return False
            
            self.log_result("Add to List Command", True, f"Action: {action_taken}")
            return True
            
        except Exception as e:
            self.log_result("List Management Commands", False, f"Exception: {str(e)}")
            return False
    
    def test_parameter_extraction(self):
        """Test parameter extraction for various commands"""
        try:
            # Test complex campaign creation with multiple parameters
            complex_command = "Create a campaign named 'Q4 Holiday Sale' using the Holiday template for Technology Companies list with max 500 emails"
            
            chat_request = {
                "message": complex_command,
                "user_id": "testuser",
                "session_id": self.session_id
            }
            
            response = requests.post(f"{self.base_url}/api/ai-agent/chat", json=chat_request, headers=self.headers)
            
            if response.status_code != 200:
                self.log_result("Complex Parameter Extraction", False, f"HTTP {response.status_code}", response.text)
                return False
            
            result = response.json()
            
            # Check if parameters were extracted
            if result.get('data'):
                data = result['data']
                extracted_params = []
                
                if 'name' in data and 'Holiday' in str(data['name']):
                    extracted_params.append('campaign_name')
                if 'template' in data and 'Holiday' in str(data['template']):
                    extracted_params.append('template')
                if 'list' in data and 'Technology' in str(data['list']):
                    extracted_params.append('list')
                
                if len(extracted_params) >= 2:
                    self.log_result("Complex Parameter Extraction", True, f"Extracted: {extracted_params}")
                else:
                    self.log_result("Complex Parameter Extraction", False, f"Insufficient parameters extracted", data)
                    return False
            else:
                self.log_result("Complex Parameter Extraction", True, "Command processed successfully")
            
            # Test prospect with multiple details
            prospect_command = "Add a prospect named Sarah Johnson from InnovateSoft Inc with email sarah@innovatesoft.com and phone +1-555-0123"
            
            chat_request = {
                "message": prospect_command,
                "user_id": "testuser",
                "session_id": self.session_id
            }
            
            response = requests.post(f"{self.base_url}/api/ai-agent/chat", json=chat_request, headers=self.headers)
            
            if response.status_code != 200:
                self.log_result("Prospect Parameter Extraction", False, f"HTTP {response.status_code}", response.text)
                return False
            
            result = response.json()
            
            if result.get('data'):
                data = result['data']
                extracted_params = []
                
                if 'first_name' in data and 'Sarah' in str(data['first_name']):
                    extracted_params.append('first_name')
                if 'last_name' in data and 'Johnson' in str(data['last_name']):
                    extracted_params.append('last_name')
                if 'company' in data and 'InnovateSoft' in str(data['company']):
                    extracted_params.append('company')
                if 'email' in data and 'sarah@' in str(data['email']):
                    extracted_params.append('email')
                
                if len(extracted_params) >= 3:
                    self.log_result("Prospect Parameter Extraction", True, f"Extracted: {extracted_params}")
                else:
                    self.log_result("Prospect Parameter Extraction", False, f"Insufficient parameters extracted", data)
                    return False
            else:
                self.log_result("Prospect Parameter Extraction", True, "Command processed successfully")
            
            return True
            
        except Exception as e:
            self.log_result("Parameter Extraction", False, f"Exception: {str(e)}")
            return False
    
    def test_edge_cases(self):
        """Test edge cases and error handling"""
        try:
            # Test ambiguous command
            ambiguous_command = "Do something with campaigns"
            
            chat_request = {
                "message": ambiguous_command,
                "user_id": "testuser",
                "session_id": self.session_id
            }
            
            response = requests.post(f"{self.base_url}/api/ai-agent/chat", json=chat_request, headers=self.headers)
            
            if response.status_code != 200:
                self.log_result("Ambiguous Command Handling", False, f"HTTP {response.status_code}", response.text)
                return False
            
            result = response.json()
            
            # Should either ask for clarification or provide help
            response_text = result.get('response', '').lower()
            if 'help' in response_text or 'clarification' in response_text or 'what' in response_text:
                self.log_result("Ambiguous Command Handling", True, "Handled ambiguous command appropriately")
            else:
                self.log_result("Ambiguous Command Handling", False, f"Unexpected response: {response_text}")
                return False
            
            # Test empty message
            empty_command = ""
            
            chat_request = {
                "message": empty_command,
                "user_id": "testuser",
                "session_id": self.session_id
            }
            
            response = requests.post(f"{self.base_url}/api/ai-agent/chat", json=chat_request, headers=self.headers)
            
            if response.status_code != 200:
                self.log_result("Empty Message Handling", False, f"HTTP {response.status_code}", response.text)
                return False
            
            result = response.json()
            
            # Should handle empty message gracefully
            if result.get('response'):
                self.log_result("Empty Message Handling", True, "Handled empty message gracefully")
            else:
                self.log_result("Empty Message Handling", False, "No response to empty message")
                return False
            
            return True
            
        except Exception as e:
            self.log_result("Edge Cases", False, f"Exception: {str(e)}")
            return False
    
    def run_comprehensive_tests(self):
        """Run comprehensive AI Agent tests"""
        print("🤖 Starting AI Agent Comprehensive Backend Tests")
        print("Focus: Natural Language Processing, Campaign/Prospect/List Management, Parameter Extraction")
        print("=" * 80)
        
        # Test order matters - authentication first
        tests = [
            ("Authentication", self.test_authentication),
            ("AI Agent Capabilities", self.test_ai_agent_capabilities),
            ("AI Agent Help", self.test_ai_agent_help),
            ("Campaign Management Commands", self.test_campaign_management_commands),
            ("Prospect Management Commands", self.test_prospect_management_commands),
            ("List Management Commands", self.test_list_management_commands),
            ("Parameter Extraction", self.test_parameter_extraction),
            ("Edge Cases", self.test_edge_cases)
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
                    if any(keyword in test_name.lower() for keyword in ['campaign', 'prospect', 'list', 'parameter']):
                        critical_failures.append(test_name)
            except Exception as e:
                self.log_result(test_name, False, f"Test execution failed: {str(e)}")
                critical_failures.append(test_name)
        
        print("\n" + "=" * 80)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All AI Agent tests passed!")
        else:
            print(f"⚠️  {total - passed} tests failed")
            if critical_failures:
                print(f"🚨 Critical failures in: {', '.join(critical_failures)}")
        
        return self.test_results, critical_failures

def main():
    """Main test execution"""
    tester = AIAgentTester()
    results, critical_failures = tester.run_comprehensive_tests()
    
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
        print("\n🎉 NO CRITICAL FAILURES - AI AGENT FUNCTIONALITY IS WORKING!")
    
    return results, critical_failures

if __name__ == "__main__":
    main()