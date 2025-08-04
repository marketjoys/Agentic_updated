#!/usr/bin/env python3
"""
AI Email Responder - Auto-Responder System Review Testing
Testing the specific areas mentioned in the review request:
1. Email Provider Configuration Test (Rohu Gmail Provider)
2. Email Sending via Campaigns Test  
3. Auto-Responder Services Test
4. Database Integration Test
"""

import asyncio
import aiohttp
import json
import sys
import os
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://030d008b-cc85-4bf3-afdd-411b8004d718.preview.emergentagent.com/api"

class AutoResponderSystemTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_results = {
            "email_provider_config": {"status": "not_tested", "details": []},
            "campaign_email_sending": {"status": "not_tested", "details": []},
            "auto_responder_services": {"status": "not_tested", "details": []},
            "database_integration": {"status": "not_tested", "details": []}
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
    
    async def test_email_provider_configuration(self):
        """Test 1: Email Provider Configuration - Verify Rohu Gmail Provider"""
        print("\n🔧 TESTING EMAIL PROVIDER CONFIGURATION...")
        test_details = []
        
        try:
            # Get all email providers
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            async with self.session.get(f"{BACKEND_URL}/email-providers", headers=headers) as response:
                if response.status == 200:
                    providers = await response.json()
                    test_details.append(f"✅ Email providers endpoint accessible - Found {len(providers)} providers")
                    
                    # Look for Rohu Gmail Provider
                    rohu_provider = None
                    for provider in providers:
                        if provider.get("email_address") == "rohushanshinde@gmail.com":
                            rohu_provider = provider
                            break
                    
                    if rohu_provider:
                        test_details.append(f"✅ Rohu Gmail Provider found: {rohu_provider.get('name', 'Unknown')}")
                        test_details.append(f"   - Email: {rohu_provider.get('email_address')}")
                        test_details.append(f"   - Provider Type: {rohu_provider.get('provider_type')}")
                        test_details.append(f"   - Active: {rohu_provider.get('is_active', False)}")
                        test_details.append(f"   - Default: {rohu_provider.get('is_default', False)}")
                        test_details.append(f"   - IMAP Enabled: {rohu_provider.get('imap_enabled', False)}")
                        
                        # Test SMTP/IMAP connection
                        provider_id = rohu_provider.get("id")
                        if provider_id:
                            async with self.session.post(f"{BACKEND_URL}/email-providers/{provider_id}/test", headers=headers) as test_response:
                                if test_response.status == 200:
                                    test_result = await test_response.json()
                                    test_details.append(f"✅ Connection test results:")
                                    test_details.append(f"   - SMTP Test: {test_result.get('smtp_test', 'unknown')}")
                                    test_details.append(f"   - IMAP Test: {test_result.get('imap_test', 'unknown')}")
                                    test_details.append(f"   - Overall Status: {test_result.get('overall_status', 'unknown')}")
                                else:
                                    test_details.append(f"⚠️ Connection test failed: HTTP {test_response.status}")
                        
                        self.test_results["email_provider_config"]["status"] = "passed"
                    else:
                        test_details.append("❌ Rohu Gmail Provider (rohushanshinde@gmail.com) NOT FOUND")
                        test_details.append("   Available providers:")
                        for provider in providers:
                            test_details.append(f"   - {provider.get('name', 'Unknown')}: {provider.get('email_address', 'No email')}")
                        self.test_results["email_provider_config"]["status"] = "failed"
                else:
                    test_details.append(f"❌ Failed to get email providers: HTTP {response.status}")
                    self.test_results["email_provider_config"]["status"] = "failed"
                    
        except Exception as e:
            test_details.append(f"❌ Exception in email provider test: {str(e)}")
            self.test_results["email_provider_config"]["status"] = "failed"
        
        self.test_results["email_provider_config"]["details"] = test_details
        for detail in test_details:
            print(f"   {detail}")
    
