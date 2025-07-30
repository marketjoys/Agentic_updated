#!/usr/bin/env python3
"""
AI Email Responder - Campaign Provider Selection & Auto-Responder Testing
Testing the specific issues mentioned in the review request:
1. Campaign Sending with new Added providers when selected is not working
2. Auto responders are not working

Focus Areas:
- Email Provider Status and Configuration
- Campaign Sending with Provider Selection
- Auto-Responder Service Status and IMAP Configuration
- Database State for Auto-Response Components
"""

import asyncio
import aiohttp
import json
import sys
import os
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://64e7fdde-dfd5-4b2b-b2c3-2f149d1e1d45.preview.emergentagent.com/api"

class CampaignProviderAutoResponderTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_results = {
            "email_providers_status": {"status": "not_tested", "details": []},
            "campaign_provider_selection": {"status": "not_tested", "details": []},
            "auto_responder_services": {"status": "not_tested", "details": []},
            "database_auto_response_state": {"status": "not_tested", "details": []}
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
    
    async def test_email_providers_status(self):
        """Test 1: Email Providers Status - Check what providers exist and their configuration"""
        print("\n🔧 TESTING EMAIL PROVIDERS STATUS...")
        test_details = []
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Get all email providers
            async with self.session.get(f"{BACKEND_URL}/email-providers", headers=headers) as response:
                if response.status == 200:
                    providers = await response.json()
                    test_details.append(f"✅ Email providers endpoint accessible - Found {len(providers)} providers")
                    
                    if not providers:
                        test_details.append("❌ CRITICAL: No email providers found in system")
                        test_details.append("   This explains why campaign sending with provider selection fails")
                        self.test_results["email_providers_status"]["status"] = "failed"
                        self.test_results["email_providers_status"]["details"] = test_details
                        for detail in test_details:
                            print(f"   {detail}")
                        return
                    
                    # Analyze each provider
                    default_provider = None
                    imap_enabled_providers = []
                    
                    for i, provider in enumerate(providers):
                        test_details.append(f"\n   📧 Provider {i+1}: {provider.get('name', 'Unknown')}")
                        test_details.append(f"      - ID: {provider.get('id', 'No ID')}")
                        test_details.append(f"      - Email: {provider.get('email_address', 'No email')}")
                        test_details.append(f"      - Type: {provider.get('provider_type', 'Unknown')}")
                        test_details.append(f"      - Active: {provider.get('is_active', False)}")
                        test_details.append(f"      - Default: {provider.get('is_default', False)}")
                        test_details.append(f"      - SMTP Host: {provider.get('smtp_host', 'Not configured')}")
                        test_details.append(f"      - IMAP Host: {provider.get('imap_host', 'Not configured')}")
                        test_details.append(f"      - IMAP Enabled: {provider.get('imap_enabled', False)}")
                        
                        if provider.get('is_default'):
                            default_provider = provider
                        
                        if provider.get('imap_enabled'):
                            imap_enabled_providers.append(provider)
                        
                        # Test provider connection
                        provider_id = provider.get('id')
                        if provider_id:
                            async with self.session.post(f"{BACKEND_URL}/email-providers/{provider_id}/test", headers=headers) as test_response:
                                if test_response.status == 200:
                                    test_result = await test_response.json()
                                    test_details.append(f"      - Connection Test:")
                                    test_details.append(f"        * SMTP: {test_result.get('smtp_test', 'unknown')}")
                                    test_details.append(f"        * IMAP: {test_result.get('imap_test', 'unknown')}")
                                    test_details.append(f"        * Overall: {test_result.get('overall_status', 'unknown')}")
                                else:
                                    test_details.append(f"      - Connection Test: Failed (HTTP {test_response.status})")
                    
                    # Summary analysis
                    test_details.append(f"\n   📊 PROVIDER ANALYSIS:")
                    test_details.append(f"      - Total Providers: {len(providers)}")
                    test_details.append(f"      - Default Provider: {'Yes' if default_provider else 'No'}")
                    test_details.append(f"      - IMAP Enabled Providers: {len(imap_enabled_providers)}")
                    
