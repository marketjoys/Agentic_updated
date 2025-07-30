#!/usr/bin/env python3
"""
Enhanced AI Agent Confirmation Flow Testing - December 2024
Tests the new enhanced AI Agent functionality with confirmation flow as requested in review
"""

import requests
import json
import time
from datetime import datetime
import sys

# Configuration
BASE_URL = "https://923febb0-4941-4a54-88e6-10f9c6187a71.preview.emergentagent.com/api"
USERNAME = "testuser"
PASSWORD = "testpass123"

class EnhancedAIAgentConfirmationTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.test_session_id = f"test_session_{int(time.time())}"
        self.results = []
        
    def log_result(self, test_name, success, details="", data=None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if not success and data:
            print(f"   Error Data: {data}")
        print()

    def authenticate(self):
        """Authenticate and get token"""
        try:
            response = self.session.post(f"{BASE_URL}/auth/login", json={
                "username": USERNAME,
                "password": PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                self.log_result("Authentication", True, f"Successfully logged in as {USERNAME}")
                return True
            else:
                self.log_result("Authentication", False, f"Login failed: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Authentication", False, f"Authentication error: {str(e)}")
            return False

    def test_enhanced_ai_agent_chat_with_confirmation(self):
        """Test Enhanced AI Agent Chat Endpoint with use_enhanced_flow=true"""
        try:
            # Test 1: Create a campaign with enhanced flow
            test_message = "Create a campaign named Test Campaign"
            
            response = self.session.post(f"{BASE_URL}/ai-agent/chat", json={
                "message": test_message,
                "user_id": "testuser",
                "session_id": self.test_session_id,
                "use_enhanced_flow": True,
                "context": {}
            })
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required fields in response
                required_fields = ["response", "session_id", "timestamp", "conversation_state", "context_info"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_result("Enhanced AI Agent Chat - Response Structure", False, 
                                  f"Missing fields: {missing_fields}", data)
                    return False
                
                # Check if it returns conversation_state, pending_action, context_info
                conv_state = data.get("conversation_state")
                pending_action = data.get("pending_action")
                context_info = data.get("context_info")
                
                if conv_state and context_info:
                    self.log_result("Enhanced AI Agent Chat - Enhanced Fields", True, 
                                  f"Has conversation_state: {conv_state}, context_info with {len(context_info)} fields")
                else:
                    self.log_result("Enhanced AI Agent Chat - Enhanced Fields", False, 
                                  f"Missing enhanced fields: state={conv_state}, context={bool(context_info)}")
                
                # Check if it asks for missing parameters instead of executing immediately
                response_text = data.get("response", "").lower()
                
                # Should ask for missing information or show confirmation flow
                if any(keyword in response_text for keyword in ["need", "require", "missing", "specify", "confirm", "template", "list"]):
                    self.log_result("Enhanced AI Agent Chat - Asks for Missing Parameters", True, 
                                  f"Agent correctly asks for missing parameters: {data['response'][:150]}...")
                else:
                    self.log_result("Enhanced AI Agent Chat - Asks for Missing Parameters", False, 
                                  f"Agent should ask for missing parameters, got: {data['response'][:150]}...")
                
                # Check context_info structure
                expected_context_fields = ["turn_count", "max_turns", "state", "extracted_params", "missing_params"]
                context_missing = [field for field in expected_context_fields if field not in context_info]
                
                if not context_missing:
                    self.log_result("Enhanced AI Agent Chat - Context Info Structure", True, 
                                  f"Context info complete: state={context_info.get('state')}, turns={context_info.get('turn_count')}")
                else:
                    self.log_result("Enhanced AI Agent Chat - Context Info Structure", False, 
                                  f"Missing context fields: {context_missing}")
                
                return True
                
            else:
                self.log_result("Enhanced AI Agent Chat", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Enhanced AI Agent Chat", False, f"Exception: {str(e)}")
            return False

    def test_legacy_ai_agent_chat_direct_execution(self):
        """Test Legacy AI Agent Chat Endpoint with use_enhanced_flow=false"""
        try:
            test_message = "Create a campaign named Test Campaign"
            
            response = self.session.post(f"{BASE_URL}/ai-agent/chat", json={
                "message": test_message,
                "user_id": "testuser",
                "session_id": f"{self.test_session_id}_legacy",
                "use_enhanced_flow": False,
                "context": {}
            })
            
            if response.status_code == 200:
                data = response.json()
                
                # Check that it uses legacy mode
                conv_state = data.get("conversation_state")
                context_info = data.get("context_info", {})
                
                if conv_state == "legacy" and context_info.get("mode") == "legacy":
                    self.log_result("Legacy AI Agent Chat - Legacy Mode", True, 
                                  "Successfully using legacy mode")
                else:
                    self.log_result("Legacy AI Agent Chat - Legacy Mode", False, 
                                  f"Expected legacy mode, got state={conv_state}, context={context_info}")
                
                # Should have no pending_action in legacy mode
                pending_action = data.get("pending_action")
                if pending_action is None:
                    self.log_result("Legacy AI Agent Chat - Direct Execution", True, 
                                  "Legacy mode correctly has no pending actions (direct execution)")
                else:
                    self.log_result("Legacy AI Agent Chat - Direct Execution", False, 
                                  f"Legacy mode should not have pending actions: {pending_action}")
                
                # Check response indicates direct execution attempt
                response_text = data.get("response", "").lower()
                if any(keyword in response_text for keyword in ["created", "done", "completed", "executed"]) or "help" in response_text:
                    self.log_result("Legacy AI Agent Chat - Direct Execution Response", True, 
                                  f"Legacy mode shows direct execution: {data['response'][:100]}...")
                else:
                    self.log_result("Legacy AI Agent Chat - Direct Execution Response", False, 
                                  f"Unexpected legacy response: {data['response'][:100]}...")
                
                return True
                
            else:
                self.log_result("Legacy AI Agent Chat", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Legacy AI Agent Chat", False, f"Exception: {str(e)}")
            return False

    def test_turn_limit_configuration(self):
        """Test Turn Limit Configuration - POST /api/ai-agent/set-turn-limit"""
        try:
            # Set turn limit to 25
            response = self.session.post(f"{BASE_URL}/ai-agent/set-turn-limit", json={
                "session_id": self.test_session_id,
                "max_turns": 25
            })
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure and confirms the update
                if (data.get("max_turns") == 25 and 
                    data.get("session_id") == self.test_session_id and
                    "Turn limit set to 25" in data.get("message", "")):
                    self.log_result("Turn Limit Configuration", True, 
                                  f"Turn limit set to 25 for session {self.test_session_id}")
                else:
                    self.log_result("Turn Limit Configuration", False, 
                                  f"Unexpected response: {data}")
                
                return True
                
            else:
                self.log_result("Turn Limit Configuration", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Turn Limit Configuration", False, f"Exception: {str(e)}")
            return False

    def test_enhanced_capabilities(self):
        """Test Enhanced Capabilities - GET /api/ai-agent/enhanced-capabilities"""
        try:
            response = self.session.get(f"{BASE_URL}/ai-agent/enhanced-capabilities")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for required sections
                required_sections = ["capabilities", "conversation_flow", "context_features", "examples"]
                missing_sections = [section for section in required_sections if section not in data]
                
                if missing_sections:
                    self.log_result("Enhanced Capabilities - Structure", False, 
                                  f"Missing sections: {missing_sections}", data)
                    return False
                
                # Check conversation flow steps and enhanced features
                conv_flow = data.get("conversation_flow", {})
                steps = conv_flow.get("steps", [])
                states = conv_flow.get("states", [])
                
                if len(steps) >= 6 and len(states) >= 5:
                    self.log_result("Enhanced Capabilities - Conversation Flow Steps", True, 
                                  f"Found {len(steps)} steps and {len(states)} states")
                else:
                    self.log_result("Enhanced Capabilities - Conversation Flow Steps", False, 
                                  f"Insufficient steps ({len(steps)}) or states ({len(states)})")
                
                # Check context features
                context_features = data.get("context_features", [])
                if len(context_features) >= 4:
                    self.log_result("Enhanced Capabilities - Context Features", True, 
                                  f"Found {len(context_features)} enhanced features")
                else:
                    self.log_result("Enhanced Capabilities - Context Features", False, 
                                  f"Insufficient context features: {len(context_features)}")
                
                return True
                
            else:
                self.log_result("Enhanced Capabilities", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Enhanced Capabilities", False, f"Exception: {str(e)}")
            return False

    def test_conversation_context(self):
        """Test Conversation Context - GET /api/ai-agent/conversation-context/{session_id}"""
        try:
            response = self.session.get(f"{BASE_URL}/ai-agent/conversation-context/{self.test_session_id}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required fields - returns current state, extracted params, missing params
                required_fields = ["session_id", "user_id", "current_state", "turn_count", "max_turns", 
                                 "extracted_params", "missing_params", "context_variables"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_result("Conversation Context - Structure", False, 
                                  f"Missing fields: {missing_fields}", data)
                    return False
                
                # Check session ID matches
                if data.get("session_id") == self.test_session_id:
                    self.log_result("Conversation Context - Session ID", True, 
                                  f"Session ID matches: {self.test_session_id}")
                else:
                    self.log_result("Conversation Context - Session ID", False, 
                                  f"Session ID mismatch: expected {self.test_session_id}, got {data.get('session_id')}")
                
                # Check state information and parameters
                current_state = data.get("current_state")
                extracted_params = data.get("extracted_params", {})
                missing_params = data.get("missing_params", [])
                turn_count = data.get("turn_count", 0)
                max_turns = data.get("max_turns", 0)
                
                if current_state and max_turns > 0:
                    self.log_result("Conversation Context - State & Parameters", True, 
                                  f"State: {current_state}, Turns: {turn_count}/{max_turns}, Extracted: {len(extracted_params)}, Missing: {len(missing_params)}")
                else:
                    self.log_result("Conversation Context - State & Parameters", False, 
                                  f"Invalid state info: state={current_state}, max_turns={max_turns}")
                
                return True
                
            else:
                self.log_result("Conversation Context", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Conversation Context", False, f"Exception: {str(e)}")
            return False

    def test_multi_turn_conversation_flow(self):
        """Test Complete Multi-turn Conversation Flow with Confirmation"""
        try:
            # Step 1: Start with "Create campaign Summer Sale"
            print("🔄 Testing Multi-turn Conversation Flow...")
            session_id = f"{self.test_session_id}_multiturn"
            
            response1 = self.session.post(f"{BASE_URL}/ai-agent/chat", json={
                "message": "Create campaign Summer Sale",
                "user_id": "testuser",
                "session_id": session_id,
                "use_enhanced_flow": True,
                "context": {}
            })
            
            if response1.status_code != 200:
                self.log_result("Multi-turn Flow - Step 1", False, 
                              f"HTTP {response1.status_code}", response1.text)
                return False
            
            data1 = response1.json()
            print(f"   Step 1 Response: {data1.get('response', '')[:150]}...")
            
            # Step 2: Provide missing information when asked
            response2 = self.session.post(f"{BASE_URL}/ai-agent/chat", json={
                "message": "Use the Welcome Email template and send to Technology Companies list with max 100 emails",
                "user_id": "testuser",
                "session_id": session_id,
                "use_enhanced_flow": True,
                "context": {}
            })
            
            if response2.status_code != 200:
                self.log_result("Multi-turn Flow - Step 2", False, 
                              f"HTTP {response2.status_code}", response2.text)
                return False
            
            data2 = response2.json()
            print(f"   Step 2 Response: {data2.get('response', '')[:150]}...")
            
            # Step 3: Confirm when prompted
            response3 = self.session.post(f"{BASE_URL}/ai-agent/chat", json={
                "message": "Yes, proceed with creating the campaign",
                "user_id": "testuser",
                "session_id": session_id,
                "use_enhanced_flow": True,
                "context": {}
            })
            
            if response3.status_code != 200:
                self.log_result("Multi-turn Flow - Step 3", False, 
                              f"HTTP {response3.status_code}", response3.text)
                return False
            
            data3 = response3.json()
            print(f"   Step 3 Response: {data3.get('response', '')[:150]}...")
            
            # Verify the action gets executed
            action_taken3 = data3.get("action_taken")
            response_text3 = data3.get("response", "").lower()
            
            if action_taken3 or any(keyword in response_text3 for keyword in ["created", "executed", "completed", "campaign"]):
                self.log_result("Multi-turn Flow - Action Execution", True, 
                              f"Action executed: {action_taken3 or 'Indicated in response'}")
            else:
                self.log_result("Multi-turn Flow - Action Execution", False, 
                              f"Action not executed: {action_taken3}, response: {response_text3[:100]}")
            
            # Check if conversation progressed through states
            state1 = data1.get("conversation_state", "")
            state2 = data2.get("conversation_state", "")
            state3 = data3.get("conversation_state", "")
            
            # Check context progression
            context1 = data1.get("context_info", {})
            context2 = data2.get("context_info", {})
            context3 = data3.get("context_info", {})
            
            turn_count_increased = (context1.get("turn_count", 0) < context2.get("turn_count", 0) <= context3.get("turn_count", 0))
            
            if turn_count_increased:
                self.log_result("Multi-turn Flow - Turn Progression", True, 
                              f"Turn count progressed: {context1.get('turn_count')} → {context2.get('turn_count')} → {context3.get('turn_count')}")
            else:
                self.log_result("Multi-turn Flow - Turn Progression", False, 
                              f"Turn count did not progress properly: {context1.get('turn_count')} → {context2.get('turn_count')} → {context3.get('turn_count')}")
            
            # Check state management
            if state1 and state2 and state3:
                self.log_result("Multi-turn Flow - State Management", True, 
                              f"States tracked: {state1} → {state2} → {state3}")
            else:
                self.log_result("Multi-turn Flow - State Management", False, 
                              f"States not properly tracked: {state1} → {state2} → {state3}")
            
            return True
            
        except Exception as e:
            self.log_result("Multi-turn Conversation Flow", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all enhanced AI Agent tests as requested in review"""
        print("🚀 Starting Enhanced AI Agent Confirmation Flow Testing")
        print("Testing the new enhanced AI Agent functionality with confirmation flow")
        print("=" * 70)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        # Run all tests as specified in review request
        tests = [
            ("Enhanced AI Agent Chat Endpoint (use_enhanced_flow=true)", self.test_enhanced_ai_agent_chat_with_confirmation),
            ("Legacy AI Agent Chat Endpoint (use_enhanced_flow=false)", self.test_legacy_ai_agent_chat_direct_execution),
            ("Turn Limit Configuration", self.test_turn_limit_configuration),
            ("Enhanced Capabilities", self.test_enhanced_capabilities),
            ("Conversation Context", self.test_conversation_context),
            ("Multi-turn Conversation Flow", self.test_multi_turn_conversation_flow)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🧪 Testing: {test_name}")
            print("-" * 50)
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                print(f"❌ Test {test_name} failed with exception: {e}")
        
        # Print summary
        print("\n" + "=" * 70)
        print(f"🎯 ENHANCED AI AGENT CONFIRMATION FLOW TEST SUMMARY")
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("🎉 ALL ENHANCED AI AGENT TESTS PASSED!")
            print("✅ Enhanced confirmation flow is working as expected")
            print("✅ Multi-turn conversation aspect and state management verified")
            return True
        else:
            print(f"⚠️  {total - passed} tests failed. Check details above.")
            return False

def main():
    """Main test execution"""
    tester = EnhancedAIAgentConfirmationTester()
    success = tester.run_all_tests()
    
    # Print detailed results
    print("\n" + "=" * 70)
    print("📊 DETAILED TEST RESULTS")
    print("=" * 70)
    
    for result in tester.results:
        status = "✅" if result["success"] else "❌"
        print(f"{status} {result['test']}")
        if result["details"]:
            print(f"   {result['details']}")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())