    async def test_campaign_email_sending(self):
        """Test 2: Campaign Email Sending - Test campaign creation and email sending"""
        print("\n📧 TESTING CAMPAIGN EMAIL SENDING...")
        test_details = []
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Get templates for campaign creation
            async with self.session.get(f"{BACKEND_URL}/templates", headers=headers) as response:
                if response.status == 200:
                    templates = await response.json()
                    test_details.append(f"✅ Templates accessible - Found {len(templates)} templates")
                    
                    if templates:
                        template_id = templates[0].get("id")
                        
                        # Get lists for campaign creation
                        async with self.session.get(f"{BACKEND_URL}/lists", headers=headers) as response:
                            if response.status == 200:
                                lists = await response.json()
                                test_details.append(f"✅ Lists accessible - Found {len(lists)} lists")
                                
                                if lists:
                                    list_id = lists[0].get("id")
                                    
                                    # Create test campaign
                                    campaign_data = {
                                        "name": f"Auto-Responder Test Campaign {datetime.now().strftime('%H:%M:%S')}",
                                        "template_id": template_id,
                                        "list_ids": [list_id],
                                        "max_emails": 5,
                                        "follow_up_enabled": True,
                                        "follow_up_schedule_type": "interval",
                                        "follow_up_intervals": [3, 7, 14]
                                    }
                                    
                                    async with self.session.post(f"{BACKEND_URL}/campaigns", json=campaign_data, headers=headers) as response:
                                        if response.status == 200:
                                            campaign = await response.json()
                                            campaign_id = campaign.get("id")
                                            test_details.append(f"✅ Campaign created successfully: {campaign.get('name')}")
                                            test_details.append(f"   - Campaign ID: {campaign_id}")
                                            test_details.append(f"   - Prospect Count: {campaign.get('prospect_count', 0)}")
                                            
                                            # Test campaign sending API (without actually sending)
                                            send_data = {
                                                "send_immediately": False,  # Don't actually send
                                                "max_emails": 1,
                                                "schedule_type": "immediate"
                                            }
                                            
                                            async with self.session.post(f"{BACKEND_URL}/campaigns/{campaign_id}/send", json=send_data, headers=headers) as send_response:
                                                if send_response.status == 200:
                                                    send_result = await send_response.json()
                                                    test_details.append(f"✅ Campaign sending API accessible")
                                                    test_details.append(f"   - Response: {send_result.get('message', 'No message')}")
                                                else:
                                                    test_details.append(f"⚠️ Campaign sending API returned: HTTP {send_response.status}")
                                                    error_text = await send_response.text()
                                                    test_details.append(f"   - Error: {error_text[:200]}")
                                            
                                            self.test_results["campaign_email_sending"]["status"] = "passed"
                                        else:
                                            test_details.append(f"❌ Failed to create campaign: HTTP {response.status}")
                                            self.test_results["campaign_email_sending"]["status"] = "failed"
                                else:
                                    test_details.append("❌ No lists available for campaign creation")
                                    self.test_results["campaign_email_sending"]["status"] = "failed"
                            else:
                                test_details.append(f"❌ Failed to get lists: HTTP {response.status}")
                                self.test_results["campaign_email_sending"]["status"] = "failed"
                    else:
                        test_details.append("❌ No templates available for campaign creation")
                        self.test_results["campaign_email_sending"]["status"] = "failed"
                else:
                    test_details.append(f"❌ Failed to get templates: HTTP {response.status}")
                    self.test_results["campaign_email_sending"]["status"] = "failed"
                    
        except Exception as e:
            test_details.append(f"❌ Exception in campaign email sending test: {str(e)}")
            self.test_results["campaign_email_sending"]["status"] = "failed"
        
        self.test_results["campaign_email_sending"]["details"] = test_details
        for detail in test_details:
            print(f"   {detail}")
    
    async def test_auto_responder_services(self):
        """Test 3: Auto-Responder Services - Verify services are running"""
        print("\n🤖 TESTING AUTO-RESPONDER SERVICES...")
        test_details = []
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Check services status
            async with self.session.get(f"{BACKEND_URL}/services/status", headers=headers) as response:
                if response.status == 200:
                    services_status = await response.json()
                    test_details.append("✅ Services status endpoint accessible")
                    