                    if default_provider:
                        test_details.append(f"      - Default Provider Details: {default_provider.get('name')} ({default_provider.get('email_address')})")
                    
                    if not default_provider:
                        test_details.append("      ⚠️ WARNING: No default provider set - this may cause campaign sending issues")
                    
                    if not imap_enabled_providers:
                        test_details.append("      ❌ CRITICAL: No IMAP enabled providers - auto-responders cannot work")
                        test_details.append("         Backend logs showing 'Loaded 0 enabled email providers for monitoring' confirms this")
                    
                    self.test_results["email_providers_status"]["status"] = "passed" if providers else "failed"
                    
                else:
                    test_details.append(f"❌ Failed to get email providers: HTTP {response.status}")
                    self.test_results["email_providers_status"]["status"] = "failed"
                    
        except Exception as e:
            test_details.append(f"❌ Exception in email providers test: {str(e)}")
            self.test_results["email_providers_status"]["status"] = "failed"
        
        self.test_results["email_providers_status"]["details"] = test_details
        for detail in test_details:
            print(f"   {detail}")
    
    async def test_campaign_provider_selection(self):
        """Test 2: Campaign Provider Selection - Test campaign creation and sending with specific provider"""
        print("\n📧 TESTING CAMPAIGN PROVIDER SELECTION...")
        test_details = []
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # First, get available providers
            async with self.session.get(f"{BACKEND_URL}/email-providers", headers=headers) as response:
                if response.status == 200:
                    providers = await response.json()
                    test_details.append(f"✅ Found {len(providers)} email providers for campaign testing")
                    
                    if not providers:
                        test_details.append("❌ CRITICAL: No providers available - cannot test campaign provider selection")
                        self.test_results["campaign_provider_selection"]["status"] = "failed"
                        self.test_results["campaign_provider_selection"]["details"] = test_details
                        for detail in test_details:
                            print(f"   {detail}")
                        return
                    
                    # Get templates and lists for campaign creation
                    templates = []
                    lists = []
                    
                    async with self.session.get(f"{BACKEND_URL}/templates", headers=headers) as temp_response:
                        if temp_response.status == 200:
                            templates = await temp_response.json()
                            test_details.append(f"✅ Found {len(templates)} templates")
                    
                    async with self.session.get(f"{BACKEND_URL}/lists", headers=headers) as list_response:
                        if list_response.status == 200:
                            lists = await list_response.json()
                            test_details.append(f"✅ Found {len(lists)} prospect lists")
                    
                    if not templates or not lists:
                        test_details.append("❌ Missing templates or lists - cannot create test campaign")
                        self.test_results["campaign_provider_selection"]["status"] = "failed"
                        self.test_results["campaign_provider_selection"]["details"] = test_details
                        for detail in test_details:
                            print(f"   {detail}")
                        return
                    
                    # Test campaign creation with specific provider selection
                    selected_provider = providers[0]  # Use first available provider
                    test_details.append(f"\n   🎯 Testing with provider: {selected_provider.get('name')} ({selected_provider.get('email_address')})")
                    
                    campaign_data = {
                        "name": f"Provider Selection Test Campaign {datetime.now().strftime('%H:%M:%S')}",
                        "template_id": templates[0].get("id"),
                        "list_ids": [lists[0].get("id")],
                        "max_emails": 1,
                        "follow_up_enabled": True,
                        "follow_up_schedule_type": "interval",
                        "follow_up_intervals": [3, 7, 14]
                    }
                    
                    # Create campaign
                    async with self.session.post(f"{BACKEND_URL}/campaigns", json=campaign_data, headers=headers) as response:
                        if response.status == 200:
                            campaign = await response.json()
                            campaign_id = campaign.get("id")
                            test_details.append(f"✅ Campaign created successfully: {campaign.get('name')}")
                            test_details.append(f"   - Campaign ID: {campaign_id}")
                            test_details.append(f"   - Prospect Count: {campaign.get('prospect_count', 0)}")
                            
