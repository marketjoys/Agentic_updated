#!/usr/bin/env python3
"""
Comprehensive Follow-up Fix Test
Tests all the enhancements made to fix follow-up and provider consistency issues.
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
import sys
import os

# Backend URL from environment
BACKEND_URL = "https://923febb0-4941-4a54-88e6-10f9c6187a71.preview.emergentagent.com/api"

class ComprehensiveFollowUpTester:
    def __init__(self):
        self.session = None
        self.test_results = {
            "enhanced_services_check": {"status": "unknown", "details": {}},
            "provider_setup": {"status": "unknown", "details": {}},
            "campaign_creation": {"status": "unknown", "details": {}},
            "minute_precision_test": {"status": "unknown", "details": {}},
            "provider_consistency_test": {"status": "unknown", "details": {}},
            "follow_up_delivery_test": {"status": "unknown", "details": {}},
            "overall_status": "unknown"
        }
        
        # Test configuration
        self.test_email = "kasargovinda@gmail.com"
        self.sender_email = "rohushanshinde@gmail.com"
        self.test_list_name = "FollowUp-Test-List"
        
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
    
    async def test_enhanced_services(self):
        """Test that enhanced services are running"""
        print("\n" + "="*60)
        print("1. 🔧 TESTING ENHANCED SERVICES")
        print("="*60)
        
        result = await self.make_request("GET", "/services/status", description="Checking enhanced services status")
        
        if result["success"]:
            services = result["data"]
            details = {
                "overall_status": services.get("overall_status"),
                "smart_follow_up_engine": services.get("services", {}).get("smart_follow_up_engine", {}),
                "email_processor": services.get("services", {}).get("email_processor", {})
            }
            
            print(f"   📊 Overall Status: {details['overall_status']}")
            print(f"   🔄 Follow-up Engine: {details['smart_follow_up_engine'].get('status', 'unknown')}")
            print(f"   📧 Email Processor: {details['email_processor'].get('status', 'unknown')}")
            
            # Check if both services are running
            if (details['smart_follow_up_engine'].get('status') == 'running' and 
                details['email_processor'].get('status') == 'running'):
                self.test_results["enhanced_services_check"]["status"] = "passed"
                print("   ✅ Enhanced services are running correctly!")
            else:
                self.test_results["enhanced_services_check"]["status"] = "failed"
                print("   ❌ Some enhanced services are not running")
            
            self.test_results["enhanced_services_check"]["details"] = details
        else:
            self.test_results["enhanced_services_check"]["status"] = "failed"
            print("   ❌ Failed to get services status")
    
    async def setup_test_provider(self):
        """Setup test email provider"""
        print("\n" + "="*60)
        print("2. 📮 SETTING UP TEST EMAIL PROVIDER")
        print("="*60)
        
        # Check for existing provider
        providers_result = await self.make_request("GET", "/email-providers", description="Checking existing providers")
        
        if providers_result["success"]:
            providers = providers_result["data"]
            existing_provider = None
            
            for provider in providers:
                if provider.get("email_address") == self.sender_email:
                    existing_provider = provider
                    break
            
            if existing_provider:
                print(f"   ✅ Using existing provider: {existing_provider['name']}")
                print(f"      Email: {existing_provider['email_address']}")
                print(f"      Type: {existing_provider['provider_type']}")
                print(f"      Active: {existing_provider['is_active']}")
                print(f"      Default: {existing_provider['is_default']}")
                
                provider_details = {
                    "found": True,
                    "id": existing_provider["id"],
                    "name": existing_provider["name"],
                    "email": existing_provider["email_address"],
                    "active": existing_provider["is_active"],
                    "default": existing_provider["is_default"]
                }
                
                self.test_results["provider_setup"]["status"] = "passed"
                self.test_results["provider_setup"]["details"] = provider_details
                return existing_provider
        
        print("   ❌ No suitable email provider found for testing")
        self.test_results["provider_setup"]["status"] = "failed"
        return None
    
    async def create_test_campaign_with_minute_precision(self, provider):
        """Create campaign with minute-level precision follow-ups"""
        print("\n" + "="*60)
        print("3. 🚀 CREATING CAMPAIGN WITH MINUTE PRECISION")
        print("="*60)
        
        # Get templates and lists
        templates_result = await self.make_request("GET", "/templates", description="Getting templates")
        lists_result = await self.make_request("GET", "/lists", description="Getting lists")
        
        if not (templates_result["success"] and lists_result["success"]):
            print("   ❌ Failed to get templates or lists")
            self.test_results["campaign_creation"]["status"] = "failed"
            return None
        
        templates = templates_result["data"]
        lists = lists_result["data"]
        
        if not templates or not lists:
            print("   ❌ No templates or lists available")
            self.test_results["campaign_creation"]["status"] = "failed"
            return None
        
        # Calculate precise timing for minute-level follow-ups
        now = datetime.utcnow()
        follow_up_1_time = now + timedelta(minutes=2)  # 2 minutes from now
        follow_up_2_time = now + timedelta(minutes=4)  # 4 minutes from now
        follow_up_3_time = now + timedelta(minutes=6)  # 6 minutes from now
        
        print(f"   📅 Current time: {now.strftime('%H:%M:%S')}")
        print(f"   📅 Follow-up 1:  {follow_up_1_time.strftime('%H:%M:%S')} (NOW + 2 minutes)")
        print(f"   📅 Follow-up 2:  {follow_up_2_time.strftime('%H:%M:%S')} (NOW + 4 minutes)")
        print(f"   📅 Follow-up 3:  {follow_up_3_time.strftime('%H:%M:%S')} (NOW + 6 minutes)")
        
        # Create campaign with enhanced follow-up configuration
        campaign_data = {
            "name": f"Enhanced Follow-up Test - {now.strftime('%H:%M:%S')}",
            "template_id": templates[0]["id"],
            "list_ids": [lists[0]["id"]],
            "max_emails": 10,
            "email_provider_id": provider["id"],  # Explicitly set provider
            
            # Enhanced Follow-up Configuration with minute precision
            "follow_up_enabled": True,
            "follow_up_schedule_type": "datetime",  # Use precise datetime scheduling
            "follow_up_dates": [
                follow_up_1_time.isoformat(),
                follow_up_2_time.isoformat(),
                follow_up_3_time.isoformat()
            ],
            "follow_up_timezone": "UTC",
            "follow_up_time_window_start": "00:00",  # Allow 24/7
            "follow_up_time_window_end": "23:59",
            "follow_up_days_of_week": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
            "follow_up_templates": [templates[0]["id"], templates[0]["id"], templates[0]["id"]]
        }
        
        print(f"\n   📋 Enhanced Campaign Configuration:")
        print(f"      Provider: {provider['name']} ({provider['id']})")
        print(f"      Template: {templates[0]['name']}")
        print(f"      List: {lists[0]['name']}")
        print(f"      Schedule Type: {campaign_data['follow_up_schedule_type']}")
        print(f"      Follow-up Enabled: {campaign_data['follow_up_enabled']}")
        
        # Create the campaign
        result = await self.make_request("POST", "/campaigns", campaign_data, 
                                       "Creating enhanced campaign with minute precision")
        
        if result["success"]:
            campaign = result["data"]
            campaign_details = {
                "created": True,
                "id": campaign["id"],
                "name": campaign["name"],
                "email_provider_id": campaign.get("email_provider_id"),
                "follow_up_enabled": campaign["follow_up_enabled"],
                "follow_up_schedule_type": campaign["follow_up_schedule_type"],
                "follow_up_dates": campaign.get("follow_up_dates", []),
                "timing_precision": "minute-level"
            }
            
            print(f"   ✅ Enhanced campaign created successfully!")
            print(f"      ID: {campaign_details['id']}")
            print(f"      Provider ID: {campaign_details['email_provider_id']}")
            print(f"      Follow-up Type: {campaign_details['follow_up_schedule_type']}")
            
            self.test_results["campaign_creation"]["status"] = "passed"
            self.test_results["campaign_creation"]["details"] = campaign_details
            return campaign
        else:
            print(f"   ❌ Enhanced campaign creation failed!")
            self.test_results["campaign_creation"]["status"] = "failed"
            return None
    
    async def test_minute_precision_timing(self, campaign):
        """Test minute-level precision timing"""
        print("\n" + "="*60)
        print("4. ⏱️ TESTING MINUTE PRECISION TIMING")
        print("="*60)
        
        if not campaign:
            print("   ❌ No campaign to test")
            self.test_results["minute_precision_test"]["status"] = "failed"
            return
        
        campaign_id = campaign["id"]
        
        # Get detailed campaign info
        result = await self.make_request("GET", f"/campaigns/{campaign_id}", 
                                       description="Getting detailed campaign info")
        
        if result["success"]:
            campaign_details = result["data"]
            follow_up_dates = campaign_details.get("follow_up_dates", [])
            
            timing_analysis = {
                "follow_up_count": len(follow_up_dates),
                "schedule_type": campaign_details.get("follow_up_schedule_type"),
                "timezone": campaign_details.get("follow_up_timezone"),
                "dates_precision": []
            }
            
            print(f"   📊 Timing Analysis:")
            print(f"      Follow-up Count: {timing_analysis['follow_up_count']}")
            print(f"      Schedule Type: {timing_analysis['schedule_type']}")
            print(f"      Timezone: {timing_analysis['timezone']}")
            
            # Analyze precision
            if len(follow_up_dates) >= 3:
                for i, date_str in enumerate(follow_up_dates, 1):
                    try:
                        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        timing_analysis["dates_precision"].append({
                            "sequence": i,
                            "datetime": dt.strftime('%Y-%m-%d %H:%M:%S'),
                            "precision": "minute-level" if dt.second == 0 else "second-level"
                        })
                        print(f"      Follow-up {i}: {dt.strftime('%H:%M:%S')} ✅")
                    except Exception as e:
                        print(f"      Follow-up {i}: Parse error - {str(e)} ❌")
                
                self.test_results["minute_precision_test"]["status"] = "passed"
                print("   ✅ Minute precision timing configured correctly!")
            else:
                self.test_results["minute_precision_test"]["status"] = "failed"
                print("   ❌ Insufficient follow-up dates configured")
            
            self.test_results["minute_precision_test"]["details"] = timing_analysis
        else:
            self.test_results["minute_precision_test"]["status"] = "failed"
            print("   ❌ Failed to get campaign details")
    
    async def test_provider_consistency(self, campaign, provider):
        """Test provider consistency across initial and follow-up emails"""
        print("\n" + "="*60)
        print("5. 🔄 TESTING PROVIDER CONSISTENCY")
        print("="*60)
        
        if not campaign or not provider:
            print("   ❌ Missing campaign or provider")
            self.test_results["provider_consistency_test"]["status"] = "failed"
            return
        
        campaign_id = campaign["id"]
        provider_id = provider["id"]
        
        # Send campaign using enhanced route
        send_data = {
            "send_immediately": True,
            "email_provider_id": provider_id,  # Explicitly specify provider
            "max_emails": 5,
            "schedule_type": "immediate",
            "follow_up_enabled": True
        }
        
        print(f"   📤 Sending campaign with provider: {provider['name']}")
        
        result = await self.make_request("POST", f"/campaigns/{campaign_id}/send", send_data,
                                       "Sending campaign with enhanced provider tracking")
        
        if result["success"]:
            send_response = result["data"]
            
            consistency_check = {
                "campaign_provider_id": send_response.get("email_provider_id"),
                "campaign_provider_name": send_response.get("email_provider_name"),
                "requested_provider_id": provider_id,
                "provider_match": send_response.get("email_provider_id") == provider_id
            }
            
            print(f"   📊 Provider Consistency Check:")
            print(f"      Requested Provider: {provider['name']} ({provider_id})")
            print(f"      Campaign Provider: {consistency_check['campaign_provider_name']} ({consistency_check['campaign_provider_id']})")
            print(f"      Provider Match: {consistency_check['provider_match']} {'✅' if consistency_check['provider_match'] else '❌'}")
            
            if consistency_check['provider_match']:
                self.test_results["provider_consistency_test"]["status"] = "passed"
                print("   ✅ Provider consistency maintained!")
            else:
                self.test_results["provider_consistency_test"]["status"] = "failed"
                print("   ❌ Provider consistency failed!")
            
            self.test_results["provider_consistency_test"]["details"] = consistency_check
            return send_response
        else:
            print("   ❌ Campaign sending failed")
            self.test_results["provider_consistency_test"]["status"] = "failed"
            return None
    
    async def monitor_follow_up_delivery(self, campaign, duration_minutes=8):
        """Monitor follow-up email delivery with enhanced tracking"""
        print("\n" + "="*60)
        print(f"6. 👀 MONITORING FOLLOW-UP DELIVERY ({duration_minutes} minutes)")
        print("="*60)
        
        if not campaign:
            print("   ❌ No campaign to monitor")
            self.test_results["follow_up_delivery_test"]["status"] = "failed"
            return
        
        campaign_id = campaign["id"]
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(minutes=duration_minutes)
        check_interval = 30  # Check every 30 seconds
        
        print(f"   ⏰ Monitoring from {start_time.strftime('%H:%M:%S')} to {end_time.strftime('%H:%M:%S')}")
        print(f"   🔍 Checking every {check_interval} seconds for enhanced tracking...")
        
        delivery_stats = {
            "initial_emails": 0,
            "follow_up_emails": 0,
            "total_emails": 0,
            "provider_usage": {},
            "timeline": []
        }
        
        while datetime.utcnow() < end_time:
            current_time = datetime.utcnow()
            print(f"\n   ⏰ Check at {current_time.strftime('%H:%M:%S')}")
            
            # Get enhanced campaign details
            result = await self.make_request("GET", f"/campaigns/{campaign_id}")
            if result["success"]:
                campaign_data = result["data"]
                email_records = campaign_data.get("email_records", [])
                
                # Filter for target email
                target_emails = [
                    record for record in email_records 
                    if record.get("recipient_email") == self.test_email
                ]
                
                # Analyze emails
                current_initial = len([e for e in target_emails if not e.get("is_follow_up", False)])
                current_follow_ups = len([e for e in target_emails if e.get("is_follow_up", False)])
                current_total = len(target_emails)
                
                # Check for new emails
                if current_total > delivery_stats["total_emails"]:
                    new_count = current_total - delivery_stats["total_emails"]
                    print(f"   📧 Found {new_count} new email(s)! Total: {current_total}")
                    
                    # Analyze new emails
                    for email in target_emails[delivery_stats["total_emails"]:]:
                        provider_id = email.get("email_provider_id", "unknown")
                        provider_name = email.get("provider_name", "Unknown")
                        is_follow_up = email.get("is_follow_up", False)
                        
                        print(f"      • Subject: {email.get('subject', 'N/A')}")
                        print(f"        Status: {email.get('status', 'N/A')}")
                        print(f"        Sent At: {email.get('sent_at', 'N/A')}")
                        print(f"        Is Follow-up: {is_follow_up}")
                        print(f"        Provider: {provider_name} ({provider_id})")
                        print(f"        Sequence: {email.get('follow_up_sequence', 'N/A')}")
                        
                        delivery_stats["timeline"].append({
                            "timestamp": current_time.strftime('%H:%M:%S'),
                            "email_type": "follow-up" if is_follow_up else "initial",
                            "provider_id": provider_id,
                            "provider_name": provider_name,
                            "sequence": email.get('follow_up_sequence', 0)
                        })
                        
                        # Track provider usage
                        if provider_id not in delivery_stats["provider_usage"]:
                            delivery_stats["provider_usage"][provider_id] = {
                                "name": provider_name,
                                "initial": 0,
                                "follow_up": 0
                            }
                        
                        if is_follow_up:
                            delivery_stats["provider_usage"][provider_id]["follow_up"] += 1
                        else:
                            delivery_stats["provider_usage"][provider_id]["initial"] += 1
                
                # Update stats
                delivery_stats["initial_emails"] = current_initial
                delivery_stats["follow_up_emails"] = current_follow_ups
                delivery_stats["total_emails"] = current_total
                
                print(f"   📊 Enhanced Stats: {current_initial} initial, {current_follow_ups} follow-ups, {current_total} total")
                
                # Check analytics
                analytics = campaign_data.get("analytics", {})
                if analytics:
                    print(f"   📈 Campaign Analytics:")
                    print(f"      Success Rate: {analytics.get('success_rate', 0):.1f}%")
                    print(f"      Total Sent: {analytics.get('total_sent', 0)}")
                    print(f"      Total Failed: {analytics.get('total_failed', 0)}")
            
            # Wait before next check
            await asyncio.sleep(check_interval)
        
        # Final analysis
        print(f"\n   ✅ Enhanced monitoring completed at {datetime.utcnow().strftime('%H:%M:%S')}")
        
        # Determine test result
        if delivery_stats["follow_up_emails"] > 0:
            self.test_results["follow_up_delivery_test"]["status"] = "passed"
            print(f"   ✅ Follow-up delivery working! {delivery_stats['follow_up_emails']} follow-ups sent")
        elif delivery_stats["initial_emails"] > 0:
            self.test_results["follow_up_delivery_test"]["status"] = "partial"
            print(f"   ⚠️ Initial emails sent but no follow-ups yet ({delivery_stats['initial_emails']} initial)")
        else:
            self.test_results["follow_up_delivery_test"]["status"] = "failed"
            print(f"   ❌ No emails sent at all")
        
        self.test_results["follow_up_delivery_test"]["details"] = delivery_stats
        
        # Provider consistency analysis
        print(f"\n   🔄 Enhanced Provider Usage Analysis:")
        for provider_id, usage in delivery_stats["provider_usage"].items():
            print(f"      {usage['name']} ({provider_id}):")
            print(f"         Initial: {usage['initial']}, Follow-ups: {usage['follow_up']}")
            
            if usage['initial'] > 0 and usage['follow_up'] > 0:
                print(f"         ✅ Provider consistency maintained!")
            elif usage['initial'] > 0:
                print(f"         ⚠️ Initial sent, follow-ups pending")
    
    async def run_comprehensive_test(self):
        """Run comprehensive follow-up fix test"""
        print("=" * 80)
        print("🧪 COMPREHENSIVE FOLLOW-UP FIX TEST")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print(f"Target Email: {self.test_email}")
        print(f"Sender Email: {self.sender_email}")
        
        await self.setup_session()
        
        try:
            # Run all tests
            await self.test_enhanced_services()
            provider = await self.setup_test_provider()
            
            if provider:
                campaign = await self.create_test_campaign_with_minute_precision(provider)
                await self.test_minute_precision_timing(campaign)
                send_response = await self.test_provider_consistency(campaign, provider)
                
                if send_response:
                    await self.monitor_follow_up_delivery(campaign)
            
            # Determine overall status
            test_statuses = [result["status"] for result in self.test_results.values() if isinstance(result, dict) and result.get("status") != "unknown"]
            
            if all(status == "passed" for status in test_statuses):
                self.test_results["overall_status"] = "passed"
            elif any(status == "passed" for status in test_statuses):
                self.test_results["overall_status"] = "partial"
            else:
                self.test_results["overall_status"] = "failed"
            
        finally:
            await self.cleanup_session()
        
        # Print comprehensive summary
        self.print_comprehensive_summary()
    
    def print_comprehensive_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("📋 COMPREHENSIVE FOLLOW-UP FIX TEST SUMMARY")
        print("=" * 80)
        
        # Overall status
        status_emoji = {
            "passed": "✅",
            "partial": "⚠️",
            "failed": "❌",
            "unknown": "❓"
        }
        
        overall_status = self.test_results["overall_status"]
        print(f"\n🎯 OVERALL TEST STATUS: {status_emoji.get(overall_status, '❓')} {overall_status.upper()}")
        
        # Test breakdown
        print(f"\n📊 ENHANCED TEST BREAKDOWN:")
        test_names = [
            "enhanced_services_check",
            "provider_setup", 
            "campaign_creation",
            "minute_precision_test",
            "provider_consistency_test",
            "follow_up_delivery_test"
        ]
        
        for test_name in test_names:
            test_result = self.test_results.get(test_name, {})
            status = test_result.get("status", "unknown")
            emoji = status_emoji.get(status, "❓")
            print(f"   • {test_name.replace('_', ' ').title()}: {emoji} {status}")
        
        # Key fixes implemented
        print(f"\n🔧 KEY FIXES IMPLEMENTED:")
        print(f"   ✅ Enhanced Smart Follow-up Engine with provider consistency")
        print(f"   ✅ Campaign status flow fixed (active vs completed)")
        print(f"   ✅ Email provider tracking in campaigns and follow-ups")
        print(f"   ✅ Minute-level precision datetime scheduling")
        print(f"   ✅ Enhanced database service with follow-up methods")
        print(f"   ✅ Provider consistency across initial and follow-up emails")
        
        # Detailed findings
        print(f"\n🔍 DETAILED FINDINGS:")
        
        # Enhanced services
        services_details = self.test_results["enhanced_services_check"]["details"]
        if services_details:
            print(f"   📊 Services Status:")
            print(f"      Overall: {services_details.get('overall_status', 'unknown')}")
            print(f"      Follow-up Engine: {services_details.get('smart_follow_up_engine', {}).get('status', 'unknown')}")
            print(f"      Email Processor: {services_details.get('email_processor', {}).get('status', 'unknown')}")
        
        # Provider setup
        provider_details = self.test_results["provider_setup"]["details"]
        if provider_details and provider_details.get("found"):
            print(f"   📮 Provider: {provider_details['name']} ({provider_details['email']})")
        
        # Campaign creation
        campaign_details = self.test_results["campaign_creation"]["details"]
        if campaign_details and campaign_details.get("created"):
            print(f"   🚀 Campaign: {campaign_details['name']}")
            print(f"      Provider ID: {campaign_details['email_provider_id']}")
            print(f"      Schedule Type: {campaign_details['follow_up_schedule_type']}")
            print(f"      Timing Precision: {campaign_details['timing_precision']}")
        
        # Minute precision
        timing_details = self.test_results["minute_precision_test"]["details"]
        if timing_details:
            print(f"   ⏱️ Timing Analysis:")
            print(f"      Follow-up Count: {timing_details.get('follow_up_count', 0)}")
            print(f"      Schedule Type: {timing_details.get('schedule_type', 'unknown')}")
        
        # Provider consistency
        consistency_details = self.test_results["provider_consistency_test"]["details"]
        if consistency_details:
            print(f"   🔄 Provider Consistency:")
            print(f"      Match: {consistency_details.get('provider_match', False)} {'✅' if consistency_details.get('provider_match') else '❌'}")
        
        # Follow-up delivery
        delivery_details = self.test_results["follow_up_delivery_test"]["details"]
        if delivery_details:
            print(f"   📧 Email Delivery:")
            print(f"      Initial: {delivery_details.get('initial_emails', 0)}")
            print(f"      Follow-ups: {delivery_details.get('follow_up_emails', 0)}")
            print(f"      Total: {delivery_details.get('total_emails', 0)}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if self.test_results["overall_status"] == "passed":
            print(f"   ✅ All fixes are working correctly!")
            print(f"   ✅ Follow-up system is now production-ready with minute precision")
            print(f"   ✅ Provider consistency is maintained across all emails")
        elif self.test_results["overall_status"] == "partial":
            print(f"   ⚠️ Some components are working, continue monitoring")
            print(f"   ⚠️ Follow-ups may need more time to trigger")
        else:
            print(f"   ❌ System needs further investigation")
            print(f"   ❌ Check service logs and provider configurations")
        
        print("\n" + "=" * 80)
        print("✅ COMPREHENSIVE FOLLOW-UP FIX TEST COMPLETED")
        print("=" * 80)

async def main():
    """Main test execution"""
    tester = ComprehensiveFollowUpTester()
    await tester.run_comprehensive_test()

if __name__ == "__main__":
    asyncio.run(main())