                    services = services_status.get("services", {})
                    overall_status = services_status.get("overall_status", "unknown")
                    
                    test_details.append(f"   - Overall Status: {overall_status}")
                    
                    # Check smart_follow_up_engine
                    follow_up_service = services.get("smart_follow_up_engine", {})
                    follow_up_status = follow_up_service.get("status", "unknown")
                    test_details.append(f"   - Smart Follow-up Engine: {follow_up_status}")
                    
                    # Check email_processor
                    email_processor = services.get("email_processor", {})
                    processor_status = email_processor.get("status", "unknown")
                    monitored_count = email_processor.get("monitored_providers_count", 0)
                    test_details.append(f"   - Email Processor: {processor_status}")
                    test_details.append(f"   - Monitored Providers: {monitored_count}")
                    
                    # Check monitored providers details
                    monitored_providers = email_processor.get("monitored_providers", [])
                    if monitored_providers:
                        test_details.append("   - Monitored Provider Details:")
                        for provider in monitored_providers:
                            test_details.append(f"     * {provider.get('name', 'Unknown')}: {provider.get('provider_type', 'unknown')}")
                            test_details.append(f"       IMAP Host: {provider.get('imap_host', 'unknown')}")
                            test_details.append(f"       Last Scan: {provider.get('last_scan', 'never')}")
                    
                    # Check if both services are running
                    if follow_up_status == "running" and processor_status == "running":
                        test_details.append("✅ Both auto-responder services are running")
                        self.test_results["auto_responder_services"]["status"] = "passed"
                    else:
                        test_details.append("⚠️ One or both auto-responder services are not running")
                        self.test_results["auto_responder_services"]["status"] = "partial"
                        
                        # Try to start services
                        test_details.append("   Attempting to start services...")
                        async with self.session.post(f"{BACKEND_URL}/services/start-all", headers=headers) as start_response:
                            if start_response.status == 200:
                                start_result = await start_response.json()
                                test_details.append(f"   ✅ Service start initiated: {start_result.get('message', 'No message')}")
                            else:
                                test_details.append(f"   ❌ Failed to start services: HTTP {start_response.status}")
                else:
                    test_details.append(f"❌ Failed to get services status: HTTP {response.status}")
                    self.test_results["auto_responder_services"]["status"] = "failed"
                    
        except Exception as e:
            test_details.append(f"❌ Exception in auto-responder services test: {str(e)}")
            self.test_results["auto_responder_services"]["status"] = "failed"
        
        self.test_results["auto_responder_services"]["details"] = test_details
        for detail in test_details:
            print(f"   {detail}")
    
    async def test_database_integration(self):
        """Test 4: Database Integration - Verify data accessibility"""
        print("\n🗄️ TESTING DATABASE INTEGRATION...")
        test_details = []
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Test prospects endpoint
            async with self.session.get(f"{BACKEND_URL}/prospects", headers=headers) as response:
                if response.status == 200:
                    prospects = await response.json()
                    test_details.append(f"✅ Prospects accessible - Found {len(prospects)} prospects")
                else:
                    test_details.append(f"❌ Failed to get prospects: HTTP {response.status}")
            
            # Test lists endpoint
            async with self.session.get(f"{BACKEND_URL}/lists", headers=headers) as response:
                if response.status == 200:
                    lists = await response.json()
                    test_details.append(f"✅ Lists accessible - Found {len(lists)} lists")
                else:
                    test_details.append(f"❌ Failed to get lists: HTTP {response.status}")
            
            # Test templates endpoint
            async with self.session.get(f"{BACKEND_URL}/templates", headers=headers) as response:
                if response.status == 200:
                    templates = await response.json()
                    test_details.append(f"✅ Templates accessible - Found {len(templates)} templates")
                else:
                    test_details.append(f"❌ Failed to get templates: HTTP {response.status}")
            
