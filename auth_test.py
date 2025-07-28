#!/usr/bin/env python3
"""
Authentication Testing for AI Email Responder
Tests user registration, login, and authentication flows
"""

import requests
import json
from datetime import datetime
import time

# Get backend URL from frontend .env file
BACKEND_URL = "https://6aa35d2d-1224-4abb-b5c1-ebe60774a6f1.preview.emergentagent.com"

class AuthTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.test_results = {}
        self.tokens = {}
    
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
    
    def test_user_registration(self):
        """Test user registration"""
        try:
            # Create unique test user
            timestamp = int(time.time())
            test_user = {
                "username": f"testuser_{timestamp}",
                "email": f"test_{timestamp}@example.com",
                "password": "testpassword123",
                "full_name": "Test User"
            }
            
            response = requests.post(f"{self.base_url}/api/auth/register", json=test_user)
            
            if response.status_code != 200:
                self.log_result("User Registration", False, f"HTTP {response.status_code}", response.text)
                return False
            
            result = response.json()
            if 'access_token' not in result:
                self.log_result("User Registration", False, "No access token in response", result)
                return False
            
            # Store token for later tests
            self.tokens['new_user'] = result['access_token']
            self.test_user = test_user
            
            self.log_result("User Registration", True, f"Successfully registered user: {test_user['username']}")
            return True
            
        except Exception as e:
            self.log_result("User Registration", False, f"Exception: {str(e)}")
            return False
    
    def test_user_login(self):
        """Test user login with existing credentials"""
        try:
            # Test with the user we just created
            if not hasattr(self, 'test_user'):
                self.log_result("User Login", False, "No test user available from registration")
                return False
            
            login_data = {
                "username": self.test_user['username'],
                "password": self.test_user['password']
            }
            
            response = requests.post(f"{self.base_url}/api/auth/login", json=login_data)
            
            if response.status_code != 200:
                self.log_result("User Login", False, f"HTTP {response.status_code}", response.text)
                return False
            
            result = response.json()
            if 'access_token' not in result:
                self.log_result("User Login", False, "No access token in response", result)
                return False
            
            # Store token for later tests
            self.tokens['login'] = result['access_token']
            
            self.log_result("User Login", True, f"Successfully logged in user: {self.test_user['username']}")
            return True
            
        except Exception as e:
            self.log_result("User Login", False, f"Exception: {str(e)}")
            return False
    
    def test_existing_user_login(self):
        """Test login with provided test credentials"""
        test_credentials = [
            {"username": "testuser", "password": "testpassword123"},
            {"username": "admin", "password": "admin123"},
            {"username": "demo", "password": "demo123"}
        ]
        
        for creds in test_credentials:
            try:
                response = requests.post(f"{self.base_url}/api/auth/login", json=creds)
                
                if response.status_code == 200:
                    result = response.json()
                    if 'access_token' in result:
                        self.tokens[creds['username']] = result['access_token']
                        self.log_result(f"Existing User Login ({creds['username']})", True, 
                                      f"Successfully logged in: {creds['username']}")
                        return True
                else:
                    self.log_result(f"Existing User Login ({creds['username']})", False, 
                                  f"HTTP {response.status_code}", response.text)
            except Exception as e:
                self.log_result(f"Existing User Login ({creds['username']})", False, f"Exception: {str(e)}")
        
        return False
    
    def test_get_current_user(self):
        """Test getting current user information"""
        try:
            # Use any available token
            token = None
            for key, value in self.tokens.items():
                token = value
                break
            
            if not token:
                self.log_result("Get Current User", False, "No authentication token available")
                return False
            
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{self.base_url}/api/auth/me", headers=headers)
            
            if response.status_code != 200:
                self.log_result("Get Current User", False, f"HTTP {response.status_code}", response.text)
                return False
            
            result = response.json()
            required_fields = ['username', 'email', 'is_active', 'created_at']
            
            for field in required_fields:
                if field not in result:
                    self.log_result("Get Current User", False, f"Missing field: {field}", result)
                    return False
            
            self.log_result("Get Current User", True, f"Retrieved user info for: {result['username']}")
            return True
            
        except Exception as e:
            self.log_result("Get Current User", False, f"Exception: {str(e)}")
            return False
    
    def test_token_refresh(self):
        """Test token refresh functionality"""
        try:
            # Use any available token
            token = None
            for key, value in self.tokens.items():
                token = value
                break
            
            if not token:
                self.log_result("Token Refresh", False, "No authentication token available")
                return False
            
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.post(f"{self.base_url}/api/auth/refresh", headers=headers)
            
            if response.status_code != 200:
                self.log_result("Token Refresh", False, f"HTTP {response.status_code}", response.text)
                return False
            
            result = response.json()
            if 'access_token' not in result:
                self.log_result("Token Refresh", False, "No access token in response", result)
                return False
            
            self.log_result("Token Refresh", True, "Successfully refreshed token")
            return True
            
        except Exception as e:
            self.log_result("Token Refresh", False, f"Exception: {str(e)}")
            return False
    
    def test_logout(self):
        """Test logout functionality"""
        try:
            # Use any available token
            token = None
            for key, value in self.tokens.items():
                token = value
                break
            
            if not token:
                self.log_result("Logout", False, "No authentication token available")
                return False
            
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.post(f"{self.base_url}/api/auth/logout", headers=headers)
            
            if response.status_code != 200:
                self.log_result("Logout", False, f"HTTP {response.status_code}", response.text)
                return False
            
            result = response.json()
            if 'message' not in result:
                self.log_result("Logout", False, "No message in response", result)
                return False
            
            self.log_result("Logout", True, "Successfully logged out")
            return True
            
        except Exception as e:
            self.log_result("Logout", False, f"Exception: {str(e)}")
            return False
    
    def test_invalid_credentials(self):
        """Test login with invalid credentials"""
        try:
            invalid_creds = {
                "username": "nonexistent_user",
                "password": "wrong_password"
            }
            
            response = requests.post(f"{self.base_url}/api/auth/login", json=invalid_creds)
            
            # Should return 401 for invalid credentials
            if response.status_code == 401:
                self.log_result("Invalid Credentials Test", True, "Correctly rejected invalid credentials")
                return True
            else:
                self.log_result("Invalid Credentials Test", False, 
                              f"Expected HTTP 401, got {response.status_code}", response.text)
                return False
            
        except Exception as e:
            self.log_result("Invalid Credentials Test", False, f"Exception: {str(e)}")
            return False
    
    def run_auth_tests(self):
        """Run all authentication tests"""
        print("🔐 Starting Authentication Tests")
        print("=" * 50)
        
        tests = [
            ("User Registration", self.test_user_registration),
            ("User Login", self.test_user_login),
            ("Existing User Login", self.test_existing_user_login),
            ("Get Current User", self.test_get_current_user),
            ("Token Refresh", self.test_token_refresh),
            ("Logout", self.test_logout),
            ("Invalid Credentials", self.test_invalid_credentials)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🧪 Running: {test_name}")
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                self.log_result(test_name, False, f"Test execution failed: {str(e)}")
        
        print("\n" + "=" * 50)
        print(f"📊 Authentication Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All authentication tests passed!")
        else:
            print(f"⚠️  {total - passed} authentication tests failed")
        
        return self.test_results

def main():
    """Main test execution"""
    tester = AuthTester()
    results = tester.run_auth_tests()
    
    # Print detailed results
    print("\n" + "=" * 50)
    print("📋 DETAILED AUTHENTICATION TEST RESULTS")
    print("=" * 50)
    
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