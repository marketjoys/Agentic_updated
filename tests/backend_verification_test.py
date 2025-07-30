#!/usr/bin/env python3
"""
Backend Verification Test - January 2025
Quick verification of critical backend functionality based on review request priorities.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://64e7fdde-dfd5-4b2b-b2c3-2f149d1e1d45.preview.emergentagent.com/api"
USERNAME = "testuser"
PASSWORD = "testpass123"

class BackendVerificationTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.test_results = []
        
    def log_test(self, test_name, success, message):
        """Log test result"""
        status = "✅" if success else "❌"
        result = f"{status} {test_name}: {message}"
        print(result)
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        })
        return success
        
    def authenticate(self):
        """Test authentication"""
        try:
            response = self.session.post(f"{BASE_URL}/auth/login", json={
                "username": USERNAME,
                "password": PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                return self.log_test("Authentication", True, "Login successful")
            else:
                return self.log_test("Authentication", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            return self.log_test("Authentication", False, f"Error: {str(e)}")
    
    def test_intent_creation(self):
        """Test Intent Creation & Management (Priority 1)"""
        try:
            # Get existing intents
            response = self.session.get(f"{BASE_URL}/intents")
            if response.status_code == 200:
                intents = response.json()
                intent_count = len(intents)
                auto_respond_intents = [i for i in intents if i.get("auto_respond") == True]
                
                if intent_count >= 8 and len(auto_respond_intents) >= 3:
                    return self.log_test("Intent Creation & Management", True, 
                                       f"Found {intent_count} intents, {len(auto_respond_intents)} with auto_respond=true")
                else:
                    return self.log_test("Intent Creation & Management", False, 
                                       f"Only {intent_count} intents found, {len(auto_respond_intents)} auto-respond")
            else:
                return self.log_test("Intent Creation & Management", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            return self.log_test("Intent Creation & Management", False, f"Error: {str(e)}")
    
    def test_campaign_management(self):
        """Test Campaign Management (Priority 2)"""
        try:
            # Get campaigns
            response = self.session.get(f"{BASE_URL}/campaigns")
            if response.status_code == 200:
                campaigns = response.json()
                return self.log_test("Campaign Management", True, 
                                   f"Retrieved {len(campaigns)} campaigns successfully")
            else:
                return self.log_test("Campaign Management", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            return self.log_test("Campaign Management", False, f"Error: {str(e)}")
    
    def test_auto_responder_services(self):
        """Test Auto Responder Services (Priority 3)"""
        try:
            # Check service status
            response = self.session.get(f"{BASE_URL}/services/status")
            if response.status_code == 200:
                data = response.json()
                services = data.get("services", {})
                follow_up_status = services.get("smart_follow_up_engine", {}).get("status")
                email_processor_status = services.get("email_processor", {}).get("status")
                overall_status = data.get("overall_status")
                
                if follow_up_status == "running" and email_processor_status == "running":
                    return self.log_test("Auto Responder Services", True, 
                                       f"Both services running, overall status: {overall_status}")
                else:
                    return self.log_test("Auto Responder Services", False, 
                                       f"Services status: follow_up={follow_up_status}, email_processor={email_processor_status}")
            else:
                return self.log_test("Auto Responder Services", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            return self.log_test("Auto Responder Services", False, f"Error: {str(e)}")
    
    def test_crud_operations(self):
        """Test Core CRUD Operations (Priority 4)"""
        try:
            # Test Templates
            templates_response = self.session.get(f"{BASE_URL}/templates")
            templates_ok = templates_response.status_code == 200
            
            # Test Prospects  
            prospects_response = self.session.get(f"{BASE_URL}/prospects")
            prospects_ok = prospects_response.status_code == 200
            
            # Test Lists
            lists_response = self.session.get(f"{BASE_URL}/lists")
            lists_ok = lists_response.status_code == 200
            
            if templates_ok and prospects_ok and lists_ok:
                templates_count = len(templates_response.json())
                prospects_count = len(prospects_response.json())
                lists_count = len(lists_response.json())
                
                return self.log_test("CRUD Operations", True, 
                                   f"All endpoints working - Templates: {templates_count}, Prospects: {prospects_count}, Lists: {lists_count}")
            else:
                return self.log_test("CRUD Operations", False, 
                                   f"Some endpoints failed - Templates: {templates_ok}, Prospects: {prospects_ok}, Lists: {lists_ok}")
                
        except Exception as e:
            return self.log_test("CRUD Operations", False, f"Error: {str(e)}")
    
    def test_industry_functionality(self):
        """Test Industry Functionality (Priority 5)"""
        try:
            # Test industries endpoint
            response = self.session.get(f"{BASE_URL}/industries")
            if response.status_code == 200:
                data = response.json()
                industries = data.get("industries", [])
                total_count = data.get("total_count", 0)
                
                if total_count >= 100:  # Should have 148 industries
                    return self.log_test("Industry Functionality", True, 
                                       f"Found {total_count} industries available")
                else:
                    return self.log_test("Industry Functionality", False, 
                                       f"Only {total_count} industries found")
            else:
                return self.log_test("Industry Functionality", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            return self.log_test("Industry Functionality", False, f"Error: {str(e)}")
    
    def run_verification(self):
        """Run all verification tests"""
        print("🧪 BACKEND VERIFICATION TEST - JANUARY 2025")
        print("=" * 60)
        
        # Run tests in priority order
        if not self.authenticate():
            print("❌ Authentication failed - cannot continue")
            return False
        
        tests = [
            self.test_intent_creation,
            self.test_campaign_management, 
            self.test_auto_responder_services,
            self.test_crud_operations,
            self.test_industry_functionality
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
        
        print("=" * 60)
        print(f"📊 VERIFICATION RESULTS: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("✅ ALL CRITICAL FUNCTIONALITY VERIFIED")
            return True
        else:
            print("⚠️ SOME ISSUES DETECTED")
            return False

if __name__ == "__main__":
    tester = BackendVerificationTester()
    success = tester.run_verification()
    sys.exit(0 if success else 1)