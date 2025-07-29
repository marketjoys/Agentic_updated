#!/usr/bin/env python3
"""
AI Email Responder - Backend Scheduling Task Handling System Testing
Testing Agent - January 2025

Comprehensive testing of backend scheduling task handling system focusing on:
1. Smart Follow-up Engine Testing
2. Campaign Scheduling Task Handling  
3. Email Processor Service Testing
4. Background Task Processing
5. Database Task Tracking
6. Service Integration Testing
7. API Endpoint Testing
"""

import asyncio
import aiohttp
import json
import sys
import os
from datetime import datetime, timedelta
import pytz
from typing import Dict, Any, List

# Configuration
BACKEND_URL = "https://5f33b0de-2474-4f94-a9e0-dac40fa9173f.preview.emergentagent.com/api"
LOGIN_CREDENTIALS = {"username": "testuser", "password": "testpass123"}

class SchedulingTaskTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_results = []
        self.created_campaigns = []
        self.created_providers = []
        
    async def setup_session(self):
        """Setup HTTP session and authenticate"""
        self.session = aiohttp.ClientSession()
        
        # Login to get auth token
        async with self.session.post(f"{BACKEND_URL}/auth/login", json=LOGIN_CREDENTIALS) as response:
            if response.status == 200:
                data = await response.json()
                self.auth_token = data.get("access_token")
                print("✅ Authentication successful")
                return True
            else:
                print(f"❌ Authentication failed: {response.status}")
                return False
    
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    def get_headers(self):
        """Get headers with auth token"""
        return {"Authorization": f"Bearer {self.auth_token}"}
    
    async def test_smart_follow_up_engine_status(self):
        """Test 1: Smart Follow-up Engine Testing - Check if the service is running"""
        print("\n🔍 TEST 1: Smart Follow-up Engine Status")
        
        try:
            # Check services status
            async with self.session.get(f"{BACKEND_URL}/services/status", headers=self.get_headers()) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Services status retrieved")
                    
                    # Check smart_follow_up_engine
                    services = data.get("services", {})
                    follow_up_engine = services.get("smart_follow_up_engine", {})
                    
                    engine_status = follow_up_engine.get('status')
                    print(f"✅ Smart Follow-up Engine Status: {engine_status}")
                    print(f"✅ Engine Description: {follow_up_engine.get('description')}")
                    
                    if engine_status == 'running':
                        self.test_results.append({"test": "Smart Follow-up Engine Status", "status": "PASS", "details": "Engine is running"})
                    elif engine_status == 'stopped':
                        self.test_results.append({"test": "Smart Follow-up Engine Status", "status": "FAIL", "details": "Engine is stopped"})
                    else:
                        self.test_results.append({"test": "Smart Follow-up Engine Status", "status": "FAIL", "details": f"Unknown status: {engine_status}"})
                        
                else:
                    error_text = await response.text()
                    print(f"❌ Services status check failed: {response.status} - {error_text}")
                    self.test_results.append({"test": "Smart Follow-up Engine Status", "status": "FAIL", "details": f"HTTP {response.status}: {error_text}"})
                    
        except Exception as e:
            print(f"❌ Smart follow-up engine status test failed: {str(e)}")
            self.test_results.append({"test": "Smart Follow-up Engine Status", "status": "FAIL", "details": str(e)})
    
    async def test_email_processor_service(self):
        """Test 2: Email Processor Service Testing - Check if IMAP monitoring is working"""
        print("\n🔍 TEST 2: Email Processor Service Testing")
        
        try:
            # Check services status
            async with self.session.get(f"{BACKEND_URL}/services/status", headers=self.get_headers()) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    services = data.get("services", {})
                    email_processor = services.get("email_processor", {})
                    
                    processor_status = email_processor.get('status')
                    monitored_providers = email_processor.get("monitored_providers", [])
                    monitored_count = email_processor.get("monitored_providers_count", 0)
                    
                    print(f"✅ Email Processor Status: {processor_status}")
                    print(f"✅ Monitored Providers Count: {monitored_count}")
                    print(f"✅ Processor Description: {email_processor.get('description')}")
                    
                    for provider in monitored_providers:
                        print(f"  - {provider.get('name')} ({provider.get('provider_type')})")
                        print(f"    Last Scan: {provider.get('last_scan', 'Never')}")
                        print(f"    IMAP Host: {provider.get('imap_host', 'N/A')}")
                    
                    if processor_status == 'running':
                        self.test_results.append({"test": "Email Processor Service", "status": "PASS", "details": f"Service running with {monitored_count} providers"})
                    else:
                        self.test_results.append({"test": "Email Processor Service", "status": "FAIL", "details": f"Service status: {processor_status}"})
                        
                else:
                    error_text = await response.text()
                    print(f"❌ Email processor status check failed: {response.status} - {error_text}")
                    self.test_results.append({"test": "Email Processor Service", "status": "FAIL", "details": f"HTTP {response.status}: {error_text}"})
                    
        except Exception as e:
            print(f"❌ Email processor service test failed: {str(e)}")
            self.test_results.append({"test": "Email Processor Service", "status": "FAIL", "details": str(e)})
    
    async def test_service_control_endpoints(self):
        """Test 3: Service Control Endpoints - Test start-all and stop-all endpoints"""
        print("\n🔍 TEST 3: Service Control Endpoints")
        
        try:
            # Test stop-all endpoint
            print("\n🛑 Testing stop-all endpoint")
            async with self.session.post(f"{BACKEND_URL}/services/stop-all", headers=self.get_headers()) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Stop-all response: {data.get('message')}")
                    results = data.get('results', {})
                    print(f"✅ Follow-up engine: {results.get('smart_follow_up_engine', {}).get('status')}")
                    print(f"✅ Email processor: {results.get('email_processor', {}).get('status')}")
                    
                    # Wait a moment for services to stop
                    await asyncio.sleep(2)
                    
                    # Test start-all endpoint
                    print("\n🚀 Testing start-all endpoint")
                    async with self.session.post(f"{BACKEND_URL}/services/start-all", headers=self.get_headers()) as start_response:
                        if start_response.status == 200:
                            start_data = await start_response.json()
                            print(f"✅ Start-all response: {start_data.get('message')}")
                            start_results = start_data.get('results', {})
                            print(f"✅ Follow-up engine: {start_results.get('smart_follow_up_engine', {}).get('status')}")
                            print(f"✅ Email processor: {start_results.get('email_processor', {}).get('status')}")
                            
                            self.test_results.append({"test": "Service Control Endpoints", "status": "PASS", "details": "Both stop-all and start-all work"})
                        else:
                            error_text = await start_response.text()
                            print(f"❌ Start-all failed: {start_response.status} - {error_text}")
                            self.test_results.append({"test": "Service Control Endpoints", "status": "FAIL", "details": f"Start-all failed: {start_response.status}"})
                else:
                    error_text = await response.text()
                    print(f"❌ Stop-all failed: {response.status} - {error_text}")
                    self.test_results.append({"test": "Service Control Endpoints", "status": "FAIL", "details": f"Stop-all failed: {response.status}"})
                    
        except Exception as e:
            print(f"❌ Service control endpoints test failed: {str(e)}")
            self.test_results.append({"test": "Service Control Endpoints", "status": "FAIL", "details": str(e)})
    
    async def test_campaign_scheduling_creation(self):
        """Test 4: Campaign Scheduling Task Handling - Test creating scheduled campaigns"""
        print("\n🔍 TEST 4: Campaign Scheduling Task Handling")
        
        # First get available templates and lists
        templates = await self.get_templates()
        lists = await self.get_lists()
        
        if not templates or not lists:
            print("❌ Need templates and lists for campaign testing")
            self.test_results.append({"test": "Campaign Scheduling Creation", "status": "FAIL", "details": "Missing templates or lists"})
            return
        
        template_id = templates[0]["id"]
        list_id = lists[0]["id"]
        
        # Test creating a scheduled campaign
        print("\n📅 Testing Scheduled Campaign Creation")
        try:
            future_time = datetime.utcnow() + timedelta(hours=2)
            scheduled_campaign = {
                "name": "Test Scheduled Campaign - Backend Test",
                "template_id": template_id,
                "list_ids": [list_id],
                "max_emails": 100,
                "schedule": future_time.isoformat() + "Z",
                "follow_up_enabled": True,
                "follow_up_schedule_type": "interval",
                "follow_up_intervals": [3, 7, 14],
                "follow_up_timezone": "UTC",
                "follow_up_time_window_start": "09:00",
                "follow_up_time_window_end": "17:00",
                "follow_up_days_of_week": ["monday", "tuesday", "wednesday", "thursday", "friday"]
            }
            
            async with self.session.post(f"{BACKEND_URL}/campaigns", 
                                       json=scheduled_campaign, 
                                       headers=self.get_headers()) as response:
                if response.status == 200:
                    data = await response.json()
                    campaign_id = data.get('id')
                    self.created_campaigns.append(campaign_id)
                    
                    print(f"✅ Scheduled campaign created: {campaign_id}")
                    print(f"✅ Campaign name: {data.get('name')}")
                    print(f"✅ Follow-up enabled: {data.get('follow_up_enabled')}")
                    print(f"✅ Schedule type: {data.get('follow_up_schedule_type')}")
                    
                    # Verify campaign was stored with scheduling data
                    async with self.session.get(f"{BACKEND_URL}/campaigns/{campaign_id}", 
                                               headers=self.get_headers()) as detail_response:
                        if detail_response.status == 200:
                            detail_data = await detail_response.json()
                            stored_schedule = detail_data.get('schedule')
                            stored_follow_up = detail_data.get('follow_up_enabled')
                            
                            print(f"✅ Stored schedule: {stored_schedule}")
                            print(f"✅ Stored follow-up enabled: {stored_follow_up}")
                            
                            if stored_schedule and stored_follow_up:
                                self.test_results.append({"test": "Campaign Scheduling Creation", "status": "PASS", "details": f"Campaign {campaign_id} created with scheduling"})
                            else:
                                self.test_results.append({"test": "Campaign Scheduling Creation", "status": "FAIL", "details": "Campaign created but scheduling data missing"})
                        else:
                            self.test_results.append({"test": "Campaign Scheduling Creation", "status": "PARTIAL", "details": "Campaign created but couldn't verify details"})
                else:
                    error_text = await response.text()
                    print(f"❌ Scheduled campaign creation failed: {response.status} - {error_text}")
                    self.test_results.append({"test": "Campaign Scheduling Creation", "status": "FAIL", "details": f"HTTP {response.status}: {error_text}"})
                    
        except Exception as e:
            print(f"❌ Campaign scheduling test failed: {str(e)}")
            self.test_results.append({"test": "Campaign Scheduling Creation", "status": "FAIL", "details": str(e)})
    
    async def test_follow_up_scheduling_types(self):
        """Test 5: Follow-up Scheduling Types - Test interval vs datetime modes"""
        print("\n🔍 TEST 5: Follow-up Scheduling Types")
        
        templates = await self.get_templates()
        lists = await self.get_lists()
        
        if not templates or not lists:
            print("❌ Need templates and lists for follow-up testing")
            self.test_results.append({"test": "Follow-up Scheduling Types", "status": "FAIL", "details": "Missing templates or lists"})
            return
        
        template_id = templates[0]["id"]
        list_id = lists[0]["id"]
        
        # Test datetime mode follow-up scheduling
        print("\n📅 Testing Datetime Mode Follow-up Scheduling")
        try:
            now = datetime.utcnow()
            follow_up_dates = [
                (now + timedelta(days=1)).isoformat() + "Z",
                (now + timedelta(days=3)).isoformat() + "Z", 
                (now + timedelta(days=7)).isoformat() + "Z"
            ]
            
            datetime_campaign = {
                "name": "Test Datetime Follow-up Campaign - Backend Test",
                "template_id": template_id,
                "list_ids": [list_id],
                "max_emails": 50,
                "follow_up_enabled": True,
                "follow_up_schedule_type": "datetime",
                "follow_up_dates": follow_up_dates,
                "follow_up_timezone": "America/New_York",
                "follow_up_time_window_start": "10:00",
                "follow_up_time_window_end": "16:00"
            }
            
            async with self.session.post(f"{BACKEND_URL}/campaigns", 
                                       json=datetime_campaign, 
                                       headers=self.get_headers()) as response:
                if response.status == 200:
                    data = await response.json()
                    campaign_id = data.get('id')
                    self.created_campaigns.append(campaign_id)
                    
                    print(f"✅ Datetime follow-up campaign created: {campaign_id}")
                    print(f"✅ Schedule type: {data.get('follow_up_schedule_type')}")
                    print(f"✅ Follow-up dates: {data.get('follow_up_dates')}")
                    print(f"✅ Timezone: {data.get('follow_up_timezone')}")
                    
                    self.test_results.append({"test": "Follow-up Scheduling Types", "status": "PASS", "details": f"Datetime mode campaign {campaign_id} created"})
                else:
                    error_text = await response.text()
                    print(f"❌ Datetime follow-up campaign failed: {response.status} - {error_text}")
                    self.test_results.append({"test": "Follow-up Scheduling Types", "status": "FAIL", "details": f"HTTP {response.status}: {error_text}"})
                    
        except Exception as e:
            print(f"❌ Follow-up scheduling types test failed: {str(e)}")
            self.test_results.append({"test": "Follow-up Scheduling Types", "status": "FAIL", "details": str(e)})
    
    async def test_database_task_tracking(self):
        """Test 6: Database Task Tracking - Check how campaigns are stored in MongoDB"""
        print("\n🔍 TEST 6: Database Task Tracking")
        
        try:
            # Get all campaigns to check database storage
            async with self.session.get(f"{BACKEND_URL}/campaigns", headers=self.get_headers()) as response:
                if response.status == 200:
                    campaigns = await response.json()
                    print(f"✅ Retrieved {len(campaigns)} campaigns from database")
                    
                    # Check if our created campaigns are stored properly
                    scheduled_campaigns = []
                    follow_up_campaigns = []
                    
                    for campaign in campaigns:
                        if campaign.get('schedule'):
                            scheduled_campaigns.append(campaign)
                        if campaign.get('follow_up_enabled'):
                            follow_up_campaigns.append(campaign)
                    
                    print(f"✅ Campaigns with scheduling: {len(scheduled_campaigns)}")
                    print(f"✅ Campaigns with follow-up: {len(follow_up_campaigns)}")
                    
                    # Check specific campaign details
                    if self.created_campaigns:
                        test_campaign_id = self.created_campaigns[0]
                        async with self.session.get(f"{BACKEND_URL}/campaigns/{test_campaign_id}", 
                                                   headers=self.get_headers()) as detail_response:
                            if detail_response.status == 200:
                                detail_data = await detail_response.json()
                                
                                # Check required scheduling fields
                                required_fields = ['id', 'name', 'follow_up_enabled', 'follow_up_schedule_type', 
                                                 'follow_up_timezone', 'follow_up_time_window_start', 'follow_up_time_window_end']
                                
                                missing_fields = []
                                for field in required_fields:
                                    if field not in detail_data:
                                        missing_fields.append(field)
                                
                                if not missing_fields:
                                    print(f"✅ Campaign {test_campaign_id} has all required scheduling fields")
                                    self.test_results.append({"test": "Database Task Tracking", "status": "PASS", "details": "Campaigns stored with proper scheduling data"})
                                else:
                                    print(f"❌ Campaign {test_campaign_id} missing fields: {missing_fields}")
                                    self.test_results.append({"test": "Database Task Tracking", "status": "FAIL", "details": f"Missing fields: {missing_fields}"})
                            else:
                                self.test_results.append({"test": "Database Task Tracking", "status": "FAIL", "details": "Could not retrieve campaign details"})
                    else:
                        self.test_results.append({"test": "Database Task Tracking", "status": "PARTIAL", "details": "No test campaigns created to verify"})
                        
                else:
                    error_text = await response.text()
                    print(f"❌ Failed to retrieve campaigns: {response.status} - {error_text}")
                    self.test_results.append({"test": "Database Task Tracking", "status": "FAIL", "details": f"HTTP {response.status}: {error_text}"})
                    
        except Exception as e:
            print(f"❌ Database task tracking test failed: {str(e)}")
            self.test_results.append({"test": "Database Task Tracking", "status": "FAIL", "details": str(e)})
    
    async def test_background_task_processing(self):
        """Test 7: Background Task Processing - Test if scheduled tasks are being processed"""
        print("\n🔍 TEST 7: Background Task Processing")
        
        try:
            # Check if services are running (prerequisite for background processing)
            async with self.session.get(f"{BACKEND_URL}/services/status", headers=self.get_headers()) as response:
                if response.status == 200:
                    data = await response.json()
                    services = data.get("services", {})
                    
                    follow_up_engine = services.get("smart_follow_up_engine", {})
                    email_processor = services.get("email_processor", {})
                    
                    follow_up_running = follow_up_engine.get('status') == 'running'
                    processor_running = email_processor.get('status') == 'running'
                    
                    print(f"✅ Follow-up engine running: {follow_up_running}")
                    print(f"✅ Email processor running: {processor_running}")
                    
                    if follow_up_running and processor_running:
                        # Check for any recent email activity (sign of background processing)
                        async with self.session.get(f"{BACKEND_URL}/real-time/dashboard-metrics", 
                                                   headers=self.get_headers()) as metrics_response:
                            if metrics_response.status == 200:
                                metrics_data = await metrics_response.json()
                                metrics = metrics_data.get('metrics', {})
                                overview = metrics.get('overview', {})
                                
                                total_emails = overview.get('total_emails_sent', 0)
                                emails_today = overview.get('emails_today', 0)
                                
                                print(f"✅ Total emails sent: {total_emails}")
                                print(f"✅ Emails sent today: {emails_today}")
                                
                                # Check recent activity
                                recent_activity = metrics.get('recent_activity', [])
                                print(f"✅ Recent activity entries: {len(recent_activity)}")
                                
                                if total_emails > 0 or len(recent_activity) > 0:
                                    self.test_results.append({"test": "Background Task Processing", "status": "PASS", "details": f"Services running, {total_emails} emails processed"})
                                else:
                                    self.test_results.append({"test": "Background Task Processing", "status": "PARTIAL", "details": "Services running but no email activity detected"})
                            else:
                                self.test_results.append({"test": "Background Task Processing", "status": "PARTIAL", "details": "Services running but couldn't check metrics"})
                    else:
                        self.test_results.append({"test": "Background Task Processing", "status": "FAIL", "details": f"Services not running - Follow-up: {follow_up_running}, Processor: {processor_running}"})
                        
                else:
                    error_text = await response.text()
                    print(f"❌ Failed to check services status: {response.status} - {error_text}")
                    self.test_results.append({"test": "Background Task Processing", "status": "FAIL", "details": f"HTTP {response.status}: {error_text}"})
                    
        except Exception as e:
            print(f"❌ Background task processing test failed: {str(e)}")
            self.test_results.append({"test": "Background Task Processing", "status": "FAIL", "details": str(e)})
    
    async def test_api_endpoints_comprehensive(self):
        """Test 8: API Endpoint Testing - Test all scheduling-related endpoints"""
        print("\n🔍 TEST 8: Comprehensive API Endpoint Testing")
        
        endpoints_to_test = [
            {"method": "GET", "endpoint": "/health", "description": "Health check"},
            {"method": "GET", "endpoint": "/services/status", "description": "Services status"},
            {"method": "GET", "endpoint": "/campaigns", "description": "Get campaigns"},
            {"method": "GET", "endpoint": "/templates", "description": "Get templates"},
            {"method": "GET", "endpoint": "/lists", "description": "Get lists"},
            {"method": "GET", "endpoint": "/email-providers", "description": "Get email providers"},
            {"method": "GET", "endpoint": "/real-time/dashboard-metrics", "description": "Dashboard metrics"}
        ]
        
        endpoint_results = []
        
        for endpoint_test in endpoints_to_test:
            try:
                method = endpoint_test["method"]
                endpoint = endpoint_test["endpoint"]
                description = endpoint_test["description"]
                
                print(f"\n🔗 Testing {method} {endpoint} - {description}")
                
                if method == "GET":
                    async with self.session.get(f"{BACKEND_URL}{endpoint}", headers=self.get_headers()) as response:
                        if response.status == 200:
                            data = await response.json()
                            print(f"✅ {endpoint} - Status: {response.status}")
                            endpoint_results.append({"endpoint": endpoint, "status": "PASS", "http_status": response.status})
                        else:
                            error_text = await response.text()
                            print(f"❌ {endpoint} - Status: {response.status} - {error_text[:100]}")
                            endpoint_results.append({"endpoint": endpoint, "status": "FAIL", "http_status": response.status})
                            
            except Exception as e:
                print(f"❌ {endpoint_test['endpoint']} test failed: {str(e)}")
                endpoint_results.append({"endpoint": endpoint_test['endpoint'], "status": "FAIL", "error": str(e)})
        
        # Summary of endpoint tests
        passed_endpoints = len([r for r in endpoint_results if r["status"] == "PASS"])
        total_endpoints = len(endpoint_results)
        
        print(f"\n📊 API Endpoint Test Summary: {passed_endpoints}/{total_endpoints} passed")
        
        if passed_endpoints == total_endpoints:
            self.test_results.append({"test": "API Endpoint Testing", "status": "PASS", "details": f"All {total_endpoints} endpoints working"})
        elif passed_endpoints > total_endpoints / 2:
            self.test_results.append({"test": "API Endpoint Testing", "status": "PARTIAL", "details": f"{passed_endpoints}/{total_endpoints} endpoints working"})
        else:
            self.test_results.append({"test": "API Endpoint Testing", "status": "FAIL", "details": f"Only {passed_endpoints}/{total_endpoints} endpoints working"})
    
    async def cleanup_test_data(self):
        """Cleanup test data created during testing"""
        print("\n🧹 Cleaning up test data...")
        
        # Delete created campaigns
        for campaign_id in self.created_campaigns:
            try:
                async with self.session.delete(f"{BACKEND_URL}/campaigns/{campaign_id}", 
                                             headers=self.get_headers()) as response:
                    if response.status == 200:
                        print(f"✅ Deleted campaign: {campaign_id}")
                    else:
                        print(f"⚠️ Failed to delete campaign: {campaign_id}")
            except Exception as e:
                print(f"⚠️ Error deleting campaign {campaign_id}: {str(e)}")
        
        # Delete created email providers
        for provider_id in self.created_providers:
            try:
                async with self.session.delete(f"{BACKEND_URL}/email-providers/{provider_id}", 
                                             headers=self.get_headers()) as response:
                    if response.status == 200:
                        print(f"✅ Deleted email provider: {provider_id}")
                    else:
                        print(f"⚠️ Failed to delete email provider: {provider_id}")
            except Exception as e:
                print(f"⚠️ Error deleting email provider {provider_id}: {str(e)}")
    
    async def get_templates(self):
        """Helper: Get available templates"""
        try:
            async with self.session.get(f"{BACKEND_URL}/templates", headers=self.get_headers()) as response:
                if response.status == 200:
                    templates = await response.json()
                    print(f"✅ Found {len(templates)} templates")
                    return templates
                else:
                    print(f"❌ Failed to get templates: {response.status}")
                    return []
        except Exception as e:
            print(f"❌ Error getting templates: {str(e)}")
            return []
    
    async def get_lists(self):
        """Helper: Get available lists"""
        try:
            async with self.session.get(f"{BACKEND_URL}/lists", headers=self.get_headers()) as response:
                if response.status == 200:
                    lists = await response.json()
                    print(f"✅ Found {len(lists)} lists")
                    return lists
                else:
                    print(f"❌ Failed to get lists: {response.status}")
                    return []
        except Exception as e:
            print(f"❌ Error getting lists: {str(e)}")
            return []
    
    def print_summary(self):
        """Print comprehensive test results summary"""
        print("\n" + "="*80)
        print("🎯 BACKEND SCHEDULING TASK HANDLING SYSTEM TEST SUMMARY")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAIL"])
        partial_tests = len([r for r in self.test_results if r["status"] == "PARTIAL"])
        
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️ Partial: {partial_tests}")
        
        if total_tests > 0:
            success_rate = (passed_tests / total_tests) * 100
            print(f"📈 Success Rate: {success_rate:.1f}%")
        
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status_icon = {"PASS": "✅", "FAIL": "❌", "PARTIAL": "⚠️"}.get(result["status"], "❓")
            print(f"{status_icon} {result['test']}: {result['status']} - {result['details']}")
        
        print("\n" + "="*80)
        
        # Determine overall assessment
        critical_tests = [
            "Smart Follow-up Engine Status",
            "Email Processor Service", 
            "Campaign Scheduling Creation",
            "Database Task Tracking"
        ]
        
        critical_failures = []
        for result in self.test_results:
            if result["test"] in critical_tests and result["status"] == "FAIL":
                critical_failures.append(result["test"])
        
        if not critical_failures and failed_tests == 0:
            print("🎉 OVERALL ASSESSMENT: BACKEND SCHEDULING SYSTEM IS FULLY FUNCTIONAL")
        elif critical_failures:
            print(f"🚨 OVERALL ASSESSMENT: CRITICAL SCHEDULING ISSUES FOUND")
            print(f"🚨 Critical failures: {', '.join(critical_failures)}")
        elif failed_tests > passed_tests:
            print("⚠️ OVERALL ASSESSMENT: MAJOR SCHEDULING ISSUES - SYSTEM PARTIALLY WORKING")
        else:
            print("⚠️ OVERALL ASSESSMENT: MINOR SCHEDULING ISSUES - SYSTEM MOSTLY WORKING")
        
        print("="*80)

async def main():
    """Main test execution"""
    print("🚀 AI Email Responder - Backend Scheduling Task Handling System Testing")
    print("Testing Agent - January 2025")
    print("Comprehensive testing of backend scheduling task handling system")
    print("="*80)
    
    tester = SchedulingTaskTester()
    
    try:
        # Setup
        if not await tester.setup_session():
            print("❌ Failed to setup session. Exiting.")
            return
        
        # Run all comprehensive tests
        await tester.test_smart_follow_up_engine_status()
        await tester.test_email_processor_service()
        await tester.test_service_control_endpoints()
        await tester.test_campaign_scheduling_creation()
        await tester.test_follow_up_scheduling_types()
        await tester.test_database_task_tracking()
        await tester.test_background_task_processing()
        await tester.test_api_endpoints_comprehensive()
        
        # Cleanup test data
        await tester.cleanup_test_data()
        
        # Print summary
        tester.print_summary()
        
    except Exception as e:
        print(f"❌ Test execution failed: {str(e)}")
    finally:
        await tester.cleanup_session()

if __name__ == "__main__":
    asyncio.run(main())