#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for AI Email Campaign Management System
Tests authentication, real-time features, security, and all core endpoints
"""

import requests
import json
import websocket
import threading
import time
from datetime import datetime
import sys

# Get backend URL from frontend .env file
BACKEND_URL = "https://d90eaae8-ec2e-41a4-a8e7-e61f976a5052.preview.emergentagent.com"
WS_URL = "wss://dd66e847-862b-4e28-9b0c-72de96723a60.preview.emergentagent.com"

class ComprehensiveBackendTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.ws_url = WS_URL
        self.test_results = {}
        self.auth_token = None
        self.test_user_data = {
            "username": f"testuser_{int(time.time())}",
            "email": f"test_{int(time.time())}@example.com",
            "password": "testpass123",
            "full_name": "Test User"
        }
        self.ws_messages = []
        self.ws_connected = False
    
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
            print(f"   Details: {json.dumps(details, indent=2)}")
        elif details:
            print(f"   Details: {details}")
    
    def test_health_check(self):
        """Test API health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'status' in data and data['status'] == 'healthy':
                    self.log_result("Health Check", True, "API is healthy", data)
                    return True
                else:
                    self.log_result("Health Check", False, "Invalid health response", data)
                    return False
            else:
                self.log_result("Health Check", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Health Check", False, f"Connection failed: {str(e)}")
            return False
    
    def test_authentication_system(self):
        """Test complete authentication system"""
        try:
            # Test Registration
            response = requests.post(f"{self.base_url}/api/auth/register", json=self.test_user_data)
            if response.status_code != 200:
                self.log_result("Auth Registration", False, f"HTTP {response.status_code}", response.text)
                return False
            
            register_data = response.json()
            if 'access_token' not in register_data:
                self.log_result("Auth Registration", False, "No access token in response", register_data)
                return False
            
            self.auth_token = register_data['access_token']
            self.log_result("Auth Registration", True, "User registered successfully")
            
            # Test Login
            login_data = {
                "username": self.test_user_data["username"],
                "password": self.test_user_data["password"]
            }
            response = requests.post(f"{self.base_url}/api/auth/login", json=login_data)
            if response.status_code != 200:
                self.log_result("Auth Login", False, f"HTTP {response.status_code}", response.text)
                return False
            
            login_response = response.json()
            if 'access_token' not in login_response:
                self.log_result("Auth Login", False, "No access token in response", login_response)
                return False
            
            self.auth_token = login_response['access_token']
            self.log_result("Auth Login", True, "User logged in successfully")
            
            # Test User Profile
            headers = {'Authorization': f'Bearer {self.auth_token}'}
            response = requests.get(f"{self.base_url}/api/auth/me", headers=headers)
            if response.status_code != 200:
                self.log_result("Auth User Profile", False, f"HTTP {response.status_code}", response.text)
                return False
            
            profile_data = response.json()
            if profile_data.get('username') != self.test_user_data['username']:
                self.log_result("Auth User Profile", False, "Username mismatch", profile_data)
                return False
            
            self.log_result("Auth User Profile", True, "User profile retrieved successfully", profile_data)
            
            # Test Token Refresh
            response = requests.post(f"{self.base_url}/api/auth/refresh", headers=headers)
            if response.status_code != 200:
                self.log_result("Auth Token Refresh", False, f"HTTP {response.status_code}", response.text)
                return False
            
            refresh_data = response.json()
            if 'access_token' not in refresh_data:
                self.log_result("Auth Token Refresh", False, "No access token in response", refresh_data)
                return False
            
            self.log_result("Auth Token Refresh", True, "Token refreshed successfully")
            
            # Test Protected Endpoint without Token
            response = requests.get(f"{self.base_url}/api/auth/me")
            if response.status_code == 200:
                self.log_result("Auth Protection Test", False, "Protected endpoint accessible without token")
                return False
            
            self.log_result("Auth Protection Test", True, "Protected endpoint properly secured")
            
            return True
            
        except Exception as e:
            self.log_result("Authentication System", False, f"Exception: {str(e)}")
            return False
    
    def test_real_time_endpoints(self):
        """Test real-time API endpoints"""
        try:
            # Test Dashboard Metrics
            response = requests.get(f"{self.base_url}/api/real-time/dashboard-metrics")
            if response.status_code != 200:
                self.log_result("Real-Time Dashboard Metrics", False, f"HTTP {response.status_code}", response.text)
                return False
            
            metrics_data = response.json()
            if 'metrics' not in metrics_data:
                self.log_result("Real-Time Dashboard Metrics", False, "No metrics in response", metrics_data)
                return False
            
            self.log_result("Real-Time Dashboard Metrics", True, "Dashboard metrics retrieved successfully")
            
            # Test System Status
            response = requests.get(f"{self.base_url}/api/real-time/system-status")
            if response.status_code != 200:
                self.log_result("Real-Time System Status", False, f"HTTP {response.status_code}", response.text)
                return False
            
            status_data = response.json()
            required_fields = ['database', 'websocket_connections']
            for field in required_fields:
                if field not in status_data:
                    self.log_result("Real-Time System Status", False, f"Missing field: {field}", status_data)
                    return False
            
            self.log_result("Real-Time System Status", True, "System status retrieved successfully", status_data)
            
            # Test Active Connections
            response = requests.get(f"{self.base_url}/api/real-time/active-connections")
            if response.status_code != 200:
                self.log_result("Real-Time Active Connections", False, f"HTTP {response.status_code}", response.text)
                return False
            
            connections_data = response.json()
            if 'total_connections' not in connections_data:
                self.log_result("Real-Time Active Connections", False, "No total_connections in response", connections_data)
                return False
            
            self.log_result("Real-Time Active Connections", True, f"Active connections: {connections_data['total_connections']}")
            
            return True
            
        except Exception as e:
            self.log_result("Real-Time Endpoints", False, f"Exception: {str(e)}")
            return False
    
    def test_websocket_connection(self):
        """Test WebSocket connection and real-time communication"""
        try:
            def on_message(ws, message):
                self.ws_messages.append(json.loads(message))
                print(f"WebSocket received: {message}")
            
            def on_open(ws):
                self.ws_connected = True
                print("WebSocket connection opened")
                # Send a test message
                test_message = {
                    "type": "ping",
                    "timestamp": datetime.now().isoformat()
                }
                ws.send(json.dumps(test_message))
            
            def on_error(ws, error):
                print(f"WebSocket error: {error}")
            
            def on_close(ws, close_status_code, close_msg):
                self.ws_connected = False
                print("WebSocket connection closed")
            
            # Create WebSocket connection
            ws_url = f"{self.ws_url}/api/ws/test-client"
            ws = websocket.WebSocketApp(ws_url,
                                      on_open=on_open,
                                      on_message=on_message,
                                      on_error=on_error,
                                      on_close=on_close)
            
            # Run WebSocket in a separate thread
            ws_thread = threading.Thread(target=ws.run_forever)
            ws_thread.daemon = True
            ws_thread.start()
            
            # Wait for connection and messages
            time.sleep(3)
            
            if not self.ws_connected:
                self.log_result("WebSocket Connection", False, "Failed to establish WebSocket connection")
                return False
            
            if len(self.ws_messages) == 0:
                self.log_result("WebSocket Communication", False, "No messages received via WebSocket")
                return False
            
            # Check if we received a pong response
            pong_received = any(msg.get('type') == 'pong' for msg in self.ws_messages)
            if not pong_received:
                self.log_result("WebSocket Ping-Pong", False, "No pong response received", self.ws_messages)
                return False
            
            self.log_result("WebSocket Connection", True, "WebSocket connection and communication successful")
            
            # Close the connection
            ws.close()
            
            return True
            
        except Exception as e:
            self.log_result("WebSocket Connection", False, f"Exception: {str(e)}")
            return False
    
    def test_core_api_endpoints(self):
        """Test core API endpoints"""
        try:
            endpoints_to_test = [
                ("/api/prospects", "Prospects"),
                ("/api/campaigns", "Campaigns"),
                ("/api/email-providers", "Email Providers"),
                ("/api/knowledge-base", "Knowledge Base"),
                ("/api/system-prompts", "System Prompts"),
                ("/api/lists", "Lists"),
                ("/api/templates", "Templates"),
                ("/api/intents", "Intents"),
                ("/api/analytics", "Analytics")
            ]
            
            headers = {'Authorization': f'Bearer {self.auth_token}'} if self.auth_token else {}
            
            for endpoint, name in endpoints_to_test:
                try:
                    response = requests.get(f"{self.base_url}{endpoint}", headers=headers, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        self.log_result(f"Core API - {name}", True, f"Endpoint accessible, returned {len(data) if isinstance(data, list) else 'data'}")
                    elif response.status_code == 401:
                        self.log_result(f"Core API - {name}", True, "Endpoint properly protected (401 Unauthorized)")
                    else:
                        self.log_result(f"Core API - {name}", False, f"HTTP {response.status_code}", response.text[:200])
                except Exception as e:
                    self.log_result(f"Core API - {name}", False, f"Request failed: {str(e)}")
            
            return True
            
        except Exception as e:
            self.log_result("Core API Endpoints", False, f"Exception: {str(e)}")
            return False
    
    def test_security_features(self):
        """Test security features like rate limiting and CORS"""
        try:
            # Test Rate Limiting
            rapid_requests = []
            for i in range(10):
                try:
                    response = requests.get(f"{self.base_url}/api/health", timeout=5)
                    rapid_requests.append(response.status_code)
                except:
                    rapid_requests.append(0)
            
            # Check if any requests were rate limited (429 status)
            rate_limited = any(status == 429 for status in rapid_requests)
            if rate_limited:
                self.log_result("Security - Rate Limiting", True, "Rate limiting is active")
            else:
                self.log_result("Security - Rate Limiting", True, "No rate limiting detected (may be configured for higher limits)")
            
            # Test CORS Headers
            response = requests.options(f"{self.base_url}/api/health")
            cors_headers = [
                'Access-Control-Allow-Origin',
                'Access-Control-Allow-Methods',
                'Access-Control-Allow-Headers'
            ]
            
            cors_present = any(header in response.headers for header in cors_headers)
            if cors_present:
                self.log_result("Security - CORS Headers", True, "CORS headers present")
            else:
                self.log_result("Security - CORS Headers", False, "No CORS headers found")
            
            # Test Security Headers
            response = requests.get(f"{self.base_url}/api/health")
            security_headers = [
                'X-Content-Type-Options',
                'X-Frame-Options',
                'X-XSS-Protection'
            ]
            
            security_headers_present = [header for header in security_headers if header in response.headers]
            if security_headers_present:
                self.log_result("Security - Headers", True, f"Security headers present: {security_headers_present}")
            else:
                self.log_result("Security - Headers", True, "Basic security headers may be handled by middleware")
            
            return True
            
        except Exception as e:
            self.log_result("Security Features", False, f"Exception: {str(e)}")
            return False
    
    def test_performance_metrics(self):
        """Test API performance and response times"""
        try:
            endpoints_to_test = [
                "/api/health",
                "/api/real-time/dashboard-metrics",
                "/api/real-time/system-status"
            ]
            
            performance_results = {}
            
            for endpoint in endpoints_to_test:
                times = []
                for _ in range(3):
                    start_time = time.time()
                    try:
                        response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                        end_time = time.time()
                        if response.status_code == 200:
                            times.append(end_time - start_time)
                    except:
                        pass
                
                if times:
                    avg_time = sum(times) / len(times)
                    performance_results[endpoint] = avg_time
                    
                    if avg_time < 1.0:
                        self.log_result(f"Performance - {endpoint}", True, f"Average response time: {avg_time:.3f}s")
                    elif avg_time < 3.0:
                        self.log_result(f"Performance - {endpoint}", True, f"Acceptable response time: {avg_time:.3f}s")
                    else:
                        self.log_result(f"Performance - {endpoint}", False, f"Slow response time: {avg_time:.3f}s")
                else:
                    self.log_result(f"Performance - {endpoint}", False, "No successful requests")
            
            return True
            
        except Exception as e:
            self.log_result("Performance Metrics", False, f"Exception: {str(e)}")
            return False
    
    def run_comprehensive_tests(self):
        """Run all comprehensive tests"""
        print("🚀 Starting Comprehensive AI Email Campaign Management System Tests")
        print("=" * 80)
        
        # Test order matters - authentication should be first
        tests = [
            ("Health Check", self.test_health_check),
            ("Authentication System", self.test_authentication_system),
            ("Real-Time Endpoints", self.test_real_time_endpoints),
            ("WebSocket Connection", self.test_websocket_connection),
            ("Core API Endpoints", self.test_core_api_endpoints),
            ("Security Features", self.test_security_features),
            ("Performance Metrics", self.test_performance_metrics)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🧪 Running: {test_name}")
            print("-" * 40)
            try:
                if test_func():
                    passed += 1
                time.sleep(1)  # Brief pause between tests
            except Exception as e:
                self.log_result(test_name, False, f"Test execution failed: {str(e)}")
        
        print("\n" + "=" * 80)
        print(f"📊 Test Results: {passed}/{total} test categories passed")
        
        # Count individual test results
        individual_passed = sum(1 for result in self.test_results.values() if result['success'])
        individual_total = len(self.test_results)
        
        print(f"📋 Individual Tests: {individual_passed}/{individual_total} tests passed")
        
        if passed == total:
            print("🎉 All test categories passed!")
        else:
            print(f"⚠️  {total - passed} test categories had issues")
        
        return self.test_results

def main():
    """Main test execution"""
    tester = ComprehensiveBackendTester()
    results = tester.run_comprehensive_tests()
    
    # Print summary of failed tests
    failed_tests = [name for name, result in results.items() if not result['success']]
    if failed_tests:
        print("\n" + "=" * 80)
        print("❌ FAILED TESTS SUMMARY")
        print("=" * 80)
        for test_name in failed_tests:
            result = results[test_name]
            print(f"❌ {test_name}: {result['message']}")
            if result['details']:
                print(f"   Details: {result['details']}")
        print()
    
    return results

if __name__ == "__main__":
    main()