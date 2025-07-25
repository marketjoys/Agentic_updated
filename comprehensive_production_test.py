#!/usr/bin/env python3
"""
COMPREHENSIVE BACKEND API TESTING - JANUARY 2025
Production Readiness Verification for AI Email Responder

Testing all endpoints and functionality as specified in the review request:
1. Authentication System
2. Campaign Management Endpoints  
3. Prospect Management Endpoints
4. Template Management Endpoints
5. List Management Endpoints
6. Email Provider Management
7. Intents & AI Functionality
8. Analytics Endpoints
9. Integration Testing
"""

import requests
import json
import io
from datetime import datetime
import time
import os

# Backend URL from environment
BACKEND_URL = "https://1a57e556-e465-4823-8ddc-9b0a2b804cbb.preview.emergentagent.com"
AUTH_TOKEN = None

class ComprehensiveBackendTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.auth_token = None
        self.headers = {}
        self.test_results = {}
        self.created_resources = {
            'prospects': [],
            'templates': [],
            'lists': [],
            'campaigns': [],
            'email_providers': []
        }
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_result(self, test_name, success, message="", details=None):
        """Log test results"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            
        self.test_results[test_name] = {
            'success': success,
            'message': message,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if details and not success:  # Only show details for failures
            print(f"   Details: {details}")
    
    def make_request(self, method, endpoint, data=None, params=None):
        """Make HTTP request with error handling"""
        try:
            url = f"{self.base_url}{endpoint}"
            
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers, params=params, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, headers=self.headers, json=data, timeout=30)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=self.headers, json=data, timeout=30)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=self.headers, timeout=30)
            else:
                return None, f"Unsupported method: {method}"
            
            return response, None
        except requests.exceptions.RequestException as e:
            return None, str(e)
    
    def test_authentication_system(self):
        """Test all authentication endpoints"""
        print("\n🔐 TESTING AUTHENTICATION SYSTEM")
        
        # Test 1: Login with valid credentials
        login_data = {"username": "testuser", "password": "testpass123"}
        response, error = self.make_request("POST", "/api/auth/login", login_data)
        
        if error:
            self.log_result("Authentication - Login", False, f"Request failed: {error}")
            return False
        
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                self.auth_token = data["access_token"]
                self.headers = {"Authorization": f"Bearer {self.auth_token}"}
                self.log_result("Authentication - Login", True, "Login successful with testuser/testpass123")
            else:
                self.log_result("Authentication - Login", False, "No access token in response")
                return False
        else:
            self.log_result("Authentication - Login", False, f"Login failed with status {response.status_code}")
            return False
        
        # Test 2: Get user profile (protected endpoint)
        response, error = self.make_request("GET", "/api/auth/me")
        if error:
            self.log_result("Authentication - Get Profile", False, f"Request failed: {error}")
        elif response.status_code == 200:
            data = response.json()
            if "username" in data:
                self.log_result("Authentication - Get Profile", True, f"Profile retrieved for user: {data['username']}")
            else:
                self.log_result("Authentication - Get Profile", False, "Invalid profile response")
        else:
            self.log_result("Authentication - Get Profile", False, f"Failed with status {response.status_code}")
        
        # Test 3: Token refresh
        response, error = self.make_request("POST", "/api/auth/refresh")
        if error:
            self.log_result("Authentication - Token Refresh", False, f"Request failed: {error}")
        elif response.status_code == 200:
            self.log_result("Authentication - Token Refresh", True, "Token refresh successful")
        else:
            self.log_result("Authentication - Token Refresh", False, f"Failed with status {response.status_code}")
        
        # Test 4: Register new user
        register_data = {"username": "newuser", "password": "newpass123"}
        response, error = self.make_request("POST", "/api/auth/register", register_data)
        if error:
            self.log_result("Authentication - Register", False, f"Request failed: {error}")
        elif response.status_code == 200:
            self.log_result("Authentication - Register", True, "User registration successful")
        else:
            self.log_result("Authentication - Register", False, f"Failed with status {response.status_code}")
        
        # Test 5: Logout
        response, error = self.make_request("POST", "/api/auth/logout")
        if error:
            self.log_result("Authentication - Logout", False, f"Request failed: {error}")
        elif response.status_code == 200:
            self.log_result("Authentication - Logout", True, "Logout successful")
        else:
            self.log_result("Authentication - Logout", False, f"Failed with status {response.status_code}")
        
        return True
    
    def test_campaign_management(self):
        """Test campaign management endpoints"""
        print("\n📧 TESTING CAMPAIGN MANAGEMENT")
        
        # Test 1: Get all campaigns
        response, error = self.make_request("GET", "/api/campaigns")
        if error:
            self.log_result("Campaigns - Get All", False, f"Request failed: {error}")
            return
        
        if response.status_code == 200:
            campaigns = response.json()
            self.log_result("Campaigns - Get All", True, f"Retrieved {len(campaigns)} campaigns")
            
            # Test campaign sending if campaigns exist
            if campaigns:
                for campaign in campaigns[:1]:  # Test first campaign only
                    if campaign.get("status") == "draft":
                        self.test_campaign_sending(campaign["id"])
                        break
        else:
            self.log_result("Campaigns - Get All", False, f"Failed with status {response.status_code}")
        
        # Test 2: Create new campaign
        campaign_data = {
            "name": "Production Test Campaign",
            "template_id": "test_template_id",
            "list_ids": ["test_list_id"],
            "max_emails": 100,
            "schedule": None
        }
        
        response, error = self.make_request("POST", "/api/campaigns", campaign_data)
        if error:
            self.log_result("Campaigns - Create", False, f"Request failed: {error}")
        elif response.status_code == 200:
            data = response.json()
            if "id" in data:
                campaign_id = data["id"]
                self.created_resources['campaigns'].append(campaign_id)
                self.log_result("Campaigns - Create", True, f"Campaign created with ID: {campaign_id}")
                
                # Test 3: Update campaign
                update_data = {"name": "Updated Production Test Campaign", "max_emails": 200}
                response, error = self.make_request("PUT", f"/api/campaigns/{campaign_id}", update_data)
                if error:
                    self.log_result("Campaigns - Update", False, f"Request failed: {error}")
                elif response.status_code == 200:
                    self.log_result("Campaigns - Update", True, "Campaign updated successfully")
                else:
                    self.log_result("Campaigns - Update", False, f"Failed with status {response.status_code}")
                
                # Test 4: Get campaign status
                response, error = self.make_request("GET", f"/api/campaigns/{campaign_id}/status")
                if error:
                    self.log_result("Campaigns - Get Status", False, f"Request failed: {error}")
                elif response.status_code == 200:
                    self.log_result("Campaigns - Get Status", True, "Campaign status retrieved")
                else:
                    self.log_result("Campaigns - Get Status", False, f"Failed with status {response.status_code}")
            else:
                self.log_result("Campaigns - Create", False, "No campaign ID in response")
        else:
            self.log_result("Campaigns - Create", False, f"Failed with status {response.status_code}")
    
    def test_campaign_sending(self, campaign_id):
        """Test campaign sending functionality"""
        send_data = {
            "send_immediately": True,
            "email_provider_id": "",
            "max_emails": 5,
            "schedule_type": "immediate"
        }
        
        response, error = self.make_request("POST", f"/api/campaigns/{campaign_id}/send", send_data)
        if error:
            self.log_result("Campaigns - Send", False, f"Request failed: {error}")
        elif response.status_code == 200:
            data = response.json()
            self.log_result("Campaigns - Send", True, f"Campaign sent: {data.get('total_sent', 0)} emails sent, {data.get('total_failed', 0)} failed")
        else:
            self.log_result("Campaigns - Send", False, f"Failed with status {response.status_code}")
    
    def test_prospect_management(self):
        """Test prospect management endpoints"""
        print("\n👥 TESTING PROSPECT MANAGEMENT")
        
        # Test 1: Get all prospects
        response, error = self.make_request("GET", "/api/prospects")
        if error:
            self.log_result("Prospects - Get All", False, f"Request failed: {error}")
        elif response.status_code == 200:
            prospects = response.json()
            self.log_result("Prospects - Get All", True, f"Retrieved {len(prospects)} prospects")
        else:
            self.log_result("Prospects - Get All", False, f"Failed with status {response.status_code}")
        
        # Test 2: Create new prospect
        prospect_data = {
            "email": "test.prospect@example.com",
            "first_name": "Test",
            "last_name": "Prospect",
            "company": "Test Company Inc",
            "job_title": "Marketing Manager",
            "industry": "Technology"
        }
        
        response, error = self.make_request("POST", "/api/prospects", prospect_data)
        if error:
            self.log_result("Prospects - Create", False, f"Request failed: {error}")
        elif response.status_code == 200:
            data = response.json()
            if "id" in data:
                prospect_id = data["id"]
                self.created_resources['prospects'].append(prospect_id)
                self.log_result("Prospects - Create", True, f"Prospect created: {data.get('email')}")
                
                # Test 3: Update prospect
                update_data = {"job_title": "Senior Marketing Manager", "company": "Updated Test Company"}
                response, error = self.make_request("PUT", f"/api/prospects/{prospect_id}", update_data)
                if error:
                    self.log_result("Prospects - Update", False, f"Request failed: {error}")
                elif response.status_code == 200:
                    self.log_result("Prospects - Update", True, "Prospect updated successfully")
                else:
                    self.log_result("Prospects - Update", False, f"Failed with status {response.status_code}")
            else:
                self.log_result("Prospects - Create", False, "No prospect ID in response")
        else:
            self.log_result("Prospects - Create", False, f"Failed with status {response.status_code}")
        
        # Test 4: CSV Upload
        csv_content = """email,first_name,last_name,company,job_title,industry
