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
BACKEND_URL = "https://bc0f5eb1-9f0c-4a91-a56f-4141def510e7.preview.emergentagent.com/api"
LOGIN_CREDENTIALS = {"username": "testuser", "password": "testpass123"}

class SchedulingTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_results = []
        
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
    
    async def test_system_timezone(self):
        """Test 1: Current System Timezone - What timezone is the backend server running in?"""
        print("\n🔍 TEST 1: Current System Timezone")
        
        try:
            # Check health endpoint for server time
            async with self.session.get(f"{BACKEND_URL}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    server_time = data.get("timestamp")
                    print(f"✅ Server timestamp: {server_time}")
                    
                    # Parse and check timezone
                    if server_time:
                        dt = datetime.fromisoformat(server_time.replace('Z', '+00:00'))
                        print(f"✅ Parsed datetime: {dt}")
                        print(f"✅ Timezone info: {dt.tzinfo}")
                        
                        # Check if it's UTC (as expected for container)
                        if dt.tzinfo is None or str(dt.tzinfo) == 'UTC' or dt.tzinfo.utcoffset(None).total_seconds() == 0:
                            print("✅ Backend server is running in UTC timezone (expected for container)")
                            self.test_results.append({"test": "System Timezone", "status": "PASS", "details": "Server running in UTC"})
                        else:
                            print(f"⚠️ Backend server timezone: {dt.tzinfo}")
                            self.test_results.append({"test": "System Timezone", "status": "INFO", "details": f"Server timezone: {dt.tzinfo}"})
                    else:
                        print("❌ No timestamp in health response")
                        self.test_results.append({"test": "System Timezone", "status": "FAIL", "details": "No timestamp in health response"})
                else:
                    print(f"❌ Health check failed: {response.status}")
                    self.test_results.append({"test": "System Timezone", "status": "FAIL", "details": f"Health check failed: {response.status}"})
                    
        except Exception as e:
            print(f"❌ System timezone test failed: {str(e)}")
            self.test_results.append({"test": "System Timezone", "status": "FAIL", "details": str(e)})
    
    async def test_campaign_scheduling_types(self):
        """Test 2: Campaign Scheduling Types - Test both interval and datetime modes"""
        print("\n🔍 TEST 2: Campaign Scheduling Types")
        
        # First get available templates and lists
        templates = await self.get_templates()
        lists = await self.get_lists()
        
        if not templates or not lists:
            print("❌ Need templates and lists for campaign testing")
            self.test_results.append({"test": "Campaign Scheduling Types", "status": "FAIL", "details": "Missing templates or lists"})
            return
        
        template_id = templates[0]["id"]
        list_id = lists[0]["id"]
        
        # Test 2A: Interval Mode (default: [3, 7, 14] days)
        print("\n📅 Testing Interval Mode Scheduling")
        try:
            interval_campaign = {
                "name": "Test Interval Campaign - Scheduling Test",
                "template_id": template_id,
                "list_ids": [list_id],
                "max_emails": 100,
                "follow_up_enabled": True,
                "follow_up_schedule_type": "interval",
                "follow_up_intervals": [3, 7, 14],
                "follow_up_timezone": "UTC",
                "follow_up_time_window_start": "09:00",
                "follow_up_time_window_end": "17:00",
                "follow_up_days_of_week": ["monday", "tuesday", "wednesday", "thursday", "friday"]
            }
            
            async with self.session.post(f"{BACKEND_URL}/campaigns", 
                                       json=interval_campaign, 
                                       headers=self.get_headers()) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Interval campaign created: {data.get('id')}")
                    print(f"✅ Follow-up schedule type: {data.get('follow_up_schedule_type')}")
                    print(f"✅ Follow-up intervals: {data.get('follow_up_intervals')}")
                    self.test_results.append({"test": "Interval Mode Scheduling", "status": "PASS", "details": f"Campaign ID: {data.get('id')}"})
                else:
                    error_text = await response.text()
                    print(f"❌ Interval campaign creation failed: {response.status} - {error_text}")
                    self.test_results.append({"test": "Interval Mode Scheduling", "status": "FAIL", "details": f"HTTP {response.status}: {error_text}"})
                    
        except Exception as e:
            print(f"❌ Interval mode test failed: {str(e)}")
            self.test_results.append({"test": "Interval Mode Scheduling", "status": "FAIL", "details": str(e)})
        
        # Test 2B: Datetime Mode (specific date/times)
        print("\n📅 Testing Datetime Mode Scheduling")
        try:
            # Create specific follow-up dates (future dates)
            now = datetime.utcnow()
            follow_up_dates = [
                (now + timedelta(days=3)).isoformat() + "Z",
                (now + timedelta(days=7)).isoformat() + "Z", 
                (now + timedelta(days=14)).isoformat() + "Z"
            ]
            
            datetime_campaign = {
                "name": "Test Datetime Campaign - Scheduling Test",
                "template_id": template_id,
                "list_ids": [list_id],
                "max_emails": 100,
                "follow_up_enabled": True,
                "follow_up_schedule_type": "datetime",
                "follow_up_dates": follow_up_dates,
                "follow_up_timezone": "UTC",
                "follow_up_time_window_start": "10:00",
                "follow_up_time_window_end": "16:00",
                "follow_up_days_of_week": ["monday", "tuesday", "wednesday", "thursday", "friday"]
            }
            
            async with self.session.post(f"{BACKEND_URL}/campaigns", 
                                       json=datetime_campaign, 
                                       headers=self.get_headers()) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Datetime campaign created: {data.get('id')}")
                    print(f"✅ Follow-up schedule type: {data.get('follow_up_schedule_type')}")
                    print(f"✅ Follow-up dates: {data.get('follow_up_dates')}")
                    print(f"✅ Follow-up timezone: {data.get('follow_up_timezone')}")
                    self.test_results.append({"test": "Datetime Mode Scheduling", "status": "PASS", "details": f"Campaign ID: {data.get('id')}"})
                else:
                    error_text = await response.text()
                    print(f"❌ Datetime campaign creation failed: {response.status} - {error_text}")
                    self.test_results.append({"test": "Datetime Mode Scheduling", "status": "FAIL", "details": f"HTTP {response.status}: {error_text}"})
                    
        except Exception as e:
            print(f"❌ Datetime mode test failed: {str(e)}")
            self.test_results.append({"test": "Datetime Mode Scheduling", "status": "FAIL", "details": str(e)})
    
    async def test_timezone_configuration(self):
        """Test 3: Timezone Configuration - Test different timezones"""
        print("\n🔍 TEST 3: Timezone Configuration")
        
        # Get templates and lists
        templates = await self.get_templates()
        lists = await self.get_lists()
        
        if not templates or not lists:
            print("❌ Need templates and lists for timezone testing")
            self.test_results.append({"test": "Timezone Configuration", "status": "FAIL", "details": "Missing templates or lists"})
            return
        
        template_id = templates[0]["id"]
        list_id = lists[0]["id"]
        
        # Test different timezones
        timezones_to_test = ["UTC", "America/New_York", "Europe/London"]
        
        for tz in timezones_to_test:
            print(f"\n🌍 Testing timezone: {tz}")
            try:
                # Create datetime in the specific timezone
                tz_obj = pytz.timezone(tz)
                now_in_tz = datetime.now(tz_obj)
                follow_up_date = (now_in_tz + timedelta(days=5)).isoformat()
                
                timezone_campaign = {
                    "name": f"Test {tz} Campaign - Timezone Test",
                    "template_id": template_id,
                    "list_ids": [list_id],
                    "max_emails": 50,
                    "follow_up_enabled": True,
                    "follow_up_schedule_type": "datetime",
                    "follow_up_dates": [follow_up_date],
                    "follow_up_timezone": tz,
                    "follow_up_time_window_start": "09:00",
                    "follow_up_time_window_end": "17:00"
                }
                
                async with self.session.post(f"{BACKEND_URL}/campaigns", 
                                           json=timezone_campaign, 
                                           headers=self.get_headers()) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ {tz} campaign created: {data.get('id')}")
                        print(f"✅ Timezone processed: {data.get('follow_up_timezone')}")
                        self.test_results.append({"test": f"Timezone {tz}", "status": "PASS", "details": f"Campaign ID: {data.get('id')}"})
                    else:
                        error_text = await response.text()
                        print(f"❌ {tz} campaign failed: {response.status} - {error_text}")
                        self.test_results.append({"test": f"Timezone {tz}", "status": "FAIL", "details": f"HTTP {response.status}: {error_text}"})
                        
            except Exception as e:
                print(f"❌ Timezone {tz} test failed: {str(e)}")
                self.test_results.append({"test": f"Timezone {tz}", "status": "FAIL", "details": str(e)})
    
    async def test_follow_up_date_processing(self):
        """Test 4: Follow-up Date Processing - Test creating campaigns with specific follow_up_dates and follow_up_timezone"""
        print("\n🔍 TEST 4: Follow-up Date Processing")
        
        # Get templates and lists
        templates = await self.get_templates()
        lists = await self.get_lists()
        
        if not templates or not lists:
            print("❌ Need templates and lists for follow-up date testing")
            self.test_results.append({"test": "Follow-up Date Processing", "status": "FAIL", "details": "Missing templates or lists"})
            return
        
        template_id = templates[0]["id"]
        list_id = lists[0]["id"]
        
        # Test with different date formats and timezones
        test_cases = [
            {
                "name": "Future Date - America/New_York",
                "timezone": "America/New_York",
                "dates": [(datetime.now() + timedelta(days=2)).isoformat() + "Z"]
            },
            {
                "name": "Multiple Future Dates - Europe/London", 
                "timezone": "Europe/London",
                "dates": [
                    (datetime.now() + timedelta(days=1)).isoformat() + "Z",
                    (datetime.now() + timedelta(days=3)).isoformat() + "Z",
                    (datetime.now() + timedelta(days=7)).isoformat() + "Z"
                ]
            },
            {
                "name": "Past Date Test - UTC",
                "timezone": "UTC", 
                "dates": [(datetime.now() - timedelta(days=1)).isoformat() + "Z"]
            }
        ]
        
        for test_case in test_cases:
            print(f"\n📅 Testing: {test_case['name']}")
            try:
                campaign_data = {
                    "name": f"Follow-up Date Test - {test_case['name']}",
                    "template_id": template_id,
                    "list_ids": [list_id],
                    "max_emails": 25,
                    "follow_up_enabled": True,
                    "follow_up_schedule_type": "datetime",
                    "follow_up_dates": test_case["dates"],
                    "follow_up_timezone": test_case["timezone"],
                    "follow_up_time_window_start": "08:00",
                    "follow_up_time_window_end": "18:00"
                }
                
                async with self.session.post(f"{BACKEND_URL}/campaigns", 
                                           json=campaign_data, 
                                           headers=self.get_headers()) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ {test_case['name']} campaign created: {data.get('id')}")
                        print(f"✅ Processed dates: {data.get('follow_up_dates')}")
                        print(f"✅ Timezone: {data.get('follow_up_timezone')}")
                        self.test_results.append({"test": f"Follow-up Date - {test_case['name']}", "status": "PASS", "details": f"Campaign ID: {data.get('id')}"})
                    else:
                        error_text = await response.text()
                        print(f"❌ {test_case['name']} failed: {response.status} - {error_text}")
                        self.test_results.append({"test": f"Follow-up Date - {test_case['name']}", "status": "FAIL", "details": f"HTTP {response.status}: {error_text}"})
                        
            except Exception as e:
                print(f"❌ Follow-up date test {test_case['name']} failed: {str(e)}")
                self.test_results.append({"test": f"Follow-up Date - {test_case['name']}", "status": "FAIL", "details": str(e)})
    
    async def test_smart_follow_up_engine_status(self):
        """Test 5: Smart Follow-Up Engine Status - Check if the follow-up engine is running and processing scheduled emails"""
        print("\n🔍 TEST 5: Smart Follow-Up Engine Status")
        
        try:
            # Check services status
            async with self.session.get(f"{BACKEND_URL}/services/status", headers=self.get_headers()) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Services status retrieved")
                    
                    # Check smart_follow_up_engine
                    services = data.get("services", {})
                    follow_up_engine = services.get("smart_follow_up_engine", {})
                    email_processor = services.get("email_processor", {})
                    
                    print(f"✅ Smart Follow-up Engine Status: {follow_up_engine.get('status')}")
                    print(f"✅ Email Processor Status: {email_processor.get('status')}")
                    print(f"✅ Overall Status: {data.get('overall_status')}")
                    
                    # Check monitored providers
                    monitored_providers = email_processor.get("monitored_providers", [])
                    print(f"✅ Monitored Providers Count: {len(monitored_providers)}")
                    
                    for provider in monitored_providers:
                        print(f"  - {provider.get('name')} ({provider.get('provider_type')})")
                    
                    # Determine if engines are working
                    if follow_up_engine.get('status') == 'running' and email_processor.get('status') == 'running':
                        self.test_results.append({"test": "Smart Follow-Up Engine Status", "status": "PASS", "details": "Both engines running"})
                    else:
                        self.test_results.append({"test": "Smart Follow-Up Engine Status", "status": "PARTIAL", "details": f"Follow-up: {follow_up_engine.get('status')}, Email Processor: {email_processor.get('status')}"})
                        
                else:
                    error_text = await response.text()
                    print(f"❌ Services status check failed: {response.status} - {error_text}")
                    self.test_results.append({"test": "Smart Follow-Up Engine Status", "status": "FAIL", "details": f"HTTP {response.status}: {error_text}"})
                    
        except Exception as e:
            print(f"❌ Smart follow-up engine status test failed: {str(e)}")
            self.test_results.append({"test": "Smart Follow-Up Engine Status", "status": "FAIL", "details": str(e)})
    
    async def test_time_window_settings(self):
        """Test 6: Time Window Settings - Test the follow_up_time_window_start and follow_up_time_window_end settings"""
        print("\n🔍 TEST 6: Time Window Settings")
        
        # Get templates and lists
        templates = await self.get_templates()
        lists = await self.get_lists()
        
        if not templates or not lists:
            print("❌ Need templates and lists for time window testing")
            self.test_results.append({"test": "Time Window Settings", "status": "FAIL", "details": "Missing templates or lists"})
            return
        
        template_id = templates[0]["id"]
        list_id = lists[0]["id"]
        
        # Test different time window configurations
        time_window_tests = [
            {
                "name": "Standard Business Hours",
                "start": "09:00",
                "end": "17:00"
            },
            {
                "name": "Extended Hours",
                "start": "08:00", 
                "end": "20:00"
            },
            {
                "name": "Early Morning Window",
                "start": "06:00",
                "end": "10:00"
            },
            {
                "name": "Evening Window",
                "start": "18:00",
                "end": "22:00"
            }
        ]
        
        for test_case in time_window_tests:
            print(f"\n⏰ Testing: {test_case['name']} ({test_case['start']} - {test_case['end']})")
            try:
                campaign_data = {
                    "name": f"Time Window Test - {test_case['name']}",
                    "template_id": template_id,
                    "list_ids": [list_id],
                    "max_emails": 20,
                    "follow_up_enabled": True,
                    "follow_up_schedule_type": "interval",
                    "follow_up_intervals": [1, 3],
                    "follow_up_timezone": "UTC",
                    "follow_up_time_window_start": test_case["start"],
                    "follow_up_time_window_end": test_case["end"],
                    "follow_up_days_of_week": ["monday", "tuesday", "wednesday", "thursday", "friday"]
                }
                
                async with self.session.post(f"{BACKEND_URL}/campaigns", 
                                           json=campaign_data, 
                                           headers=self.get_headers()) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ {test_case['name']} campaign created: {data.get('id')}")
                        
                        # Verify the campaign was created with correct time windows
                        campaign_id = data.get('id')
                        if campaign_id:
                            # Get campaign details to verify time windows
                            async with self.session.get(f"{BACKEND_URL}/campaigns/{campaign_id}", 
                                                       headers=self.get_headers()) as detail_response:
                                if detail_response.status == 200:
                                    detail_data = await detail_response.json()
                                    actual_start = detail_data.get('follow_up_time_window_start')
                                    actual_end = detail_data.get('follow_up_time_window_end')
                                    print(f"✅ Time window verified: {actual_start} - {actual_end}")
                                    
                                    if actual_start == test_case["start"] and actual_end == test_case["end"]:
                                        self.test_results.append({"test": f"Time Window - {test_case['name']}", "status": "PASS", "details": f"Window: {actual_start}-{actual_end}"})
                                    else:
                                        self.test_results.append({"test": f"Time Window - {test_case['name']}", "status": "FAIL", "details": f"Expected: {test_case['start']}-{test_case['end']}, Got: {actual_start}-{actual_end}"})
                                else:
                                    self.test_results.append({"test": f"Time Window - {test_case['name']}", "status": "PARTIAL", "details": "Campaign created but couldn't verify details"})
                        else:
                            self.test_results.append({"test": f"Time Window - {test_case['name']}", "status": "PARTIAL", "details": "Campaign created but no ID returned"})
                            
                    else:
                        error_text = await response.text()
                        print(f"❌ {test_case['name']} failed: {response.status} - {error_text}")
                        self.test_results.append({"test": f"Time Window - {test_case['name']}", "status": "FAIL", "details": f"HTTP {response.status}: {error_text}"})
                        
            except Exception as e:
                print(f"❌ Time window test {test_case['name']} failed: {str(e)}")
                self.test_results.append({"test": f"Time Window - {test_case['name']}", "status": "FAIL", "details": str(e)})
    
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
        """Print test results summary"""
        print("\n" + "="*80)
        print("🎯 SCHEDULING AND TIMEZONE TESTING SUMMARY")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAIL"])
        partial_tests = len([r for r in self.test_results if r["status"] == "PARTIAL"])
        info_tests = len([r for r in self.test_results if r["status"] == "INFO"])
        
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️ Partial: {partial_tests}")
        print(f"ℹ️ Info: {info_tests}")
        
        if total_tests > 0:
            success_rate = (passed_tests / total_tests) * 100
            print(f"📈 Success Rate: {success_rate:.1f}%")
        
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status_icon = {"PASS": "✅", "FAIL": "❌", "PARTIAL": "⚠️", "INFO": "ℹ️"}.get(result["status"], "❓")
            print(f"{status_icon} {result['test']}: {result['status']} - {result['details']}")
        
        print("\n" + "="*80)
        
        # Determine overall assessment
        if failed_tests == 0 and passed_tests > 0:
            print("🎉 OVERALL ASSESSMENT: SCHEDULING FUNCTIONALITY IS WORKING")
        elif failed_tests > passed_tests:
            print("🚨 OVERALL ASSESSMENT: CRITICAL SCHEDULING ISSUES FOUND")
        else:
            print("⚠️ OVERALL ASSESSMENT: SCHEDULING PARTIALLY WORKING - SOME ISSUES FOUND")
        
        print("="*80)

async def main():
    """Main test execution"""
    print("🚀 AI Email Responder - Scheduling and Timezone Testing")
    print("Testing Agent - January 2025")
    print("Focus: Scheduling functionality and timezone handling issues")
    print("="*80)
    
    tester = SchedulingTester()
    
    try:
        # Setup
        if not await tester.setup_session():
            print("❌ Failed to setup session. Exiting.")
            return
        
        # Run all tests
        await tester.test_system_timezone()
        await tester.test_campaign_scheduling_types()
        await tester.test_timezone_configuration()
        await tester.test_follow_up_date_processing()
        await tester.test_smart_follow_up_engine_status()
        await tester.test_time_window_settings()
        
        # Print summary
        tester.print_summary()
        
    except Exception as e:
        print(f"❌ Test execution failed: {str(e)}")
    finally:
        await tester.cleanup_session()

if __name__ == "__main__":
    asyncio.run(main())