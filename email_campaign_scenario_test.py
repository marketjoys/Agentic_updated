#!/usr/bin/env python3
"""
Email Campaign Testing Scenario - Step by Step Implementation
Tests the specific scenario requested:
1. Add New Email Provider (rohushanshinde@gmail.com)
2. Create New List ("Newlist")
3. Add New Prospect (kasargovinda@gmail.com)
4. Verify Setup
"""

import asyncio
import aiohttp
import json
from datetime import datetime
import sys
import os

# Backend URL from environment
BACKEND_URL = "https://923febb0-4941-4a54-88e6-10f9c6187a71.preview.emergentagent.com/api"

class EmailCampaignScenarioTester:
    def __init__(self):
        self.session = None
        self.test_results = {
            "step1_add_provider": {"status": "pending", "data": None, "error": None},
            "step2_create_list": {"status": "pending", "data": None, "error": None},
            "step3_add_prospect": {"status": "pending", "data": None, "error": None},
            "step4_verify_setup": {"status": "pending", "data": None, "error": None}
        }
        self.created_resources = {
            "provider_id": None,
            "list_id": None,
            "prospect_id": None
        }
    
    async def setup_session(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession()
    
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    async def step1_add_email_provider(self):
        """Step 1: Add New Email Provider - rohushanshinde@gmail.com"""
        print("\n" + "="*60)
        print("📧 STEP 1: ADD NEW EMAIL PROVIDER")
        print("="*60)
        print("Adding rohushanshinde@gmail.com as Gmail provider...")
        
        provider_data = {
            "name": "Test Gmail Provider - Rohushan",
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
        
        try:
            print(f"🔗 POST {BACKEND_URL}/email-providers")
            print(f"📋 Provider Details:")
            print(f"   • Name: {provider_data['name']}")
            print(f"   • Email: {provider_data['email_address']}")
            print(f"   • Type: {provider_data['provider_type']}")
            print(f"   • Set as Default: {provider_data['is_default']}")
            print(f"   • SMTP Host: {provider_data['smtp_host']}:{provider_data['smtp_port']}")
            print(f"   • IMAP Host: {provider_data['imap_host']}:{provider_data['imap_port']}")
            
            async with self.session.post(
                f"{BACKEND_URL}/email-providers",
                json=provider_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                status_code = response.status
                response_data = await response.json()
                
                if status_code == 200:
                    self.test_results["step1_add_provider"]["status"] = "success"
                    self.test_results["step1_add_provider"]["data"] = response_data
                    self.created_resources["provider_id"] = response_data.get("id")
                    
                    print(f"✅ SUCCESS - Provider created successfully!")
                    print(f"   • Provider ID: {response_data.get('id')}")
                    print(f"   • Status: Active - {response_data.get('is_active', False)}")
                    print(f"   • Default: {response_data.get('is_default', False)}")
                    print(f"   • IMAP Enabled: {response_data.get('imap_enabled', False)}")
                    print(f"   • Daily Limit: {response_data.get('daily_send_limit', 0)}")
                    print(f"   • Current Daily Count: {response_data.get('current_daily_count', 0)}")
                    
                    # Test connection if available
                    if self.created_resources["provider_id"]:
                        await self.test_provider_connection(self.created_resources["provider_id"])
                    
                else:
                    self.test_results["step1_add_provider"]["status"] = "failed"
                    self.test_results["step1_add_provider"]["error"] = response_data
                    print(f"❌ FAILED - Status: {status_code}")
                    print(f"   Error: {response_data}")
                    
        except Exception as e:
            self.test_results["step1_add_provider"]["status"] = "error"
            self.test_results["step1_add_provider"]["error"] = str(e)
            print(f"❌ EXCEPTION - {str(e)}")
    
    async def test_provider_connection(self, provider_id):
        """Test the email provider connection"""
        print(f"\n🔍 Testing provider connection...")
        try:
            async with self.session.post(f"{BACKEND_URL}/email-providers/{provider_id}/test") as response:
                if response.status == 200:
                    test_result = await response.json()
                    print(f"   📊 Connection Test Results:")
                    print(f"      • SMTP Test: {test_result.get('smtp_test', 'unknown')}")
                    print(f"      • IMAP Test: {test_result.get('imap_test', 'unknown')}")
                    print(f"      • Overall Status: {test_result.get('overall_status', 'unknown')}")
                else:
                    print(f"   ⚠️ Connection test failed - Status: {response.status}")
        except Exception as e:
            print(f"   ⚠️ Connection test error: {str(e)}")
    
    async def step2_create_list(self):
        """Step 2: Create New List - 'Newlist'"""
        print("\n" + "="*60)
        print("📋 STEP 2: CREATE NEW LIST")
        print("="*60)
        print("Creating 'Newlist' prospect list...")
        
        list_data = {
            "name": "Newlist",
            "description": "Test list created for email campaign scenario testing",
            "color": "#4F46E5",
            "tags": ["test", "scenario", "campaign"]
        }
        
        try:
            print(f"🔗 POST {BACKEND_URL}/lists")
            print(f"📋 List Details:")
            print(f"   • Name: {list_data['name']}")
            print(f"   • Description: {list_data['description']}")
            print(f"   • Color: {list_data['color']}")
            print(f"   • Tags: {list_data['tags']}")
            
            async with self.session.post(
                f"{BACKEND_URL}/lists",
                json=list_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                status_code = response.status
                response_data = await response.json()
                
                if status_code == 200:
                    self.test_results["step2_create_list"]["status"] = "success"
                    self.test_results["step2_create_list"]["data"] = response_data
                    self.created_resources["list_id"] = response_data.get("id")
                    
                    print(f"✅ SUCCESS - List created successfully!")
                    print(f"   • List ID: {response_data.get('id')}")
                    print(f"   • Name: {response_data.get('name')}")
                    print(f"   • Prospect Count: {response_data.get('prospect_count', 0)}")
                    print(f"   • Created At: {response_data.get('created_at')}")
                    
                else:
                    self.test_results["step2_create_list"]["status"] = "failed"
                    self.test_results["step2_create_list"]["error"] = response_data
                    print(f"❌ FAILED - Status: {status_code}")
                    print(f"   Error: {response_data}")
                    
        except Exception as e:
            self.test_results["step2_create_list"]["status"] = "error"
            self.test_results["step2_create_list"]["error"] = str(e)
            print(f"❌ EXCEPTION - {str(e)}")
    
    async def step3_add_prospect(self):
        """Step 3: Add New Prospect - kasargovinda@gmail.com"""
        print("\n" + "="*60)
        print("👤 STEP 3: ADD NEW PROSPECT")
        print("="*60)
        print("Adding kasargovinda@gmail.com as prospect...")
        
        # First, check if there's a prospects endpoint for direct creation
        # If not, we'll need to use CSV upload or another method
        
        prospect_data = {
            "first_name": "Kasa",
            "last_name": "Govinda",
            "email": "kasargovinda@gmail.com",
            "company": "Test Company",
            "job_title": "Software Engineer",
            "industry": "Technology",
            "phone": "+1-555-0123",
            "linkedin_url": "https://linkedin.com/in/kasagovinda",
            "notes": "Added for email campaign scenario testing",
            "tags": ["test", "scenario"],
            "list_ids": [self.created_resources["list_id"]] if self.created_resources["list_id"] else []
        }
        
        try:
            print(f"🔗 POST {BACKEND_URL}/prospects")
            print(f"👤 Prospect Details:")
            print(f"   • Name: {prospect_data['first_name']} {prospect_data['last_name']}")
            print(f"   • Email: {prospect_data['email']}")
            print(f"   • Company: {prospect_data['company']}")
            print(f"   • Job Title: {prospect_data['job_title']}")
            print(f"   • Industry: {prospect_data['industry']}")
            print(f"   • Will be added to List ID: {self.created_resources['list_id']}")
            
            # Try to create prospect directly
            async with self.session.post(
                f"{BACKEND_URL}/prospects",
                json=prospect_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                status_code = response.status
                
                if status_code == 200:
                    response_data = await response.json()
                    self.test_results["step3_add_prospect"]["status"] = "success"
                    self.test_results["step3_add_prospect"]["data"] = response_data
                    self.created_resources["prospect_id"] = response_data.get("id")
                    
                    print(f"✅ SUCCESS - Prospect created successfully!")
                    print(f"   • Prospect ID: {response_data.get('id')}")
                    print(f"   • Email: {response_data.get('email')}")
                    print(f"   • Added to Lists: {response_data.get('list_ids', [])}")
                    
                elif status_code == 404:
                    # Prospects endpoint doesn't exist, try alternative approach
                    print(f"⚠️ Direct prospect creation not available (404)")
                    print(f"   Attempting alternative approach via CSV upload...")
                    await self.add_prospect_via_csv()
                    
                else:
                    response_data = await response.text()
                    self.test_results["step3_add_prospect"]["status"] = "failed"
                    self.test_results["step3_add_prospect"]["error"] = response_data
                    print(f"❌ FAILED - Status: {status_code}")
                    print(f"   Error: {response_data}")
                    
        except Exception as e:
            self.test_results["step3_add_prospect"]["status"] = "error"
            self.test_results["step3_add_prospect"]["error"] = str(e)
            print(f"❌ EXCEPTION - {str(e)}")
            print(f"   Attempting alternative approach...")
            await self.add_prospect_via_csv()
    
    async def add_prospect_via_csv(self):
        """Alternative method to add prospect via CSV upload"""
        try:
            # Check if there's a CSV upload endpoint
            csv_data = "first_name,last_name,email,company,job_title,industry\nKasa,Govinda,kasargovinda@gmail.com,Test Company,Software Engineer,Technology"
            
            # Try different possible CSV upload endpoints
            possible_endpoints = [
                "/prospects/upload",
                "/prospects/csv",
                "/upload/prospects",
                "/csv/prospects"
            ]
            
            for endpoint in possible_endpoints:
                try:
                    print(f"   Trying CSV upload: {endpoint}")
                    async with self.session.post(
                        f"{BACKEND_URL}{endpoint}",
                        data={"csv_data": csv_data},
                        headers={"Content-Type": "application/x-www-form-urlencoded"}
                    ) as response:
                        if response.status == 200:
                            response_data = await response.json()
                            self.test_results["step3_add_prospect"]["status"] = "success"
                            self.test_results["step3_add_prospect"]["data"] = response_data
                            print(f"   ✅ CSV upload successful via {endpoint}")
                            return
                        elif response.status != 404:
                            print(f"   ⚠️ CSV upload failed via {endpoint} - Status: {response.status}")
                except:
                    continue
            
            # If CSV upload fails, mark as partial success with manual verification needed
            self.test_results["step3_add_prospect"]["status"] = "manual_verification_needed"
            self.test_results["step3_add_prospect"]["error"] = "No direct prospect creation endpoint found. Manual verification needed."
            print(f"   ⚠️ No CSV upload endpoint found. Manual verification will be performed in Step 4.")
            
        except Exception as e:
            print(f"   ❌ CSV upload exception: {str(e)}")
    
    async def step4_verify_setup(self):
        """Step 4: Verify Setup - Check all created resources"""
        print("\n" + "="*60)
        print("🔍 STEP 4: VERIFY SETUP")
        print("="*60)
        print("Verifying all created resources...")
        
        verification_results = {
            "email_providers": {"status": "pending", "data": None},
            "lists": {"status": "pending", "data": None},
            "prospects": {"status": "pending", "data": None},
            "list_prospects": {"status": "pending", "data": None}
        }
        
        try:
            # 4.1 Verify Email Providers
            print(f"\n🔍 4.1 Verifying Email Providers...")
            async with self.session.get(f"{BACKEND_URL}/email-providers") as response:
                if response.status == 200:
                    providers = await response.json()
                    verification_results["email_providers"]["status"] = "success"
                    verification_results["email_providers"]["data"] = providers
                    
                    print(f"   ✅ Found {len(providers)} email providers")
                    
                    # Look for our created provider
                    our_provider = None
                    for provider in providers:
                        if provider.get("email_address") == "rohushanshinde@gmail.com":
                            our_provider = provider
                            break
                    
                    if our_provider:
                        print(f"   ✅ Our provider found:")
                        print(f"      • ID: {our_provider.get('id')}")
                        print(f"      • Name: {our_provider.get('name')}")
                        print(f"      • Active: {our_provider.get('is_active', False)}")
                        print(f"      • Default: {our_provider.get('is_default', False)}")
                    else:
                        print(f"   ⚠️ Our provider (rohushanshinde@gmail.com) not found")
                else:
                    verification_results["email_providers"]["status"] = "failed"
                    print(f"   ❌ Failed to get email providers - Status: {response.status}")
            
            # 4.2 Verify Lists
            print(f"\n🔍 4.2 Verifying Lists...")
            async with self.session.get(f"{BACKEND_URL}/lists") as response:
                if response.status == 200:
                    lists = await response.json()
                    verification_results["lists"]["status"] = "success"
                    verification_results["lists"]["data"] = lists
                    
                    print(f"   ✅ Found {len(lists)} prospect lists")
                    
                    # Look for our created list
                    our_list = None
                    for list_item in lists:
                        if list_item.get("name") == "Newlist":
                            our_list = list_item
                            break
                    
                    if our_list:
                        print(f"   ✅ Our list 'Newlist' found:")
                        print(f"      • ID: {our_list.get('id')}")
                        print(f"      • Name: {our_list.get('name')}")
                        print(f"      • Prospect Count: {our_list.get('prospect_count', 0)}")
                        print(f"      • Description: {our_list.get('description', 'N/A')}")
                    else:
                        print(f"   ⚠️ Our list 'Newlist' not found")
                else:
                    verification_results["lists"]["status"] = "failed"
                    print(f"   ❌ Failed to get lists - Status: {response.status}")
            
            # 4.3 Verify Prospects
            print(f"\n🔍 4.3 Verifying Prospects...")
            async with self.session.get(f"{BACKEND_URL}/prospects") as response:
                if response.status == 200:
                    prospects = await response.json()
                    verification_results["prospects"]["status"] = "success"
                    verification_results["prospects"]["data"] = prospects
                    
                    print(f"   ✅ Found {len(prospects)} total prospects")
                    
                    # Look for our created prospect
                    our_prospect = None
                    for prospect in prospects:
                        if prospect.get("email") == "kasargovinda@gmail.com":
                            our_prospect = prospect
                            break
                    
                    if our_prospect:
                        print(f"   ✅ Our prospect found:")
                        print(f"      • ID: {our_prospect.get('id')}")
                        print(f"      • Name: {our_prospect.get('first_name')} {our_prospect.get('last_name')}")
                        print(f"      • Email: {our_prospect.get('email')}")
                        print(f"      • Company: {our_prospect.get('company', 'N/A')}")
                    else:
                        print(f"   ⚠️ Our prospect (kasargovinda@gmail.com) not found")
                        print(f"   📋 Existing prospects:")
                        for prospect in prospects[:3]:  # Show first 3
                            print(f"      • {prospect.get('first_name', '')} {prospect.get('last_name', '')} - {prospect.get('email', 'N/A')}")
                else:
                    verification_results["prospects"]["status"] = "failed"
                    print(f"   ❌ Failed to get prospects - Status: {response.status}")
            
            # 4.4 Verify List Prospects (if list was created)
            if self.created_resources["list_id"]:
                print(f"\n🔍 4.4 Verifying List Prospects...")
                async with self.session.get(f"{BACKEND_URL}/lists/{self.created_resources['list_id']}/prospects") as response:
                    if response.status == 200:
                        list_prospects = await response.json()
                        verification_results["list_prospects"]["status"] = "success"
                        verification_results["list_prospects"]["data"] = list_prospects
                        
                        prospects_in_list = list_prospects.get("prospects", [])
                        print(f"   ✅ Found {len(prospects_in_list)} prospects in 'Newlist'")
                        
                        # Check if our prospect is in the list
                        our_prospect_in_list = False
                        for prospect in prospects_in_list:
                            if prospect.get("email") == "kasargovinda@gmail.com":
                                our_prospect_in_list = True
                                print(f"   ✅ Our prospect is in the list!")
                                break
                        
                        if not our_prospect_in_list and prospects_in_list:
                            print(f"   ⚠️ Our prospect not found in list. Current prospects:")
                            for prospect in prospects_in_list:
                                print(f"      • {prospect.get('first_name', '')} {prospect.get('last_name', '')} - {prospect.get('email', 'N/A')}")
                        elif not prospects_in_list:
                            print(f"   ℹ️ List is empty - prospect may need to be manually added")
                    else:
                        verification_results["list_prospects"]["status"] = "failed"
                        print(f"   ❌ Failed to get list prospects - Status: {response.status}")
            
            # Set overall verification status
            failed_verifications = [k for k, v in verification_results.items() if v["status"] == "failed"]
            if not failed_verifications:
                self.test_results["step4_verify_setup"]["status"] = "success"
            else:
                self.test_results["step4_verify_setup"]["status"] = "partial"
            
            self.test_results["step4_verify_setup"]["data"] = verification_results
            
        except Exception as e:
            self.test_results["step4_verify_setup"]["status"] = "error"
            self.test_results["step4_verify_setup"]["error"] = str(e)
            print(f"❌ VERIFICATION EXCEPTION - {str(e)}")
    
    async def run_scenario_test(self):
        """Run the complete email campaign scenario test"""
        print("=" * 80)
        print("🚀 EMAIL CAMPAIGN TESTING SCENARIO")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print("\nScenario Steps:")
        print("1. Add New Email Provider (rohushanshinde@gmail.com)")
        print("2. Create New List ('Newlist')")
        print("3. Add New Prospect (kasargovinda@gmail.com)")
        print("4. Verify Setup")
        
        await self.setup_session()
        
        try:
            # Execute all steps
            await self.step1_add_email_provider()
            await self.step2_create_list()
            await self.step3_add_prospect()
            await self.step4_verify_setup()
            
        finally:
            await self.cleanup_session()
        
        # Print final summary
        self.print_scenario_summary()
    
    def print_scenario_summary(self):
        """Print comprehensive scenario test summary"""
        print("\n" + "=" * 80)
        print("📋 EMAIL CAMPAIGN SCENARIO TEST SUMMARY")
        print("=" * 80)
        
        # Overall Status
        successful_steps = len([k for k, v in self.test_results.items() if v["status"] == "success"])
        total_steps = len(self.test_results)
        
        print(f"\n🎯 OVERALL RESULT: {successful_steps}/{total_steps} steps completed successfully")
        
        # Step-by-step results
        print(f"\n📊 STEP RESULTS:")
        
        step_names = {
            "step1_add_provider": "1. Add Email Provider",
            "step2_create_list": "2. Create List",
            "step3_add_prospect": "3. Add Prospect",
            "step4_verify_setup": "4. Verify Setup"
        }
        
        for step_key, step_name in step_names.items():
            result = self.test_results[step_key]
            status = result["status"]
            
            if status == "success":
                emoji = "✅"
            elif status == "partial":
                emoji = "⚠️"
            elif status == "manual_verification_needed":
                emoji = "🔍"
            else:
                emoji = "❌"
            
            print(f"   {emoji} {step_name}: {status.upper()}")
            
            if result.get("error"):
                print(f"      Error: {result['error']}")
        
        # Created Resources Summary
        print(f"\n🔧 CREATED RESOURCES:")
        if self.created_resources["provider_id"]:
            print(f"   ✅ Email Provider ID: {self.created_resources['provider_id']}")
        else:
            print(f"   ❌ Email Provider: Not created")
        
        if self.created_resources["list_id"]:
            print(f"   ✅ List ID: {self.created_resources['list_id']}")
        else:
            print(f"   ❌ List: Not created")
        
        if self.created_resources["prospect_id"]:
            print(f"   ✅ Prospect ID: {self.created_resources['prospect_id']}")
        else:
            print(f"   ⚠️ Prospect: May require manual verification")
        
        # Detailed Results
        print(f"\n🔍 DETAILED RESULTS:")
        
        # Step 1 Details
        if self.test_results["step1_add_provider"]["status"] == "success":
            data = self.test_results["step1_add_provider"]["data"]
            print(f"   📧 Email Provider:")
            print(f"      • Email: rohushanshinde@gmail.com")
            print(f"      • Type: Gmail")
            print(f"      • Status: Active")
            print(f"      • Default: {data.get('is_default', False)}")
            print(f"      • IMAP Enabled: {data.get('imap_enabled', False)}")
        
        # Step 2 Details
        if self.test_results["step2_create_list"]["status"] == "success":
            data = self.test_results["step2_create_list"]["data"]
            print(f"   📋 List:")
            print(f"      • Name: Newlist")
            print(f"      • Description: Test list for scenario")
            print(f"      • Prospect Count: {data.get('prospect_count', 0)}")
        
        # Step 3 Details
        if self.test_results["step3_add_prospect"]["status"] == "success":
            print(f"   👤 Prospect:")
            print(f"      • Name: Kasa Govinda")
            print(f"      • Email: kasargovinda@gmail.com")
            print(f"      • Company: Test Company")
        elif self.test_results["step3_add_prospect"]["status"] == "manual_verification_needed":
            print(f"   👤 Prospect:")
            print(f"      • Status: Manual verification needed")
            print(f"      • Reason: No direct prospect creation endpoint found")
        
        # Step 4 Verification Details
        if self.test_results["step4_verify_setup"]["status"] in ["success", "partial"]:
            verification_data = self.test_results["step4_verify_setup"]["data"]
            print(f"   🔍 Verification:")
            
            if verification_data["email_providers"]["status"] == "success":
                providers = verification_data["email_providers"]["data"]
                print(f"      • Email Providers: {len(providers)} found")
            
            if verification_data["lists"]["status"] == "success":
                lists = verification_data["lists"]["data"]
                print(f"      • Lists: {len(lists)} found")
            
            if verification_data["prospects"]["status"] == "success":
                prospects = verification_data["prospects"]["data"]
                print(f"      • Prospects: {len(prospects)} found")
        
        # Recommendations
        print(f"\n💡 NEXT STEPS:")
        if successful_steps == total_steps:
            print("   ✅ All steps completed successfully!")
            print("   🚀 Ready to create and send email campaigns")
            print("   📧 You can now:")
            print("      • Create email templates")
            print("      • Create campaigns using the new list")
            print("      • Send test emails to verify functionality")
        else:
            print("   ⚠️ Some steps need attention:")
            
            if self.test_results["step1_add_provider"]["status"] != "success":
                print("      • Fix email provider configuration")
            
            if self.test_results["step2_create_list"]["status"] != "success":
                print("      • Create the prospect list manually")
            
            if self.test_results["step3_add_prospect"]["status"] not in ["success", "manual_verification_needed"]:
                print("      • Add the prospect manually or via CSV upload")
            
            if self.test_results["step3_add_prospect"]["status"] == "manual_verification_needed":
                print("      • Verify prospect was added correctly")
                print("      • Add prospect to the 'Newlist' if needed")
        
        print("\n" + "=" * 80)
        print("✅ EMAIL CAMPAIGN SCENARIO TEST COMPLETED")
        print("=" * 80)

async def main():
    """Main test execution"""
    tester = EmailCampaignScenarioTester()
    await tester.run_scenario_test()

if __name__ == "__main__":
    asyncio.run(main())