csv.test@example.com,CSV,Test,CSV Company,Developer,Technology"""
        
        response, error = self.make_request("POST", "/api/prospects/upload", params={"file_content": csv_content})
        if error:
            self.log_result("Prospects - CSV Upload", False, f"Request failed: {error}")
        elif response.status_code == 200:
            data = response.json()
            self.log_result("Prospects - CSV Upload", True, f"CSV uploaded: {data.get('prospects_added', 0)} prospects added")
        else:
            self.log_result("Prospects - CSV Upload", False, f"Failed with status {response.status_code}")
    
    def test_template_management(self):
        """Test template management endpoints"""
        print("\n📝 TESTING TEMPLATE MANAGEMENT")
        
        # Test 1: Get all templates
        response, error = self.make_request("GET", "/api/templates")
        if error:
            self.log_result("Templates - Get All", False, f"Request failed: {error}")
        elif response.status_code == 200:
            templates = response.json()
            self.log_result("Templates - Get All", True, f"Retrieved {len(templates)} templates")
        else:
            self.log_result("Templates - Get All", False, f"Failed with status {response.status_code}")
        
        # Test 2: Create new template
        template_data = {
            "name": "Production Test Template",
            "subject": "Welcome {{first_name}} from {{company}}!",
            "content": "<p>Hello {{first_name}},</p><p>Welcome to our platform! We're excited to work with {{company}}.</p>",
            "type": "initial"
        }
        
        response, error = self.make_request("POST", "/api/templates", template_data)
        if error:
            self.log_result("Templates - Create", False, f"Request failed: {error}")
        elif response.status_code == 200:
            data = response.json()
            if "id" in data:
                template_id = data["id"]
                self.created_resources['templates'].append(template_id)
                self.log_result("Templates - Create", True, f"Template created: {data.get('name')}")
                
                # Test 3: Update template
                update_data = {"name": "Updated Production Test Template", "subject": "Updated: Welcome {{first_name}}!"}
                response, error = self.make_request("PUT", f"/api/templates/{template_id}", update_data)
                if error:
                    self.log_result("Templates - Update", False, f"Request failed: {error}")
                elif response.status_code == 200:
                    self.log_result("Templates - Update", True, "Template updated successfully")
                else:
                    self.log_result("Templates - Update", False, f"Failed with status {response.status_code}")
            else:
                self.log_result("Templates - Create", False, "No template ID in response")
        else:
            self.log_result("Templates - Create", False, f"Failed with status {response.status_code}")
    
    def test_list_management(self):
        """Test list management endpoints"""
        print("\n📋 TESTING LIST MANAGEMENT")
        
        # Test 1: Get all lists
        response, error = self.make_request("GET", "/api/lists")
        if error:
            self.log_result("Lists - Get All", False, f"Request failed: {error}")
            return
        
        if response.status_code == 200:
            lists = response.json()
            self.log_result("Lists - Get All", True, f"Retrieved {len(lists)} lists")
            
            # Test list details and prospect operations if lists exist
            if lists:
                list_id = lists[0]["id"]
                self.test_list_operations(list_id)
        else:
            self.log_result("Lists - Get All", False, f"Failed with status {response.status_code}")
        
        # Test 2: Create new list
        list_data = {
            "name": "Production Test List",
            "description": "Test list for production verification",
            "color": "#3B82F6",
            "tags": ["test", "production"]
        }
        
        response, error = self.make_request("POST", "/api/lists", list_data)
        if error:
            self.log_result("Lists - Create", False, f"Request failed: {error}")
        elif response.status_code == 200:
            data = response.json()
            if "id" in data:
                list_id = data["id"]
                self.created_resources['lists'].append(list_id)
                self.log_result("Lists - Create", True, f"List created: {data.get('name')}")
                
                # Test 3: Update list
                update_data = {"name": "Updated Production Test List", "description": "Updated description"}
                response, error = self.make_request("PUT", f"/api/lists/{list_id}", update_data)
                if error:
                    self.log_result("Lists - Update", False, f"Request failed: {error}")
                elif response.status_code == 200:
                    self.log_result("Lists - Update", True, "List updated successfully")
                else:
                    self.log_result("Lists - Update", False, f"Failed with status {response.status_code}")
                
                # Test 4: Get specific list
                response, error = self.make_request("GET", f"/api/lists/{list_id}")
                if error:
                    self.log_result("Lists - Get Specific", False, f"Request failed: {error}")
                elif response.status_code == 200:
                    self.log_result("Lists - Get Specific", True, "List details retrieved")
                else:
                    self.log_result("Lists - Get Specific", False, f"Failed with status {response.status_code}")
            else:
                self.log_result("Lists - Create", False, "No list ID in response")
        else:
            self.log_result("Lists - Create", False, f"Failed with status {response.status_code}")
    
    def test_list_operations(self, list_id):
        """Test list prospect operations"""
        # Test: Get list prospects
        response, error = self.make_request("GET", f"/api/lists/{list_id}/prospects")
        if error:
            self.log_result("Lists - Get Prospects", False, f"Request failed: {error}")
        elif response.status_code == 200:
            data = response.json()
            self.log_result("Lists - Get Prospects", True, f"Retrieved {data.get('total_count', 0)} prospects from list")
        else:
            self.log_result("Lists - Get Prospects", False, f"Failed with status {response.status_code}")
        
        # Test: Add prospects to list (if we have created prospects)
        if self.created_resources['prospects']:
            add_data = {"prospect_ids": self.created_resources['prospects'][:1]}
            response, error = self.make_request("POST", f"/api/lists/{list_id}/prospects", add_data)
            if error:
                self.log_result("Lists - Add Prospects", False, f"Request failed: {error}")
            elif response.status_code == 200:
                self.log_result("Lists - Add Prospects", True, "Prospects added to list successfully")
                
                # Test: Remove prospects from list
                response, error = self.make_request("DELETE", f"/api/lists/{list_id}/prospects", add_data)
                if error:
                    self.log_result("Lists - Remove Prospects", False, f"Request failed: {error}")
                elif response.status_code == 200:
                    self.log_result("Lists - Remove Prospects", True, "Prospects removed from list successfully")
                else:
                    self.log_result("Lists - Remove Prospects", False, f"Failed with status {response.status_code}")
            else:
                self.log_result("Lists - Add Prospects", False, f"Failed with status {response.status_code}")
    
    def test_email_providers(self):
        """Test email provider management"""
        print("\n📮 TESTING EMAIL PROVIDER MANAGEMENT")
        
        # Test 1: Get all email providers
        response, error = self.make_request("GET", "/api/email-providers")
        if error:
            self.log_result("Email Providers - Get All", False, f"Request failed: {error}")
        elif response.status_code == 200:
            providers = response.json()
            self.log_result("Email Providers - Get All", True, f"Retrieved {len(providers)} email providers")
        else:
            self.log_result("Email Providers - Get All", False, f"Failed with status {response.status_code}")
        
        # Test 2: Create new email provider
        provider_data = {
            "name": "Test Gmail Provider",
            "provider_type": "gmail",
            "email_address": "test@gmail.com",
            "display_name": "Test Provider",
            "smtp_host": "smtp.gmail.com",
            "smtp_port": 587,
            "smtp_username": "test@gmail.com",
            "smtp_password": "test_password",
            "daily_send_limit": 500,
            "hourly_send_limit": 50,
            "skip_connection_test": True
        }
        
        response, error = self.make_request("POST", "/api/email-providers", provider_data)
        if error:
            self.log_result("Email Providers - Create", False, f"Request failed: {error}")
        elif response.status_code == 200:
            data = response.json()
            if "id" in data:
                provider_id = data["id"]
                self.created_resources['email_providers'].append(provider_id)
                self.log_result("Email Providers - Create", True, f"Email provider created: {data.get('name')}")
                
                # Test 3: Update email provider
                update_data = {"name": "Updated Test Gmail Provider", "daily_send_limit": 1000}
                response, error = self.make_request("PUT", f"/api/email-providers/{provider_id}", update_data)
                if error:
                    self.log_result("Email Providers - Update", False, f"Request failed: {error}")
                elif response.status_code == 200:
                    self.log_result("Email Providers - Update", True, "Email provider updated successfully")
                else:
                    self.log_result("Email Providers - Update", False, f"Failed with status {response.status_code}")
                
                # Test 4: Test connection
                response, error = self.make_request("POST", f"/api/email-providers/{provider_id}/test")
                if error:
                    self.log_result("Email Providers - Test Connection", False, f"Request failed: {error}")
                elif response.status_code == 200:
                    self.log_result("Email Providers - Test Connection", True, "Connection test successful")
                else:
                    self.log_result("Email Providers - Test Connection", False, f"Failed with status {response.status_code}")
                
                # Test 5: Set as default
                response, error = self.make_request("POST", f"/api/email-providers/{provider_id}/set-default")
                if error:
                    self.log_result("Email Providers - Set Default", False, f"Request failed: {error}")
                elif response.status_code == 200:
                    self.log_result("Email Providers - Set Default", True, "Provider set as default successfully")
                else:
                    self.log_result("Email Providers - Set Default", False, f"Failed with status {response.status_code}")
            else:
                self.log_result("Email Providers - Create", False, "No provider ID in response")
        else:
            self.log_result("Email Providers - Create", False, f"Failed with status {response.status_code}")
    
    def test_intents_and_ai(self):
        """Test intents and AI functionality"""
        print("\n🤖 TESTING INTENTS & AI FUNCTIONALITY")
        
        # Test 1: Get all intents
        response, error = self.make_request("GET", "/api/intents")
        if error:
            self.log_result("Intents - Get All", False, f"Request failed: {error}")
        elif response.status_code == 200:
            intents = response.json()
            self.log_result("Intents - Get All", True, f"Retrieved {len(intents)} intents")
        else:
            self.log_result("Intents - Get All", False, f"Failed with status {response.status_code}")
        
        # Test 2: AI Agent capabilities (if available)
        response, error = self.make_request("GET", "/api/ai-agent/capabilities")
        if error:
            self.log_result("AI Agent - Capabilities", False, f"Request failed: {error}")
        elif response.status_code == 200:
            data = response.json()
            self.log_result("AI Agent - Capabilities", True, f"AI Agent capabilities retrieved: {len(data.get('capabilities', []))} categories")
        else:
            self.log_result("AI Agent - Capabilities", False, f"Failed with status {response.status_code}")
        
        # Test 3: AI Agent help
        response, error = self.make_request("GET", "/api/ai-agent/help")
        if error:
            self.log_result("AI Agent - Help", False, f"Request failed: {error}")
        elif response.status_code == 200:
            self.log_result("AI Agent - Help", True, "AI Agent help retrieved successfully")
        else:
            self.log_result("AI Agent - Help", False, f"Failed with status {response.status_code}")
        
        # Test 4: AI Agent chat
        chat_data = {"message": "Show me all my campaigns"}
        response, error = self.make_request("POST", "/api/ai-agent/chat", chat_data)
        if error:
            self.log_result("AI Agent - Chat", False, f"Request failed: {error}")
        elif response.status_code == 200:
            data = response.json()
            self.log_result("AI Agent - Chat", True, f"AI Agent responded: {data.get('response', '')[:50]}...")
        else:
            self.log_result("AI Agent - Chat", False, f"Failed with status {response.status_code}")
    
    def test_analytics(self):
        """Test analytics endpoints"""
        print("\n📊 TESTING ANALYTICS")
        
        # Test 1: Overall analytics
        response, error = self.make_request("GET", "/api/analytics")
        if error:
            self.log_result("Analytics - Overall", False, f"Request failed: {error}")
        elif response.status_code == 200:
            data = response.json()
            self.log_result("Analytics - Overall", True, f"Analytics retrieved: {data.get('total_campaigns', 0)} campaigns, {data.get('total_prospects', 0)} prospects")
        else:
            self.log_result("Analytics - Overall", False, f"Failed with status {response.status_code}")
        
        # Test 2: Real-time dashboard metrics
        response, error = self.make_request("GET", "/api/real-time/dashboard-metrics")
        if error:
            self.log_result("Analytics - Real-time Metrics", False, f"Request failed: {error}")
        elif response.status_code == 200:
            data = response.json()
            metrics = data.get('metrics', {}).get('overview', {})
            self.log_result("Analytics - Real-time Metrics", True, f"Real-time metrics: {metrics.get('total_prospects', 0)} prospects, {metrics.get('emails_today', 0)} emails today")
        else:
            self.log_result("Analytics - Real-time Metrics", False, f"Failed with status {response.status_code}")
        
        # Test 3: Campaign analytics (if we have campaigns)
        if self.created_resources['campaigns']:
            campaign_id = self.created_resources['campaigns'][0]
            response, error = self.make_request("GET", f"/api/analytics/campaign/{campaign_id}")
            if error:
                self.log_result("Analytics - Campaign Specific", False, f"Request failed: {error}")
            elif response.status_code == 200:
                data = response.json()
                self.log_result("Analytics - Campaign Specific", True, f"Campaign analytics: {data.get('total_sent', 0)} sent, {data.get('open_rate', 0)}% open rate")
            else:
                self.log_result("Analytics - Campaign Specific", False, f"Failed with status {response.status_code}")
    
    def cleanup_resources(self):
        """Clean up created test resources"""
        print("\n🧹 CLEANING UP TEST RESOURCES")
        
        # Delete created campaigns
        for campaign_id in self.created_resources['campaigns']:
            response, error = self.make_request("DELETE", f"/api/campaigns/{campaign_id}")
            if response and response.status_code == 200:
                print(f"✅ Deleted campaign: {campaign_id}")
        
        # Delete created templates
        for template_id in self.created_resources['templates']:
            response, error = self.make_request("DELETE", f"/api/templates/{template_id}")
            if response and response.status_code == 200:
                print(f"✅ Deleted template: {template_id}")
        
        # Delete created prospects
        for prospect_id in self.created_resources['prospects']:
            response, error = self.make_request("DELETE", f"/api/prospects/{prospect_id}")
            if response and response.status_code == 200:
                print(f"✅ Deleted prospect: {prospect_id}")
        
        # Delete created lists
        for list_id in self.created_resources['lists']:
            response, error = self.make_request("DELETE", f"/api/lists/{list_id}")
            if response and response.status_code == 200:
                print(f"✅ Deleted list: {list_id}")
        
        # Delete created email providers
        for provider_id in self.created_resources['email_providers']:
            response, error = self.make_request("DELETE", f"/api/email-providers/{provider_id}")
            if response and response.status_code == 200:
                print(f"✅ Deleted email provider: {provider_id}")
    
    def run_comprehensive_test(self):
        """Run all comprehensive tests"""
        print("🚀 STARTING COMPREHENSIVE BACKEND API TESTING")
        print("=" * 60)
        
        start_time = datetime.now()
        
        # Run all test categories
        if not self.test_authentication_system():
            print("❌ Authentication failed - stopping tests")
            return
        
        self.test_campaign_management()
        self.test_prospect_management()
        self.test_template_management()
        self.test_list_management()
        self.test_email_providers()
        self.test_intents_and_ai()
        self.test_analytics()
        
        # Cleanup
        self.cleanup_resources()
        
        # Final results
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print("\n" + "=" * 60)
        print("🎯 COMPREHENSIVE TEST RESULTS SUMMARY")
        print("=" * 60)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"📊 Total Tests: {self.total_tests}")
        print(f"✅ Passed: {self.passed_tests}")
        print(f"❌ Failed: {self.total_tests - self.passed_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print(f"⏱️  Duration: {duration:.1f} seconds")
        
        # Categorize results
        critical_failures = []
        minor_issues = []
        
        for test_name, result in self.test_results.items():
            if not result['success']:
                if any(keyword in test_name.lower() for keyword in ['login', 'auth', 'send', 'create']):
                    critical_failures.append(test_name)
                else:
                    minor_issues.append(test_name)
        
        if critical_failures:
            print(f"\n🚨 CRITICAL FAILURES ({len(critical_failures)}):")
            for failure in critical_failures:
                print(f"   ❌ {failure}: {self.test_results[failure]['message']}")
        
        if minor_issues:
            print(f"\n⚠️  MINOR ISSUES ({len(minor_issues)}):")
            for issue in minor_issues:
                print(f"   ⚠️  {issue}: {self.test_results[issue]['message']}")
        
        if success_rate >= 90:
            print(f"\n🎉 EXCELLENT: Backend is production-ready with {success_rate:.1f}% success rate!")
        elif success_rate >= 80:
            print(f"\n✅ GOOD: Backend is mostly functional with {success_rate:.1f}% success rate")
        elif success_rate >= 70:
            print(f"\n⚠️  FAIR: Backend has some issues with {success_rate:.1f}% success rate")
        else:
            print(f"\n❌ POOR: Backend needs significant work with {success_rate:.1f}% success rate")
        
        return success_rate >= 80

if __name__ == "__main__":
    tester = ComprehensiveBackendTester()
    tester.run_comprehensive_test()