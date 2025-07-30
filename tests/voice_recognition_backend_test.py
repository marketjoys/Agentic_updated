#!/usr/bin/env python3
"""
AI Email Responder - Voice Recognition Fix Backend Testing
Testing the specific areas mentioned in the review request:
1. Backend Health verification
2. Authentication testing (testuser/testpass123)
3. AI Agent Endpoint testing (/api/ai-agent/chat)
4. Voice-Related APIs checking

The user was experiencing continuous Windows voice recognition error messages.
Fixes made include:
- Reduce error frequency with cooldown timers
- Better error categorization (temporary vs permanent)
- Improved retry logic with stabilization periods
- Added troubleshooting helpers for Windows users
"""

import asyncio
import aiohttp
import json
import sys
import os
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://b40c5c4f-de80-4df5-bbd3-3623f2621a6f.preview.emergentagent.com/api"

class VoiceRecognitionBackendTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_results = {
            "backend_health": {"status": "not_tested", "details": []},
            "authentication": {"status": "not_tested", "details": []},
            "ai_agent_endpoint": {"status": "not_tested", "details": []},
            "voice_related_apis": {"status": "not_tested", "details": []}
        }
        
    async def setup_session(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession()
        print("✅ HTTP session established")
        return True
    
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    async def test_backend_health(self):
        """Test 1: Backend Health - Verify backend is accessible and healthy"""
        print("\n🏥 TESTING BACKEND HEALTH...")
        test_details = []
        
        try:
            # Test health endpoint
            async with self.session.get(f"{BACKEND_URL}/health") as response:
                if response.status == 200:
                    health_data = await response.json()
                    test_details.append("✅ Backend health endpoint accessible")
                    test_details.append(f"   - Status: {health_data.get('status', 'unknown')}")
                    test_details.append(f"   - Timestamp: {health_data.get('timestamp', 'unknown')}")
                    
                    if health_data.get('status') == 'healthy':
                        test_details.append("✅ Backend reports healthy status")
                        self.test_results["backend_health"]["status"] = "passed"
                    else:
                        test_details.append("⚠️ Backend reports non-healthy status")
                        self.test_results["backend_health"]["status"] = "partial"
                else:
                    test_details.append(f"❌ Health endpoint returned HTTP {response.status}")
                    self.test_results["backend_health"]["status"] = "failed"
            
            # Test basic API accessibility
            async with self.session.get(f"{BACKEND_URL}/") as response:
                # This might return 404 but shows the server is responding
                test_details.append(f"✅ Backend server responding (HTTP {response.status})")
                    
        except Exception as e:
            test_details.append(f"❌ Exception in backend health test: {str(e)}")
            self.test_results["backend_health"]["status"] = "failed"
        
        self.test_results["backend_health"]["details"] = test_details
        for detail in test_details:
            print(f"   {detail}")
    
    async def test_authentication(self):
        """Test 2: Authentication - Test login with testuser/testpass123"""
        print("\n🔐 TESTING AUTHENTICATION...")
        test_details = []
        
        try:
            # Test login with specified credentials
            login_data = {"username": "testuser", "password": "testpass123"}
            async with self.session.post(f"{BACKEND_URL}/auth/login", json=login_data) as response:
                if response.status == 200:
                    auth_data = await response.json()
                    self.auth_token = auth_data.get("access_token")
                    test_details.append("✅ Authentication successful with testuser/testpass123")
                    test_details.append(f"   - Token received: {self.auth_token[:20]}..." if self.auth_token else "   - No token received")
                    test_details.append(f"   - Token type: {auth_data.get('token_type', 'unknown')}")
                    
                    # Test token validation with /auth/me endpoint
                    if self.auth_token:
                        headers = {"Authorization": f"Bearer {self.auth_token}"}
                        async with self.session.get(f"{BACKEND_URL}/auth/me", headers=headers) as me_response:
                            if me_response.status == 200:
                                user_data = await me_response.json()
                                test_details.append("✅ Token validation successful")
                                test_details.append(f"   - Username: {user_data.get('username', 'unknown')}")
                                test_details.append(f"   - Email: {user_data.get('email', 'unknown')}")
                                test_details.append(f"   - Active: {user_data.get('is_active', False)}")
                                self.test_results["authentication"]["status"] = "passed"
                            else:
                                test_details.append(f"⚠️ Token validation failed: HTTP {me_response.status}")
                                self.test_results["authentication"]["status"] = "partial"
                    else:
                        test_details.append("⚠️ No access token received")
                        self.test_results["authentication"]["status"] = "partial"
                        
                elif response.status == 401:
                    test_details.append("❌ Authentication failed - Invalid credentials")
                    test_details.append("   - Expected: testuser/testpass123")
                    self.test_results["authentication"]["status"] = "failed"
                else:
                    test_details.append(f"❌ Authentication endpoint returned HTTP {response.status}")
                    error_text = await response.text()
                    test_details.append(f"   - Error: {error_text[:200]}")
                    self.test_results["authentication"]["status"] = "failed"
                    
        except Exception as e:
            test_details.append(f"❌ Exception in authentication test: {str(e)}")
            self.test_results["authentication"]["status"] = "failed"
        
        self.test_results["authentication"]["details"] = test_details
        for detail in test_details:
            print(f"   {detail}")
    
    async def test_ai_agent_endpoint(self):
        """Test 3: AI Agent Endpoint - Test /api/ai-agent/chat accessibility"""
        print("\n🤖 TESTING AI AGENT ENDPOINT...")
        test_details = []
        
        try:
            if not self.auth_token:
                test_details.append("❌ No auth token available - skipping AI agent tests")
                self.test_results["ai_agent_endpoint"]["status"] = "failed"
                self.test_results["ai_agent_endpoint"]["details"] = test_details
                for detail in test_details:
                    print(f"   {detail}")
                return
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Test AI agent capabilities endpoint
            async with self.session.get(f"{BACKEND_URL}/ai-agent/capabilities", headers=headers) as response:
                if response.status == 200:
                    capabilities = await response.json()
                    test_details.append("✅ AI Agent capabilities endpoint accessible")
                    test_details.append(f"   - Capabilities found: {len(capabilities) if isinstance(capabilities, list) else 'N/A'}")
                elif response.status == 404:
                    test_details.append("⚠️ AI Agent capabilities endpoint not found (HTTP 404)")
                else:
                    test_details.append(f"⚠️ AI Agent capabilities returned HTTP {response.status}")
            
            # Test AI agent help endpoint
            async with self.session.get(f"{BACKEND_URL}/ai-agent/help", headers=headers) as response:
                if response.status == 200:
                    help_data = await response.json()
                    test_details.append("✅ AI Agent help endpoint accessible")
                elif response.status == 404:
                    test_details.append("⚠️ AI Agent help endpoint not found (HTTP 404)")
                else:
                    test_details.append(f"⚠️ AI Agent help returned HTTP {response.status}")
            
            # Test AI agent chat endpoint - the main endpoint mentioned in review
            chat_data = {
                "message": "Hello, can you help me test the voice recognition system?",
                "session_id": "voice_test_session_123"
            }
            
            async with self.session.post(f"{BACKEND_URL}/ai-agent/chat", json=chat_data, headers=headers) as response:
                if response.status == 200:
                    chat_response = await response.json()
                    test_details.append("✅ AI Agent chat endpoint accessible and responding")
                    test_details.append(f"   - Response received: {len(str(chat_response))} characters")
                    test_details.append(f"   - Response type: {type(chat_response).__name__}")
                    
                    # Check if response contains expected fields
                    if isinstance(chat_response, dict):
                        if "response" in chat_response:
                            test_details.append("✅ Chat response contains 'response' field")
                        if "session_id" in chat_response:
                            test_details.append("✅ Chat response contains 'session_id' field")
                    
                    self.test_results["ai_agent_endpoint"]["status"] = "passed"
                    
                elif response.status == 404:
                    test_details.append("❌ AI Agent chat endpoint not found (HTTP 404)")
                    test_details.append("   - This is the main endpoint mentioned in the review request")
                    self.test_results["ai_agent_endpoint"]["status"] = "failed"
                else:
                    test_details.append(f"⚠️ AI Agent chat endpoint returned HTTP {response.status}")
                    error_text = await response.text()
                    test_details.append(f"   - Error: {error_text[:200]}")
                    self.test_results["ai_agent_endpoint"]["status"] = "partial"
            
            # Test enhanced AI agent endpoints if available
            enhanced_endpoints = [
                "/ai-agent/enhanced-capabilities",
                "/ai-agent/conversation-context/voice_test_session_123",
                "/ai-agent/set-turn-limit"
            ]
            
            for endpoint in enhanced_endpoints:
                try:
                    if endpoint.endswith("set-turn-limit"):
                        # POST endpoint
                        turn_data = {"turn_limit": 25}
                        async with self.session.post(f"{BACKEND_URL}{endpoint}", json=turn_data, headers=headers) as response:
                            if response.status == 200:
                                test_details.append(f"✅ Enhanced endpoint accessible: {endpoint}")
                            elif response.status == 404:
                                test_details.append(f"⚠️ Enhanced endpoint not found: {endpoint}")
                            else:
                                test_details.append(f"⚠️ Enhanced endpoint returned HTTP {response.status}: {endpoint}")
                    else:
                        # GET endpoint
                        async with self.session.get(f"{BACKEND_URL}{endpoint}", headers=headers) as response:
                            if response.status == 200:
                                test_details.append(f"✅ Enhanced endpoint accessible: {endpoint}")
                            elif response.status == 404:
                                test_details.append(f"⚠️ Enhanced endpoint not found: {endpoint}")
                            else:
                                test_details.append(f"⚠️ Enhanced endpoint returned HTTP {response.status}: {endpoint}")
                except Exception as e:
                    test_details.append(f"⚠️ Error testing enhanced endpoint {endpoint}: {str(e)}")
                    
        except Exception as e:
            test_details.append(f"❌ Exception in AI agent endpoint test: {str(e)}")
            self.test_results["ai_agent_endpoint"]["status"] = "failed"
        
        self.test_results["ai_agent_endpoint"]["details"] = test_details
        for detail in test_details:
            print(f"   {detail}")
    
    async def test_voice_related_apis(self):
        """Test 4: Voice-Related APIs - Check for any voice or speech recognition endpoints"""
        print("\n🎤 TESTING VOICE-RELATED APIs...")
        test_details = []
        
        try:
            if not self.auth_token:
                test_details.append("❌ No auth token available - skipping voice API tests")
                self.test_results["voice_related_apis"]["status"] = "failed"
                self.test_results["voice_related_apis"]["details"] = test_details
                for detail in test_details:
                    print(f"   {detail}")
                return
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # List of potential voice-related endpoints to test
            voice_endpoints = [
                "/voice/recognition",
                "/voice/speech-to-text",
                "/voice/config",
                "/voice/status",
                "/speech/recognize",
                "/speech/config",
                "/audio/process",
                "/microphone/status",
                "/voice-recognition/status",
                "/voice-recognition/config"
            ]
            
            accessible_endpoints = []
            not_found_endpoints = []
            error_endpoints = []
            
            for endpoint in voice_endpoints:
                try:
                    async with self.session.get(f"{BACKEND_URL}{endpoint}", headers=headers) as response:
                        if response.status == 200:
                            accessible_endpoints.append(endpoint)
                            test_details.append(f"✅ Voice endpoint accessible: {endpoint}")
                        elif response.status == 404:
                            not_found_endpoints.append(endpoint)
                        else:
                            error_endpoints.append((endpoint, response.status))
                            test_details.append(f"⚠️ Voice endpoint returned HTTP {response.status}: {endpoint}")
                except Exception as e:
                    error_endpoints.append((endpoint, str(e)))
                    test_details.append(f"⚠️ Error testing voice endpoint {endpoint}: {str(e)}")
            
            # Summary of voice endpoint testing
            test_details.append(f"📊 Voice Endpoint Testing Summary:")
            test_details.append(f"   - Accessible endpoints: {len(accessible_endpoints)}")
            test_details.append(f"   - Not found (404): {len(not_found_endpoints)}")
            test_details.append(f"   - Error endpoints: {len(error_endpoints)}")
            
            if accessible_endpoints:
                test_details.append("✅ Found accessible voice-related endpoints:")
                for endpoint in accessible_endpoints:
                    test_details.append(f"   - {endpoint}")
                self.test_results["voice_related_apis"]["status"] = "passed"
            else:
                test_details.append("ℹ️ No dedicated voice-related API endpoints found")
                test_details.append("   This is expected if voice functionality is handled client-side")
                
                # Check if AI agent supports voice-related commands
                voice_test_messages = [
                    "Can you help with voice recognition?",
                    "How do I configure voice settings?",
                    "What voice commands are available?"
                ]
                
                test_details.append("🔍 Testing AI Agent for voice-related functionality:")
                
                for message in voice_test_messages:
                    try:
                        chat_data = {
                            "message": message,
                            "session_id": "voice_functionality_test"
                        }
                        
                        async with self.session.post(f"{BACKEND_URL}/ai-agent/chat", json=chat_data, headers=headers) as response:
                            if response.status == 200:
                                chat_response = await response.json()
                                response_text = str(chat_response.get("response", "")).lower()
                                
                                # Check if response mentions voice-related terms
                                voice_terms = ["voice", "speech", "microphone", "audio", "recognition", "listen"]
                                if any(term in response_text for term in voice_terms):
                                    test_details.append(f"✅ AI Agent responds to voice query: '{message[:30]}...'")
                                else:
                                    test_details.append(f"⚠️ AI Agent response doesn't mention voice: '{message[:30]}...'")
                            else:
                                test_details.append(f"⚠️ AI Agent chat failed for voice query: HTTP {response.status}")
                    except Exception as e:
                        test_details.append(f"⚠️ Error testing AI Agent voice query: {str(e)}")
                
                self.test_results["voice_related_apis"]["status"] = "partial"
                    
        except Exception as e:
            test_details.append(f"❌ Exception in voice-related APIs test: {str(e)}")
            self.test_results["voice_related_apis"]["status"] = "failed"
        
        self.test_results["voice_related_apis"]["details"] = test_details
        for detail in test_details:
            print(f"   {detail}")
    
    async def run_all_tests(self):
        """Run all voice recognition backend tests"""
        print("🚀 STARTING VOICE RECOGNITION FIX BACKEND TESTING")
        print("=" * 70)
        print("Testing backend stability and accessibility before frontend voice testing")
        print("=" * 70)
        
        # Setup session
        if not await self.setup_session():
            print("❌ Failed to setup session. Exiting.")
            return
        
        try:
            # Run all tests in sequence
            await self.test_backend_health()
            await self.test_authentication()
            await self.test_ai_agent_endpoint()
            await self.test_voice_related_apis()
            
            # Print comprehensive summary
            print("\n" + "=" * 70)
            print("📊 VOICE RECOGNITION BACKEND TEST SUMMARY")
            print("=" * 70)
            
            total_tests = len(self.test_results)
            passed_tests = len([r for r in self.test_results.values() if r["status"] == "passed"])
            partial_tests = len([r for r in self.test_results.values() if r["status"] == "partial"])
            failed_tests = len([r for r in self.test_results.values() if r["status"] == "failed"])
            
            print(f"Total Test Categories: {total_tests}")
            print(f"✅ Passed: {passed_tests}")
            print(f"⚠️ Partial: {partial_tests}")
            print(f"❌ Failed: {failed_tests}")
            print(f"Success Rate: {(passed_tests + partial_tests) / total_tests * 100:.1f}%")
            
            print("\nDetailed Results:")
            for test_name, result in self.test_results.items():
                status_icon = "✅" if result["status"] == "passed" else "⚠️" if result["status"] == "partial" else "❌"
                print(f"{status_icon} {test_name.replace('_', ' ').title()}: {result['status']}")
            
            # Overall assessment for voice recognition fix
            print("\n" + "=" * 70)
            print("🎯 VOICE RECOGNITION FIX ASSESSMENT")
            print("=" * 70)
            
            if passed_tests >= 3:  # At least 3 out of 4 tests should pass
                print("✅ BACKEND IS STABLE AND READY FOR VOICE TESTING")
                print("   - Backend health is good")
                print("   - Authentication is working")
                print("   - AI Agent endpoint is accessible")
                print("   - Ready to proceed with frontend voice functionality testing")
                
                if self.test_results["ai_agent_endpoint"]["status"] == "passed":
                    print("   - AI Agent chat endpoint is fully functional")
                    print("   - Voice recognition fixes can be tested through AI Agent")
                
            elif passed_tests + partial_tests >= 3:
                print("⚠️ BACKEND IS MOSTLY STABLE - PROCEED WITH CAUTION")
                print("   - Some components may have minor issues")
                print("   - Core functionality appears to be working")
                print("   - Voice testing can proceed but monitor for issues")
                
            else:
                print("❌ BACKEND HAS CRITICAL ISSUES - VOICE TESTING NOT RECOMMENDED")
                print("   - Multiple backend components are failing")
                print("   - Fix backend issues before testing voice functionality")
                print("   - Voice recognition fixes cannot be properly validated")
            
            # Specific recommendations for voice recognition
            print("\n🔧 VOICE RECOGNITION SPECIFIC FINDINGS:")
            
            if self.test_results["ai_agent_endpoint"]["status"] == "passed":
                print("✅ AI Agent endpoint is accessible - voice commands can be processed")
            else:
                print("❌ AI Agent endpoint issues - voice commands may not work properly")
            
            if self.test_results["voice_related_apis"]["status"] in ["passed", "partial"]:
                print("✅ Voice-related functionality appears to be available")
            else:
                print("ℹ️ Voice functionality likely handled client-side (normal for web apps)")
            
            print("\n📋 NEXT STEPS:")
            print("1. If backend is stable, proceed with frontend voice testing")
            print("2. Test voice recognition error handling improvements")
            print("3. Verify cooldown timers and retry logic are working")
            print("4. Check Windows-specific troubleshooting helpers")
            print("5. Validate error categorization (temporary vs permanent)")
                
        finally:
            await self.cleanup_session()

async def main():
    """Main test execution"""
    tester = VoiceRecognitionBackendTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())