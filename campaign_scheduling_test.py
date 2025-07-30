#!/usr/bin/env python3
"""
Campaign Creation and Scheduling Test
Tests the specific scenario: Create campaign with precise timing and follow-ups
- Initial email: NOW + 3 minutes
- Follow-up 1: Initial email + 1 minute  
- Follow-up 2: Initial email + 3 minutes
- Follow-up 3: Initial email + 5 minutes
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
import sys
import os

# Backend URL from environment
BACKEND_URL = "https://c9bf2a3a-3cde-4b42-9b26-a4c6b0fb8d18.preview.emergentagent.com/api"

class CampaignSchedulingTester:
    def __init__(self):
        self.session = None
        self.test_results = {
            "setup_verification": {"status": "unknown", "details": {}},
            "campaign_creation": {"status": "unknown", "details": {}},
            "campaign_verification": {"status": "unknown", "details": {}},
            "timing_verification": {"status": "unknown", "details": {}},
            "overall_status": "unknown"
        }
        
        # Test data
        self.target_email = "kasargovinda@gmail.com"
        self.sender_email = "rohushanshinde@gmail.com"
        self.target_list_name = "Newlist"
        
    async def setup_session(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession()
    
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    async def make_request(self, method, endpoint, data=None, description=""):
        """Make HTTP request and handle response"""
        try:
            url = f"{BACKEND_URL}{endpoint}"
            print(f"\n🔍 {description}")
            print(f"   {method.upper()} {url}")
            
            if method.lower() == "get":
                async with self.session.get(url) as response:
                    status_code = response.status
                    response_data = await response.json()
            elif method.lower() == "post":
                headers = {"Content-Type": "application/json"}
                async with self.session.post(url, json=data, headers=headers) as response:
                    status_code = response.status
                    response_data = await response.json()
            
            if status_code in [200, 201]:
                print(f"   ✅ SUCCESS - Status: {status_code}")
                return {"success": True, "status_code": status_code, "data": response_data}
            else:
                print(f"   ❌ FAILED - Status: {status_code}")
                print(f"   Response: {response_data}")
                return {"success": False, "status_code": status_code, "data": response_data}
                
        except Exception as e:
            print(f"   ❌ EXCEPTION - {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def verify_setup_prerequisites(self):
        """Verify that all prerequisites are in place"""
        print("\n" + "="*60)
        print("🔧 VERIFYING SETUP PREREQUISITES")
        print("="*60)
        
        setup_details = {}
        setup_ok = True
        
        # 1. Check email providers
        result = await self.make_request("GET", "/email-providers", description="Checking email providers")
        if result["success"]:
            providers = result["data"]
            sender_provider = None
            for provider in providers:
                if provider.get("email_address") == self.sender_email:
                    sender_provider = provider
                    break
            
            if sender_provider:
                setup_details["sender_provider"] = {
                    "found": True,
                    "name": sender_provider.get("name"),
                    "is_default": sender_provider.get("is_default", False),
                    "is_active": sender_provider.get("is_active", False)
                }
                print(f"   ✅ Sender provider found: {sender_provider.get('name')}")
                print(f"      Default: {sender_provider.get('is_default')}, Active: {sender_provider.get('is_active')}")
            else:
                setup_details["sender_provider"] = {"found": False}
                print(f"   ❌ Sender provider not found: {self.sender_email}")
                setup_ok = False
        else:
            setup_ok = False
        
        # 2. Check prospect lists
        result = await self.make_request("GET", "/lists", description="Checking prospect lists")
        if result["success"]:
            lists = result["data"]
            target_list = None
            for list_item in lists:
                if list_item.get("name") == self.target_list_name:
                    target_list = list_item
                    break
            
            if target_list:
                setup_details["target_list"] = {
                    "found": True,
                    "id": target_list.get("id"),
                    "name": target_list.get("name"),
                    "prospect_count": target_list.get("prospect_count", 0)
                }
                print(f"   ✅ Target list found: {target_list.get('name')}")
                print(f"      ID: {target_list.get('id')}, Prospects: {target_list.get('prospect_count', 0)}")
            else:
                setup_details["target_list"] = {"found": False}
                print(f"   ❌ Target list not found: {self.target_list_name}")
                setup_ok = False
        else:
            setup_ok = False
        
        # 3. Check if target prospect exists in the list
        if setup_details.get("target_list", {}).get("found"):
            list_id = setup_details["target_list"]["id"]
            result = await self.make_request("GET", f"/lists/{list_id}/prospects", 
                                           description=f"Checking prospects in {self.target_list_name}")
            if result["success"]:
                prospects = result["data"].get("prospects", [])
                target_prospect = None
                for prospect in prospects:
                    if prospect.get("email") == self.target_email:
                        target_prospect = prospect
                        break
                
                if target_prospect:
                    setup_details["target_prospect"] = {
                        "found": True,
                        "id": target_prospect.get("id"),
                        "email": target_prospect.get("email"),
                        "name": f"{target_prospect.get('first_name', '')} {target_prospect.get('last_name', '')}"
                    }
                    print(f"   ✅ Target prospect found: {target_prospect.get('email')}")
                else:
                    setup_details["target_prospect"] = {"found": False}
                    print(f"   ❌ Target prospect not found: {self.target_email}")
                    setup_ok = False
        
        # 4. Check available templates
        result = await self.make_request("GET", "/templates", description="Checking available templates")
        if result["success"]:
            templates = result["data"]
            if templates:
                setup_details["templates"] = {
                    "count": len(templates),
                    "available": [{"id": t.get("id"), "name": t.get("name")} for t in templates[:5]]
                }
                print(f"   ✅ Templates available: {len(templates)}")
                for template in templates[:3]:
                    print(f"      - {template.get('name')} (ID: {template.get('id')})")
            else:
                setup_details["templates"] = {"count": 0}
                print(f"   ❌ No templates available")
                setup_ok = False
        else:
            setup_ok = False
        
        self.test_results["setup_verification"]["details"] = setup_details
        self.test_results["setup_verification"]["status"] = "passed" if setup_ok else "failed"
        
        return setup_ok, setup_details
    
    async def create_campaign_with_precise_timing(self, setup_details):
        """Create campaign with precise timing as specified"""
        print("\n" + "="*60)
        print("🚀 CREATING CAMPAIGN WITH PRECISE TIMING")
        print("="*60)
        
        # Calculate precise timestamps
        now = datetime.utcnow()
        initial_send_time = now + timedelta(minutes=3)
        follow_up_1_time = initial_send_time + timedelta(minutes=1)
        follow_up_2_time = initial_send_time + timedelta(minutes=3)
        follow_up_3_time = initial_send_time + timedelta(minutes=5)
        
        print(f"   📅 Current time: {now.isoformat()}")
        print(f"   📅 Initial send: {initial_send_time.isoformat()} (NOW + 3 minutes)")
        print(f"   📅 Follow-up 1:  {follow_up_1_time.isoformat()} (Initial + 1 minute)")
        print(f"   📅 Follow-up 2:  {follow_up_2_time.isoformat()} (Initial + 3 minutes)")
        print(f"   📅 Follow-up 3:  {follow_up_3_time.isoformat()} (Initial + 5 minutes)")
        
        # Get first available template
        template_id = setup_details["templates"]["available"][0]["id"]
        template_name = setup_details["templates"]["available"][0]["name"]
        list_id = setup_details["target_list"]["id"]
        
        # Create campaign data with datetime-based scheduling
        campaign_data = {
            "name": f"Precise Timing Campaign - {now.strftime('%H:%M:%S')}",
            "template_id": template_id,
            "list_ids": [list_id],
            "max_emails": 1000,
            "schedule": initial_send_time.isoformat(),
            
            # Enhanced Follow-up Configuration with datetime scheduling
            "follow_up_enabled": True,
            "follow_up_schedule_type": "datetime",  # Use datetime instead of interval
            "follow_up_dates": [
                follow_up_1_time.isoformat(),
                follow_up_2_time.isoformat(),
                follow_up_3_time.isoformat()
            ],
            "follow_up_timezone": "UTC",
            "follow_up_time_window_start": "00:00",
            "follow_up_time_window_end": "23:59",
            "follow_up_days_of_week": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
            "follow_up_templates": [template_id, template_id, template_id]  # Use same template for all follow-ups
        }
        
        print(f"\n   📋 Campaign Configuration:")
        print(f"      Name: {campaign_data['name']}")
        print(f"      Template: {template_name} ({template_id})")
        print(f"      Target List: {setup_details['target_list']['name']} ({list_id})")
        print(f"      Schedule Type: {campaign_data['follow_up_schedule_type']}")
        print(f"      Follow-up Enabled: {campaign_data['follow_up_enabled']}")
        
        # Create the campaign
        result = await self.make_request("POST", "/campaigns", campaign_data, 
                                       "Creating campaign with precise timing")
        
        campaign_details = {}
        if result["success"]:
            campaign_response = result["data"]
            campaign_details = {
                "created": True,
                "id": campaign_response.get("id"),
                "name": campaign_response.get("name"),
                "status": campaign_response.get("status"),
                "prospect_count": campaign_response.get("prospect_count"),
                "follow_up_enabled": campaign_response.get("follow_up_enabled"),
                "follow_up_schedule_type": campaign_response.get("follow_up_schedule_type"),
                "follow_up_dates": campaign_response.get("follow_up_dates", []),
                "created_at": campaign_response.get("created_at")
            }
            
            print(f"   ✅ Campaign created successfully!")
            print(f"      ID: {campaign_details['id']}")
            print(f"      Status: {campaign_details['status']}")
            print(f"      Prospect Count: {campaign_details['prospect_count']}")
            
            self.test_results["campaign_creation"]["status"] = "passed"
        else:
            campaign_details = {"created": False, "error": result.get("error", "Unknown error")}
            print(f"   ❌ Campaign creation failed!")
            self.test_results["campaign_creation"]["status"] = "failed"
        
        self.test_results["campaign_creation"]["details"] = campaign_details
        return campaign_details
    
    async def verify_campaign_details(self, campaign_details):
        """Verify the created campaign has correct details and timing"""
        print("\n" + "="*60)
        print("🔍 VERIFYING CAMPAIGN DETAILS")
        print("="*60)
        
        if not campaign_details.get("created"):
            print("   ❌ Cannot verify - campaign was not created")
            self.test_results["campaign_verification"]["status"] = "failed"
            return False
        
        campaign_id = campaign_details["id"]
        
        # Get detailed campaign information
        result = await self.make_request("GET", f"/campaigns/{campaign_id}", 
                                       description=f"Getting campaign details for {campaign_id}")
        
        verification_details = {}
        if result["success"]:
            campaign_data = result["data"]
            
            verification_details = {
                "id": campaign_data.get("id"),
                "name": campaign_data.get("name"),
                "status": campaign_data.get("status"),
                "template_id": campaign_data.get("template_id"),
                "list_ids": campaign_data.get("list_ids", []),
                "follow_up_enabled": campaign_data.get("follow_up_enabled"),
                "follow_up_schedule_type": campaign_data.get("follow_up_schedule_type"),
                "follow_up_dates": campaign_data.get("follow_up_dates", []),
                "follow_up_timezone": campaign_data.get("follow_up_timezone"),
                "template": campaign_data.get("template"),
                "lists": campaign_data.get("lists", []),
                "prospect_count": campaign_data.get("prospect_count", 0)
            }
            
            print(f"   ✅ Campaign details retrieved successfully!")
            print(f"      ID: {verification_details['id']}")
            print(f"      Name: {verification_details['name']}")
            print(f"      Status: {verification_details['status']}")
            print(f"      Follow-up Enabled: {verification_details['follow_up_enabled']}")
            print(f"      Schedule Type: {verification_details['follow_up_schedule_type']}")
            print(f"      Timezone: {verification_details['follow_up_timezone']}")
            
            # Verify follow-up dates
            follow_up_dates = verification_details.get("follow_up_dates", [])
            print(f"\n   📅 Follow-up Schedule ({len(follow_up_dates)} dates):")
            for i, date_str in enumerate(follow_up_dates, 1):
                print(f"      Follow-up {i}: {date_str}")
            
            # Verify target list and prospects
            lists = verification_details.get("lists", [])
            print(f"\n   📋 Target Lists ({len(lists)} lists):")
            for list_item in lists:
                print(f"      - {list_item.get('name')} (ID: {list_item.get('id')})")
                print(f"        Prospects: {list_item.get('prospect_count', 0)}")
            
            # Verify template
            template = verification_details.get("template")
            if template:
                print(f"\n   📝 Template:")
                print(f"      Name: {template.get('name')}")
                print(f"      Type: {template.get('type')}")
            
            self.test_results["campaign_verification"]["status"] = "passed"
            
        else:
            verification_details = {"error": result.get("error", "Failed to get campaign details")}
            print(f"   ❌ Failed to get campaign details")
            self.test_results["campaign_verification"]["status"] = "failed"
        
        self.test_results["campaign_verification"]["details"] = verification_details
        return verification_details
    
    async def verify_timing_precision(self, verification_details):
        """Verify that the timing is set correctly with minute precision"""
        print("\n" + "="*60)
        print("⏰ VERIFYING TIMING PRECISION")
        print("="*60)
        
        timing_details = {}
        timing_ok = True
        
        if not verification_details or "follow_up_dates" not in verification_details:
            print("   ❌ Cannot verify timing - no follow-up dates found")
            self.test_results["timing_verification"]["status"] = "failed"
            return False
        
        follow_up_dates = verification_details["follow_up_dates"]
        
        if len(follow_up_dates) != 3:
            print(f"   ❌ Expected 3 follow-up dates, found {len(follow_up_dates)}")
            timing_ok = False
        else:
            print(f"   ✅ Correct number of follow-up dates: {len(follow_up_dates)}")
        
        # Parse and verify timing intervals
        if len(follow_up_dates) >= 3:
            try:
                # Parse datetime strings
                dates = []
                for date_str in follow_up_dates:
                    # Handle different datetime formats
                    if date_str.endswith('Z'):
                        date_str = date_str[:-1] + '+00:00'
                    dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    dates.append(dt)
                
                timing_details["parsed_dates"] = [dt.isoformat() for dt in dates]
                
                # Calculate intervals between follow-ups
                if len(dates) >= 2:
                    interval_1_2 = (dates[1] - dates[0]).total_seconds() / 60  # minutes
                    interval_2_3 = (dates[2] - dates[1]).total_seconds() / 60  # minutes
                    
                    timing_details["intervals"] = {
                        "follow_up_1_to_2": f"{interval_1_2:.1f} minutes",
                        "follow_up_2_to_3": f"{interval_2_3:.1f} minutes"
                    }
                    
                    print(f"   📊 Timing Analysis:")
                    print(f"      Follow-up 1: {dates[0].isoformat()}")
                    print(f"      Follow-up 2: {dates[1].isoformat()} (+{interval_1_2:.1f} min)")
                    print(f"      Follow-up 3: {dates[2].isoformat()} (+{interval_2_3:.1f} min)")
                    
                    # Verify expected intervals (1 minute, then 2 minutes)
                    expected_intervals = [2.0, 2.0]  # 1+3-1=2, 5-3=2
                    actual_intervals = [interval_1_2, interval_2_3]
                    
                    for i, (expected, actual) in enumerate(zip(expected_intervals, actual_intervals)):
                        if abs(actual - expected) <= 0.1:  # Allow 0.1 minute tolerance
                            print(f"      ✅ Interval {i+1}: {actual:.1f} min (expected {expected:.1f} min)")
                        else:
                            print(f"      ❌ Interval {i+1}: {actual:.1f} min (expected {expected:.1f} min)")
                            timing_ok = False
                
            except Exception as e:
                print(f"   ❌ Error parsing follow-up dates: {str(e)}")
                timing_details["parse_error"] = str(e)
                timing_ok = False
        
        # Verify schedule type is datetime
        schedule_type = verification_details.get("follow_up_schedule_type")
        if schedule_type == "datetime":
            print(f"   ✅ Schedule type: {schedule_type}")
            timing_details["schedule_type"] = schedule_type
        else:
            print(f"   ❌ Expected schedule type 'datetime', got '{schedule_type}'")
            timing_ok = False
        
        # Verify timezone
        timezone = verification_details.get("follow_up_timezone")
        if timezone == "UTC":
            print(f"   ✅ Timezone: {timezone}")
            timing_details["timezone"] = timezone
        else:
            print(f"   ⚠️  Timezone: {timezone} (expected UTC)")
        
        timing_details["precision_verified"] = timing_ok
        self.test_results["timing_verification"]["details"] = timing_details
        self.test_results["timing_verification"]["status"] = "passed" if timing_ok else "failed"
        
        return timing_ok
    
    async def run_campaign_scheduling_test(self):
        """Run the complete campaign scheduling test"""
        print("=" * 80)
        print("🎯 CAMPAIGN CREATION AND SCHEDULING TEST")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print(f"Target: {self.target_email} in list '{self.target_list_name}'")
        print(f"Sender: {self.sender_email}")
        
        await self.setup_session()
        
        try:
            # Step 1: Verify prerequisites
            setup_ok, setup_details = await self.verify_setup_prerequisites()
            if not setup_ok:
                print("\n❌ CRITICAL: Prerequisites not met - cannot proceed with campaign creation")
                self.test_results["overall_status"] = "failed"
                return
            
            # Step 2: Create campaign with precise timing
            campaign_details = await self.create_campaign_with_precise_timing(setup_details)
            if not campaign_details.get("created"):
                print("\n❌ CRITICAL: Campaign creation failed")
                self.test_results["overall_status"] = "failed"
                return
            
            # Step 3: Verify campaign details
            verification_details = await self.verify_campaign_details(campaign_details)
            if not verification_details:
                print("\n❌ CRITICAL: Campaign verification failed")
                self.test_results["overall_status"] = "failed"
                return
            
            # Step 4: Verify timing precision
            timing_ok = await self.verify_timing_precision(verification_details)
            
            # Determine overall status
            if (self.test_results["setup_verification"]["status"] == "passed" and
                self.test_results["campaign_creation"]["status"] == "passed" and
                self.test_results["campaign_verification"]["status"] == "passed" and
                self.test_results["timing_verification"]["status"] == "passed"):
                self.test_results["overall_status"] = "passed"
            else:
                self.test_results["overall_status"] = "failed"
            
        finally:
            await self.cleanup_session()
        
        # Print final summary
        self.print_test_summary()
    
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("📋 CAMPAIGN SCHEDULING TEST SUMMARY")
        print("=" * 80)
        
        # Overall status
        status_emoji = {
            "passed": "✅",
            "failed": "❌",
            "unknown": "❓"
        }
        
        overall_status = self.test_results["overall_status"]
        print(f"\n🎯 OVERALL TEST STATUS: {status_emoji.get(overall_status, '❓')} {overall_status.upper()}")
        
        # Test breakdown
        print(f"\n📊 TEST BREAKDOWN:")
        for test_name, test_result in self.test_results.items():
            if test_name == "overall_status":
                continue
            status = test_result.get("status", "unknown")
            emoji = status_emoji.get(status, "❓")
            print(f"   • {test_name.replace('_', ' ').title()}: {emoji} {status}")
        
        # Key findings
        print(f"\n🔍 KEY FINDINGS:")
        
        # Setup verification
        setup_details = self.test_results["setup_verification"]["details"]
        if setup_details.get("sender_provider", {}).get("found"):
            provider = setup_details["sender_provider"]
            print(f"   ✅ Sender provider: {provider.get('name')} (Default: {provider.get('is_default')})")
        
        if setup_details.get("target_list", {}).get("found"):
            list_info = setup_details["target_list"]
            print(f"   ✅ Target list: {list_info.get('name')} ({list_info.get('prospect_count')} prospects)")
        
        if setup_details.get("target_prospect", {}).get("found"):
            prospect = setup_details["target_prospect"]
            print(f"   ✅ Target prospect: {prospect.get('email')}")
        
        # Campaign creation
        campaign_details = self.test_results["campaign_creation"]["details"]
        if campaign_details.get("created"):
            print(f"   ✅ Campaign created: {campaign_details.get('name')}")
            print(f"      ID: {campaign_details.get('id')}")
            print(f"      Status: {campaign_details.get('status')}")
        
        # Timing verification
        timing_details = self.test_results["timing_verification"]["details"]
        if timing_details.get("precision_verified"):
            print(f"   ✅ Timing precision verified")
            if "intervals" in timing_details:
                intervals = timing_details["intervals"]
                print(f"      Follow-up intervals: {intervals}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if self.test_results["overall_status"] == "passed":
            print("   • Campaign creation and scheduling is working correctly")
            print("   • System supports minute-level precision for follow-ups")
            print("   • Datetime-based scheduling is functional")
        else:
            failed_tests = [k for k, v in self.test_results.items() 
                          if isinstance(v, dict) and v.get("status") == "failed"]
            for test in failed_tests:
                print(f"   • Fix issues with: {test.replace('_', ' ')}")
        
        print("\n" + "=" * 80)
        print("✅ CAMPAIGN SCHEDULING TEST COMPLETED")
        print("=" * 80)

async def main():
    """Main test execution"""
    tester = CampaignSchedulingTester()
    await tester.run_campaign_scheduling_test()

if __name__ == "__main__":
    asyncio.run(main())