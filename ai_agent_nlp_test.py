#!/usr/bin/env python3
"""
AI Agent Natural Language Processing Testing - December 2024
Comprehensive testing of AI Agent functionality per review request:

1. List Creation Commands
2. Prospect Creation Commands  
3. Show/Display Commands
4. AI Agent Infrastructure endpoints
5. Parameter Extraction Testing
6. Action Router Testing

Focus on natural language processing improvements and regex pattern fixes.
"""

import requests
import json
import time
from datetime import datetime

# Get backend URL from frontend .env file
BACKEND_URL = "https://12bc1cb8-a382-4b5c-b19c-7f947822cd9a.preview.emergentagent.com"

class AIAgentNLPTester:
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
    
    def test_ai_agent_infrastructure(self):
        """Test AI Agent Infrastructure endpoints"""
        try:
            # Test /api/ai-agent/capabilities
            response = requests.get(f"{self.base_url}/api/ai-agent/capabilities", headers=self.headers)
            if response.status_code != 200:
                self.log_result("AI Agent Capabilities", False, f"HTTP {response.status_code}", response.text)
                return False
            
            capabilities = response.json()
            self.log_result("AI Agent Capabilities", True, f"Retrieved capabilities with {len(capabilities.get('capabilities', {}))} categories")
            
            # Test /api/ai-agent/help
            response = requests.get(f"{self.base_url}/api/ai-agent/help", headers=self.headers)
            if response.status_code != 200:
                self.log_result("AI Agent Help", False, f"HTTP {response.status_code}", response.text)
                return False
            
            help_data = response.json()
            self.log_result("AI Agent Help", True, f"Retrieved help data with {len(help_data.get('help', {}).get('examples', []))} examples")
            
            # Test /api/ai-agent/chat endpoint exists
            test_chat = {
                "message": "Hello",
                "context": {"user_id": "testuser", "session_id": "test_session"}
            }
            response = requests.post(f"{self.base_url}/api/ai-agent/chat", json=test_chat, headers=self.headers)
            if response.status_code != 200:
                self.log_result("AI Agent Chat Endpoint", False, f"HTTP {response.status_code}", response.text)
                return False
            
            self.log_result("AI Agent Chat Endpoint", True, "Chat endpoint accessible")
            return True
            
        except Exception as e:
            self.log_result("AI Agent Infrastructure", False, f"Exception: {str(e)}")
            return False
    
    def test_list_creation_commands(self):
        """Test List Creation Commands with multi-word names"""
        test_commands = [
            "Create a new list called Test Marketing List",
            "Create a list named VIP Customers for premium clients", 
            "Make a new list called Technology Companies"
        ]
        
        results = []
        for i, command in enumerate(test_commands):
            try:
                chat_request = {
                    "message": command,
                    "context": {
                        "user_id": "testuser",
                        "session_id": f"list_test_session_{i}"
                    }
                }
                
                response = requests.post(f"{self.base_url}/api/ai-agent/chat", json=chat_request, headers=self.headers)
                
                if response.status_code != 200:
                    results.append(f"Command '{command}' failed with HTTP {response.status_code}")
                    continue
                
                chat_response = response.json()
                
                # Check if action was taken
                action_taken = chat_response.get('action_taken')
                if action_taken != 'create_list':
                    results.append(f"Command '{command}' - Wrong action: {action_taken}")
                    continue
                
                # Check if list was created with correct name
                data = chat_response.get('data')
                if not data or 'id' not in data:
                    results.append(f"Command '{command}' - No list created")
                    continue
                
                created_name = data.get('name', '')
                expected_names = ["Test Marketing List", "VIP Customers", "Technology Companies"]
                expected_name = expected_names[i]
                
                # Check if full multi-word name was extracted correctly
                if expected_name not in created_name:
                    results.append(f"Command '{command}' - Name extraction failed. Expected: '{expected_name}', Got: '{created_name}'")
                    continue
                
                # Track created resource for cleanup
                self.created_resources['lists'].append(data['id'])
                results.append(f"✅ Command '{command}' - Successfully created list: '{created_name}'")
                
            except Exception as e:
                results.append(f"Command '{command}' - Exception: {str(e)}")
        
        # Evaluate results
        success_count = len([r for r in results if r.startswith('✅')])
        total_count = len(test_commands)
        
        if success_count == total_count:
            self.log_result("List Creation Commands", True, f"All {total_count} commands successful", results)
            return True
        else:
            self.log_result("List Creation Commands", False, f"{success_count}/{total_count} commands successful", results)
            return False
    
    def test_prospect_creation_commands(self):
        """Test Prospect Creation Commands with name and company extraction"""
        test_commands = [
            "Add a prospect named John Smith from TechCorp",
            "Create a prospect Mike Davis at DataScience AI",
            "Add Sarah Johnson from InnovateSoft"
        ]
        
        results = []
        for i, command in enumerate(test_commands):
            try:
                # Add unique timestamp to avoid duplicate email issues
                unique_id = int(time.time()) + i
                modified_command = command.replace("John Smith", f"John Smith{unique_id}").replace("Mike Davis", f"Mike Davis{unique_id}").replace("Sarah Johnson", f"Sarah Johnson{unique_id}")
                
                chat_request = {
                    "message": modified_command,
                    "context": {
                        "user_id": "testuser",
                        "session_id": f"prospect_test_session_{i}"
                    }
                }
                
                response = requests.post(f"{self.base_url}/api/ai-agent/chat", json=chat_request, headers=self.headers)
                
                if response.status_code != 200:
                    results.append(f"Command '{command}' failed with HTTP {response.status_code}")
                    continue
                
                chat_response = response.json()
                
                # Check if action was taken
                action_taken = chat_response.get('action_taken')
                if action_taken != 'create_prospect':
                    results.append(f"Command '{command}' - Wrong action: {action_taken}")
                    continue
                
                # Check if prospect was created
                data = chat_response.get('data')
                if not data or 'id' not in data:
                    # Check if it failed due to existing email (acceptable)
                    response_text = chat_response.get('response', '')
                    if 'already exists' in response_text:
                        results.append(f"⚠️ Command '{command}' - Prospect already exists (acceptable)")
                        continue
                    else:
                        results.append(f"Command '{command}' - No prospect created")
                        continue
                
                # Verify name extraction
                first_name = data.get('first_name', '')
                last_name = data.get('last_name', '')
                company = data.get('company', '')
                
                expected_data = [
                    {"first": "John", "last": f"Smith{unique_id}", "company": "TechCorp"},
                    {"first": "Mike", "last": f"Davis{unique_id}", "company": "DataScience AI"},
                    {"first": "Sarah", "last": f"Johnson{unique_id}", "company": "InnovateSoft"}
                ]
                
                expected = expected_data[i]
                
                # Check name extraction
                name_correct = (expected["first"] in first_name and expected["last"] in last_name)
                company_correct = expected["company"] in company
                
                if not name_correct:
                    results.append(f"Command '{command}' - Name extraction failed. Expected: '{expected['first']} {expected['last']}', Got: '{first_name} {last_name}'")
                    continue
                
                if not company_correct:
                    results.append(f"Command '{command}' - Company extraction failed. Expected: '{expected['company']}', Got: '{company}'")
                    continue
                
                # Track created resource for cleanup
                self.created_resources['prospects'].append(data['id'])
                results.append(f"✅ Command '{command}' - Successfully created prospect: '{first_name} {last_name}' from '{company}'")
                
            except Exception as e:
                results.append(f"Command '{command}' - Exception: {str(e)}")
        
        # Evaluate results
        success_count = len([r for r in results if r.startswith('✅')])
        warning_count = len([r for r in results if r.startswith('⚠️')])
        total_count = len(test_commands)
        
        if success_count + warning_count == total_count:
            self.log_result("Prospect Creation Commands", True, f"{success_count} successful, {warning_count} warnings", results)
            return True
        else:
            self.log_result("Prospect Creation Commands", False, f"{success_count}/{total_count} commands successful", results)
            return False
    
    def test_show_display_commands(self):
        """Test Show/Display Commands"""
        test_commands = [
            ("Show me all my lists", "list_lists"),
            ("Show me all my prospects", "list_prospects"), 
            ("Show me all my campaigns", "list_campaigns")
        ]
        
        results = []
        for i, (command, expected_action) in enumerate(test_commands):
            try:
                chat_request = {
                    "message": command,
                    "context": {
                        "user_id": "testuser",
                        "session_id": f"show_test_session_{i}"
                    }
                }
                
                response = requests.post(f"{self.base_url}/api/ai-agent/chat", json=chat_request, headers=self.headers)
                
                if response.status_code != 200:
                    results.append(f"Command '{command}' failed with HTTP {response.status_code}")
                    continue
                
                chat_response = response.json()
                
                # Check if correct action was taken
                action_taken = chat_response.get('action_taken')
                if action_taken != expected_action:
                    results.append(f"Command '{command}' - Wrong action: {action_taken}, expected: {expected_action}")
                    continue
                
                # Check if response contains relevant information
                response_text = chat_response.get('response', '').lower()
                entity_name = expected_action.split('_')[1]  # Extract 'lists', 'prospects', 'campaigns'
                
                if entity_name not in response_text:
                    results.append(f"Command '{command}' - Response doesn't mention {entity_name}")
                    continue
                
                results.append(f"✅ Command '{command}' - Correctly identified action and provided response")
                
            except Exception as e:
                results.append(f"Command '{command}' - Exception: {str(e)}")
        
        # Evaluate results
        success_count = len([r for r in results if r.startswith('✅')])
        total_count = len(test_commands)
        
        if success_count == total_count:
            self.log_result("Show/Display Commands", True, f"All {total_count} commands successful", results)
            return True
        else:
            self.log_result("Show/Display Commands", False, f"{success_count}/{total_count} commands successful", results)
            return False
    
    def test_parameter_extraction(self):
        """Test Parameter Extraction for multi-word names and complex patterns"""
        test_cases = [
            {
                "command": "Create a list called Advanced Marketing Automation List",
                "expected_name": "Advanced Marketing Automation List",
                "test_type": "Multi-word list name"
            },
            {
                "command": "Add prospect Michael O'Connor from Global Tech Solutions Inc",
                "expected_first": "Michael",
                "expected_last": "O'Connor", 
                "expected_company": "Global Tech Solutions Inc",
                "test_type": "Complex name and company"
            },
            {
                "command": "Create a new list named VIP Premium Customers for high-value clients",
                "expected_name": "VIP Premium Customers",
                "test_type": "Multi-word with description"
            }
        ]
        
        results = []
        for i, test_case in enumerate(test_cases):
            try:
                unique_id = int(time.time()) + i
                command = test_case["command"]
                
                # Modify prospect commands to avoid duplicates
                if "prospect" in command.lower():
                    command = command.replace("Michael O'Connor", f"Michael O'Connor{unique_id}")
                
                chat_request = {
                    "message": command,
                    "context": {
                        "user_id": "testuser",
                        "session_id": f"param_test_session_{i}"
                    }
                }
                
                response = requests.post(f"{self.base_url}/api/ai-agent/chat", json=chat_request, headers=self.headers)
                
                if response.status_code != 200:
                    results.append(f"{test_case['test_type']} - HTTP {response.status_code}")
                    continue
                
                chat_response = response.json()
                data = chat_response.get('data')
                
                if not data:
                    results.append(f"{test_case['test_type']} - No data returned")
                    continue
                
                # Test list name extraction
                if "expected_name" in test_case:
                    actual_name = data.get('name', '')
                    expected_name = test_case["expected_name"]
                    
                    if expected_name in actual_name:
                        results.append(f"✅ {test_case['test_type']} - Correct name extraction: '{actual_name}'")
                        if 'id' in data:
                            self.created_resources['lists'].append(data['id'])
                    else:
                        results.append(f"❌ {test_case['test_type']} - Name extraction failed. Expected: '{expected_name}', Got: '{actual_name}'")
                
                # Test prospect name extraction
                if "expected_first" in test_case:
                    actual_first = data.get('first_name', '')
                    actual_last = data.get('last_name', '')
                    actual_company = data.get('company', '')
                    
                    expected_first = test_case["expected_first"]
                    expected_last = test_case["expected_last"]
                    expected_company = test_case["expected_company"]
                    
                    first_correct = expected_first in actual_first
                    last_correct = expected_last in actual_last
                    company_correct = expected_company in actual_company
                    
                    if first_correct and last_correct and company_correct:
                        results.append(f"✅ {test_case['test_type']} - Correct extraction: '{actual_first} {actual_last}' from '{actual_company}'")
                        if 'id' in data:
                            self.created_resources['prospects'].append(data['id'])
                    else:
                        results.append(f"❌ {test_case['test_type']} - Extraction failed. Expected: '{expected_first} {expected_last}' from '{expected_company}', Got: '{actual_first} {actual_last}' from '{actual_company}'")
                
            except Exception as e:
                results.append(f"{test_case['test_type']} - Exception: {str(e)}")
        
        # Evaluate results
        success_count = len([r for r in results if r.startswith('✅')])
        total_count = len(test_cases)
        
        if success_count == total_count:
            self.log_result("Parameter Extraction", True, f"All {total_count} extractions successful", results)
            return True
        else:
            self.log_result("Parameter Extraction", False, f"{success_count}/{total_count} extractions successful", results)
            return False
    
    def test_action_router(self):
        """Test Action Router functionality"""
        try:
            # Test that backend CRUD operations work
            backend_tests = []
            
            # Test list creation directly
            list_data = {
                "name": "Action Router Test List",
                "description": "Test list for action router",
                "color": "#FF5722",
                "tags": ["test"]
            }
            
            response = requests.post(f"{self.base_url}/api/lists", json=list_data, headers=self.headers)
            if response.status_code == 200:
                created_list = response.json()
                if 'id' in created_list:
                    self.created_resources['lists'].append(created_list['id'])
                    backend_tests.append("✅ Direct list creation successful")
                else:
                    backend_tests.append("❌ Direct list creation - no ID returned")
            else:
                backend_tests.append(f"❌ Direct list creation failed - HTTP {response.status_code}")
            
            # Test prospect creation directly
            unique_id = int(time.time())
            prospect_data = {
                "email": f"actionrouter.test.{unique_id}@example.com",
                "first_name": "Action",
                "last_name": "Router",
                "company": "Test Corp"
            }
            
            response = requests.post(f"{self.base_url}/api/prospects", json=prospect_data, headers=self.headers)
            if response.status_code == 200:
                created_prospect = response.json()
                if 'id' in created_prospect:
                    self.created_resources['prospects'].append(created_prospect['id'])
                    backend_tests.append("✅ Direct prospect creation successful")
                else:
                    backend_tests.append("❌ Direct prospect creation - no ID returned")
            else:
                backend_tests.append(f"❌ Direct prospect creation failed - HTTP {response.status_code}")
            
            # Test data retrieval
            response = requests.get(f"{self.base_url}/api/lists", headers=self.headers)
            if response.status_code == 200:
                lists = response.json()
                backend_tests.append(f"✅ List retrieval successful - {len(lists)} lists")
            else:
                backend_tests.append(f"❌ List retrieval failed - HTTP {response.status_code}")
            
            response = requests.get(f"{self.base_url}/api/prospects", headers=self.headers)
            if response.status_code == 200:
                prospects = response.json()
                backend_tests.append(f"✅ Prospect retrieval successful - {len(prospects)} prospects")
            else:
                backend_tests.append(f"❌ Prospect retrieval failed - HTTP {response.status_code}")
            
            # Evaluate results
            success_count = len([t for t in backend_tests if t.startswith('✅')])
            total_count = len(backend_tests)
            
            if success_count == total_count:
                self.log_result("Action Router", True, f"All {total_count} backend operations successful", backend_tests)
                return True
            else:
                self.log_result("Action Router", False, f"{success_count}/{total_count} backend operations successful", backend_tests)
                return False
                
        except Exception as e:
            self.log_result("Action Router", False, f"Exception: {str(e)}")
            return False
    
    def test_email_generation(self):
        """Test email generation when email is not provided"""
        try:
            command = "Add prospect Test User from Example Company"
            unique_id = int(time.time())
            command = command.replace("Test User", f"Test User{unique_id}")
            
            chat_request = {
                "message": command,
                "context": {
                    "user_id": "testuser",
                    "session_id": "email_gen_test"
                }
            }
            
            response = requests.post(f"{self.base_url}/api/ai-agent/chat", json=chat_request, headers=self.headers)
            
            if response.status_code != 200:
                self.log_result("Email Generation", False, f"HTTP {response.status_code}", response.text)
                return False
            
            chat_response = response.json()
            data = chat_response.get('data')
            
            if not data:
                self.log_result("Email Generation", False, "No data returned")
                return False
            
            email = data.get('email', '')
            first_name = data.get('first_name', '')
            company = data.get('company', '')
            
            # Check if email was generated
            if email and '@' in email:
                # Check if email contains elements from name and company
                if first_name.lower() in email.lower() and 'example' in email.lower():
                    self.log_result("Email Generation", True, f"Email generated successfully: {email}")
                    if 'id' in data:
                        self.created_resources['prospects'].append(data['id'])
                    return True
                else:
                    self.log_result("Email Generation", False, f"Email generation logic incorrect: {email}")
                    return False
            else:
                self.log_result("Email Generation", False, "No email generated")
                return False
                
        except Exception as e:
            self.log_result("Email Generation", False, f"Exception: {str(e)}")
            return False
    
    def cleanup_resources(self):
        """Clean up created test resources"""
        print("\n🧹 Cleaning up AI Agent NLP test resources...")
        
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
    
    def run_comprehensive_tests(self):
        """Run comprehensive AI Agent NLP tests"""
        print("🤖 Starting AI Agent Natural Language Processing Tests")
        print("Focus: Multi-word name extraction, parameter parsing, regex pattern fixes")
        print("=" * 80)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return self.test_results
        
        # Test order matters for dependencies
        tests = [
            ("AI Agent Infrastructure", self.test_ai_agent_infrastructure),
            ("List Creation Commands", self.test_list_creation_commands),
            ("Prospect Creation Commands", self.test_prospect_creation_commands),
            ("Show/Display Commands", self.test_show_display_commands),
            ("Parameter Extraction", self.test_parameter_extraction),
            ("Action Router", self.test_action_router),
            ("Email Generation", self.test_email_generation)
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
                    if any(keyword in test_name.lower() for keyword in ['list creation', 'prospect creation', 'parameter extraction']):
                        critical_failures.append(test_name)
            except Exception as e:
                self.log_result(test_name, False, f"Test execution failed: {str(e)}")
                critical_failures.append(test_name)
        
        print("\n" + "=" * 80)
        print(f"📊 AI Agent NLP Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All AI Agent NLP tests passed!")
        else:
            print(f"⚠️  {total - passed} AI Agent NLP tests failed")
            if critical_failures:
                print(f"🚨 Critical failures in: {', '.join(critical_failures)}")
        
        # Cleanup
        self.cleanup_resources()
        
        return self.test_results, critical_failures

def main():
    """Main test execution"""
    tester = AIAgentNLPTester()
    results, critical_failures = tester.run_comprehensive_tests()
    
    # Print detailed results
    print("\n" + "=" * 80)
    print("📋 DETAILED AI AGENT NLP TEST RESULTS")
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
    print("📝 AI AGENT NLP TESTING SUMMARY")
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
        
        print("\n🔍 ROOT CAUSE ANALYSIS:")
        print("Based on previous testing, the main issues are:")
        print("1. Multi-word list names being truncated (regex pattern issue)")
        print("2. Complex prospect name parsing failures")
        print("3. Regex patterns using non-greedy matching (+?) stopping at first word")
        print("4. Parameter extraction not handling varied natural language formats")
    else:
        print("\n✅ NO CRITICAL FAILURES")
    
    return results, critical_failures

if __name__ == "__main__":
    main()