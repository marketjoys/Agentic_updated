#!/usr/bin/env python3
"""
Follow-up Email Investigation Test
Investigates why follow-up emails aren't being delivered to kasargovinda@gmail.com
despite logs showing they were sent.
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
import sys
import os

# Backend URL from environment
BACKEND_URL = "https://2383b216-6221-4f25-b50c-73dce9a2ad0d.preview.emergentagent.com/api"

class FollowUpInvestigator:
    def __init__(self):
        self.session = None
        self.target_email = "kasargovinda@gmail.com"
        self.investigation_results = {
            "email_records": [],
            "follow_up_engine_status": {},
            "email_providers": [],
            "campaigns": [],
            "services_status": {},
            "smtp_logs": [],
            "test_results": {}
        }
    
    async def setup_session(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession()
    
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    async def make_request(self, method, endpoint, data=None):
        """Make HTTP request to backend"""
        try:
            url = f"{BACKEND_URL}{endpoint}"
            print(f"🔍 {method.upper()} {url}")
            
            if method.lower() == "get":
                async with self.session.get(url) as response:
                    status_code = response.status
                    response_data = await response.json() if response.content_type == 'application/json' else await response.text()
            elif method.lower() == "post":
                async with self.session.post(url, json=data) as response:
                    status_code = response.status
                    response_data = await response.json() if response.content_type == 'application/json' else await response.text()
            
            if status_code == 200:
                print(f"   ✅ SUCCESS - Status: {status_code}")
                return {"success": True, "status_code": status_code, "data": response_data}
            else:
                print(f"   ❌ FAILED - Status: {status_code}")
                print(f"   Error: {response_data}")
                return {"success": False, "status_code": status_code, "error": response_data}
                
        except Exception as e:
            print(f"   ❌ EXCEPTION - {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def check_email_records(self):
        """Check all email records for kasargovinda@gmail.com"""
        print("\n" + "="*60)
        print("1. 📧 CHECKING EMAIL RECORDS FOR kasargovinda@gmail.com")
        print("="*60)
        
        # Get all campaigns first to find ones targeting our email
        campaigns_result = await self.make_request("GET", "/campaigns")
        if not campaigns_result["success"]:
            print("❌ Failed to get campaigns")
            return
        
        campaigns = campaigns_result["data"]
        self.investigation_results["campaigns"] = campaigns
        
        print(f"Found {len(campaigns)} campaigns")
        
        # Check each campaign for email records
        target_campaigns = []
        for campaign in campaigns:
            campaign_id = campaign.get("id")
            if not campaign_id:
                continue
                
            # Get detailed campaign info including email records
            campaign_detail_result = await self.make_request("GET", f"/campaigns/{campaign_id}")
            if campaign_detail_result["success"]:
                campaign_detail = campaign_detail_result["data"]
                email_records = campaign_detail.get("email_records", [])
                
                # Filter for our target email
                target_email_records = [
                    record for record in email_records 
                    if record.get("recipient_email") == self.target_email
                ]
                
                if target_email_records:
                    target_campaigns.append({
                        "campaign": campaign_detail,
                        "email_records": target_email_records
                    })
                    
                    print(f"\n📋 Campaign: {campaign.get('name', 'Unknown')}")
                    print(f"   Campaign ID: {campaign_id}")
                    print(f"   Status: {campaign.get('status', 'Unknown')}")
                    print(f"   Follow-up enabled: {campaign.get('follow_up_enabled', False)}")
                    
                    print(f"\n   📧 Email Records for {self.target_email}:")
                    for i, record in enumerate(target_email_records, 1):
                        print(f"      {i}. Email ID: {record.get('id', 'N/A')}")
                        print(f"         Subject: {record.get('subject', 'N/A')}")
                        print(f"         Status: {record.get('status', 'N/A')}")
                        print(f"         Sent At: {record.get('sent_at', 'N/A')}")
                        print(f"         Provider ID: {record.get('email_provider_id', 'N/A')}")
                        print(f"         Is Follow-up: {record.get('is_follow_up', False)}")
                        print(f"         Follow-up Sequence: {record.get('follow_up_sequence', 'N/A')}")
                        print(f"         Campaign ID: {record.get('campaign_id', 'N/A')}")
                        print()
        
        self.investigation_results["email_records"] = target_campaigns
        
        if not target_campaigns:
            print(f"❌ No email records found for {self.target_email}")
        else:
            print(f"✅ Found email records in {len(target_campaigns)} campaigns")
    
    async def verify_follow_up_engine(self):
        """Verify follow-up engine status and processing"""
        print("\n" + "="*60)
        print("2. 🔧 VERIFYING FOLLOW-UP ENGINE")
        print("="*60)
        
        # Get services status
        services_result = await self.make_request("GET", "/services/status")
        if not services_result["success"]:
            print("❌ Failed to get services status")
            return
        
        services = services_result["data"]
        self.investigation_results["services_status"] = services
        
        print(f"Overall Status: {services.get('overall_status', 'unknown')}")
        
        if "services" in services:
            follow_up_engine = services["services"].get("smart_follow_up_engine", {})
            email_processor = services["services"].get("email_processor", {})
            
            print(f"\n🔄 Follow-up Engine:")
            print(f"   Status: {follow_up_engine.get('status', 'unknown')}")
            print(f"   Description: {follow_up_engine.get('description', 'N/A')}")
            
            print(f"\n📧 Email Processor:")
            print(f"   Status: {email_processor.get('status', 'unknown')}")
            print(f"   Description: {email_processor.get('description', 'N/A')}")
            print(f"   Monitored Providers: {email_processor.get('monitored_providers_count', 0)}")
            
            if "monitored_providers" in email_processor:
                print(f"   Provider Details:")
                for provider in email_processor["monitored_providers"]:
                    print(f"      - {provider.get('name', 'Unknown')} ({provider.get('provider_type', 'Unknown')})")
                    print(f"        Last Scan: {provider.get('last_scan', 'Never')}")
        
        # Check for active campaigns with follow-up enabled
        print(f"\n📋 Active Campaigns with Follow-up:")
        campaigns = self.investigation_results.get("campaigns", [])
        follow_up_campaigns = [
            c for c in campaigns 
            if c.get("follow_up_enabled", False) and c.get("status") in ["active", "completed"]
        ]
        
        if follow_up_campaigns:
            for campaign in follow_up_campaigns:
                print(f"   - {campaign.get('name', 'Unknown')}")
                print(f"     Status: {campaign.get('status', 'Unknown')}")
                print(f"     Follow-up Type: {campaign.get('follow_up_schedule_type', 'interval')}")
                print(f"     Follow-up Intervals: {campaign.get('follow_up_intervals', [])}")
        else:
            print("   ❌ No active campaigns with follow-up enabled")
    
    async def check_email_providers(self):
        """Check email provider configuration and usage"""
        print("\n" + "="*60)
        print("3. 📮 CHECKING EMAIL PROVIDERS")
        print("="*60)
        
        providers_result = await self.make_request("GET", "/email-providers")
        if not providers_result["success"]:
            print("❌ Failed to get email providers")
            return
        
        providers = providers_result["data"]
        self.investigation_results["email_providers"] = providers
        
        print(f"Found {len(providers)} email providers")
        
        for i, provider in enumerate(providers, 1):
            print(f"\n{i}. Provider: {provider.get('name', 'Unknown')}")
            print(f"   ID: {provider.get('id', 'N/A')}")
            print(f"   Type: {provider.get('provider_type', 'Unknown')}")
            print(f"   Email: {provider.get('email_address', 'N/A')}")
            print(f"   Active: {provider.get('is_active', False)}")
            print(f"   Default: {provider.get('is_default', False)}")
            print(f"   IMAP Enabled: {provider.get('imap_enabled', False)}")
            print(f"   Daily Limit: {provider.get('daily_send_limit', 0)}")
            print(f"   Current Daily Count: {provider.get('current_daily_count', 0)}")
            
            # Test provider connection
            test_result = await self.make_request("POST", f"/email-providers/{provider.get('id')}/test")
            if test_result["success"]:
                test_data = test_result["data"]
                print(f"   Connection Test:")
                print(f"      SMTP: {test_data.get('smtp_test', 'unknown')}")
                print(f"      IMAP: {test_data.get('imap_test', 'unknown')}")
                print(f"      Overall: {test_data.get('overall_status', 'unknown')}")
        
        # Check which provider was used for initial vs follow-up emails
        print(f"\n📊 Provider Usage Analysis:")
        email_records = self.investigation_results.get("email_records", [])
        provider_usage = {}
        
        for campaign_data in email_records:
            for record in campaign_data["email_records"]:
                provider_id = record.get("email_provider_id")
                is_follow_up = record.get("is_follow_up", False)
                
                if provider_id not in provider_usage:
                    provider_usage[provider_id] = {"initial": 0, "follow_up": 0}
                
                if is_follow_up:
                    provider_usage[provider_id]["follow_up"] += 1
                else:
                    provider_usage[provider_id]["initial"] += 1
        
        for provider_id, usage in provider_usage.items():
            provider_name = next(
                (p.get("name", "Unknown") for p in providers if p.get("id") == provider_id),
                "Unknown Provider"
            )
            print(f"   {provider_name} ({provider_id}):")
            print(f"      Initial emails: {usage['initial']}")
            print(f"      Follow-up emails: {usage['follow_up']}")
    
    async def check_smtp_logs(self):
        """Check for SMTP errors in backend logs"""
        print("\n" + "="*60)
        print("4. 📋 CHECKING SMTP LOGS")
        print("="*60)
        
        # Note: In a real implementation, this would check actual log files
        # For now, we'll simulate by checking recent email records for errors
        print("Checking recent email records for SMTP errors...")
        
        email_records = self.investigation_results.get("email_records", [])
        smtp_errors = []
        
        for campaign_data in email_records:
            for record in campaign_data["email_records"]:
                if record.get("status") == "failed":
                    smtp_errors.append({
                        "email_id": record.get("id"),
                        "subject": record.get("subject"),
                        "sent_at": record.get("sent_at"),
                        "error": record.get("error_message", "Unknown error"),
                        "is_follow_up": record.get("is_follow_up", False)
                    })
        
        if smtp_errors:
            print(f"❌ Found {len(smtp_errors)} SMTP errors:")
            for error in smtp_errors:
                print(f"   - Email ID: {error['email_id']}")
                print(f"     Subject: {error['subject']}")
                print(f"     Time: {error['sent_at']}")
                print(f"     Follow-up: {error['is_follow_up']}")
                print(f"     Error: {error['error']}")
                print()
        else:
            print("✅ No SMTP errors found in email records")
        
        self.investigation_results["smtp_logs"] = smtp_errors
    
    async def test_follow_up_sending(self):
        """Test manual follow-up email sending"""
        print("\n" + "="*60)
        print("5. 🧪 TESTING FOLLOW-UP SENDING")
        print("="*60)
        
        # Find a campaign that targets our email
        email_records = self.investigation_results.get("email_records", [])
        if not email_records:
            print("❌ No campaigns found targeting kasargovinda@gmail.com")
            return
        
        # Get the first campaign
        campaign_data = email_records[0]
        campaign = campaign_data["campaign"]
        campaign_id = campaign.get("id")
        
        print(f"Testing with campaign: {campaign.get('name', 'Unknown')}")
        print(f"Campaign ID: {campaign_id}")
        
        # Try to send the campaign (this might trigger follow-ups if configured)
        send_data = {
            "send_immediately": True,
            "email_provider_id": "",  # Use default
            "max_emails": 1,
            "schedule_type": "immediate",
            "follow_up_enabled": True,
            "follow_up_intervals": [1, 3, 5],  # 1, 3, 5 minutes for testing
            "follow_up_templates": []
        }
        
        print(f"\nAttempting to send campaign...")
        send_result = await self.make_request("POST", f"/campaigns/{campaign_id}/send", send_data)
        
        if send_result["success"]:
            print("✅ Campaign send request successful")
            send_response = send_result["data"]
            print(f"   Response: {send_response}")
            
            # Wait a moment and check for new email records
            print("\nWaiting 30 seconds to check for follow-up processing...")
            await asyncio.sleep(30)
            
            # Re-check campaign for new email records
            updated_campaign_result = await self.make_request("GET", f"/campaigns/{campaign_id}")
            if updated_campaign_result["success"]:
                updated_campaign = updated_campaign_result["data"]
                updated_email_records = updated_campaign.get("email_records", [])
                
                # Filter for our target email
                updated_target_records = [
                    record for record in updated_email_records 
                    if record.get("recipient_email") == self.target_email
                ]
                
                print(f"\n📧 Updated email records for {self.target_email}:")
                for i, record in enumerate(updated_target_records, 1):
                    print(f"   {i}. Subject: {record.get('subject', 'N/A')}")
                    print(f"      Status: {record.get('status', 'N/A')}")
                    print(f"      Sent At: {record.get('sent_at', 'N/A')}")
                    print(f"      Is Follow-up: {record.get('is_follow_up', False)}")
                    print(f"      Follow-up Sequence: {record.get('follow_up_sequence', 'N/A')}")
                
                # Compare with original records
                original_count = len(campaign_data["email_records"])
                updated_count = len(updated_target_records)
                
                if updated_count > original_count:
                    print(f"✅ New emails detected! {updated_count - original_count} new records")
                else:
                    print(f"⚠️ No new emails detected (still {updated_count} records)")
        else:
            print("❌ Campaign send request failed")
            print(f"   Error: {send_result.get('error', 'Unknown error')}")
        
        self.investigation_results["test_results"] = send_result
    
    async def run_investigation(self):
        """Run complete follow-up investigation"""
        print("=" * 80)
        print("🔍 FOLLOW-UP EMAIL DELIVERY INVESTIGATION")
        print("=" * 80)
        print(f"Target Email: {self.target_email}")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Investigation Time: {datetime.now().isoformat()}")
        
        await self.setup_session()
        
        try:
            # Run all investigation steps
            await self.check_email_records()
            await self.verify_follow_up_engine()
            await self.check_email_providers()
            await self.check_smtp_logs()
            await self.test_follow_up_sending()
            
        finally:
            await self.cleanup_session()
        
        # Print investigation summary
        self.print_investigation_summary()
    
    def print_investigation_summary(self):
        """Print comprehensive investigation summary"""
        print("\n" + "=" * 80)
        print("📋 INVESTIGATION SUMMARY")
        print("=" * 80)
        
        # Email Records Summary
        email_records = self.investigation_results.get("email_records", [])
        total_emails = sum(len(campaign_data["email_records"]) for campaign_data in email_records)
        follow_up_emails = sum(
            len([r for r in campaign_data["email_records"] if r.get("is_follow_up", False)])
            for campaign_data in email_records
        )
        initial_emails = total_emails - follow_up_emails
        
        print(f"\n📧 EMAIL RECORDS FOR {self.target_email}:")
        print(f"   • Total emails: {total_emails}")
        print(f"   • Initial emails: {initial_emails}")
        print(f"   • Follow-up emails: {follow_up_emails}")
        print(f"   • Campaigns involved: {len(email_records)}")
        
        # Services Status Summary
        services = self.investigation_results.get("services_status", {})
        if "services" in services:
            follow_up_status = services["services"].get("smart_follow_up_engine", {}).get("status", "unknown")
            email_proc_status = services["services"].get("email_processor", {}).get("status", "unknown")
            
            print(f"\n🔧 SERVICES STATUS:")
            print(f"   • Follow-up Engine: {follow_up_status}")
            print(f"   • Email Processor: {email_proc_status}")
            print(f"   • Overall Status: {services.get('overall_status', 'unknown')}")
        
        # Provider Summary
        providers = self.investigation_results.get("email_providers", [])
        active_providers = [p for p in providers if p.get("is_active", False)]
        default_providers = [p for p in providers if p.get("is_default", False)]
        
        print(f"\n📮 EMAIL PROVIDERS:")
        print(f"   • Total providers: {len(providers)}")
        print(f"   • Active providers: {len(active_providers)}")
        print(f"   • Default providers: {len(default_providers)}")
        
        # SMTP Errors Summary
        smtp_errors = self.investigation_results.get("smtp_logs", [])
        follow_up_errors = [e for e in smtp_errors if e.get("is_follow_up", False)]
        
        print(f"\n📋 SMTP ERRORS:")
        print(f"   • Total errors: {len(smtp_errors)}")
        print(f"   • Follow-up errors: {len(follow_up_errors)}")
        
        # Findings and Recommendations
        print(f"\n🔍 KEY FINDINGS:")
        
        if total_emails == 0:
            print("   ❌ No email records found for kasargovinda@gmail.com")
        elif follow_up_emails == 0:
            print("   ⚠️ No follow-up emails found - follow-ups may not be triggering")
        else:
            print(f"   ✅ Found {follow_up_emails} follow-up emails in database")
        
        if follow_up_status != "running":
            print("   ❌ Follow-up engine is not running")
        else:
            print("   ✅ Follow-up engine is running")
        
        if len(active_providers) == 0:
            print("   ❌ No active email providers")
        elif len(default_providers) == 0:
            print("   ⚠️ No default email provider set")
        else:
            print("   ✅ Email providers configured properly")
        
        if len(follow_up_errors) > 0:
            print(f"   ❌ {len(follow_up_errors)} SMTP errors in follow-up emails")
        
        print(f"\n💡 RECOMMENDATIONS:")
        
        if total_emails == 0:
            print("   • Create and send a campaign targeting kasargovinda@gmail.com")
        
        if follow_up_emails == 0 and total_emails > 0:
            print("   • Check follow-up configuration in campaigns")
            print("   • Verify follow-up timing and intervals")
        
        if follow_up_status != "running":
            print("   • Start the follow-up engine service")
        
        if len(smtp_errors) > 0:
            print("   • Investigate SMTP connection issues")
            print("   • Check email provider credentials")
        
        if follow_up_emails > 0:
            print("   • Check Gmail Sent folder for follow-up emails")
            print("   • Verify SMTP logs for actual delivery status")
            print("   • Consider checking spam/junk folders")
        
        print("\n" + "=" * 80)
        print("✅ INVESTIGATION COMPLETED")
        print("=" * 80)

async def main():
    """Main investigation execution"""
    investigator = FollowUpInvestigator()
    await investigator.run_investigation()

if __name__ == "__main__":
    asyncio.run(main())