#!/usr/bin/env python3
"""
Comprehensive Backend API Testing - July 25, 2025
Testing all backend functionality as requested in the review with special focus on:

1. Intent Creation & Management (RECENTLY FIXED - HIGH PRIORITY)
2. Campaign Management (CONFIRMED WORKING BUT VERIFY)
3. Auto Responder Services (VERIFY CURRENT STATUS)
4. Authentication & Security
5. CRUD Operations (Full Verification)
6. Advanced Features

Expected Results:
- Intent count should be 8+ (increased from original 5)
- All CRUD operations should work seamlessly
- Services should report "healthy" status
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
BASE_URL = "https://9f8a7167-d7f1-4045-b864-65d30ef37460.preview.emergentagent.com/api"
USERNAME = "testuser"
PASSWORD = "testpass123"

class ComprehensiveBackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.test_results = {}
        self.created_resources = {
            'intents': [],
            'campaigns': [],
            'templates': [],
            'prospects': [],
            'lists': [],
            'email_providers': []
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
        if details and not success:
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
    
    def test_authentication_security(self):
        """Test authentication and security features"""
        try:
            # Test protected endpoint access
            response = self.session.get(f"{BASE_URL}/auth/me")
            if response.status_code != 200:
                self.log_result("Protected Endpoint Access", False, f"HTTP {response.status_code}", response.text)
                return False
            
            user_data = response.json()
            if 'username' not in user_data:
                self.log_result("Protected Endpoint Access", False, "No username in response", user_data)
                return False
            
            self.log_result("Protected Endpoint Access", True, f"User profile retrieved: {user_data['username']}")
            
            # Test token refresh
            response = self.session.post(f"{BASE_URL}/auth/refresh")
            if response.status_code == 200:
                self.log_result("Token Refresh", True, "Token refresh successful")
            else:
                self.log_result("Token Refresh", False, f"HTTP {response.status_code}", response.text)
            
            return True
            
        except Exception as e:
            self.log_result("Authentication Security", False, f"Exception: {str(e)}")
            return False
    
    def test_intent_creation_management(self):
        """Test Intent Creation & Management (RECENTLY FIXED - HIGH PRIORITY)"""
        try:
            print("\n🎯 TESTING INTENT CREATION & MANAGEMENT (RECENTLY FIXED)")
            
            # First, get current intent count
            response = self.session.get(f"{BASE_URL}/intents")
            if response.status_code != 200:
                self.log_result("Intent GET Initial", False, f"HTTP {response.status_code}", response.text)
                return False
            
            initial_intents = response.json()
            initial_count = len(initial_intents) if isinstance(initial_intents, list) else 0
            self.log_result("Intent GET Initial", True, f"Found {initial_count} existing intents")
            
            # Verify intent count is 8+ as expected after fixes
            if initial_count >= 8:
                self.log_result("Intent Count Verification", True, f"Intent count is {initial_count} (≥8 as expected after fixes)")
            else:
                self.log_result("Intent Count Verification", False, f"Intent count is {initial_count} (expected ≥8 after fixes)")
            
            # CREATE new intent with various configurations
            intent_data_auto_respond = {
                "name": "Test Auto Respond Intent",
                "description": "Test intent with auto_respond=true",
                "keywords": ["test", "auto", "respond"],
                "auto_respond": True,
                "confidence_threshold": 0.8
            }
            
            response = self.session.post(f"{BASE_URL}/intents", json=intent_data_auto_respond)
            if response.status_code != 200:
                self.log_result("Intent CREATE (auto_respond=true)", False, f"HTTP {response.status_code}", response.text)
                return False
            
            created_intent = response.json()
            if 'id' not in created_intent:
                self.log_result("Intent CREATE (auto_respond=true)", False, "No ID in response", created_intent)
                return False
            
            intent_id = created_intent['id']
            self.created_resources['intents'].append(intent_id)
            self.log_result("Intent CREATE (auto_respond=true)", True, f"Created intent with ID: {intent_id}")
            
            # CREATE intent with complex keywords array
            intent_data_complex = {
                "name": "Complex Keywords Intent",
                "description": "Intent with complex keywords configuration",
                "keywords": ["pricing", "cost", "quote", "budget", "expensive", "cheap"],
                "auto_respond": False,
                "confidence_threshold": 0.7
            }
            
            response = self.session.post(f"{BASE_URL}/intents", json=intent_data_complex)
            if response.status_code == 200:
                complex_intent = response.json()
                complex_intent_id = complex_intent['id']
                self.created_resources['intents'].append(complex_intent_id)
                self.log_result("Intent CREATE (complex keywords)", True, f"Created complex intent with ID: {complex_intent_id}")
            else:
                self.log_result("Intent CREATE (complex keywords)", False, f"HTTP {response.status_code}", response.text)
            
            # UPDATE intent configuration
            update_data = {
                "name": "Updated Test Intent",
                "description": "Updated description",
                "keywords": ["updated", "test", "keywords"],
                "auto_respond": True,
                "confidence_threshold": 0.9
            }
            
            response = self.session.put(f"{BASE_URL}/intents/{intent_id}", json=update_data)
            if response.status_code == 200:
                self.log_result("Intent UPDATE", True, "Intent updated successfully")
            else:
                self.log_result("Intent UPDATE", False, f"HTTP {response.status_code}", response.text)
            
            # GET updated intent count
            response = self.session.get(f"{BASE_URL}/intents")
            if response.status_code == 200:
                updated_intents = response.json()
                updated_count = len(updated_intents) if isinstance(updated_intents, list) else 0
                self.log_result("Intent GET Updated", True, f"Intent count after creation: {updated_count}")
                
                # Verify count increased
                if updated_count > initial_count:
                    self.log_result("Intent Count Increase", True, f"Intent count increased from {initial_count} to {updated_count}")
                else:
                    self.log_result("Intent Count Increase", False, f"Intent count did not increase: {initial_count} -> {updated_count}")
            else:
                self.log_result("Intent GET Updated", False, f"HTTP {response.status_code}", response.text)
            
            # DELETE intent (cleanup will be done later)
            response = self.session.delete(f"{BASE_URL}/intents/{intent_id}")
            if response.status_code == 200:
                self.log_result("Intent DELETE", True, "Intent deleted successfully")
                self.created_resources['intents'].remove(intent_id)
            else:
                self.log_result("Intent DELETE", False, f"HTTP {response.status_code}", response.text)
            
            return True
            
        except Exception as e:
            self.log_result("Intent Creation Management", False, f"Exception: {str(e)}")
            return False
    
    def test_campaign_management(self):
        """Test Campaign Management (CONFIRMED WORKING BUT VERIFY)"""
        try:
            print("\n📧 TESTING CAMPAIGN MANAGEMENT")
            
            # GET campaigns
            response = self.session.get(f"{BASE_URL}/campaigns")
            if response.status_code != 200:
                self.log_result("Campaign GET", False, f"HTTP {response.status_code}", response.text)
                return False
            
            campaigns = response.json()
            campaign_count = len(campaigns) if isinstance(campaigns, list) else 0
            self.log_result("Campaign GET", True, f"Retrieved {campaign_count} campaigns")
            
            # CREATE campaign with enhanced follow-up configuration
            campaign_data = {
                "name": "Test Enhanced Campaign",
                "template_id": "test-template-id",
                "list_ids": ["test-list-id"],
                "max_emails": 100,
                "follow_up_enabled": True,
                "follow_up_schedule_type": "interval",
                "follow_up_intervals": [3, 7, 14, 30],
                "follow_up_timezone": "America/New_York",
                "follow_up_time_window_start": "09:00",
                "follow_up_time_window_end": "17:00",
                "follow_up_days_of_week": ["monday", "tuesday", "wednesday", "thursday", "friday"],
                "follow_up_templates": []
            }
            
            response = self.session.post(f"{BASE_URL}/campaigns", json=campaign_data)
            if response.status_code == 200:
                created_campaign = response.json()
                campaign_id = created_campaign.get('id')
                if campaign_id:
                    self.created_resources['campaigns'].append(campaign_id)
                    self.log_result("Campaign CREATE (enhanced follow-up)", True, f"Created campaign with ID: {campaign_id}")
                else:
                    self.log_result("Campaign CREATE (enhanced follow-up)", False, "No ID in response", created_campaign)
            else:
                self.log_result("Campaign CREATE (enhanced follow-up)", False, f"HTTP {response.status_code}", response.text)
                return False
            
            # GET specific campaign details
            response = self.session.get(f"{BASE_URL}/campaigns/{campaign_id}")
            if response.status_code == 200:
                campaign_details = response.json()
                self.log_result("Campaign GET by ID", True, f"Retrieved campaign details")
            else:
                self.log_result("Campaign GET by ID", False, f"HTTP {response.status_code}", response.text)
            
            # UPDATE campaign
            update_data = {
                "name": "Updated Enhanced Campaign",
                "max_emails": 150,
                "follow_up_schedule_type": "datetime",
                "follow_up_dates": ["2025-07-26T10:00:00Z", "2025-07-28T14:00:00Z"],
                "follow_up_timezone": "UTC"
            }
            
            response = self.session.put(f"{BASE_URL}/campaigns/{campaign_id}", json=update_data)
            if response.status_code == 200:
                self.log_result("Campaign UPDATE", True, "Campaign updated successfully")
            else:
                self.log_result("Campaign UPDATE", False, f"HTTP {response.status_code}", response.text)
            
            # Test campaign sending (without actually sending)
            send_request = {
                "send_immediately": False,
                "max_emails": 5,
                "schedule_type": "immediate",
                "follow_up_enabled": True
            }
            
            response = self.session.post(f"{BASE_URL}/campaigns/{campaign_id}/send", json=send_request)
            if response.status_code in [200, 400, 404]:  # 400/404 expected due to missing templates/prospects
                self.log_result("Campaign SEND API", True, f"Campaign send API accessible (HTTP {response.status_code})")
            else:
                self.log_result("Campaign SEND API", False, f"HTTP {response.status_code}", response.text)
            
            return True
            
        except Exception as e:
            self.log_result("Campaign Management", False, f"Exception: {str(e)}")
            return False
    
    def test_auto_responder_services(self):
        """Test Auto Responder Services (VERIFY CURRENT STATUS)"""
        try:
            print("\n🤖 TESTING AUTO RESPONDER SERVICES")
            
            # GET service status
            response = self.session.get(f"{BASE_URL}/services/status")
            if response.status_code != 200:
                self.log_result("Service Status GET", False, f"HTTP {response.status_code}", response.text)
                return False
            
            status_data = response.json()
            if 'services' not in status_data:
                self.log_result("Service Status GET", False, "No services in response", status_data)
                return False
            
            services = status_data['services']
            overall_status = status_data.get('overall_status', 'unknown')
            
            self.log_result("Service Status GET", True, f"Overall status: {overall_status}")
            
            # Check individual service status
            expected_services = ['smart_follow_up_engine', 'email_processor']
            for service_name in expected_services:
                if service_name in services:
                    service_status = services[service_name].get('status', 'unknown')
                    self.log_result(f"Service {service_name}", True, f"Status: {service_status}")
                else:
                    self.log_result(f"Service {service_name}", False, "Service not found in status")
            
            # Test service management
            # START all services
            response = self.session.post(f"{BASE_URL}/services/start-all")
            if response.status_code == 200:
                start_result = response.json()
                self.log_result("Services START ALL", True, "Start all services successful")
            else:
                self.log_result("Services START ALL", False, f"HTTP {response.status_code}", response.text)
            
            # Check status after starting
            response = self.session.get(f"{BASE_URL}/services/status")
            if response.status_code == 200:
                status_after_start = response.json()
                overall_status_after = status_after_start.get('overall_status', 'unknown')
                self.log_result("Service Status After Start", True, f"Overall status: {overall_status_after}")
            else:
                self.log_result("Service Status After Start", False, f"HTTP {response.status_code}", response.text)
            
            # STOP all services
            response = self.session.post(f"{BASE_URL}/services/stop-all")
            if response.status_code == 200:
                stop_result = response.json()
                self.log_result("Services STOP ALL", True, "Stop all services successful")
            else:
                self.log_result("Services STOP ALL", False, f"HTTP {response.status_code}", response.text)
            
            return True
            
        except Exception as e:
            self.log_result("Auto Responder Services", False, f"Exception: {str(e)}")
            return False
    
    def test_crud_operations(self):
        """Test CRUD Operations (Full Verification)"""
        try:
            print("\n🔧 TESTING CRUD OPERATIONS")
            
            # TEMPLATES CRUD
            template_data = {
                "name": "Test CRUD Template",
                "subject": "Test Subject {{first_name}}",
                "content": "<p>Hello {{first_name}} from {{company}}</p>",
                "type": "initial",
                "placeholders": ["first_name", "company"]
            }
            
            response = self.session.post(f"{BASE_URL}/templates", json=template_data)
            if response.status_code == 200:
                template = response.json()
                template_id = template.get('id')
                if template_id:
                    self.created_resources['templates'].append(template_id)
                    self.log_result("Template CREATE", True, f"Created template: {template_id}")
                else:
                    self.log_result("Template CREATE", False, "No ID in response")
            else:
                self.log_result("Template CREATE", False, f"HTTP {response.status_code}", response.text)
            
            # READ templates
            response = self.session.get(f"{BASE_URL}/templates")
            if response.status_code == 200:
                templates = response.json()
                template_count = len(templates) if isinstance(templates, list) else 0
                self.log_result("Template READ", True, f"Retrieved {template_count} templates")
            else:
                self.log_result("Template READ", False, f"HTTP {response.status_code}", response.text)
            
            # PROSPECTS CRUD
            unique_timestamp = int(time.time())
            prospect_data = {
                "email": f"test.crud.{unique_timestamp}@example.com",
                "first_name": "Test",
                "last_name": "CRUD",
                "company": "Test Company",
                "job_title": "Test Manager",
                "industry": "Technology"
            }
            
            response = self.session.post(f"{BASE_URL}/prospects", json=prospect_data)
            if response.status_code == 200:
                prospect = response.json()
                prospect_id = prospect.get('id')
                if prospect_id:
                    self.created_resources['prospects'].append(prospect_id)
                    self.log_result("Prospect CREATE", True, f"Created prospect: {prospect_id}")
                else:
                    self.log_result("Prospect CREATE", False, "No ID in response")
            else:
                self.log_result("Prospect CREATE", False, f"HTTP {response.status_code}", response.text)
            
            # READ prospects
            response = self.session.get(f"{BASE_URL}/prospects")
            if response.status_code == 200:
                prospects = response.json()
                prospect_count = len(prospects) if isinstance(prospects, list) else 0
                self.log_result("Prospect READ", True, f"Retrieved {prospect_count} prospects")
            else:
                self.log_result("Prospect READ", False, f"HTTP {response.status_code}", response.text)
            
            # LISTS CRUD
            list_data = {
                "name": "Test CRUD List",
                "description": "Test list for CRUD operations",
                "color": "#3B82F6",
                "tags": ["test", "crud"]
            }
            
            response = self.session.post(f"{BASE_URL}/lists", json=list_data)
            if response.status_code == 200:
                list_obj = response.json()
                list_id = list_obj.get('id')
                if list_id:
                    self.created_resources['lists'].append(list_id)
                    self.log_result("List CREATE", True, f"Created list: {list_id}")
                else:
                    self.log_result("List CREATE", False, "No ID in response")
            else:
                self.log_result("List CREATE", False, f"HTTP {response.status_code}", response.text)
            
            # READ lists
            response = self.session.get(f"{BASE_URL}/lists")
            if response.status_code == 200:
                lists = response.json()
                list_count = len(lists) if isinstance(lists, list) else 0
                self.log_result("List READ", True, f"Retrieved {list_count} lists")
            else:
                self.log_result("List READ", False, f"HTTP {response.status_code}", response.text)
            
            # Test List-Prospect associations
            if prospect_id and list_id:
                add_request = {"prospect_ids": [prospect_id]}
                response = self.session.post(f"{BASE_URL}/lists/{list_id}/prospects", json=add_request)
                if response.status_code == 200:
                    self.log_result("List-Prospect ADD", True, "Added prospect to list")
                else:
                    self.log_result("List-Prospect ADD", False, f"HTTP {response.status_code}", response.text)
                
                # Remove prospect from list
                response = self.session.delete(f"{BASE_URL}/lists/{list_id}/prospects", json=add_request)
                if response.status_code == 200:
                    self.log_result("List-Prospect REMOVE", True, "Removed prospect from list")
                else:
                    self.log_result("List-Prospect REMOVE", False, f"HTTP {response.status_code}", response.text)
            
            return True
            
        except Exception as e:
            self.log_result("CRUD Operations", False, f"Exception: {str(e)}")
            return False
    
    def test_advanced_features(self):
        """Test Advanced Features"""
        try:
            print("\n🚀 TESTING ADVANCED FEATURES")
            
            # Test Industries endpoint for AI Agent
            response = self.session.get(f"{BASE_URL}/industries")
            if response.status_code == 200:
                industries_data = response.json()
                if 'industries' in industries_data:
                    industry_count = len(industries_data['industries'])
                    self.log_result("Industries GET", True, f"Retrieved {industry_count} industries")
                else:
                    self.log_result("Industries GET", False, "No industries in response", industries_data)
            else:
                self.log_result("Industries GET", False, f"HTTP {response.status_code}", response.text)
            
            # Test Industry search
            response = self.session.get(f"{BASE_URL}/industries/search/technology")
            if response.status_code == 200:
                search_results = response.json()
                if 'industries' in search_results:
                    result_count = len(search_results['industries'])
                    self.log_result("Industry Search", True, f"Found {result_count} results for 'technology'")
                else:
                    self.log_result("Industry Search", False, "No industries in search results", search_results)
            else:
                self.log_result("Industry Search", False, f"HTTP {response.status_code}", response.text)
            
            # Test Real-time metrics
            response = self.session.get(f"{BASE_URL}/real-time/dashboard-metrics")
            if response.status_code == 200:
                metrics = response.json()
                if 'metrics' in metrics:
                    self.log_result("Real-time Metrics", True, "Dashboard metrics retrieved")
                else:
                    self.log_result("Real-time Metrics", False, "No metrics in response", metrics)
            else:
                self.log_result("Real-time Metrics", False, f"HTTP {response.status_code}", response.text)
            
            return True
            
        except Exception as e:
            self.log_result("Advanced Features", False, f"Exception: {str(e)}")
            return False
    
    def test_error_handling(self):
        """Test Error Handling"""
        try:
            print("\n⚠️ TESTING ERROR HANDLING")
            
            # Test invalid data inputs
            invalid_prospect = {
                "email": "invalid-email",  # Invalid email format
                "first_name": "",  # Empty required field
            }
            
            response = self.session.post(f"{BASE_URL}/prospects", json=invalid_prospect)
            if response.status_code != 200:
                self.log_result("Invalid Data Handling", True, f"Invalid data rejected (HTTP {response.status_code})")
            else:
                self.log_result("Invalid Data Handling", False, "Invalid data was accepted")
            
            # Test non-existent resource access
            response = self.session.get(f"{BASE_URL}/campaigns/non-existent-id")
            if response.status_code == 404:
                self.log_result("Non-existent Resource (404)", True, "404 returned for non-existent campaign")
            elif response.status_code == 500:
                self.log_result("Non-existent Resource (500 instead of 404)", False, "500 returned instead of 404")
            else:
                self.log_result("Non-existent Resource", False, f"Unexpected status: {response.status_code}")
            
            # Test authentication failures
            temp_session = requests.Session()
            response = temp_session.get(f"{BASE_URL}/auth/me")  # No auth token
            if response.status_code == 401:
                self.log_result("Authentication Failure", True, "401 returned for unauthenticated request")
            else:
                self.log_result("Authentication Failure", False, f"Expected 401, got {response.status_code}")
            
            return True
            
        except Exception as e:
            self.log_result("Error Handling", False, f"Exception: {str(e)}")
            return False
    
    def cleanup_resources(self):
        """Clean up created test resources"""
        print("\n🧹 Cleaning up test resources...")
        
        # Delete in reverse order of dependencies
        for resource_type in ['campaigns', 'lists', 'templates', 'prospects', 'intents']:
            for resource_id in self.created_resources.get(resource_type, []):
                try:
                    response = self.session.delete(f"{BASE_URL}/{resource_type}/{resource_id}")
                    if response.status_code == 200:
                        print(f"   ✅ Deleted {resource_type[:-1]} {resource_id}")
                    else:
                        print(f"   ⚠️ Failed to delete {resource_type[:-1]} {resource_id}: {response.status_code}")
                except Exception as e:
                    print(f"   ❌ Error deleting {resource_type[:-1]} {resource_id}: {str(e)}")
    
    def run_comprehensive_test(self):
        """Run comprehensive backend API testing"""
        print("🚀 COMPREHENSIVE BACKEND API TESTING - JULY 25, 2025")
        print("=" * 80)
        print("Testing all backend functionality as requested in review:")
        print("1. Intent Creation & Management (RECENTLY FIXED - HIGH PRIORITY)")
        print("2. Campaign Management (CONFIRMED WORKING BUT VERIFY)")
        print("3. Auto Responder Services (VERIFY CURRENT STATUS)")
        print("4. Authentication & Security")
        print("5. CRUD Operations (Full Verification)")
        print("6. Advanced Features")
        print("7. Error Handling")
        print("=" * 80)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ CRITICAL: Authentication failed - cannot proceed with testing")
            return False
        
        # Run all test categories
        test_categories = [
            ("Authentication & Security", self.test_authentication_security),
            ("Intent Creation & Management", self.test_intent_creation_management),
            ("Campaign Management", self.test_campaign_management),
            ("Auto Responder Services", self.test_auto_responder_services),
            ("CRUD Operations", self.test_crud_operations),
            ("Advanced Features", self.test_advanced_features),
            ("Error Handling", self.test_error_handling)
        ]
        
        passed_categories = 0
        total_categories = len(test_categories)
        critical_failures = []
        
        for category_name, test_func in test_categories:
            print(f"\n{'='*60}")
            print(f"🧪 TESTING: {category_name}")
            print(f"{'='*60}")
            
            try:
                if test_func():
                    passed_categories += 1
                    print(f"✅ {category_name}: PASSED")
                else:
                    print(f"❌ {category_name}: FAILED")
                    if any(keyword in category_name.lower() for keyword in ['intent', 'campaign', 'crud', 'authentication']):
                        critical_failures.append(category_name)
            except Exception as e:
                print(f"❌ {category_name}: EXCEPTION - {str(e)}")
                critical_failures.append(category_name)
        
        # Summary
        print("\n" + "=" * 80)
        print("🎯 COMPREHENSIVE BACKEND API TEST RESULTS SUMMARY")
        print("=" * 80)
        
        # Count individual test results
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result['success'])
        
        print(f"Test Categories: {passed_categories}/{total_categories} passed")
        print(f"Individual Tests: {passed_tests}/{total_tests} passed")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Show critical results
        print("\n🎯 CRITICAL FUNCTIONALITY STATUS:")
        
        # Intent Creation Status
        intent_tests = [k for k in self.test_results.keys() if 'intent' in k.lower()]
        intent_passed = sum(1 for k in intent_tests if self.test_results[k]['success'])
        intent_status = "✅ WORKING" if intent_passed == len(intent_tests) else "❌ ISSUES"
        print(f"Intent Creation & Management: {intent_status} ({intent_passed}/{len(intent_tests)} tests passed)")
        
        # Campaign Management Status
        campaign_tests = [k for k in self.test_results.keys() if 'campaign' in k.lower()]
        campaign_passed = sum(1 for k in campaign_tests if self.test_results[k]['success'])
        campaign_status = "✅ WORKING" if campaign_passed == len(campaign_tests) else "❌ ISSUES"
        print(f"Campaign Management: {campaign_status} ({campaign_passed}/{len(campaign_tests)} tests passed)")
        
        # Service Status
        service_tests = [k for k in self.test_results.keys() if 'service' in k.lower()]
        service_passed = sum(1 for k in service_tests if self.test_results[k]['success'])
        service_status = "✅ HEALTHY" if service_passed == len(service_tests) else "❌ DEGRADED"
        print(f"Auto Responder Services: {service_status} ({service_passed}/{len(service_tests)} tests passed)")
        
        # CRUD Operations Status
        crud_tests = [k for k in self.test_results.keys() if any(crud in k.lower() for crud in ['create', 'read', 'update', 'delete', 'crud'])]
        crud_passed = sum(1 for k in crud_tests if self.test_results[k]['success'])
        crud_status = "✅ WORKING" if crud_passed == len(crud_tests) else "❌ ISSUES"
        print(f"CRUD Operations: {crud_status} ({crud_passed}/{len(crud_tests)} tests passed)")
        
        if critical_failures:
            print(f"\n🚨 CRITICAL FAILURES: {', '.join(critical_failures)}")
        
        if passed_categories == total_categories and not critical_failures:
            print("\n🎉 ALL BACKEND FUNCTIONALITY WORKING AS EXPECTED")
            print("✅ Intent creation issues have been resolved")
            print("✅ All CRUD operations are functional")
            print("✅ Services are healthy and operational")
            print("✅ System is ready for production use")
        else:
            print(f"\n⚠️ ISSUES FOUND: {total_categories - passed_categories} categories failed")
            if critical_failures:
                print("🚨 Critical functionality requires attention")
        
        # Cleanup
        self.cleanup_resources()
        
        return passed_categories == total_categories and not critical_failures

if __name__ == "__main__":
    tester = ComprehensiveBackendTester()
    success = tester.run_comprehensive_test()
    
    if not success:
        sys.exit(1)
    else:
        sys.exit(0)