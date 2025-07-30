#!/usr/bin/env python3
"""
Follow-up Email Delivery Test
Recreates the scenario and investigates follow-up email delivery issues
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
import sys
import os

# Backend URL from environment
BACKEND_URL = "https://b40c5c4f-de80-4df5-bbd3-3623f2621a6f.preview.emergentagent.com/api"

class FollowUpDeliveryTester:
    def __init__(self):
        self.session = None
        self.target_email = "kasargovinda@gmail.com"
        self.test_data = {
            "email_provider_id": None,
            "prospect_list_id": None,
            "prospect_id": None,
            "campaign_id": None,
            "template_id": None
        }
        self.results = {
            "setup_successful": False,
            "campaign_sent": False,
            "initial_emails": [],
            "follow_up_emails": [],
            "provider_issues": [],
            "timing_analysis": {}
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
    
    async def setup_email_provider(self):
        """Setup email provider with working credentials"""
        print("\n" + "="*60)
        print("1. 📮 SETTING UP EMAIL PROVIDER")
        print("="*60)
        
        # First, check if rohushanshinde@gmail.com provider already exists
        providers_result = await self.make_request("GET", "/email-providers")
        if providers_result["success"]:
            providers = providers_result["data"]
            existing_provider = None
            
            for provider in providers:
                if provider.get("email_address") == "rohushanshinde@gmail.com":
                    existing_provider = provider
                    break
            
            if existing_provider:
                self.test_data["email_provider_id"] = existing_provider["id"]
                print(f"✅ Using existing email provider: {existing_provider['id']}")
                print(f"   Name: {existing_provider.get('name', 'Unknown')}")
                print(f"   Email: {existing_provider.get('email_address', 'Unknown')}")
                print(f"   Active: {existing_provider.get('is_active', False)}")
                print(f"   Default: {existing_provider.get('is_default', False)}")
                
                # Test the provider
                test_result = await self.make_request("POST", f"/email-providers/{self.test_data['email_provider_id']}/test")
                if test_result["success"]:
                    test_data = test_result["data"]
                    print(f"📧 Provider test results:")
                    print(f"   SMTP: {test_data.get('smtp_test', 'unknown')}")
                    print(f"   IMAP: {test_data.get('imap_test', 'unknown')}")
                    print(f"   Overall: {test_data.get('overall_status', 'unknown')}")
                    
                    if test_data.get('overall_status') != 'passed':
                        self.results["provider_issues"].append("Provider connection test failed")
                
                return True
        
        # If no existing provider, create new one
        provider_data = {
            "name": "Test Provider for Follow-up Investigation",
            "provider_type": "gmail",
            "email_address": "rohushanshinde@gmail.com",
            "display_name": "Rohushan Shinde",
            "smtp_host": "smtp.gmail.com",
            "smtp_port": 587,
            "smtp_username": "rohushanshinde@gmail.com",
            "smtp_password": "pajbdmcpcegppguz",
            "smtp_use_tls": True,
            "imap_host": "imap.gmail.com",
            "imap_port": 993,
            "imap_username": "rohushanshinde@gmail.com",
            "imap_password": "pajbdmcpcegppguz",
            "daily_send_limit": 500,
            "hourly_send_limit": 50,
            "is_default": True,
            "skip_connection_test": False
        }
        
        result = await self.make_request("POST", "/email-providers", provider_data)
        if result["success"]:
            self.test_data["email_provider_id"] = result["data"]["id"]
            print(f"✅ Email provider created: {result['data']['id']}")
            
            # Test the provider
            test_result = await self.make_request("POST", f"/email-providers/{self.test_data['email_provider_id']}/test")
            if test_result["success"]:
                test_data = test_result["data"]
                print(f"📧 Provider test results:")
                print(f"   SMTP: {test_data.get('smtp_test', 'unknown')}")
                print(f"   IMAP: {test_data.get('imap_test', 'unknown')}")
                print(f"   Overall: {test_data.get('overall_status', 'unknown')}")
                
                if test_data.get('overall_status') != 'passed':
                    self.results["provider_issues"].append("Provider connection test failed")
            
            return True
        else:
            print(f"❌ Failed to create email provider: {result.get('error', 'Unknown error')}")
            return False
    
    async def setup_prospect_list(self):
        """Setup prospect list"""
        print("\n" + "="*60)
        print("2. 📋 SETTING UP PROSPECT LIST")
        print("="*60)
        
        list_data = {
            "name": "Follow-up Investigation List",
            "description": "List for testing follow-up email delivery",
            "color": "#3B82F6",
            "tags": ["test", "follow-up"]
        }
        
        result = await self.make_request("POST", "/lists", list_data)
        if result["success"]:
            self.test_data["prospect_list_id"] = result["data"]["id"]
            print(f"✅ Prospect list created: {result['data']['id']}")
            return True
        else:
            print(f"❌ Failed to create prospect list: {result.get('error', 'Unknown error')}")
            return False
    
    async def setup_prospect(self):
        """Setup prospect (kasargovinda@gmail.com)"""
        print("\n" + "="*60)
        print("3. 👤 SETTING UP PROSPECT")
        print("="*60)
        
        # First, let's check if we can create prospects directly via API
        # If not, we'll need to use the database service
        
        try:
            # Try to create prospect using database service
            import sys
            sys.path.append('/app/backend')
            from app.services.database import db_service
            from app.utils.helpers import generate_id
            
            await db_service.connect()
            
            prospect_data = {
                "id": generate_id(),
                "first_name": "Kasargovinda",
                "last_name": "Test",
                "email": self.target_email,
                "company": "Test Company",
                "job_title": "Test Manager",
                "industry": "Technology",
                "phone": "+1234567890",
                "list_ids": [self.test_data["prospect_list_id"]],
                "tags": ["test", "follow-up-investigation"],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = await db_service.create_prospect(prospect_data)
            if result:
                self.test_data["prospect_id"] = prospect_data["id"]
                print(f"✅ Prospect created: {prospect_data['id']}")
                print(f"   Name: {prospect_data['first_name']} {prospect_data['last_name']}")
                print(f"   Email: {prospect_data['email']}")
                print(f"   Company: {prospect_data['company']}")
                return True
            else:
                print("❌ Failed to create prospect")
                return False
                
        except Exception as e:
            print(f"❌ Error creating prospect: {str(e)}")
            return False
    
    async def get_template(self):
        """Get an available email template"""
        print("\n" + "="*60)
        print("4. 📝 GETTING EMAIL TEMPLATE")
        print("="*60)
        
        result = await self.make_request("GET", "/templates")
        if result["success"] and result["data"]:
            templates = result["data"]
            # Use the first available template
            template = templates[0]
            self.test_data["template_id"] = template["id"]
            print(f"✅ Using template: {template.get('name', 'Unknown')}")
            print(f"   Template ID: {template['id']}")
            return True
        else:
            print("❌ No templates available")
            return False
    
    async def create_campaign(self):
        """Create campaign with follow-up enabled"""
        print("\n" + "="*60)
        print("5. 🚀 CREATING CAMPAIGN WITH FOLLOW-UP")
        print("="*60)
        
        # Create campaign with precise follow-up timing
        campaign_data = {
            "name": f"Follow-up Investigation Campaign - {datetime.now().strftime('%H:%M:%S')}",
            "template_id": self.test_data["template_id"],
            "list_ids": [self.test_data["prospect_list_id"]],
            "max_emails": 10,
            "schedule": None,
            "follow_up_enabled": True,
            "follow_up_schedule_type": "datetime",
            "follow_up_intervals": [1, 3, 5],  # 1, 3, 5 minutes for testing
            "follow_up_dates": [
                (datetime.utcnow() + timedelta(minutes=1)).isoformat(),
                (datetime.utcnow() + timedelta(minutes=3)).isoformat(),
                (datetime.utcnow() + timedelta(minutes=5)).isoformat()
            ],
            "follow_up_timezone": "UTC",
            "follow_up_time_window_start": "00:00",
            "follow_up_time_window_end": "23:59",
            "follow_up_days_of_week": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
            "follow_up_templates": []
        }
        
        result = await self.make_request("POST", "/campaigns", campaign_data)
        if result["success"]:
            self.test_data["campaign_id"] = result["data"]["id"]
            print(f"✅ Campaign created: {result['data']['id']}")
            print(f"   Name: {result['data']['name']}")
            print(f"   Follow-up enabled: {result['data']['follow_up_enabled']}")
            print(f"   Follow-up type: {result['data']['follow_up_schedule_type']}")
            print(f"   Follow-up dates: {result['data'].get('follow_up_dates', [])}")
            return True
        else:
            print(f"❌ Failed to create campaign: {result.get('error', 'Unknown error')}")
            return False
    
    async def send_campaign(self):
        """Send the campaign"""
        print("\n" + "="*60)
        print("6. 📤 SENDING CAMPAIGN")
        print("="*60)
        
        send_data = {
            "send_immediately": True,
            "email_provider_id": self.test_data["email_provider_id"],
            "max_emails": 10,
            "schedule_type": "immediate",
            "follow_up_enabled": True,
            "follow_up_intervals": [1, 3, 5],  # 1, 3, 5 minutes
            "follow_up_templates": []
        }
        
        result = await self.make_request("POST", f"/campaigns/{self.test_data['campaign_id']}/send", send_data)
        if result["success"]:
            print(f"✅ Campaign sent successfully")
            print(f"   Response: {result['data']}")
            self.results["campaign_sent"] = True
            return True
        else:
            print(f"❌ Failed to send campaign: {result.get('error', 'Unknown error')}")
            return False
    
    async def monitor_email_delivery(self, duration_minutes=10):
        """Monitor email delivery for specified duration"""
        print("\n" + "="*60)
        print(f"7. 👀 MONITORING EMAIL DELIVERY ({duration_minutes} minutes)")
        print("="*60)
        
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(minutes=duration_minutes)
        check_interval = 30  # Check every 30 seconds
        
        print(f"Monitoring from {start_time.strftime('%H:%M:%S')} to {end_time.strftime('%H:%M:%S')}")
        print(f"Checking every {check_interval} seconds...")
        
        previous_email_count = 0
        
        while datetime.utcnow() < end_time:
            current_time = datetime.utcnow()
            print(f"\n⏰ Check at {current_time.strftime('%H:%M:%S')}")
            
            # Get campaign details with email records
            result = await self.make_request("GET", f"/campaigns/{self.test_data['campaign_id']}")
            if result["success"]:
                campaign = result["data"]
                email_records = campaign.get("email_records", [])
                
                # Filter for our target email
                target_emails = [
                    record for record in email_records 
                    if record.get("recipient_email") == self.target_email
                ]
                
                if len(target_emails) > previous_email_count:
                    new_emails = target_emails[previous_email_count:]
                    print(f"📧 Found {len(new_emails)} new email(s)!")
                    
                    for email in new_emails:
                        print(f"   • Subject: {email.get('subject', 'N/A')}")
                        print(f"     Status: {email.get('status', 'N/A')}")
                        print(f"     Sent At: {email.get('sent_at', 'N/A')}")
                        print(f"     Is Follow-up: {email.get('is_follow_up', False)}")
                        print(f"     Follow-up Sequence: {email.get('follow_up_sequence', 'N/A')}")
                        print(f"     Provider ID: {email.get('email_provider_id', 'N/A')}")
                        
                        # Categorize emails
                        if email.get('is_follow_up', False):
                            self.results["follow_up_emails"].append(email)
                        else:
                            self.results["initial_emails"].append(email)
                    
                    previous_email_count = len(target_emails)
                else:
                    print(f"📊 No new emails (total: {len(target_emails)})")
                
                # Show analytics
                analytics = campaign.get("analytics", {})
                print(f"📈 Campaign Analytics:")
                print(f"   Total sent: {analytics.get('total_sent', 0)}")
                print(f"   Total failed: {analytics.get('total_failed', 0)}")
                print(f"   Success rate: {analytics.get('success_rate', 0):.1f}%")
            
            # Wait before next check
            await asyncio.sleep(check_interval)
        
        print(f"\n✅ Monitoring completed at {datetime.utcnow().strftime('%H:%M:%S')}")
    
    async def analyze_provider_usage(self):
        """Analyze which provider was used for different emails"""
        print("\n" + "="*60)
        print("8. 🔍 ANALYZING PROVIDER USAGE")
        print("="*60)
        
        all_emails = self.results["initial_emails"] + self.results["follow_up_emails"]
        
        if not all_emails:
            print("❌ No emails found to analyze")
            return
        
        # Get provider details
        providers_result = await self.make_request("GET", "/email-providers")
        if not providers_result["success"]:
            print("❌ Failed to get provider details")
            return
        
        providers = {p["id"]: p for p in providers_result["data"]}
        
        print(f"📊 Email Provider Usage Analysis:")
        print(f"   Total emails analyzed: {len(all_emails)}")
        
        provider_usage = {}
        for email in all_emails:
            provider_id = email.get("email_provider_id")
            is_follow_up = email.get("is_follow_up", False)
            
            if provider_id not in provider_usage:
                provider_usage[provider_id] = {"initial": 0, "follow_up": 0}
            
            if is_follow_up:
                provider_usage[provider_id]["follow_up"] += 1
            else:
                provider_usage[provider_id]["initial"] += 1
        
        for provider_id, usage in provider_usage.items():
            provider = providers.get(provider_id, {})
            provider_name = provider.get("name", "Unknown Provider")
            provider_email = provider.get("email_address", "Unknown")
            
            print(f"\n   📮 {provider_name} ({provider_email}):")
            print(f"      Initial emails: {usage['initial']}")
            print(f"      Follow-up emails: {usage['follow_up']}")
            print(f"      Total: {usage['initial'] + usage['follow_up']}")
            
            # Check if this provider appears in Gmail Sent folder
            if provider_email == "rohushanshinde@gmail.com":
                print(f"      ⚠️  This is the sender's Gmail - check Sent folder for delivery confirmation")
    
    async def check_follow_up_engine_logs(self):
        """Check follow-up engine processing"""
        print("\n" + "="*60)
        print("9. 🔧 CHECKING FOLLOW-UP ENGINE STATUS")
        print("="*60)
        
        # Get services status
        result = await self.make_request("GET", "/services/status")
        if result["success"]:
            services = result["data"]
            
            follow_up_engine = services.get("services", {}).get("smart_follow_up_engine", {})
            print(f"Follow-up Engine Status: {follow_up_engine.get('status', 'unknown')}")
            
            # Check for active campaigns
            campaigns_result = await self.make_request("GET", "/campaigns")
            if campaigns_result["success"]:
                campaigns = campaigns_result["data"]
                active_campaigns = [c for c in campaigns if c.get("status") in ["active", "completed"]]
                follow_up_campaigns = [c for c in active_campaigns if c.get("follow_up_enabled", False)]
                
                print(f"Active campaigns: {len(active_campaigns)}")
                print(f"Follow-up enabled campaigns: {len(follow_up_campaigns)}")
                
                for campaign in follow_up_campaigns:
                    print(f"   • {campaign.get('name', 'Unknown')}")
                    print(f"     Status: {campaign.get('status', 'Unknown')}")
                    print(f"     Follow-up type: {campaign.get('follow_up_schedule_type', 'interval')}")
    
    async def run_comprehensive_test(self):
        """Run comprehensive follow-up delivery test"""
        print("=" * 80)
        print("🔍 FOLLOW-UP EMAIL DELIVERY COMPREHENSIVE TEST")
        print("=" * 80)
        print(f"Target Email: {self.target_email}")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        
        await self.setup_session()
        
        try:
            # Setup phase
            print("\n🚀 SETUP PHASE")
            print("-" * 40)
            
            if not await self.setup_email_provider():
                print("❌ Setup failed at email provider step")
                return
            
            if not await self.setup_prospect_list():
                print("❌ Setup failed at prospect list step")
                return
            
            if not await self.setup_prospect():
                print("❌ Setup failed at prospect step")
                return
            
            if not await self.get_template():
                print("❌ Setup failed at template step")
                return
            
            if not await self.create_campaign():
                print("❌ Setup failed at campaign creation step")
                return
            
            self.results["setup_successful"] = True
            print("\n✅ SETUP PHASE COMPLETED SUCCESSFULLY")
            
            # Execution phase
            print("\n🚀 EXECUTION PHASE")
            print("-" * 40)
            
            if not await self.send_campaign():
                print("❌ Campaign sending failed")
                return
            
            # Monitoring phase
            print("\n🚀 MONITORING PHASE")
            print("-" * 40)
            
            await self.monitor_email_delivery(duration_minutes=8)
            
            # Analysis phase
            print("\n🚀 ANALYSIS PHASE")
            print("-" * 40)
            
            await self.analyze_provider_usage()
            await self.check_follow_up_engine_logs()
            
        finally:
            await self.cleanup_session()
        
        # Print final results
        self.print_final_results()
    
    def print_final_results(self):
        """Print comprehensive test results"""
        print("\n" + "=" * 80)
        print("📋 COMPREHENSIVE TEST RESULTS")
        print("=" * 80)
        
        # Setup Results
        print(f"\n🚀 SETUP RESULTS:")
        print(f"   Setup successful: {'✅' if self.results['setup_successful'] else '❌'}")
        print(f"   Campaign sent: {'✅' if self.results['campaign_sent'] else '❌'}")
        
        # Email Delivery Results
        initial_count = len(self.results["initial_emails"])
        follow_up_count = len(self.results["follow_up_emails"])
        total_count = initial_count + follow_up_count
        
        print(f"\n📧 EMAIL DELIVERY RESULTS:")
        print(f"   Total emails sent: {total_count}")
        print(f"   Initial emails: {initial_count}")
        print(f"   Follow-up emails: {follow_up_count}")
        
        # Detailed Email Analysis
        if self.results["initial_emails"]:
            print(f"\n📤 INITIAL EMAILS:")
            for i, email in enumerate(self.results["initial_emails"], 1):
                print(f"   {i}. Subject: {email.get('subject', 'N/A')}")
                print(f"      Status: {email.get('status', 'N/A')}")
                print(f"      Sent At: {email.get('sent_at', 'N/A')}")
        
        if self.results["follow_up_emails"]:
            print(f"\n🔄 FOLLOW-UP EMAILS:")
            for i, email in enumerate(self.results["follow_up_emails"], 1):
                print(f"   {i}. Subject: {email.get('subject', 'N/A')}")
                print(f"      Status: {email.get('status', 'N/A')}")
                print(f"      Sent At: {email.get('sent_at', 'N/A')}")
                print(f"      Sequence: {email.get('follow_up_sequence', 'N/A')}")
        
        # Provider Issues
        if self.results["provider_issues"]:
            print(f"\n⚠️ PROVIDER ISSUES:")
            for issue in self.results["provider_issues"]:
                print(f"   • {issue}")
        
        # Key Findings
        print(f"\n🔍 KEY FINDINGS:")
        
        if not self.results["setup_successful"]:
            print("   ❌ Test setup failed - cannot proceed with investigation")
        elif not self.results["campaign_sent"]:
            print("   ❌ Campaign sending failed - no emails to analyze")
        elif total_count == 0:
            print("   ❌ No emails were sent - possible system issue")
        elif initial_count > 0 and follow_up_count == 0:
            print("   ⚠️ Initial emails sent but no follow-ups - follow-up system may not be working")
        elif follow_up_count > 0:
            print("   ✅ Follow-up emails are being sent by the system")
            print("   ⚠️ If follow-ups don't appear in Gmail, check:")
            print("      • Gmail Sent folder")
            print("      • Spam/Junk folders")
            print("      • Email delivery logs")
            print("      • SMTP authentication issues")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        
        if self.results["provider_issues"]:
            print("   • Fix email provider connection issues")
        
        if follow_up_count == 0 and initial_count > 0:
            print("   • Check follow-up engine configuration")
            print("   • Verify follow-up timing settings")
            print("   • Check campaign follow-up settings")
        
        if follow_up_count > 0:
            print("   • Follow-up system is working - delivery issue may be:")
            print("     - Gmail filtering/spam detection")
            print("     - SMTP delivery delays")
            print("     - Email client synchronization")
            print("   • Check rohushanshinde@gmail.com Sent folder for confirmation")
        
        print("\n" + "=" * 80)
        print("✅ COMPREHENSIVE TEST COMPLETED")
        print("=" * 80)

async def main():
    """Main test execution"""
    tester = FollowUpDeliveryTester()
    await tester.run_comprehensive_test()

if __name__ == "__main__":
    asyncio.run(main())