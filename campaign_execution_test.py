#!/usr/bin/env python3
"""
Campaign Execution and Monitoring Test
Tests campaign sending, status monitoring, and follow-up execution
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
import sys
import os
import time

# Backend URL from environment
BACKEND_URL = "https://b40c5c4f-de80-4df5-bbd3-3623f2621a6f.preview.emergentagent.com/api"

class CampaignExecutionTester:
    def __init__(self):
        self.session = None
        self.campaign_id = "cbfe8cc7-6fac-4229-90cf-448a8f75f270"  # From test_result.md
        self.results = {
            "campaign_send": {"status": "unknown", "data": {}},
            "campaign_status": {"status": "unknown", "data": {}},
            "email_records": {"status": "unknown", "data": []},
            "services_status": {"status": "unknown", "data": {}},
            "follow_up_monitoring": {"status": "unknown", "data": {}},
            "overall_status": "unknown"
        }
    
    async def setup_session(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession()
    
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    async def test_post_endpoint(self, endpoint, data, description):
        """Test a POST endpoint and return results"""
        try:
            print(f"\n🔍 Testing {description}...")
            print(f"   URL: {BACKEND_URL}{endpoint}")
            print(f"   Data: {json.dumps(data, indent=2)}")
            
            async with self.session.post(f"{BACKEND_URL}{endpoint}", json=data) as response:
                status_code = response.status
                
                if status_code in [200, 201]:
                    response_data = await response.json()
                    print(f"   ✅ SUCCESS - Status: {status_code}")
                    print(f"   Response: {json.dumps(response_data, indent=2)}")
                    return {"success": True, "status_code": status_code, "data": response_data}
                else:
                    error_text = await response.text()
                    print(f"   ❌ FAILED - Status: {status_code}")
                    print(f"   Error: {error_text}")
                    return {"success": False, "status_code": status_code, "error": error_text}
                    
        except Exception as e:
            print(f"   ❌ EXCEPTION - {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def test_get_endpoint(self, endpoint, description):
        """Test a GET endpoint and return results"""
        try:
            print(f"\n🔍 Testing {description}...")
            print(f"   URL: {BACKEND_URL}{endpoint}")
            
            async with self.session.get(f"{BACKEND_URL}{endpoint}") as response:
                status_code = response.status
                
                if status_code == 200:
                    data = await response.json()
                    print(f"   ✅ SUCCESS - Status: {status_code}")
                    return {"success": True, "status_code": status_code, "data": data}
                else:
                    error_text = await response.text()
                    print(f"   ❌ FAILED - Status: {status_code}")
                    print(f"   Error: {error_text}")
                    return {"success": False, "status_code": status_code, "error": error_text}
                    
        except Exception as e:
            print(f"   ❌ EXCEPTION - {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def step_7_start_campaign_execution(self):
        """Step 7: Start Campaign Execution"""
        print("\n" + "="*60)
        print("📤 STEP 7: START CAMPAIGN EXECUTION")
        print("="*60)
        
        # Prepare campaign send request
        send_data = {
            "send_immediately": True,
            "email_provider_id": "90e8c90e-770c-42ef-9bb9-78631b77d793",  # Use the correct provider ID
            "max_emails": 1000,
            "schedule_type": "immediate",
            "follow_up_enabled": True,
            "follow_up_intervals": [1, 3, 5],  # 1, 3, 5 minute intervals as mentioned
            "follow_up_templates": []
        }
        
        result = await self.test_post_endpoint(
            f"/campaigns/{self.campaign_id}/send", 
            send_data, 
            f"Campaign Send (ID: {self.campaign_id})"
        )
        
        self.results["campaign_send"] = result
        
        if result["success"]:
            print(f"   📊 Campaign send initiated successfully!")
            send_response = result["data"]
            print(f"   Campaign Status: {send_response.get('status', 'Unknown')}")
            print(f"   Emails to Send: {send_response.get('emails_to_send', 'Unknown')}")
            print(f"   Provider Used: {send_response.get('email_provider', 'Unknown')}")
            return True
        else:
            print(f"   ❌ Campaign send failed!")
            return False
    
    async def step_8_monitor_campaign_status(self):
        """Step 8: Monitor Campaign Status"""
        print("\n" + "="*60)
        print("📊 STEP 8: MONITOR CAMPAIGN STATUS")
        print("="*60)
        
        # Get detailed campaign information
        result = await self.test_get_endpoint(
            f"/campaigns/{self.campaign_id}", 
            f"Campaign Details (ID: {self.campaign_id})"
        )
        
        self.results["campaign_status"] = result
        
        if result["success"]:
            campaign_data = result["data"]
            print(f"   📊 Campaign Status Monitoring:")
            print(f"   Campaign Name: {campaign_data.get('name', 'Unknown')}")
            print(f"   Status: {campaign_data.get('status', 'Unknown')}")
            print(f"   Follow-up Enabled: {campaign_data.get('follow_up_enabled', False)}")
            print(f"   Follow-up Schedule Type: {campaign_data.get('follow_up_schedule_type', 'Unknown')}")
            
            # Check email records
            email_records = campaign_data.get('email_records', [])
            self.results["email_records"]["data"] = email_records
            self.results["email_records"]["status"] = "working"
            
            print(f"   📧 Email Records: {len(email_records)} found")
            
            # Analyze email records
            sent_emails = [r for r in email_records if r.get('status') == 'sent']
            failed_emails = [r for r in email_records if r.get('status') == 'failed']
            pending_emails = [r for r in email_records if r.get('status') == 'pending']
            
            print(f"      - Sent: {len(sent_emails)}")
            print(f"      - Failed: {len(failed_emails)}")
            print(f"      - Pending: {len(pending_emails)}")
            
            # Show recent email records
            for i, record in enumerate(email_records[:3]):  # Show first 3
                print(f"      Email {i+1}:")
                print(f"        Recipient: {record.get('recipient_email', 'Unknown')}")
                print(f"        Status: {record.get('status', 'Unknown')}")
                print(f"        Sent At: {record.get('sent_at', 'Not sent')}")
                print(f"        Subject: {record.get('subject', 'No subject')}")
            
            # Check analytics
            analytics = campaign_data.get('analytics', {})
            if analytics:
                print(f"   📈 Campaign Analytics:")
                print(f"      - Total Sent: {analytics.get('total_sent', 0)}")
                print(f"      - Total Failed: {analytics.get('total_failed', 0)}")
                print(f"      - Success Rate: {analytics.get('success_rate', 0):.1f}%")
            
            return True
        else:
            print(f"   ❌ Failed to get campaign status!")
            return False
    
    async def step_9_check_services_status(self):
        """Step 9: Check Services Status"""
        print("\n" + "="*60)
        print("🔧 STEP 9: CHECK SERVICES STATUS")
        print("="*60)
        
        # Get services status
        result = await self.test_get_endpoint("/services/status", "Services Status")
        
        self.results["services_status"] = result
        
        if result["success"]:
            services_data = result["data"]
            print(f"   📊 Services Status Overview:")
            print(f"   Overall Status: {services_data.get('overall_status', 'Unknown')}")
            
            services = services_data.get('services', {})
            
            # Check Follow-up Engine
            follow_up_engine = services.get('smart_follow_up_engine', {})
            follow_up_status = follow_up_engine.get('status', 'unknown')
            print(f"   🔄 Follow-up Engine: {follow_up_status}")
            print(f"      Description: {follow_up_engine.get('description', 'N/A')}")
            
            # Check Email Processor
            email_processor = services.get('email_processor', {})
            email_proc_status = email_processor.get('status', 'unknown')
            print(f"   📧 Email Processor: {email_proc_status}")
            print(f"      Description: {email_processor.get('description', 'N/A')}")
            
            # Check monitored providers
            monitored_providers = email_processor.get('monitored_providers', [])
            print(f"      Monitored Providers: {len(monitored_providers)}")
            
            for provider in monitored_providers:
                print(f"        - {provider.get('name', 'Unknown')} ({provider.get('provider_type', 'Unknown')})")
                print(f"          Last Scan: {provider.get('last_scan', 'Never')}")
                print(f"          IMAP Host: {provider.get('imap_host', 'N/A')}")
            
            # Check if IMAP monitoring is working
            if monitored_providers:
                print(f"   ✅ IMAP monitoring is active for {len(monitored_providers)} providers")
            else:
                print(f"   ⚠️  No providers being monitored for IMAP")
            
            return True
        else:
            print(f"   ❌ Failed to get services status!")
            return False
    
    async def monitor_follow_up_execution(self):
        """Monitor for follow-up execution"""
        print("\n" + "="*60)
        print("⏰ MONITORING FOLLOW-UP EXECUTION")
        print("="*60)
        
        print("   Monitoring for follow-up emails (checking every 30 seconds for 5 minutes)...")
        
        start_time = datetime.now()
        monitoring_duration = timedelta(minutes=5)
        check_interval = 30  # seconds
        
        follow_up_detected = False
        
        while datetime.now() - start_time < monitoring_duration:
            # Check campaign status for new email records
            result = await self.test_get_endpoint(
                f"/campaigns/{self.campaign_id}", 
                f"Follow-up Monitoring Check"
            )
            
            if result["success"]:
                campaign_data = result["data"]
                email_records = campaign_data.get('email_records', [])
                
                # Look for follow-up emails
                follow_up_emails = [r for r in email_records if 'follow' in r.get('subject', '').lower()]
                
                if follow_up_emails and not follow_up_detected:
                    follow_up_detected = True
                    print(f"   ✅ Follow-up emails detected! Found {len(follow_up_emails)} follow-up emails")
                    
                    for follow_up in follow_up_emails:
                        print(f"      - Subject: {follow_up.get('subject', 'No subject')}")
                        print(f"        Status: {follow_up.get('status', 'Unknown')}")
                        print(f"        Scheduled: {follow_up.get('scheduled_at', 'Not scheduled')}")
                
                print(f"   📊 Current email records: {len(email_records)} total")
                
                # Check if we should continue monitoring
                if follow_up_detected:
                    print(f"   ✅ Follow-up execution confirmed - monitoring complete")
                    break
            
            # Wait before next check
            print(f"   ⏳ Waiting {check_interval} seconds before next check...")
            await asyncio.sleep(check_interval)
        
        if not follow_up_detected:
            print(f"   ⚠️  No follow-up emails detected during monitoring period")
        
        self.results["follow_up_monitoring"]["status"] = "working" if follow_up_detected else "no_activity"
        self.results["follow_up_monitoring"]["data"] = {"follow_up_detected": follow_up_detected}
        
        return follow_up_detected
    
    async def run_campaign_execution_test(self):
        """Run complete campaign execution and monitoring test"""
        print("=" * 80)
        print("🚀 CAMPAIGN EXECUTION AND MONITORING TEST")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Campaign ID: {self.campaign_id}")
        print(f"Test Time: {datetime.now().isoformat()}")
        
        await self.setup_session()
        
        try:
            # Execute all steps
            step_7_success = await self.step_7_start_campaign_execution()
            step_8_success = await self.step_8_monitor_campaign_status()
            step_9_success = await self.step_9_check_services_status()
            
            # Monitor follow-up execution
            follow_up_success = await self.monitor_follow_up_execution()
            
            # Determine overall status
            if step_7_success and step_8_success and step_9_success:
                if follow_up_success:
                    self.results["overall_status"] = "fully_working"
                else:
                    self.results["overall_status"] = "partially_working"
            else:
                self.results["overall_status"] = "failed"
            
        finally:
            await self.cleanup_session()
        
        # Print comprehensive summary
        self.print_execution_summary()
    
    def print_execution_summary(self):
        """Print campaign execution test summary"""
        print("\n" + "=" * 80)
        print("📋 CAMPAIGN EXECUTION TEST SUMMARY")
        print("=" * 80)
        
        # Overall Status
        status_emoji = {
            "fully_working": "✅",
            "partially_working": "⚠️",
            "failed": "❌",
            "unknown": "❓"
        }
        
        overall_status = self.results["overall_status"]
        print(f"\n🎯 OVERALL TEST STATUS: {status_emoji.get(overall_status, '❓')} {overall_status.upper()}")
        
        # Step Results
        print(f"\n📊 STEP RESULTS:")
        
        # Step 7: Campaign Send
        send_status = "✅ SUCCESS" if self.results["campaign_send"].get("success") else "❌ FAILED"
        print(f"   Step 7 - Campaign Send: {send_status}")
        
        # Step 8: Campaign Status
        status_check = "✅ SUCCESS" if self.results["campaign_status"].get("success") else "❌ FAILED"
        print(f"   Step 8 - Campaign Status: {status_check}")
        
        # Step 9: Services Status
        services_check = "✅ SUCCESS" if self.results["services_status"].get("success") else "❌ FAILED"
        print(f"   Step 9 - Services Status: {services_check}")
        
        # Follow-up Monitoring
        follow_up_status = self.results["follow_up_monitoring"]["status"]
        follow_up_emoji = "✅" if follow_up_status == "working" else "⚠️" if follow_up_status == "no_activity" else "❌"
        print(f"   Follow-up Monitoring: {follow_up_emoji} {follow_up_status.upper()}")
        
        # Detailed Analysis
        print(f"\n🔍 DETAILED ANALYSIS:")
        
        # Email Records Analysis
        email_records = self.results["email_records"]["data"]
        if email_records:
            sent_count = len([r for r in email_records if r.get('status') == 'sent'])
            failed_count = len([r for r in email_records if r.get('status') == 'failed'])
            pending_count = len([r for r in email_records if r.get('status') == 'pending'])
            
            print(f"   📧 Email Records: {len(email_records)} total")
            print(f"      - Sent: {sent_count}")
            print(f"      - Failed: {failed_count}")
            print(f"      - Pending: {pending_count}")
        else:
            print(f"   📧 Email Records: No records found")
        
        # Services Analysis
        services_data = self.results["services_status"].get("data", {})
        if services_data and "services" in services_data:
            services = services_data["services"]
            
            follow_up_running = services.get("smart_follow_up_engine", {}).get("status") == "running"
            email_proc_running = services.get("email_processor", {}).get("status") == "running"
            
            print(f"   🔧 Background Services:")
            print(f"      - Follow-up Engine: {'✅ Running' if follow_up_running else '❌ Stopped'}")
            print(f"      - Email Processor: {'✅ Running' if email_proc_running else '❌ Stopped'}")
            
            # IMAP Monitoring
            monitored_providers = services.get("email_processor", {}).get("monitored_providers", [])
            print(f"      - IMAP Monitoring: {len(monitored_providers)} providers")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        
        if not self.results["campaign_send"].get("success"):
            print("   • Check campaign send endpoint - may need debugging")
        
        if not self.results["campaign_status"].get("success"):
            print("   • Verify campaign exists and is accessible")
        
        if self.results["follow_up_monitoring"]["status"] == "no_activity":
            print("   • Follow-up emails may need more time to trigger")
            print("   • Check follow-up engine configuration and timing")
        
        services_data = self.results["services_status"].get("data", {})
        if services_data and "services" in services_data:
            services = services_data["services"]
            if services.get("smart_follow_up_engine", {}).get("status") != "running":
                print("   • Start the follow-up engine for automated follow-ups")
            if services.get("email_processor", {}).get("status") != "running":
                print("   • Start the email processor for IMAP monitoring")
        
        print("\n" + "=" * 80)
        print("✅ CAMPAIGN EXECUTION TEST COMPLETED")
        print("=" * 80)

async def main():
    """Main test execution"""
    tester = CampaignExecutionTester()
    await tester.run_campaign_execution_test()

if __name__ == "__main__":
    asyncio.run(main())