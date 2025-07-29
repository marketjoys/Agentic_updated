#!/usr/bin/env python3
"""
Follow-up System Debug Test
Testing Agent - January 2025

Debugging the follow-up system that is not working:
1. Campaign ID: "eb04934d-7d92-4344-b624-dc57791f2ff7" 
2. Campaign is "active" with follow_up_enabled: true
3. Campaign has datetime-based follow-ups scheduled at 09:04:45, 09:06:45, 09:08:45 UTC
4. Current time is past all these times (09:11 UTC)
5. Prospect "kasargovinda@gmail.com" has follow_up_status: "active" and follow_up_count: 0
6. But follow-up engine logs show "Found 0 active follow-up campaigns"
"""

import asyncio
import aiohttp
import json
import sys
import os
from datetime import datetime, timedelta
import pytz
from typing import Dict, Any, List

# Add backend path for direct database access
sys.path.append('/app/backend')
from app.services.database import db_service
from app.services.smart_follow_up_engine import smart_follow_up_engine

# Configuration
BACKEND_URL = "https://9f8a7167-d7f1-4045-b864-65d30ef37460.preview.emergentagent.com/api"
LOGIN_CREDENTIALS = {"username": "testuser", "password": "testpass123"}

class FollowUpDebugger:
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
    
    async def debug_database_query(self):
        """Test 1: Debug get_active_follow_up_campaigns database query directly"""
        print("\n🔍 TEST 1: Database Query Debug - get_active_follow_up_campaigns")
        
        try:
            # Connect to database directly
            await db_service.connect()
            
            # Test the exact query used by the follow-up engine
            campaigns = await db_service.get_active_follow_up_campaigns()
            
            print(f"✅ Found {len(campaigns)} active follow-up campaigns from database")
            
            # Check specific campaign
            target_campaign_id = "eb04934d-7d92-4344-b624-dc57791f2ff7"
            target_campaign = None
            
            for campaign in campaigns:
                print(f"  - Campaign ID: {campaign.get('id')}")
                print(f"    Name: {campaign.get('name')}")
                print(f"    Status: {campaign.get('status')}")
                print(f"    Follow-up enabled: {campaign.get('follow_up_enabled')}")
                print(f"    Follow-up schedule type: {campaign.get('follow_up_schedule_type')}")
                print(f"    Follow-up dates: {campaign.get('follow_up_dates')}")
                print()
                
                if campaign.get('id') == target_campaign_id:
                    target_campaign = campaign
            
            if target_campaign:
                print(f"✅ Found target campaign: {target_campaign_id}")
                self.test_results.append({"test": "Database Query - Target Campaign Found", "status": "PASS", "details": f"Campaign found with status: {target_campaign.get('status')}"})
            else:
                print(f"❌ Target campaign {target_campaign_id} not found in active follow-up campaigns")
                
                # Check if campaign exists at all
                all_campaigns = await db_service.get_campaigns()
                target_exists = any(c.get('id') == target_campaign_id for c in all_campaigns)
                
                if target_exists:
                    target_campaign = next(c for c in all_campaigns if c.get('id') == target_campaign_id)
                    print(f"❌ Campaign exists but not in active follow-up list:")
                    print(f"    Status: {target_campaign.get('status')}")
                    print(f"    Follow-up enabled: {target_campaign.get('follow_up_enabled')}")
                    self.test_results.append({"test": "Database Query - Target Campaign Found", "status": "FAIL", "details": f"Campaign exists but not active. Status: {target_campaign.get('status')}, Follow-up enabled: {target_campaign.get('follow_up_enabled')}"})
                else:
                    print(f"❌ Campaign {target_campaign_id} does not exist at all")
                    self.test_results.append({"test": "Database Query - Target Campaign Found", "status": "FAIL", "details": "Campaign does not exist"})
                    
        except Exception as e:
            print(f"❌ Database query test failed: {str(e)}")
            self.test_results.append({"test": "Database Query Debug", "status": "FAIL", "details": str(e)})
    
    async def debug_campaign_status(self):
        """Test 2: Check campaign status and why it's not being picked up"""
        print("\n🔍 TEST 2: Campaign Status Debug")
        
        try:
            await db_service.connect()
            
            target_campaign_id = "eb04934d-7d92-4344-b624-dc57791f2ff7"
            
            # Get campaign directly
            campaign = await db_service.get_campaign_by_id(target_campaign_id)
            
            if not campaign:
                print(f"❌ Campaign {target_campaign_id} not found")
                self.test_results.append({"test": "Campaign Status Debug", "status": "FAIL", "details": "Campaign not found"})
                return
            
            print(f"✅ Campaign found: {campaign.get('name')}")
            print(f"  Status: {campaign.get('status')}")
            print(f"  Follow-up enabled: {campaign.get('follow_up_enabled')}")
            print(f"  Follow-up schedule type: {campaign.get('follow_up_schedule_type')}")
            print(f"  Follow-up dates: {campaign.get('follow_up_dates')}")
            print(f"  Follow-up timezone: {campaign.get('follow_up_timezone')}")
            print(f"  Created at: {campaign.get('created_at')}")
            print(f"  Updated at: {campaign.get('updated_at')}")
            
            # Check why it's not in active follow-up campaigns
            issues = []
            
            if not campaign.get('follow_up_enabled'):
                issues.append("Follow-up not enabled")
            
            status = campaign.get('status')
            if status not in ["active", "running", "sent"]:
                issues.append(f"Status '{status}' not in active list")
            
            if issues:
                print(f"❌ Issues preventing campaign from being active:")
                for issue in issues:
                    print(f"  - {issue}")
                self.test_results.append({"test": "Campaign Status Debug", "status": "FAIL", "details": f"Issues: {', '.join(issues)}"})
            else:
                print(f"✅ Campaign should be active for follow-ups")
                self.test_results.append({"test": "Campaign Status Debug", "status": "PASS", "details": "Campaign meets active criteria"})
                
        except Exception as e:
            print(f"❌ Campaign status debug failed: {str(e)}")
            self.test_results.append({"test": "Campaign Status Debug", "status": "FAIL", "details": str(e)})
    
    async def debug_prospect_status(self):
        """Test 3: Check prospect status for follow-ups"""
        print("\n🔍 TEST 3: Prospect Status Debug")
        
        try:
            await db_service.connect()
            
            target_email = "kasargovinda@gmail.com"
            
            # Get prospect by email
            prospect = await db_service.get_prospect_by_email(target_email)
            
            if not prospect:
                print(f"❌ Prospect {target_email} not found")
                self.test_results.append({"test": "Prospect Status Debug", "status": "FAIL", "details": "Prospect not found"})
                return
            
            print(f"✅ Prospect found: {prospect.get('email')}")
            print(f"  ID: {prospect.get('id')}")
            print(f"  Follow-up status: {prospect.get('follow_up_status')}")
            print(f"  Follow-up count: {prospect.get('follow_up_count')}")
            print(f"  Last contact: {prospect.get('last_contact')}")
            print(f"  Last follow-up: {prospect.get('last_follow_up')}")
            print(f"  Campaign ID: {prospect.get('campaign_id')}")
            print(f"  Status: {prospect.get('status')}")
            print(f"  Responded at: {prospect.get('responded_at')}")
            print(f"  Response type: {prospect.get('response_type')}")
            
            # Check if prospect needs follow-up
            target_campaign_id = "eb04934d-7d92-4344-b624-dc57791f2ff7"
            prospects_needing_follow_up = await db_service.get_prospects_needing_follow_up(target_campaign_id)
            
            prospect_needs_follow_up = any(p.get('id') == prospect.get('id') for p in prospects_needing_follow_up)
            
            if prospect_needs_follow_up:
                print(f"✅ Prospect is in the 'needs follow-up' list")
                self.test_results.append({"test": "Prospect Status Debug", "status": "PASS", "details": "Prospect needs follow-up"})
            else:
                print(f"❌ Prospect is NOT in the 'needs follow-up' list")
                print(f"  Total prospects needing follow-up for campaign: {len(prospects_needing_follow_up)}")
                
                # Check why
                issues = []
                if prospect.get('follow_up_status') != 'active':
                    issues.append(f"Follow-up status is '{prospect.get('follow_up_status')}', not 'active'")
                if prospect.get('status') == 'unsubscribed':
                    issues.append("Prospect is unsubscribed")
                if prospect.get('campaign_id') != target_campaign_id:
                    issues.append(f"Prospect campaign_id '{prospect.get('campaign_id')}' doesn't match target '{target_campaign_id}'")
                
                if issues:
                    print(f"  Issues:")
                    for issue in issues:
                        print(f"    - {issue}")
                
                self.test_results.append({"test": "Prospect Status Debug", "status": "FAIL", "details": f"Issues: {', '.join(issues) if issues else 'Unknown'}"})
                
        except Exception as e:
            print(f"❌ Prospect status debug failed: {str(e)}")
            self.test_results.append({"test": "Prospect Status Debug", "status": "FAIL", "details": str(e)})
    
    async def debug_timing_logic(self):
        """Test 4: Debug the follow-up timing logic in _should_send_follow_up_now method"""
        print("\n🔍 TEST 4: Follow-up Timing Logic Debug")
        
        try:
            await db_service.connect()
            
            target_campaign_id = "eb04934d-7d92-4344-b624-dc57791f2ff7"
            target_email = "kasargovinda@gmail.com"
            
            # Get campaign and prospect
            campaign = await db_service.get_campaign_by_id(target_campaign_id)
            prospect = await db_service.get_prospect_by_email(target_email)
            
            if not campaign or not prospect:
                print(f"❌ Missing campaign or prospect")
                self.test_results.append({"test": "Timing Logic Debug", "status": "FAIL", "details": "Missing campaign or prospect"})
                return
            
            print(f"✅ Testing timing logic for:")
            print(f"  Campaign: {campaign.get('name')}")
            print(f"  Prospect: {prospect.get('email')}")
            print(f"  Current UTC time: {datetime.utcnow()}")
            
            # Get campaign timezone and current time
            campaign_timezone = campaign.get("follow_up_timezone", "UTC")
            tz = pytz.timezone(campaign_timezone)
            current_time = datetime.now(tz)
            
            print(f"  Campaign timezone: {campaign_timezone}")
            print(f"  Current time in campaign timezone: {current_time}")
            
            # Check schedule type
            schedule_type = campaign.get("follow_up_schedule_type", "interval")
            print(f"  Schedule type: {schedule_type}")
            
            if schedule_type == "datetime":
                follow_up_dates = campaign.get("follow_up_dates", [])
                print(f"  Follow-up dates: {follow_up_dates}")
                
                follow_up_count = prospect.get("follow_up_count", 0)
                print(f"  Current follow-up count: {follow_up_count}")
                
                if follow_up_count < len(follow_up_dates):
                    target_datetime = follow_up_dates[follow_up_count]
                    print(f"  Next follow-up target: {target_datetime}")
                    
                    # Convert to campaign timezone if needed
                    if hasattr(target_datetime, 'tzinfo'):
                        if target_datetime.tzinfo is None:
                            target_datetime = tz.localize(target_datetime)
                        else:
                            target_datetime = target_datetime.astimezone(tz)
                    
                    print(f"  Target datetime in campaign timezone: {target_datetime}")
                    
                    # Check if it's time to send (within 5 minutes window)
                    time_diff = (current_time - target_datetime).total_seconds()
                    print(f"  Time difference (seconds): {time_diff}")
                    print(f"  Within 5-minute window (-300 to 300): {-300 <= time_diff <= 300}")
                    
                    if -300 <= time_diff <= 300:
                        print(f"  ✅ Time window check passed")
                        
                        # Check campaign time window
                        current_day = current_time.strftime("%A").lower()
                        allowed_days = campaign.get("follow_up_days_of_week", 
                                                 ["monday", "tuesday", "wednesday", "thursday", "friday"])
                        print(f"  Current day: {current_day}")
                        print(f"  Allowed days: {allowed_days}")
                        print(f"  Day check passed: {current_day in allowed_days}")
                        
                        start_time = campaign.get("follow_up_time_window_start", "09:00")
                        end_time = campaign.get("follow_up_time_window_end", "17:00")
                        current_time_str = current_time.strftime("%H:%M")
                        print(f"  Time window: {start_time} - {end_time}")
                        print(f"  Current time: {current_time_str}")
                        print(f"  Time window check passed: {start_time <= current_time_str <= end_time}")
                        
                        if current_day in allowed_days and start_time <= current_time_str <= end_time:
                            print(f"  ✅ All timing checks passed - should send follow-up")
                            self.test_results.append({"test": "Timing Logic Debug", "status": "PASS", "details": "All timing checks passed"})
                        else:
                            print(f"  ❌ Time window or day check failed")
                            self.test_results.append({"test": "Timing Logic Debug", "status": "FAIL", "details": "Time window or day check failed"})
                    else:
                        print(f"  ❌ Not within 5-minute window")
                        self.test_results.append({"test": "Timing Logic Debug", "status": "FAIL", "details": f"Not within 5-minute window. Time diff: {time_diff} seconds"})
                else:
                    print(f"  ❌ Follow-up count ({follow_up_count}) >= number of dates ({len(follow_up_dates)})")
                    self.test_results.append({"test": "Timing Logic Debug", "status": "FAIL", "details": f"Follow-up count exceeded. Count: {follow_up_count}, Dates: {len(follow_up_dates)}"})
            else:
                print(f"  ❌ Schedule type is '{schedule_type}', not 'datetime'")
                self.test_results.append({"test": "Timing Logic Debug", "status": "FAIL", "details": f"Schedule type is '{schedule_type}', not 'datetime'"})
                
        except Exception as e:
            print(f"❌ Timing logic debug failed: {str(e)}")
            self.test_results.append({"test": "Timing Logic Debug", "status": "FAIL", "details": str(e)})
    
    async def debug_follow_up_engine_processing(self):
        """Test 5: Debug the actual follow-up engine processing"""
        print("\n🔍 TEST 5: Follow-up Engine Processing Debug")
        
        try:
            # Check if follow-up engine is running
            print(f"  Follow-up engine processing status: {smart_follow_up_engine.processing}")
            
            if not smart_follow_up_engine.processing:
                print(f"  ❌ Follow-up engine is not running")
                self.test_results.append({"test": "Follow-up Engine Processing", "status": "FAIL", "details": "Engine not running"})
                return
            
            # Manually trigger the follow-up check
            print(f"  ✅ Manually triggering follow-up check...")
            
            await smart_follow_up_engine._check_and_send_follow_ups()
            
            print(f"  ✅ Follow-up check completed")
            self.test_results.append({"test": "Follow-up Engine Processing", "status": "PASS", "details": "Manual follow-up check completed"})
            
        except Exception as e:
            print(f"❌ Follow-up engine processing debug failed: {str(e)}")
            self.test_results.append({"test": "Follow-up Engine Processing", "status": "FAIL", "details": str(e)})
    
    async def debug_campaign_creation_test(self):
        """Test 6: Create a test campaign with immediate follow-up to verify system works"""
        print("\n🔍 TEST 6: Test Campaign Creation for Immediate Follow-up")
        
        try:
            # Get templates and lists
            templates = await self.get_templates()
            lists = await self.get_lists()
            
            if not templates or not lists:
                print("❌ Need templates and lists for test campaign")
                self.test_results.append({"test": "Test Campaign Creation", "status": "FAIL", "details": "Missing templates or lists"})
                return
            
            template_id = templates[0]["id"]
            list_id = lists[0]["id"]
            
            # Create a campaign with follow-up dates in the past (should trigger immediately)
            now = datetime.utcnow()
            past_dates = [
                (now - timedelta(minutes=5)).isoformat() + "Z",
                (now - timedelta(minutes=3)).isoformat() + "Z",
                (now - timedelta(minutes=1)).isoformat() + "Z"
            ]
            
            test_campaign = {
                "name": "DEBUG Test Campaign - Immediate Follow-up",
                "template_id": template_id,
                "list_ids": [list_id],
                "max_emails": 10,
                "follow_up_enabled": True,
                "follow_up_schedule_type": "datetime",
                "follow_up_dates": past_dates,
                "follow_up_timezone": "UTC",
                "follow_up_time_window_start": "00:00",
                "follow_up_time_window_end": "23:59",
                "follow_up_days_of_week": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
            }
            
            async with self.session.post(f"{BACKEND_URL}/campaigns", 
                                       json=test_campaign, 
                                       headers=self.get_headers()) as response:
                if response.status == 200:
                    data = await response.json()
                    campaign_id = data.get('id')
                    print(f"✅ Test campaign created: {campaign_id}")
                    
                    # Update campaign status to active
                    await db_service.connect()
                    await db_service.update_campaign(campaign_id, {"status": "active"})
                    print(f"✅ Campaign status updated to active")
                    
                    # Check if it appears in active follow-up campaigns
                    active_campaigns = await db_service.get_active_follow_up_campaigns()
                    test_campaign_found = any(c.get('id') == campaign_id for c in active_campaigns)
                    
                    if test_campaign_found:
                        print(f"✅ Test campaign found in active follow-up campaigns")
                        self.test_results.append({"test": "Test Campaign Creation", "status": "PASS", "details": f"Campaign {campaign_id} created and active"})
                    else:
                        print(f"❌ Test campaign NOT found in active follow-up campaigns")
                        self.test_results.append({"test": "Test Campaign Creation", "status": "FAIL", "details": "Campaign created but not active"})
                        
                else:
                    error_text = await response.text()
                    print(f"❌ Test campaign creation failed: {response.status} - {error_text}")
                    self.test_results.append({"test": "Test Campaign Creation", "status": "FAIL", "details": f"HTTP {response.status}: {error_text}"})
                    
        except Exception as e:
            print(f"❌ Test campaign creation failed: {str(e)}")
            self.test_results.append({"test": "Test Campaign Creation", "status": "FAIL", "details": str(e)})
    
    async def get_templates(self):
        """Helper: Get available templates"""
        try:
            async with self.session.get(f"{BACKEND_URL}/templates", headers=self.get_headers()) as response:
                if response.status == 200:
                    templates = await response.json()
                    return templates
                else:
                    return []
        except Exception:
            return []
    
    async def get_lists(self):
        """Helper: Get available lists"""
        try:
            async with self.session.get(f"{BACKEND_URL}/lists", headers=self.get_headers()) as response:
                if response.status == 200:
                    lists = await response.json()
                    return lists
                else:
                    return []
        except Exception:
            return []
    
    def print_summary(self):
        """Print test results summary"""
        print("\n" + "="*80)
        print("🎯 FOLLOW-UP SYSTEM DEBUG SUMMARY")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAIL"])
        
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status_icon = {"PASS": "✅", "FAIL": "❌"}.get(result["status"], "❓")
            print(f"{status_icon} {result['test']}: {result['status']} - {result['details']}")
        
        print("\n" + "="*80)
        
        # Root cause analysis
        print("🔍 ROOT CAUSE ANALYSIS:")
        
        if failed_tests > 0:
            print("❌ ISSUES FOUND:")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(f"  - {result['test']}: {result['details']}")
        else:
            print("✅ NO CRITICAL ISSUES FOUND")
        
        print("="*80)

async def main():
    """Main debug execution"""
    print("🚀 Follow-up System Debug Test")
    print("Testing Agent - January 2025")
    print("Debugging why follow-ups are not being sent")
    print("="*80)
    
    debugger = FollowUpDebugger()
    
    try:
        # Setup
        if not await debugger.setup_session():
            print("❌ Failed to setup session. Exiting.")
            return
        
        # Run all debug tests
        await debugger.debug_database_query()
        await debugger.debug_campaign_status()
        await debugger.debug_prospect_status()
        await debugger.debug_timing_logic()
        await debugger.debug_follow_up_engine_processing()
        await debugger.debug_campaign_creation_test()
        
        # Print summary
        debugger.print_summary()
        
    except Exception as e:
        print(f"❌ Debug execution failed: {str(e)}")
    finally:
        await debugger.cleanup_session()

if __name__ == "__main__":
    asyncio.run(main())