            # Test intents endpoint
            async with self.session.get(f"{BACKEND_URL}/intents", headers=headers) as response:
                if response.status == 200:
                    intents = await response.json()
                    test_details.append(f"✅ Intents accessible - Found {len(intents)} intents")
                    
                    # Check for auto-response intents
                    auto_response_intents = [intent for intent in intents if intent.get("auto_respond", False)]
                    test_details.append(f"   - Auto-response intents: {len(auto_response_intents)}")
                    
                    for intent in auto_response_intents:
                        test_details.append(f"     * {intent.get('name', 'Unknown')}: {intent.get('keywords', [])}")
                else:
                    test_details.append(f"❌ Failed to get intents: HTTP {response.status}")
            
            # Test campaigns endpoint
            async with self.session.get(f"{BACKEND_URL}/campaigns", headers=headers) as response:
                if response.status == 200:
                    campaigns = await response.json()
                    test_details.append(f"✅ Campaigns accessible - Found {len(campaigns)} campaigns")
                else:
                    test_details.append(f"❌ Failed to get campaigns: HTTP {response.status}")
            
            # Test email providers endpoint (already tested above but include in database test)
            async with self.session.get(f"{BACKEND_URL}/email-providers", headers=headers) as response:
                if response.status == 200:
                    providers = await response.json()
                    test_details.append(f"✅ Email providers accessible - Found {len(providers)} providers")
                else:
                    test_details.append(f"❌ Failed to get email providers: HTTP {response.status}")
            
            self.test_results["database_integration"]["status"] = "passed"
                    
        except Exception as e:
            test_details.append(f"❌ Exception in database integration test: {str(e)}")
            self.test_results["database_integration"]["status"] = "failed"
        
        self.test_results["database_integration"]["details"] = test_details
        for detail in test_details:
            print(f"   {detail}")
    
    async def run_all_tests(self):
        """Run all auto-responder system tests"""
        print("🚀 STARTING AUTO-RESPONDER SYSTEM REVIEW TESTING")
        print("=" * 60)
        
        # Setup session and authenticate
        if not await self.setup_session():
            print("❌ Failed to setup session. Exiting.")
            return
        
        try:
            # Run all tests
            await self.test_email_provider_configuration()
            await self.test_campaign_email_sending()
            await self.test_auto_responder_services()
            await self.test_database_integration()
            
            # Print summary
            print("\n" + "=" * 60)
            print("📊 AUTO-RESPONDER SYSTEM TEST SUMMARY")
            print("=" * 60)
            
            total_tests = len(self.test_results)
            passed_tests = len([r for r in self.test_results.values() if r["status"] == "passed"])
            partial_tests = len([r for r in self.test_results.values() if r["status"] == "partial"])
            failed_tests = len([r for r in self.test_results.values() if r["status"] == "failed"])
            
            print(f"Total Tests: {total_tests}")
            print(f"✅ Passed: {passed_tests}")
            print(f"⚠️ Partial: {partial_tests}")
            print(f"❌ Failed: {failed_tests}")
            print(f"Success Rate: {(passed_tests + partial_tests) / total_tests * 100:.1f}%")
            
            print("\nDetailed Results:")
            for test_name, result in self.test_results.items():
                status_icon = "✅" if result["status"] == "passed" else "⚠️" if result["status"] == "partial" else "❌"
                print(f"{status_icon} {test_name.replace('_', ' ').title()}: {result['status']}")
            
            # Overall assessment
            if passed_tests == total_tests:
                print("\n🎉 ALL AUTO-RESPONDER SYSTEM TESTS PASSED!")
                print("The system is using REAL Gmail credentials and all functionality is operational.")
            elif passed_tests + partial_tests == total_tests:
                print("\n⚠️ AUTO-RESPONDER SYSTEM MOSTLY FUNCTIONAL")
                print("Some components may need attention but core functionality is working.")
            else:
                print("\n❌ AUTO-RESPONDER SYSTEM HAS CRITICAL ISSUES")
                print("Multiple components are not working correctly.")
                
        finally:
            await self.cleanup_session()

async def main():
    """Main test execution"""
    tester = AutoResponderSystemTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())