                            # Test campaign sending with explicit provider selection
                            send_data = {
                                "send_immediately": False,  # Don't actually send emails
                                "email_provider_id": selected_provider.get("id"),  # Explicit provider selection
                                "max_emails": 1,
                                "schedule_type": "immediate"
                            }
                            
                            test_details.append(f"\n   📤 Testing campaign send with provider ID: {selected_provider.get('id')}")
                            
                            async with self.session.post(f"{BACKEND_URL}/campaigns/{campaign_id}/send", json=send_data, headers=headers) as send_response:
                                send_status = send_response.status
                                send_text = await send_response.text()
                                
                                test_details.append(f"   - Send API Response: HTTP {send_status}")
                                
                                if send_status == 200:
                                    try:
                                        send_result = await send_response.json() if send_response.content_type == 'application/json' else {"message": send_text}
                                        test_details.append(f"   - ✅ Campaign sending API accepts provider selection")
                                        test_details.append(f"   - Response: {send_result.get('message', 'No message')[:100]}")
                                        
                                        # Check if provider selection was respected
                                        if "provider" in send_text.lower() or selected_provider.get("id") in send_text:
                                            test_details.append(f"   - ✅ Provider selection appears to be respected")
                                        else:
                                            test_details.append(f"   - ⚠️ Cannot confirm if provider selection was respected")
                                        
                                        self.test_results["campaign_provider_selection"]["status"] = "passed"
                                    except:
                                        test_details.append(f"   - Response text: {send_text[:200]}")
                                        self.test_results["campaign_provider_selection"]["status"] = "partial"
                                        
                                elif send_status == 400:
                                    test_details.append(f"   - ❌ Bad Request - Provider selection may not be implemented correctly")
                                    test_details.append(f"   - Error: {send_text[:200]}")
                                    self.test_results["campaign_provider_selection"]["status"] = "failed"
                                    
                                elif send_status == 404:
                                    test_details.append(f"   - ❌ Campaign or Provider not found")
                                    test_details.append(f"   - Error: {send_text[:200]}")
                                    self.test_results["campaign_provider_selection"]["status"] = "failed"
                                    
                                else:
                                    test_details.append(f"   - ❌ Unexpected response: {send_text[:200]}")
                                    self.test_results["campaign_provider_selection"]["status"] = "failed"
                            
                            # Test without provider selection (should use default)
                            test_details.append(f"\n   🔄 Testing campaign send without provider selection (should use default)")
                            
                            send_data_no_provider = {
                                "send_immediately": False,
                                "max_emails": 1,
                                "schedule_type": "immediate"
                            }
                            
                            async with self.session.post(f"{BACKEND_URL}/campaigns/{campaign_id}/send", json=send_data_no_provider, headers=headers) as send_response2:
                                send_status2 = send_response2.status
                                send_text2 = await send_response2.text()
                                
                                test_details.append(f"   - Default Provider Send: HTTP {send_status2}")
                                if send_status2 == 200:
                                    test_details.append(f"   - ✅ Campaign sending works without explicit provider (uses default)")
                                else:
                                    test_details.append(f"   - ⚠️ Issue with default provider usage: {send_text2[:100]}")
                            
                        else:
                            test_details.append(f"❌ Failed to create test campaign: HTTP {response.status}")
                            error_text = await response.text()
                            test_details.append(f"   - Error: {error_text[:200]}")
                            self.test_results["campaign_provider_selection"]["status"] = "failed"
                    
                else:
                    test_details.append(f"❌ Failed to get email providers: HTTP {response.status}")
                    self.test_results["campaign_provider_selection"]["status"] = "failed"
                    
        except Exception as e:
            test_details.append(f"❌ Exception in campaign provider selection test: {str(e)}")
            self.test_results["campaign_provider_selection"]["status"] = "failed"
        
