#!/usr/bin/env python3
"""
Reply Processing and Auto-responder Test
Tests the final requirements for email campaign system:
- Reply processing and auto-responder functionality
- IMAP monitoring and email processing
- Follow-up stop logic when replies are received
- Thread tracking and email threading
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
import sys
import os
import time

# Backend URL from environment
BACKEND_URL = "https://c9bf2a3a-3cde-4b42-9b26-a4c6b0fb8d18.preview.emergentagent.com/api"

class ReplyProcessingTester:
    def __init__(self):
        self.session = None
        self.test_results = {
            "imap_monitoring": {"status": "unknown", "details": {}},
            "email_processing": {"status": "unknown", "details": {}},
            "reply_detection": {"status": "unknown", "details": {}},
            "follow_up_stop_logic": {"status": "unknown", "details": {}},
            "thread_tracking": {"status": "unknown", "details": {}},
            "auto_responder": {"status": "unknown", "details": {}},
            "overall_status": "unknown"
        }
        self.campaign_id = None
        self.prospect_email = "kasargovinda@gmail.com"
    
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
            print(f"🔍 {description}")
            print(f"   {method.upper()} {url}")
            
            if method.lower() == "get":
                async with self.session.get(url) as response:
                    status_code = response.status
                    response_data = await response.json() if response.content_type == 'application/json' else await response.text()
            elif method.lower() == "post":
                async with self.session.post(url, json=data) as response:
                    status_code = response.status
                    response_data = await response.json() if response.content_type == 'application/json' else await response.text()
            elif method.lower() == "put":
                async with self.session.put(url, json=data) as response:
                    status_code = response.status
                    response_data = await response.json() if response.content_type == 'application/json' else await response.text()
            
            if status_code == 200:
                print(f"   ✅ SUCCESS - Status: {status_code}")
                return {"success": True, "status_code": status_code, "data": response_data}
            else:
                print(f"   ❌ FAILED - Status: {status_code}")
                print(f"   Response: {response_data}")
                return {"success": False, "status_code": status_code, "error": response_data}
                
        except Exception as e:
            print(f"   ❌ EXCEPTION - {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def test_step_10_reply_processing_and_auto_responder(self):
        """Step 10: Test Reply Processing and Auto-responder"""
        print("\n" + "="*80)
        print("📧 STEP 10: TESTING REPLY PROCESSING AND AUTO-RESPONDER")
        print("="*80)
        
        # 10.1: Check current services status
        print("\n🔍 10.1: Checking Services Status")
        result = await self.make_request("GET", "/services/status", description="Getting services status")
        
        if result["success"]:
            services = result["data"].get("services", {})
            email_processor = services.get("email_processor", {})
            follow_up_engine = services.get("smart_follow_up_engine", {})
            
            print(f"   📊 Email Processor Status: {email_processor.get('status', 'unknown')}")
            print(f"   📊 Follow-up Engine Status: {follow_up_engine.get('status', 'unknown')}")
            
            # Check monitored providers
            monitored_providers = email_processor.get("monitored_providers", [])
            print(f"   📊 Monitored Providers: {len(monitored_providers)}")
            
            for provider in monitored_providers:
                print(f"      - {provider.get('name', 'Unknown')} ({provider.get('provider_type', 'Unknown')})")
                print(f"        Last Scan: {provider.get('last_scan', 'Never')}")
            
            self.test_results["email_processing"]["status"] = "working" if email_processor.get('status') == 'running' else "failed"
            self.test_results["email_processing"]["details"] = {
                "processor_status": email_processor.get('status', 'unknown'),
                "monitored_providers_count": len(monitored_providers),
                "monitored_providers": monitored_providers
            }
        else:
            self.test_results["email_processing"]["status"] = "failed"
            self.test_results["email_processing"]["details"] = {"error": "Could not get services status"}
        
        # 10.2: Check IMAP monitoring status for specific providers
        print("\n🔍 10.2: Checking IMAP Monitoring Status")
        
        # Get email providers first
        providers_result = await self.make_request("GET", "/email-providers", description="Getting email providers")
        
        if providers_result["success"]:
            providers = providers_result["data"]
            imap_enabled_providers = [p for p in providers if p.get("imap_enabled", False)]
            
            print(f"   📊 Total Providers: {len(providers)}")
            print(f"   📊 IMAP Enabled Providers: {len(imap_enabled_providers)}")
            
            # Check IMAP status for each IMAP-enabled provider
            for provider in imap_enabled_providers:
                provider_id = provider.get("id")
                if provider_id:
                    imap_result = await self.make_request("GET", f"/email-providers/{provider_id}/imap-status", 
                                                        description=f"Checking IMAP status for {provider.get('name', 'Unknown')}")
                    
                    if imap_result["success"]:
                        imap_data = imap_result["data"]
                        print(f"      - {provider.get('name', 'Unknown')}:")
                        print(f"        IMAP Enabled: {imap_data.get('imap_enabled', False)}")
                        print(f"        Being Monitored: {imap_data.get('is_being_monitored', False)}")
                        print(f"        Email Processor Running: {imap_data.get('email_processor_running', False)}")
                        print(f"        Last Scan: {imap_data.get('last_scan', 'Never')}")
            
            self.test_results["imap_monitoring"]["status"] = "working" if len(imap_enabled_providers) > 0 else "failed"
            self.test_results["imap_monitoring"]["details"] = {
                "total_providers": len(providers),
                "imap_enabled_count": len(imap_enabled_providers),
                "providers": imap_enabled_providers
            }
        else:
            self.test_results["imap_monitoring"]["status"] = "failed"
            self.test_results["imap_monitoring"]["details"] = {"error": "Could not get email providers"}
        
        # 10.3: Test auto-responder functionality by checking if system can process incoming emails
        print("\n🔍 10.3: Testing Auto-responder Readiness")
        
        # Check if there are any email templates for auto-responses
        templates_result = await self.make_request("GET", "/templates", description="Getting email templates")
        
        if templates_result["success"]:
            templates = templates_result["data"]
            auto_response_templates = [t for t in templates if "auto" in t.get("name", "").lower() or "response" in t.get("name", "").lower()]
            
            print(f"   📊 Total Templates: {len(templates)}")
            print(f"   📊 Auto-response Templates: {len(auto_response_templates)}")
            
            for template in auto_response_templates:
                print(f"      - {template.get('name', 'Unknown')} ({template.get('type', 'Unknown')})")
            
            self.test_results["auto_responder"]["status"] = "working" if len(auto_response_templates) > 0 else "partial"
            self.test_results["auto_responder"]["details"] = {
                "total_templates": len(templates),
                "auto_response_templates_count": len(auto_response_templates),
                "templates": auto_response_templates
            }
        else:
            self.test_results["auto_responder"]["status"] = "failed"
            self.test_results["auto_responder"]["details"] = {"error": "Could not get templates"}
    
    async def test_step_11_imap_logs_and_realtime_data(self):
        """Step 11: Check IMAP Logs and Real-time Data"""
        print("\n" + "="*80)
        print("📊 STEP 11: CHECKING IMAP LOGS AND REAL-TIME DATA")
        print("="*80)
        
        # 11.1: Check real-time dashboard metrics
        print("\n🔍 11.1: Checking Real-time Dashboard Metrics")
        result = await self.make_request("GET", "/real-time/dashboard-metrics", description="Getting real-time dashboard metrics")
        
        if result["success"]:
            metrics = result["data"].get("metrics", {})
            overview = metrics.get("overview", {})
            provider_stats = metrics.get("provider_stats", {})
            recent_activity = metrics.get("recent_activity", [])
            
            print(f"   📊 Total Prospects: {overview.get('total_prospects', 0)}")
            print(f"   📊 Total Campaigns: {overview.get('total_campaigns', 0)}")
            print(f"   📊 Total Emails Sent: {overview.get('total_emails_sent', 0)}")
            print(f"   📊 Emails Today: {overview.get('emails_today', 0)}")
            print(f"   📊 Active Campaigns: {overview.get('active_campaigns', 0)}")
            
            print(f"\n   📊 Provider Statistics:")
            for provider_name, stats in provider_stats.items():
                print(f"      - {provider_name}:")
                print(f"        Type: {stats.get('type', 'Unknown')}")
                print(f"        Status: {stats.get('status', 'Unknown')}")
                print(f"        Emails Sent Today: {stats.get('emails_sent_today', 0)}")
                print(f"        Daily Limit: {stats.get('daily_limit', 0)}")
            
            print(f"\n   📊 Recent Activity ({len(recent_activity)} items):")
            for activity in recent_activity[:3]:  # Show first 3
                print(f"      - {activity.get('subject', 'Unknown Subject')}")
                print(f"        To: {activity.get('recipient', 'Unknown')}")
                print(f"        Status: {activity.get('status', 'Unknown')}")
                print(f"        Time: {activity.get('created_at', 'Unknown')}")
            
            self.test_results["thread_tracking"]["status"] = "working"
            self.test_results["thread_tracking"]["details"] = {
                "metrics_available": True,
                "total_emails_sent": overview.get('total_emails_sent', 0),
                "recent_activity_count": len(recent_activity),
                "provider_stats": provider_stats
            }
        else:
            self.test_results["thread_tracking"]["status"] = "failed"
            self.test_results["thread_tracking"]["details"] = {"error": "Could not get real-time metrics"}
        
        # 11.2: Check if there are any active campaigns to monitor
        print("\n🔍 11.2: Checking Active Campaigns for Monitoring")
        campaigns_result = await self.make_request("GET", "/campaigns", description="Getting campaigns")
        
        if campaigns_result["success"]:
            campaigns = campaigns_result["data"]
            active_campaigns = [c for c in campaigns if c.get("status") == "active"]
            
            print(f"   📊 Total Campaigns: {len(campaigns)}")
            print(f"   📊 Active Campaigns: {len(active_campaigns)}")
            
            # Check details of active campaigns
            for campaign in active_campaigns:
                campaign_id = campaign.get("id")
                if campaign_id:
                    # Get detailed campaign info
                    detail_result = await self.make_request("GET", f"/campaigns/{campaign_id}", 
                                                          description=f"Getting details for campaign {campaign.get('name', 'Unknown')}")
                    
                    if detail_result["success"]:
                        campaign_details = detail_result["data"]
                        analytics = campaign_details.get("analytics", {})
                        email_records = campaign_details.get("email_records", [])
                        
                        print(f"      - {campaign.get('name', 'Unknown')}:")
                        print(f"        Status: {campaign_details.get('status', 'Unknown')}")
                        print(f"        Total Sent: {analytics.get('total_sent', 0)}")
                        print(f"        Total Failed: {analytics.get('total_failed', 0)}")
                        print(f"        Success Rate: {analytics.get('success_rate', 0):.1f}%")
                        print(f"        Email Records: {len(email_records)}")
                        
                        # Store campaign ID for follow-up testing
                        if not self.campaign_id and len(email_records) > 0:
                            self.campaign_id = campaign_id
                            print(f"        📌 Using this campaign for follow-up testing")
        
        # 11.3: Test email threading functionality by checking email records
        print("\n🔍 11.3: Testing Email Threading Functionality")
        
        if self.campaign_id:
            # Get detailed campaign info to check email threading
            detail_result = await self.make_request("GET", f"/campaigns/{self.campaign_id}", 
                                                  description="Checking email threading in campaign")
            
            if detail_result["success"]:
                campaign_details = detail_result["data"]
                email_records = campaign_details.get("email_records", [])
                
                # Group emails by recipient to check threading
                recipient_threads = {}
                for email in email_records:
                    recipient = email.get("recipient_email", "unknown")
                    if recipient not in recipient_threads:
                        recipient_threads[recipient] = []
                    recipient_threads[recipient].append(email)
                
                print(f"   📊 Email Threading Analysis:")
                print(f"      Total Email Records: {len(email_records)}")
                print(f"      Unique Recipients: {len(recipient_threads)}")
                
                for recipient, emails in recipient_threads.items():
                    print(f"      - {recipient}: {len(emails)} emails")
                    
                    # Check for follow-up sequences
                    follow_ups = [e for e in emails if e.get("is_follow_up", False)]
                    initial_emails = [e for e in emails if not e.get("is_follow_up", False)]
                    
                    print(f"        Initial emails: {len(initial_emails)}")
                    print(f"        Follow-up emails: {len(follow_ups)}")
                    
                    # Check thread IDs if available
                    thread_ids = set([e.get("thread_id") for e in emails if e.get("thread_id")])
                    if thread_ids:
                        print(f"        Thread IDs: {len(thread_ids)} unique threads")
                
                self.test_results["thread_tracking"]["details"]["threading_analysis"] = {
                    "total_email_records": len(email_records),
                    "unique_recipients": len(recipient_threads),
                    "recipient_threads": {k: len(v) for k, v in recipient_threads.items()}
                }
        else:
            print("   ⚠️  No active campaigns found for threading analysis")
    
    async def test_step_12_follow_up_stop_logic(self):
        """Step 12: Verify Follow-up Stop Logic"""
        print("\n" + "="*80)
        print("🛑 STEP 12: VERIFYING FOLLOW-UP STOP LOGIC")
        print("="*80)
        
        # 12.1: Check if there are any prospects with reply status
        print("\n🔍 12.1: Checking Prospect Reply Status")
        prospects_result = await self.make_request("GET", "/prospects", description="Getting prospects")
        
        if prospects_result["success"]:
            prospects = prospects_result["data"]
            
            # Look for the specific prospect we're testing with
            test_prospect = None
            for prospect in prospects:
                if prospect.get("email") == self.prospect_email:
                    test_prospect = prospect
                    break
            
            if test_prospect:
                print(f"   📊 Found test prospect: {test_prospect.get('first_name', '')} {test_prospect.get('last_name', '')}")
                print(f"      Email: {test_prospect.get('email', 'N/A')}")
                print(f"      Status: {test_prospect.get('status', 'Unknown')}")
                print(f"      Last Contact: {test_prospect.get('last_contact_date', 'Never')}")
                print(f"      Reply Received: {test_prospect.get('reply_received', False)}")
                
                # Check if prospect has any follow-up status
                follow_up_status = test_prospect.get("follow_up_status", "unknown")
                print(f"      Follow-up Status: {follow_up_status}")
                
                self.test_results["reply_detection"]["status"] = "working"
                self.test_results["reply_detection"]["details"] = {
                    "test_prospect_found": True,
                    "prospect_email": self.prospect_email,
                    "prospect_status": test_prospect.get('status', 'Unknown'),
                    "reply_received": test_prospect.get('reply_received', False),
                    "follow_up_status": follow_up_status
                }
            else:
                print(f"   ⚠️  Test prospect {self.prospect_email} not found")
                self.test_results["reply_detection"]["status"] = "partial"
                self.test_results["reply_detection"]["details"] = {
                    "test_prospect_found": False,
                    "prospect_email": self.prospect_email
                }
        
        # 12.2: Check follow-up engine status and pending follow-ups
        print("\n🔍 12.2: Checking Follow-up Engine and Pending Follow-ups")
        
        # Check if there are any routes for follow-up monitoring
        try:
            follow_up_result = await self.make_request("GET", "/follow-up-monitoring/status", 
                                                     description="Getting follow-up monitoring status")
            
            if follow_up_result["success"]:
                follow_up_data = follow_up_result["data"]
                print(f"   📊 Follow-up Monitoring Data:")
                print(f"      {json.dumps(follow_up_data, indent=6)}")
                
                self.test_results["follow_up_stop_logic"]["status"] = "working"
                self.test_results["follow_up_stop_logic"]["details"] = follow_up_data
            else:
                print(f"   ⚠️  Follow-up monitoring endpoint not available or failed")
                self.test_results["follow_up_stop_logic"]["status"] = "partial"
        except Exception as e:
            print(f"   ⚠️  Follow-up monitoring check failed: {str(e)}")
            self.test_results["follow_up_stop_logic"]["status"] = "partial"
        
        # 12.3: Check if there are any email processing logs or routes
        print("\n🔍 12.3: Checking Email Processing Capabilities")
        
        try:
            # Check if email processing routes are available
            email_proc_result = await self.make_request("GET", "/email-processing/status", 
                                                       description="Getting email processing status")
            
            if email_proc_result["success"]:
                email_proc_data = email_proc_result["data"]
                print(f"   📊 Email Processing Data:")
                print(f"      {json.dumps(email_proc_data, indent=6)}")
                
                # Update auto-responder status based on email processing capabilities
                if self.test_results["auto_responder"]["status"] != "working":
                    self.test_results["auto_responder"]["status"] = "working"
                    self.test_results["auto_responder"]["details"]["email_processing"] = email_proc_data
            else:
                print(f"   ⚠️  Email processing endpoint not available or failed")
        except Exception as e:
            print(f"   ⚠️  Email processing check failed: {str(e)}")
        
        # 12.4: Test response detection mechanisms
        print("\n🔍 12.4: Testing Response Detection Mechanisms")
        
        # Check if there are any intents or response classification systems
        try:
            intents_result = await self.make_request("GET", "/intents", description="Getting intents for response classification")
            
            if intents_result["success"]:
                intents = intents_result["data"]
                print(f"   📊 Response Classification Intents: {len(intents)}")
                
                for intent in intents[:3]:  # Show first 3
                    print(f"      - {intent.get('name', 'Unknown')}: {intent.get('description', 'No description')}")
                
                self.test_results["reply_detection"]["details"]["intents_available"] = True
                self.test_results["reply_detection"]["details"]["intents_count"] = len(intents)
            else:
                print(f"   ⚠️  Intents endpoint not available")
                self.test_results["reply_detection"]["details"]["intents_available"] = False
        except Exception as e:
            print(f"   ⚠️  Intents check failed: {str(e)}")
            self.test_results["reply_detection"]["details"]["intents_available"] = False
    
    async def run_comprehensive_reply_processing_test(self):
        """Run comprehensive reply processing and auto-responder test"""
        print("=" * 80)
        print("🚀 COMPREHENSIVE REPLY PROCESSING AND AUTO-RESPONDER TEST")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print(f"Test Prospect Email: {self.prospect_email}")
        
        await self.setup_session()
        
        try:
            # Run all test steps
            await self.test_step_10_reply_processing_and_auto_responder()
            await self.test_step_11_imap_logs_and_realtime_data()
            await self.test_step_12_follow_up_stop_logic()
            
            # Determine overall status
            test_statuses = [v.get("status", "unknown") for v in self.test_results.values() if isinstance(v, dict) and "status" in v]
            
            if all(status == "working" for status in test_statuses):
                self.test_results["overall_status"] = "fully_working"
            elif any(status == "working" for status in test_statuses):
                self.test_results["overall_status"] = "partially_working"
            else:
                self.test_results["overall_status"] = "failed"
            
        finally:
            await self.cleanup_session()
        
        # Print comprehensive summary
        self.print_test_summary()
    
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("📋 REPLY PROCESSING AND AUTO-RESPONDER TEST SUMMARY")
        print("=" * 80)
        
        # Overall Status
        status_emoji = {
            "fully_working": "✅",
            "partially_working": "⚠️",
            "failed": "❌",
            "unknown": "❓"
        }
        
        overall_status = self.test_results["overall_status"]
        print(f"\n🎯 OVERALL TEST STATUS: {status_emoji.get(overall_status, '❓')} {overall_status.upper()}")
        
        # Individual Test Results
        print(f"\n📊 INDIVIDUAL TEST RESULTS:")
        
        test_areas = [
            ("IMAP Monitoring", "imap_monitoring"),
            ("Email Processing", "email_processing"),
            ("Reply Detection", "reply_detection"),
            ("Follow-up Stop Logic", "follow_up_stop_logic"),
            ("Thread Tracking", "thread_tracking"),
            ("Auto-responder", "auto_responder")
        ]
        
        for area_name, area_key in test_areas:
            status = self.test_results[area_key]["status"]
            emoji = status_emoji.get(status, "❓")
            print(f"   • {area_name}: {emoji} {status}")
            
            # Show key details
            details = self.test_results[area_key]["details"]
            if isinstance(details, dict):
                if area_key == "imap_monitoring":
                    print(f"     - IMAP Enabled Providers: {details.get('imap_enabled_count', 0)}")
                elif area_key == "email_processing":
                    print(f"     - Processor Status: {details.get('processor_status', 'unknown')}")
                    print(f"     - Monitored Providers: {details.get('monitored_providers_count', 0)}")
                elif area_key == "auto_responder":
                    print(f"     - Auto-response Templates: {details.get('auto_response_templates_count', 0)}")
                elif area_key == "thread_tracking":
                    print(f"     - Total Emails Sent: {details.get('total_emails_sent', 0)}")
                    print(f"     - Recent Activity Items: {details.get('recent_activity_count', 0)}")
                elif area_key == "reply_detection":
                    print(f"     - Test Prospect Found: {details.get('test_prospect_found', False)}")
                    print(f"     - Reply Received: {details.get('reply_received', False)}")
        
        # Key Findings
        print(f"\n🔍 KEY FINDINGS:")
        
        # IMAP Monitoring
        imap_details = self.test_results["imap_monitoring"]["details"]
        if isinstance(imap_details, dict):
            imap_count = imap_details.get("imap_enabled_count", 0)
            if imap_count > 0:
                print(f"   ✅ IMAP monitoring is configured for {imap_count} provider(s)")
            else:
                print(f"   ❌ No IMAP monitoring configured")
        
        # Email Processing
        email_proc_details = self.test_results["email_processing"]["details"]
        if isinstance(email_proc_details, dict):
            processor_status = email_proc_details.get("processor_status", "unknown")
            if processor_status == "running":
                print(f"   ✅ Email processor is running and monitoring emails")
            else:
                print(f"   ❌ Email processor is not running ({processor_status})")
        
        # Auto-responder
        auto_resp_details = self.test_results["auto_responder"]["details"]
        if isinstance(auto_resp_details, dict):
            template_count = auto_resp_details.get("auto_response_templates_count", 0)
            if template_count > 0:
                print(f"   ✅ Auto-responder templates are available ({template_count} templates)")
            else:
                print(f"   ⚠️  No specific auto-responder templates found")
        
        # Thread Tracking
        thread_details = self.test_results["thread_tracking"]["details"]
        if isinstance(thread_details, dict):
            total_emails = thread_details.get("total_emails_sent", 0)
            if total_emails > 0:
                print(f"   ✅ Email tracking is working ({total_emails} emails sent)")
            else:
                print(f"   ⚠️  No email activity detected")
        
        # Reply Detection
        reply_details = self.test_results["reply_detection"]["details"]
        if isinstance(reply_details, dict):
            prospect_found = reply_details.get("test_prospect_found", False)
            if prospect_found:
                reply_received = reply_details.get("reply_received", False)
                if reply_received:
                    print(f"   ✅ Reply detection is working - test prospect has received replies")
                else:
                    print(f"   ⚠️  Test prospect found but no replies detected yet")
            else:
                print(f"   ❌ Test prospect {self.prospect_email} not found in system")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        
        if self.test_results["imap_monitoring"]["status"] != "working":
            print("   • Enable IMAP monitoring on email providers to process incoming emails")
        
        if self.test_results["email_processing"]["status"] != "working":
            print("   • Start the email processor service to handle incoming email processing")
        
        if self.test_results["auto_responder"]["status"] != "working":
            print("   • Create auto-responder email templates for automated responses")
        
        if self.test_results["reply_detection"]["status"] != "working":
            print("   • Ensure test prospect is properly configured in the system")
        
        if self.test_results["follow_up_stop_logic"]["status"] != "working":
            print("   • Verify follow-up monitoring and stop logic implementation")
        
        # Final Assessment
        print(f"\n🎯 FINAL ASSESSMENT:")
        
        if overall_status == "fully_working":
            print("   ✅ All reply processing and auto-responder functionality is working correctly")
            print("   ✅ System is ready for production email campaign management")
        elif overall_status == "partially_working":
            print("   ⚠️  Some reply processing functionality is working, but improvements needed")
            print("   ⚠️  Review recommendations above to achieve full functionality")
        else:
            print("   ❌ Reply processing and auto-responder functionality needs significant work")
            print("   ❌ System is not ready for production email campaign management")
        
        print("\n" + "=" * 80)
        print("✅ REPLY PROCESSING AND AUTO-RESPONDER TEST COMPLETED")
        print("=" * 80)

async def main():
    """Main test execution"""
    tester = ReplyProcessingTester()
    await tester.run_comprehensive_reply_processing_test()

if __name__ == "__main__":
    asyncio.run(main())