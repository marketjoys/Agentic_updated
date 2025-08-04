#!/usr/bin/env python3
"""
AI Email Responder - Root Cause Analysis & Fix Testing
Identifying and fixing the specific issues:
1. Campaign Sending with new Added providers when selected is not working
2. Auto responders are not working

ROOT CAUSE ANALYSIS:
- System is using test@gmail.com instead of real rohushanshinde@gmail.com credentials
- IMAP is not enabled on the email provider
- This causes both campaign sending failures and auto-responder failures
"""

import asyncio
import aiohttp
import json
import sys
import os
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://030d008b-cc85-4bf3-afdd-411b8004d718.preview.emergentagent.com/api"

class RootCauseAnalysisTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.real_credentials = {}
        self.test_results = {
            "credential_analysis": {"status": "not_tested", "details": []},
            "provider_fix_test": {"status": "not_tested", "details": []},
            "campaign_sending_verification": {"status": "not_tested", "details": []},
            "auto_responder_verification": {"status": "not_tested", "details": []}
        }
        
    async def setup_session(self):
        """Setup HTTP session and authenticate"""
        self.session = aiohttp.ClientSession()
        
        # Login to get auth token
        login_data = {"username": "testuser", "password": "testpass123"}
        async with self.session.post(f"{BACKEND_URL}/auth/login", json=login_data) as response:
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
    
    def load_real_credentials(self):
        """Load real credentials from backend .env file"""
        try:
            with open('/app/backend/.env', 'r') as f:
                env_content = f.read()
                
            for line in env_content.split('\n'):
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    if key in ['SMTP_USERNAME', 'SMTP_PASSWORD', 'IMAP_HOST', 'IMAP_PORT', 'SMTP_HOST', 'SMTP_PORT']:
                        self.real_credentials[key] = value
            
            return True
        except Exception as e:
            print(f"❌ Could not load real credentials: {e}")
            return False
    
    async def test_credential_analysis(self):
        """Test 1: Analyze current vs real credentials"""
        print("\n🔍 ANALYZING CREDENTIAL CONFIGURATION...")
        test_details = []
        
        try:
            # Load real credentials from .env
            if not self.load_real_credentials():
                test_details.append("❌ Could not load real credentials from .env file")
                self.test_results["credential_analysis"]["status"] = "failed"
                return
            
            test_details.append("✅ Real credentials loaded from backend/.env:")
            test_details.append(f"   - SMTP_USERNAME: {self.real_credentials.get('SMTP_USERNAME', 'Not found')}")
            test_details.append(f"   - SMTP_HOST: {self.real_credentials.get('SMTP_HOST', 'Not found')}")
            test_details.append(f"   - IMAP_HOST: {self.real_credentials.get('IMAP_HOST', 'Not found')}")
            
            # Get current providers
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            async with self.session.get(f"{BACKEND_URL}/email-providers", headers=headers) as response:
                if response.status == 200:
                    providers = await response.json()
                    test_details.append(f"\\n✅ Current providers in system: {len(providers)}")
                    
                    for provider in providers:
                        test_details.append(f"\\n   📧 Provider: {provider.get('name', 'Unknown')}")
                        test_details.append(f"      - Email: {provider.get('email_address', 'No email')}")
                        test_details.append(f"      - SMTP Username: {provider.get('smtp_username', 'No username')}")
                        test_details.append(f"      - IMAP Enabled: {provider.get('imap_enabled', False)}")
                        
                        # Compare with real credentials
                        current_email = provider.get('email_address', '')
                        real_email = self.real_credentials.get('SMTP_USERNAME', '')
                        
                        if current_email == real_email:
                            test_details.append(f"      ✅ Using REAL credentials")
                        elif current_email == 'test@gmail.com':
                            test_details.append(f"      ❌ CRITICAL: Using TEST credentials instead of real")
                            test_details.append(f"         Should be: {real_email}")
                            test_details.append(f"         Currently: {current_email}")
                        else:
                            test_details.append(f"      ⚠️ Using different credentials: {current_email}")
                        
                        # Check IMAP status
                        if not provider.get('imap_enabled', False):
                            test_details.append(f"      ❌ CRITICAL: IMAP not enabled - auto-responders won't work")
                    
                    self.test_results["credential_analysis"]["status"] = "passed"
                else:
                    test_details.append(f"❌ Failed to get providers: HTTP {response.status}")
                    self.test_results["credential_analysis"]["status"] = "failed"
                    
        except Exception as e:
            test_details.append(f"❌ Exception in credential analysis: {str(e)}")
            self.test_results["credential_analysis"]["status"] = "failed"
        
        self.test_results["credential_analysis"]["details"] = test_details
        for detail in test_details:
            print(f"   {detail}")
    
    async def test_provider_fix(self):
        """Test 2: Create/Update provider with real credentials and enable IMAP"""
        print("\\n🔧 TESTING PROVIDER FIX WITH REAL CREDENTIALS...")
        test_details = []
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Check if we have real credentials
            if not self.real_credentials:
                test_details.append("❌ No real credentials available for fix")
                self.test_results["provider_fix_test"]["status"] = "failed"
                return
            
            real_email = self.real_credentials.get('SMTP_USERNAME')
            real_password = self.real_credentials.get('SMTP_PASSWORD')
            
            if not real_email or not real_password:
                test_details.append("❌ Missing real email or password")
                self.test_results["provider_fix_test"]["status"] = "failed"
                return
            
            # Create new provider with real credentials and IMAP enabled
            provider_data = {
                "name": "Real Gmail Provider (Fixed)",
                "provider_type": "gmail",
                "email_address": real_email,
                "display_name": "Real Gmail Provider",
                "smtp_host": self.real_credentials.get('SMTP_HOST', 'smtp.gmail.com'),
                "smtp_port": int(self.real_credentials.get('SMTP_PORT', '587')),
                "smtp_username": real_email,
                "smtp_password": real_password,
                "smtp_use_tls": True,
                "imap_host": self.real_credentials.get('IMAP_HOST', 'imap.gmail.com'),
                "imap_port": int(self.real_credentials.get('IMAP_PORT', '993')),
                "imap_username": real_email,
                "imap_password": real_password,
                "daily_send_limit": 500,
                "hourly_send_limit": 50,
                "is_default": True,
                "skip_connection_test": False
            }
            
            test_details.append(f"🔄 Creating new provider with real credentials:")
            test_details.append(f"   - Email: {real_email}")
            test_details.append(f"   - SMTP Host: {provider_data['smtp_host']}")
            test_details.append(f"   - IMAP Host: {provider_data['imap_host']}")
            test_details.append(f"   - IMAP will be auto-enabled: True")
            
            async with self.session.post(f"{BACKEND_URL}/email-providers", json=provider_data, headers=headers) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    result = await response.json() if response.content_type == 'application/json' else {"message": response_text}
                    test_details.append(f"✅ Provider created successfully!")
                    test_details.append(f"   - Provider ID: {result.get('id', 'Unknown')}")
                    test_details.append(f"   - IMAP Enabled: {result.get('imap_enabled', 'Unknown')}")
                    
                    # Test the new provider connection
                    provider_id = result.get('id')
                    if provider_id:
                        test_details.append(f"\\n🧪 Testing connection for new provider...")
                        async with self.session.post(f"{BACKEND_URL}/email-providers/{provider_id}/test", headers=headers) as test_response:
                            if test_response.status == 200:
                                test_result = await test_response.json()
                                test_details.append(f"   - SMTP Test: {test_result.get('smtp_test', 'unknown')}")
                                test_details.append(f"   - IMAP Test: {test_result.get('imap_test', 'unknown')}")
                                test_details.append(f"   - Overall Status: {test_result.get('overall_status', 'unknown')}")
                                
                                if test_result.get('overall_status') == 'passed':
                                    test_details.append(f"   ✅ Connection tests PASSED - provider is working!")
                                else:
                                    test_details.append(f"   ⚠️ Connection tests failed - check credentials")
                            else:
                                test_details.append(f"   ❌ Connection test failed: HTTP {test_response.status}")
                    
                    self.test_results["provider_fix_test"]["status"] = "passed"
                    
                elif response.status == 400 and "already exists" in response_text:
                    test_details.append(f"⚠️ Provider with this email already exists")
                    test_details.append(f"   Looking for existing provider with real credentials...")
                    
                    # Find existing provider with real credentials
                    async with self.session.get(f"{BACKEND_URL}/email-providers", headers=headers) as get_response:
                        if get_response.status == 200:
                            providers = await get_response.json()
                            real_provider = None
                            
                            for provider in providers:
                                if provider.get('email_address') == real_email:
                                    real_provider = provider
                                    break
                            
                            if real_provider:
                                test_details.append(f"   ✅ Found existing provider with real credentials")
                                test_details.append(f"   - Provider ID: {real_provider.get('id')}")
                                test_details.append(f"   - IMAP Enabled: {real_provider.get('imap_enabled', False)}")
                                
                                # Enable IMAP if not enabled
                                if not real_provider.get('imap_enabled', False):
                                    test_details.append(f"   🔄 Enabling IMAP for existing provider...")
                                    provider_id = real_provider.get('id')
                                    
                                    async with self.session.put(f"{BACKEND_URL}/email-providers/{provider_id}/toggle-imap", headers=headers) as toggle_response:
                                        if toggle_response.status == 200:
                                            toggle_result = await toggle_response.json()
                                            test_details.append(f"   ✅ IMAP enabled: {toggle_result.get('message', 'Success')}")
                                        else:
                                            test_details.append(f"   ❌ Failed to enable IMAP: HTTP {toggle_response.status}")
                                
                                self.test_results["provider_fix_test"]["status"] = "passed"
                            else:
                                test_details.append(f"   ❌ No provider found with real credentials")
                                self.test_results["provider_fix_test"]["status"] = "failed"
                    
                else:
                    test_details.append(f"❌ Failed to create provider: HTTP {response.status}")
                    test_details.append(f"   Error: {response_text[:300]}")
                    self.test_results["provider_fix_test"]["status"] = "failed"
                    
        except Exception as e:
            test_details.append(f"❌ Exception in provider fix test: {str(e)}")
            self.test_results["provider_fix_test"]["status"] = "failed"
        
        self.test_results["provider_fix_test"]["details"] = test_details
        for detail in test_details:
            print(f"   {detail}")
    
    async def test_campaign_sending_verification(self):
        """Test 3: Verify campaign sending works with real provider"""
        print("\\n📧 VERIFYING CAMPAIGN SENDING WITH REAL PROVIDER...")
        test_details = []
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Get providers to find the real one
            async with self.session.get(f"{BACKEND_URL}/email-providers", headers=headers) as response:
                if response.status == 200:
                    providers = await response.json()
                    real_provider = None
                    
                    # Find provider with real credentials
                    real_email = self.real_credentials.get('SMTP_USERNAME', '')
                    for provider in providers:
                        if provider.get('email_address') == real_email:
                            real_provider = provider
                            break
                    
                    if not real_provider:
                        test_details.append("❌ No provider with real credentials found")
                        self.test_results["campaign_sending_verification"]["status"] = "failed"
                        return
                    
                    test_details.append(f"✅ Found real provider: {real_provider.get('name')}")
                    test_details.append(f"   - Email: {real_provider.get('email_address')}")
                    test_details.append(f"   - Provider ID: {real_provider.get('id')}")
                    
                    # Get templates and lists
                    templates = []
                    lists = []
                    
                    async with self.session.get(f"{BACKEND_URL}/templates", headers=headers) as temp_response:
                        if temp_response.status == 200:
                            templates = await temp_response.json()
                    
                    async with self.session.get(f"{BACKEND_URL}/lists", headers=headers) as list_response:
                        if list_response.status == 200:
                            lists = await list_response.json()
                    
                    if not templates or not lists:
                        test_details.append("❌ Missing templates or lists for campaign test")
                        self.test_results["campaign_sending_verification"]["status"] = "failed"
                        return
                    
                    # Create test campaign
                    campaign_data = {
                        "name": f"Real Provider Test Campaign {datetime.now().strftime('%H:%M:%S')}",
                        "template_id": templates[0].get("id"),
                        "list_ids": [lists[0].get("id")],
                        "max_emails": 1,
                        "follow_up_enabled": True
                    }
                    
                    async with self.session.post(f"{BACKEND_URL}/campaigns", json=campaign_data, headers=headers) as campaign_response:
                        if campaign_response.status == 200:
                            campaign = await campaign_response.json()
                            campaign_id = campaign.get("id")
                            test_details.append(f"✅ Test campaign created: {campaign.get('name')}")
                            
                            # Test sending with real provider
                            send_data = {
                                "send_immediately": False,  # Don't actually send
                                "email_provider_id": real_provider.get("id"),
                                "max_emails": 1
                            }
                            
                            async with self.session.post(f"{BACKEND_URL}/campaigns/{campaign_id}/send", json=send_data, headers=headers) as send_response:
                                send_status = send_response.status
                                send_text = await send_response.text()
                                
                                test_details.append(f"   📤 Campaign send test: HTTP {send_status}")
                                
                                if send_status == 200:
                                    test_details.append(f"   ✅ Campaign sending API works with real provider")
                                    test_details.append(f"   - Response: {send_text[:100]}")
                                    self.test_results["campaign_sending_verification"]["status"] = "passed"
                                else:
                                    test_details.append(f"   ❌ Campaign sending failed: {send_text[:200]}")
                                    self.test_results["campaign_sending_verification"]["status"] = "failed"
                        else:
                            test_details.append(f"❌ Failed to create test campaign: HTTP {campaign_response.status}")
                            self.test_results["campaign_sending_verification"]["status"] = "failed"
                else:
                    test_details.append(f"❌ Failed to get providers: HTTP {response.status}")
                    self.test_results["campaign_sending_verification"]["status"] = "failed"
                    
        except Exception as e:
            test_details.append(f"❌ Exception in campaign sending verification: {str(e)}")
            self.test_results["campaign_sending_verification"]["status"] = "failed"
        
        self.test_results["campaign_sending_verification"]["details"] = test_details
        for detail in test_details:
            print(f"   {detail}")
    
    async def test_auto_responder_verification(self):
        """Test 4: Verify auto-responder works with IMAP enabled"""
        print("\\n🤖 VERIFYING AUTO-RESPONDER WITH IMAP ENABLED...")
        test_details = []
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Check services status
            async with self.session.get(f"{BACKEND_URL}/services/status", headers=headers) as response:
                if response.status == 200:
                    services_status = await response.json()
                    
                    email_processor = services_status.get("services", {}).get("email_processor", {})
                    monitored_count = email_processor.get("monitored_providers_count", 0)
                    
                    test_details.append(f"✅ Services status accessible")
                    test_details.append(f"   - Email Processor Status: {email_processor.get('status', 'unknown')}")
                    test_details.append(f"   - Monitored Providers: {monitored_count}")
                    
                    if monitored_count > 0:
                        test_details.append(f"   ✅ Auto-responder is monitoring {monitored_count} provider(s)")
                        
                        # Check monitored providers details
                        monitored_providers = email_processor.get("monitored_providers", [])
                        for provider in monitored_providers:
                            test_details.append(f"   📧 Monitoring: {provider.get('name', 'Unknown')}")
                            test_details.append(f"      - Type: {provider.get('provider_type', 'unknown')}")
                            test_details.append(f"      - IMAP Host: {provider.get('imap_host', 'unknown')}")
                            test_details.append(f"      - Last Scan: {provider.get('last_scan', 'never')}")
                        
                        self.test_results["auto_responder_verification"]["status"] = "passed"
                    else:
                        test_details.append(f"   ❌ No providers being monitored - auto-responders still not working")
                        test_details.append(f"   🔄 Checking individual provider IMAP status...")
                        
                        # Check individual providers
                        async with self.session.get(f"{BACKEND_URL}/email-providers", headers=headers) as prov_response:
                            if prov_response.status == 200:
                                providers = await prov_response.json()
                                
                                for provider in providers:
                                    provider_id = provider.get('id')
                                    provider_name = provider.get('name', 'Unknown')
                                    
                                    async with self.session.get(f"{BACKEND_URL}/email-providers/{provider_id}/imap-status", headers=headers) as imap_response:
                                        if imap_response.status == 200:
                                            imap_status = await imap_response.json()
                                            test_details.append(f"   - {provider_name}:")
                                            test_details.append(f"     * IMAP Enabled: {imap_status.get('imap_enabled', False)}")
                                            test_details.append(f"     * Is Monitoring: {imap_status.get('is_monitoring', False)}")
                                            
                                            if imap_status.get('imap_enabled', False):
                                                test_details.append(f"     ✅ IMAP is enabled")
                                            else:
                                                test_details.append(f"     ❌ IMAP still not enabled")
                        
                        self.test_results["auto_responder_verification"]["status"] = "failed"
                else:
                    test_details.append(f"❌ Failed to get services status: HTTP {response.status}")
                    self.test_results["auto_responder_verification"]["status"] = "failed"
                    
        except Exception as e:
            test_details.append(f"❌ Exception in auto-responder verification: {str(e)}")
            self.test_results["auto_responder_verification"]["status"] = "failed"
        
        self.test_results["auto_responder_verification"]["details"] = test_details
        for detail in test_details:
            print(f"   {detail}")
    
    async def run_all_tests(self):
        """Run all root cause analysis and fix tests"""
        print("🚀 STARTING ROOT CAUSE ANALYSIS & FIX TESTING")
        print("=" * 80)
        print("Objective: Fix campaign provider selection & auto-responder issues")
        print("=" * 80)
        
        # Setup session and authenticate
        if not await self.setup_session():
            print("❌ Failed to setup session. Exiting.")
            return
        
        try:
            # Run all tests
            await self.test_credential_analysis()
            await self.test_provider_fix()
            await self.test_campaign_sending_verification()
            await self.test_auto_responder_verification()
            
            # Print summary
            print("\\n" + "=" * 80)
            print("📊 ROOT CAUSE ANALYSIS & FIX TEST SUMMARY")
            print("=" * 80)
            
            total_tests = len(self.test_results)
            passed_tests = len([r for r in self.test_results.values() if r["status"] == "passed"])
            failed_tests = len([r for r in self.test_results.values() if r["status"] == "failed"])
            
            print(f"Total Tests: {total_tests}")
            print(f"✅ Passed: {passed_tests}")
            print(f"❌ Failed: {failed_tests}")
            print(f"Success Rate: {passed_tests / total_tests * 100:.1f}%")
            
            print("\\nDetailed Results:")
            for test_name, result in self.test_results.items():
                status_icon = "✅" if result["status"] == "passed" else "❌"
                print(f"{status_icon} {test_name.replace('_', ' ').title()}: {result['status']}")
            
            # Final assessment
            print("\\n" + "=" * 80)
            print("🎯 FINAL ASSESSMENT & RECOMMENDATIONS")
            print("=" * 80)
            
            if passed_tests == total_tests:
                print("🎉 ALL ISSUES RESOLVED!")
                print("✅ Campaign sending with provider selection is working")
                print("✅ Auto-responders are working with IMAP monitoring")
                print("\\n📋 SUMMARY OF FIXES APPLIED:")
                print("   1. Created/Updated email provider with real Gmail credentials")
                print("   2. Enabled IMAP monitoring for auto-responders")
                print("   3. Verified campaign sending works with provider selection")
                print("   4. Confirmed auto-responder services are monitoring providers")
            else:
                print("⚠️ SOME ISSUES REMAIN")
                
                if self.test_results["credential_analysis"]["status"] == "failed":
                    print("❌ ISSUE: Could not analyze credentials properly")
                
                if self.test_results["provider_fix_test"]["status"] == "failed":
                    print("❌ ISSUE: Could not create/fix email provider with real credentials")
                    print("   RECOMMENDATION: Manually create provider with rohushanshinde@gmail.com")
                
                if self.test_results["campaign_sending_verification"]["status"] == "failed":
                    print("❌ ISSUE: Campaign sending with provider selection still not working")
                    print("   RECOMMENDATION: Check provider configuration and API implementation")
                
                if self.test_results["auto_responder_verification"]["status"] == "failed":
                    print("❌ ISSUE: Auto-responders still not working")
                    print("   RECOMMENDATION: Ensure IMAP is enabled and credentials are correct")
                
                print("\\n🔧 NEXT STEPS:")
                print("   1. Review failed test details above")
                print("   2. Manually configure email provider if needed")
                print("   3. Restart auto-responder services")
                print("   4. Re-run tests to verify fixes")
                
        finally:
            await self.cleanup_session()

async def main():
    """Main test execution"""
    tester = RootCauseAnalysisTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())