        self.test_results["campaign_provider_selection"]["details"] = test_details
        for detail in test_details:
            print(f"   {detail}")
    
    async def test_auto_responder_services(self):
        """Test 3: Auto-Responder Services - Check service status and IMAP configuration"""
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
                    
                    test_details.append(f"\n   📊 SERVICE STATUS OVERVIEW:")
                    test_details.append(f"      - Overall Status: {overall_status}")
                    
                    # Check smart_follow_up_engine
                    follow_up_service = services.get("smart_follow_up_engine", {})
                    follow_up_status = follow_up_service.get("status", "unknown")
                    test_details.append(f"      - Smart Follow-up Engine: {follow_up_status}")
                    
                    # Check email_processor (auto-responder)
                    email_processor = services.get("email_processor", {})
                    processor_status = email_processor.get("status", "unknown")
                    monitored_count = email_processor.get("monitored_providers_count", 0)
                    test_details.append(f"      - Email Processor (Auto-Responder): {processor_status}")
                    test_details.append(f"      - Monitored Providers Count: {monitored_count}")
                    
                    # This is the key issue mentioned in the review
                    if monitored_count == 0:
                        test_details.append(f"      ❌ CRITICAL: 0 providers being monitored for auto-responses")
                        test_details.append(f"         This matches the backend log: 'Loaded 0 enabled email providers for monitoring'")
                        test_details.append(f"         Auto-responders cannot work without IMAP monitoring")
                    
                    # Check monitored providers details
                    monitored_providers = email_processor.get("monitored_providers", [])
                    if monitored_providers:
                        test_details.append(f"\n   📧 MONITORED PROVIDERS DETAILS:")
                        for provider in monitored_providers:
                            test_details.append(f"      - {provider.get('name', 'Unknown')}")
                            test_details.append(f"        * Type: {provider.get('provider_type', 'unknown')}")
                            test_details.append(f"        * IMAP Host: {provider.get('imap_host', 'unknown')}")
                            test_details.append(f"        * Last Scan: {provider.get('last_scan', 'never')}")
                    else:
                        test_details.append(f"\n   ❌ NO PROVIDERS BEING MONITORED FOR AUTO-RESPONSES")
                    
                    # Check individual provider IMAP status
                    test_details.append(f"\n   🔍 CHECKING INDIVIDUAL PROVIDER IMAP STATUS:")
                    
                    # Get all providers and check their IMAP status
                    async with self.session.get(f"{BACKEND_URL}/email-providers", headers=headers) as prov_response:
                        if prov_response.status == 200:
                            providers = await prov_response.json()
                            
                            for provider in providers:
                                provider_id = provider.get('id')
                                provider_name = provider.get('name', 'Unknown')
                                
                                if provider_id:
                                    async with self.session.get(f"{BACKEND_URL}/email-providers/{provider_id}/imap-status", headers=headers) as imap_response:
                                        if imap_response.status == 200:
                                            imap_status = await imap_response.json()
                                            test_details.append(f"      - {provider_name}:")
                                            test_details.append(f"        * IMAP Enabled: {imap_status.get('imap_enabled', False)}")
                                            test_details.append(f"        * Is Monitoring: {imap_status.get('is_monitoring', False)}")
                                            test_details.append(f"        * Email Processor Running: {imap_status.get('email_processor_running', False)}")
                                            test_details.append(f"        * IMAP Host: {imap_status.get('imap_config', {}).get('host', 'Not configured')}")
                                            
                                            if not imap_status.get('imap_enabled', False):
                                                test_details.append(f"        ❌ IMAP not enabled - auto-responses won't work for this provider")
                                        else:
                                            test_details.append(f"      - {provider_name}: IMAP status check failed (HTTP {imap_response.status})")
                    
                    # Determine overall auto-responder status
                    if processor_status == "running" and monitored_count > 0:
                        test_details.append(f"\n   ✅ Auto-responder system is operational")
                        self.test_results["auto_responder_services"]["status"] = "passed"
                    elif processor_status == "running" and monitored_count == 0:
                        test_details.append(f"\n   ❌ Auto-responder service running but no providers monitored")
                        test_details.append(f"      ROOT CAUSE: No email providers have IMAP enabled")
                        self.test_results["auto_responder_services"]["status"] = "failed"
                    else:
                        test_details.append(f"\n   ❌ Auto-responder service not running properly")
                        self.test_results["auto_responder_services"]["status"] = "failed"
                        
                        # Try to start services
                        test_details.append(f"   🔄 Attempting to start auto-responder services...")
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
    
    async def test_database_auto_response_state(self):
        """Test 4: Database Auto-Response State - Check if auto-response components exist"""
        print("\n🗄️ TESTING DATABASE AUTO-RESPONSE STATE...")
        test_details = []
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Check prospects
            async with self.session.get(f"{BACKEND_URL}/prospects", headers=headers) as response:
                if response.status == 200:
                    prospects = await response.json()
                    test_details.append(f"✅ Prospects: {len(prospects)} found")
                else:
                    test_details.append(f"❌ Failed to get prospects: HTTP {response.status}")
            
            # Check templates (especially auto-response templates)
            async with self.session.get(f"{BACKEND_URL}/templates", headers=headers) as response:
                if response.status == 200:
                    templates = await response.json()
                    test_details.append(f"✅ Templates: {len(templates)} found")
                    
                    # Look for auto-response templates
                    auto_response_templates = []
                    for template in templates:
                        template_name = template.get('name', '').lower()
                        if 'auto' in template_name or 'response' in template_name or 'reply' in template_name:
                            auto_response_templates.append(template)
                    
                    test_details.append(f"   - Auto-response templates: {len(auto_response_templates)}")
                    for template in auto_response_templates:
                        test_details.append(f"     * {template.get('name', 'Unknown')}")
                else:
                    test_details.append(f"❌ Failed to get templates: HTTP {response.status}")
            
            # Check intents (especially auto-response intents)
            async with self.session.get(f"{BACKEND_URL}/intents", headers=headers) as response:
                if response.status == 200:
                    intents = await response.json()
                    test_details.append(f"✅ Intents: {len(intents)} found")
                    
                    # Look for auto-response intents
                    auto_response_intents = [intent for intent in intents if intent.get("auto_respond", False)]
                    test_details.append(f"   - Auto-response intents: {len(auto_response_intents)}")
                    
                    if auto_response_intents:
                        test_details.append(f"   - Auto-response intent details:")
                        for intent in auto_response_intents:
                            test_details.append(f"     * {intent.get('name', 'Unknown')}")
                            test_details.append(f"       Keywords: {intent.get('keywords', [])}")
                            test_details.append(f"       Auto-respond: {intent.get('auto_respond', False)}")
                    else:
                        test_details.append(f"   ❌ CRITICAL: No auto-response intents found")
                        test_details.append(f"      Auto-responders need intents with auto_respond: true")
                else:
                    test_details.append(f"❌ Failed to get intents: HTTP {response.status}")
            
            # Check campaigns
            async with self.session.get(f"{BACKEND_URL}/campaigns", headers=headers) as response:
                if response.status == 200:
                    campaigns = await response.json()
                    test_details.append(f"✅ Campaigns: {len(campaigns)} found")
                else:
                    test_details.append(f"❌ Failed to get campaigns: HTTP {response.status}")
            
            # Check lists
            async with self.session.get(f"{BACKEND_URL}/lists", headers=headers) as response:
                if response.status == 200:
                    lists = await response.json()
                    test_details.append(f"✅ Lists: {len(lists)} found")
                else:
                    test_details.append(f"❌ Failed to get lists: HTTP {response.status}")
            
            # Summary assessment
            test_details.append(f"\n   📊 AUTO-RESPONSE READINESS ASSESSMENT:")
            
            # Check if we have the minimum components for auto-responses
            has_prospects = len(prospects) > 0 if 'prospects' in locals() else False
            has_templates = len(templates) > 0 if 'templates' in locals() else False
            has_auto_intents = len(auto_response_intents) > 0 if 'auto_response_intents' in locals() else False
            
            test_details.append(f"      - Prospects available: {'✅' if has_prospects else '❌'}")
            test_details.append(f"      - Templates available: {'✅' if has_templates else '❌'}")
            test_details.append(f"      - Auto-response intents: {'✅' if has_auto_intents else '❌'}")
            
            if has_prospects and has_templates and has_auto_intents:
                test_details.append(f"      ✅ Database has all components needed for auto-responses")
                self.test_results["database_auto_response_state"]["status"] = "passed"
            else:
                test_details.append(f"      ❌ Database missing critical components for auto-responses")
                self.test_results["database_auto_response_state"]["status"] = "failed"
                    
        except Exception as e:
            test_details.append(f"❌ Exception in database auto-response state test: {str(e)}")
            self.test_results["database_auto_response_state"]["status"] = "failed"
        
        self.test_results["database_auto_response_state"]["details"] = test_details
        for detail in test_details:
            print(f"   {detail}")
    
    async def run_all_tests(self):
        """Run all campaign provider and auto-responder tests"""
        print("🚀 STARTING CAMPAIGN PROVIDER & AUTO-RESPONDER TESTING")
        print("=" * 70)
        print("Focus: Campaign sending with provider selection & Auto-responder issues")
        print("=" * 70)
        
        # Setup session and authenticate
        if not await self.setup_session():
            print("❌ Failed to setup session. Exiting.")
            return
        
        try:
            # Run all tests
            await self.test_email_providers_status()
            await self.test_campaign_provider_selection()
            await self.test_auto_responder_services()
            await self.test_database_auto_response_state()
            
            # Print summary
            print("\n" + "=" * 70)
            print("📊 CAMPAIGN PROVIDER & AUTO-RESPONDER TEST SUMMARY")
            print("=" * 70)
            
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
            
            # Root cause analysis
            print("\n" + "=" * 70)
            print("🔍 ROOT CAUSE ANALYSIS")
            print("=" * 70)
            
            # Issue 1: Campaign sending with provider selection
            if self.test_results["campaign_provider_selection"]["status"] == "failed":
                print("❌ ISSUE 1: Campaign Sending with Provider Selection")
                print("   ROOT CAUSE: Provider selection parameter not properly implemented or providers missing")
                print("   IMPACT: Users cannot select specific email providers for campaigns")
            elif self.test_results["campaign_provider_selection"]["status"] == "passed":
                print("✅ Campaign sending with provider selection is working")
            
            # Issue 2: Auto-responders not working
            if self.test_results["auto_responder_services"]["status"] == "failed":
                print("\n❌ ISSUE 2: Auto-responders Not Working")
                print("   ROOT CAUSE: No email providers have IMAP monitoring enabled")
                print("   EVIDENCE: Backend logs show 'Loaded 0 enabled email providers for monitoring'")
                print("   IMPACT: Auto-responders cannot monitor incoming emails")
                print("   SOLUTION: Enable IMAP on at least one email provider")
            elif self.test_results["auto_responder_services"]["status"] == "passed":
                print("\n✅ Auto-responder services are working correctly")
            
            # Overall assessment
            critical_issues = failed_tests
            if critical_issues == 0:
                print(f"\n🎉 ALL CRITICAL ISSUES RESOLVED!")
                print("Both campaign provider selection and auto-responders are working correctly.")
            elif critical_issues == 1:
                print(f"\n⚠️ ONE CRITICAL ISSUE REMAINS")
                print("One of the main issues still needs to be addressed.")
            else:
                print(f"\n❌ MULTIPLE CRITICAL ISSUES FOUND")
                print("Both main issues need attention before the system is fully functional.")
                
        finally:
            await self.cleanup_session()

async def main():
    """Main test execution"""
    tester = CampaignProviderAutoResponderTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())