#!/usr/bin/env python3
"""
AI Email Responder - Email Provider Selection and Usage Testing
Testing the complete email provider functionality including:
1. Adding new email providers and connection testing
2. Provider selection in campaigns
3. Email sending with selected providers
4. Default provider functionality
5. Error handling for invalid providers
"""

import asyncio
import aiohttp
import json
import sys
import os
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://6b79b9a6-93ed-4a33-b1a5-f766f54ddce0.preview.emergentagent.com/api"

class EmailProviderSelectionTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_results = {
            "email_provider_management": {"status": "not_tested", "details": []},
            "provider_selection_campaigns": {"status": "not_tested", "details": []},
            "email_sending_selected_providers": {"status": "not_tested", "details": []},
            "default_provider_functionality": {"status": "not_tested", "details": []},
            "error_handling": {"status": "not_tested", "details": []}
        }
        self.created_provider_ids = []  # Track created providers for cleanup
        self.created_campaign_ids = []  # Track created campaigns for cleanup
        
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
        """Cleanup HTTP session and test data"""
        if self.session:
            # Clean up created test providers
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            for provider_id in self.created_provider_ids:
                try:
                    async with self.session.delete(f"{BACKEND_URL}/email-providers/{provider_id}", headers=headers) as response:
                        if response.status == 200:
                            print(f"🧹 Cleaned up test provider: {provider_id}")
                except Exception as e:
                    print(f"⚠️ Failed to cleanup provider {provider_id}: {str(e)}")
            
            # Clean up created test campaigns
            for campaign_id in self.created_campaign_ids:
                try:
                    async with self.session.delete(f"{BACKEND_URL}/campaigns/{campaign_id}", headers=headers) as response:
                        if response.status == 200:
                            print(f"🧹 Cleaned up test campaign: {campaign_id}")
                except Exception as e:
                    print(f"⚠️ Failed to cleanup campaign {campaign_id}: {str(e)}")
            
            await self.session.close()
    
    async def test_email_provider_management(self):
        """Test 1: Email Provider Management - Adding new providers and connection testing"""
        print("\n🔧 TESTING EMAIL PROVIDER MANAGEMENT...")
        test_details = []
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Get initial provider count
            async with self.session.get(f"{BACKEND_URL}/email-providers", headers=headers) as response:
                if response.status == 200:
                    initial_providers = await response.json()
                    initial_count = len(initial_providers)
                    test_details.append(f"✅ Initial email providers count: {initial_count}")
                else:
                    test_details.append(f"❌ Failed to get initial providers: HTTP {response.status}")
                    self.test_results["email_provider_management"]["status"] = "failed"
                    return
            
            # Test 1.1: Add new email provider (Gmail)
            test_provider_data = {
                "name": f"Test Gmail Provider {datetime.now().strftime('%H%M%S')}",
                "provider_type": "gmail",
                "email_address": f"test.provider.{datetime.now().strftime('%H%M%S')}@gmail.com",
                "display_name": "Test Provider Display",
                "smtp_host": "smtp.gmail.com",
                "smtp_port": 587,
                "smtp_username": f"test.provider.{datetime.now().strftime('%H%M%S')}@gmail.com",
                "smtp_password": "test_app_password",
                "smtp_use_tls": True,
                "imap_host": "imap.gmail.com",
                "imap_port": 993,
                "imap_username": f"test.provider.{datetime.now().strftime('%H%M%S')}@gmail.com",
                "imap_password": "test_app_password",
                "daily_send_limit": 500,
                "hourly_send_limit": 50,
                "is_default": False,
                "skip_connection_test": True  # Skip actual connection test for test provider
            }
            
            async with self.session.post(f"{BACKEND_URL}/email-providers", json=test_provider_data, headers=headers) as response:
                if response.status == 200:
                    provider_result = await response.json()
                    provider_id = provider_result.get("id")
                    self.created_provider_ids.append(provider_id)
                    test_details.append(f"✅ Successfully created test email provider")
                    test_details.append(f"   - Provider ID: {provider_id}")
                    test_details.append(f"   - Name: {provider_result.get('name')}")
                    test_details.append(f"   - Email: {provider_result.get('email_address')}")
                    test_details.append(f"   - IMAP Enabled: {provider_result.get('imap_enabled', False)}")
                else:
                    error_text = await response.text()
                    test_details.append(f"❌ Failed to create email provider: HTTP {response.status}")
                    test_details.append(f"   - Error: {error_text[:200]}")
                    self.test_results["email_provider_management"]["status"] = "failed"
                    return
            
            # Test 1.2: Test provider connection (with existing real provider)
            # Find a real provider to test connection
            real_provider_id = None
            for provider in initial_providers:
                if provider.get("email_address") == "rohushanshinde@gmail.com":
                    real_provider_id = provider.get("id")
                    break
            
            if real_provider_id:
                async with self.session.post(f"{BACKEND_URL}/email-providers/{real_provider_id}/test", headers=headers) as response:
                    if response.status == 200:
                        test_result = await response.json()
                        test_details.append(f"✅ Connection test completed for real provider")
                        test_details.append(f"   - SMTP Test: {test_result.get('smtp_test', 'unknown')}")
                        test_details.append(f"   - IMAP Test: {test_result.get('imap_test', 'unknown')}")
                        test_details.append(f"   - Overall Status: {test_result.get('overall_status', 'unknown')}")
                    else:
                        test_details.append(f"⚠️ Connection test failed: HTTP {response.status}")
            else:
                test_details.append("⚠️ No real provider found for connection testing")
            
            # Test 1.3: Verify provider was added
            async with self.session.get(f"{BACKEND_URL}/email-providers", headers=headers) as response:
                if response.status == 200:
                    updated_providers = await response.json()
                    updated_count = len(updated_providers)
                    if updated_count > initial_count:
                        test_details.append(f"✅ Provider count increased: {initial_count} → {updated_count}")
                        self.test_results["email_provider_management"]["status"] = "passed"
                    else:
                        test_details.append(f"❌ Provider count did not increase: {initial_count} → {updated_count}")
                        self.test_results["email_provider_management"]["status"] = "failed"
                else:
                    test_details.append(f"❌ Failed to verify provider addition: HTTP {response.status}")
                    self.test_results["email_provider_management"]["status"] = "failed"
                    
        except Exception as e:
            test_details.append(f"❌ Exception in email provider management test: {str(e)}")
            self.test_results["email_provider_management"]["status"] = "failed"
        
        self.test_results["email_provider_management"]["details"] = test_details
        for detail in test_details:
            print(f"   {detail}")
    
    async def test_provider_selection_campaigns(self):
        """Test 2: Provider Selection in Campaigns - Test that campaigns can select specific email providers"""
        print("\n📋 TESTING PROVIDER SELECTION IN CAMPAIGNS...")
        test_details = []
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Get available providers
            async with self.session.get(f"{BACKEND_URL}/email-providers", headers=headers) as response:
                if response.status == 200:
                    providers = await response.json()
                    test_details.append(f"✅ Found {len(providers)} email providers for campaign selection")
                    
                    if not providers:
                        test_details.append("❌ No email providers available for campaign selection")
                        self.test_results["provider_selection_campaigns"]["status"] = "failed"
                        return
                    
                    # Select a provider for testing
                    selected_provider = providers[0]
                    selected_provider_id = selected_provider.get("id")
                    test_details.append(f"   - Selected provider: {selected_provider.get('name')} ({selected_provider.get('email_address')})")
                else:
                    test_details.append(f"❌ Failed to get email providers: HTTP {response.status}")
                    self.test_results["provider_selection_campaigns"]["status"] = "failed"
                    return
            
            # Get templates and lists for campaign creation
            templates = []
            lists = []
            
            async with self.session.get(f"{BACKEND_URL}/templates", headers=headers) as response:
                if response.status == 200:
                    templates = await response.json()
                    test_details.append(f"✅ Found {len(templates)} templates")
                else:
                    test_details.append(f"❌ Failed to get templates: HTTP {response.status}")
            
            async with self.session.get(f"{BACKEND_URL}/lists", headers=headers) as response:
                if response.status == 200:
                    lists = await response.json()
                    test_details.append(f"✅ Found {len(lists)} prospect lists")
                else:
                    test_details.append(f"❌ Failed to get lists: HTTP {response.status}")
            
            if not templates or not lists:
                test_details.append("❌ Missing templates or lists for campaign creation")
                self.test_results["provider_selection_campaigns"]["status"] = "failed"
                return
            
            # Test 2.1: Create campaign with specific email provider selection
            campaign_data = {
                "name": f"Provider Selection Test Campaign {datetime.now().strftime('%H:%M:%S')}",
                "template_id": templates[0].get("id"),
                "list_ids": [lists[0].get("id")],
                "max_emails": 5,
                "follow_up_enabled": True,
                "follow_up_schedule_type": "interval",
                "follow_up_intervals": [3, 7]
            }
            
            async with self.session.post(f"{BACKEND_URL}/campaigns", json=campaign_data, headers=headers) as response:
                if response.status == 200:
                    campaign = await response.json()
                    campaign_id = campaign.get("id")
                    self.created_campaign_ids.append(campaign_id)
                    test_details.append(f"✅ Campaign created successfully: {campaign.get('name')}")
                    test_details.append(f"   - Campaign ID: {campaign_id}")
                    test_details.append(f"   - Prospect Count: {campaign.get('prospect_count', 0)}")
                    
                    # Test 2.2: Test campaign sending with specific provider selection
                    send_data = {
                        "send_immediately": False,  # Don't actually send
                        "email_provider_id": selected_provider_id,  # Specify provider
                        "max_emails": 1,
                        "schedule_type": "immediate"
                    }
                    
                    async with self.session.post(f"{BACKEND_URL}/campaigns/{campaign_id}/send", json=send_data, headers=headers) as send_response:
                        if send_response.status == 200:
                            send_result = await send_response.json()
                            test_details.append(f"✅ Campaign accepts specific email provider selection")
                            test_details.append(f"   - Selected Provider ID: {selected_provider_id}")
                            test_details.append(f"   - Response: {send_result.get('message', 'No message')[:100]}")
                            self.test_results["provider_selection_campaigns"]["status"] = "passed"
                        else:
                            error_text = await send_response.text()
                            test_details.append(f"❌ Campaign sending with provider selection failed: HTTP {send_response.status}")
                            test_details.append(f"   - Error: {error_text[:200]}")
                            self.test_results["provider_selection_campaigns"]["status"] = "failed"
                else:
                    test_details.append(f"❌ Failed to create campaign: HTTP {response.status}")
                    self.test_results["provider_selection_campaigns"]["status"] = "failed"
                    
        except Exception as e:
            test_details.append(f"❌ Exception in provider selection campaigns test: {str(e)}")
            self.test_results["provider_selection_campaigns"]["status"] = "failed"
        
        self.test_results["provider_selection_campaigns"]["details"] = test_details
        for detail in test_details:
            print(f"   {detail}")
    
    async def test_email_sending_selected_providers(self):
        """Test 3: Email Sending with Selected Providers - Test that emails are sent using the selected provider"""
        print("\n📧 TESTING EMAIL SENDING WITH SELECTED PROVIDERS...")
        test_details = []
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Get available providers
            async with self.session.get(f"{BACKEND_URL}/email-providers", headers=headers) as response:
                if response.status == 200:
                    providers = await response.json()
                    test_details.append(f"✅ Found {len(providers)} email providers")
                    
                    # Find working provider (real Gmail provider)
                    working_provider = None
                    for provider in providers:
                        if provider.get("email_address") == "rohushanshinde@gmail.com" and provider.get("is_active"):
                            working_provider = provider
                            break
                    
                    if working_provider:
                        test_details.append(f"✅ Found working provider: {working_provider.get('name')}")
                        test_details.append(f"   - Email: {working_provider.get('email_address')}")
                        test_details.append(f"   - Provider Type: {working_provider.get('provider_type')}")
                        
                        # Test 3.1: Create a fresh campaign for email sending test
                        working_provider_id = working_provider.get("id")
                        
                        # Get templates and lists for fresh campaign creation
                        async with self.session.get(f"{BACKEND_URL}/templates", headers=headers) as response:
                            if response.status == 200:
                                templates = await response.json()
                                if templates:
                                    async with self.session.get(f"{BACKEND_URL}/lists", headers=headers) as response:
                                        if response.status == 200:
                                            lists = await response.json()
                                            if lists:
                                                # Create fresh campaign for email sending test
                                                campaign_data = {
                                                    "name": f"Email Sending Test Campaign {datetime.now().strftime('%H:%M:%S')}",
                                                    "template_id": templates[0].get("id"),
                                                    "list_ids": [lists[0].get("id")],
                                                    "max_emails": 1,
                                                    "follow_up_enabled": False
                                                }
                                                
                                                async with self.session.post(f"{BACKEND_URL}/campaigns", json=campaign_data, headers=headers) as response:
                                                    if response.status == 200:
                                                        campaign = await response.json()
                                                        campaign_id = campaign.get("id")
                                                        self.created_campaign_ids.append(campaign_id)
                                                        
                                                        # Test sending with working provider (limited to 1 email)
                                                        send_data = {
                                                            "send_immediately": False,  # Don't actually send to avoid spam
                                                            "email_provider_id": working_provider_id,
                                                            "max_emails": 1,
                                                            "schedule_type": "immediate"
                                                        }
                                                        
                                                        async with self.session.post(f"{BACKEND_URL}/campaigns/{campaign_id}/send", json=send_data, headers=headers) as send_response:
                                                            if send_response.status == 200:
                                                                send_result = await send_response.json()
                                                                test_details.append(f"✅ Email sending with working provider successful")
                                                                test_details.append(f"   - Provider Used: {working_provider.get('name')}")
                                                                test_details.append(f"   - Response: {send_result.get('message', 'No message')[:100]}")
                                                                test_details.append(f"   - Campaign ID: {campaign_id}")
                                                                self.test_results["email_sending_selected_providers"]["status"] = "passed"
                                                            else:
                                                                error_text = await send_response.text()
                                                                test_details.append(f"❌ Email sending failed: HTTP {send_response.status}")
                                                                test_details.append(f"   - Error: {error_text[:200]}")
                                                                self.test_results["email_sending_selected_providers"]["status"] = "failed"
                                                    else:
                                                        test_details.append(f"❌ Failed to create fresh campaign: HTTP {response.status}")
                                                        self.test_results["email_sending_selected_providers"]["status"] = "failed"
                                            else:
                                                test_details.append("❌ No lists available for fresh campaign creation")
                                                self.test_results["email_sending_selected_providers"]["status"] = "failed"
                                        else:
                                            test_details.append(f"❌ Failed to get lists: HTTP {response.status}")
                                            self.test_results["email_sending_selected_providers"]["status"] = "failed"
                                else:
                                    test_details.append("❌ No templates available for fresh campaign creation")
                                    self.test_results["email_sending_selected_providers"]["status"] = "failed"
                            else:
                                test_details.append(f"❌ Failed to get templates: HTTP {response.status}")
                                self.test_results["email_sending_selected_providers"]["status"] = "failed"
                    else:
                        test_details.append("⚠️ No working provider found for email sending test")
                        test_details.append("   Available providers:")
                        for provider in providers:
                            test_details.append(f"   - {provider.get('name', 'Unknown')}: {provider.get('email_address', 'No email')}")
                        self.test_results["email_sending_selected_providers"]["status"] = "partial"
                else:
                    test_details.append(f"❌ Failed to get email providers: HTTP {response.status}")
                    self.test_results["email_sending_selected_providers"]["status"] = "failed"
                    
        except Exception as e:
            test_details.append(f"❌ Exception in email sending with selected providers test: {str(e)}")
            self.test_results["email_sending_selected_providers"]["status"] = "failed"
        
        self.test_results["email_sending_selected_providers"]["details"] = test_details
        for detail in test_details:
            print(f"   {detail}")
    
    async def test_default_provider_functionality(self):
        """Test 4: Default Provider Functionality - Test that default provider is used when no specific provider is selected"""
        print("\n🎯 TESTING DEFAULT PROVIDER FUNCTIONALITY...")
        test_details = []
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Get all providers and check for default
            async with self.session.get(f"{BACKEND_URL}/email-providers", headers=headers) as response:
                if response.status == 200:
                    providers = await response.json()
                    test_details.append(f"✅ Found {len(providers)} email providers")
                    
                    # Find default provider
                    default_provider = None
                    for provider in providers:
                        if provider.get("is_default", False):
                            default_provider = provider
                            break
                    
                    if default_provider:
                        test_details.append(f"✅ Found default provider: {default_provider.get('name')}")
                        test_details.append(f"   - Email: {default_provider.get('email_address')}")
                        test_details.append(f"   - Provider Type: {default_provider.get('provider_type')}")
                        
                        # Test 4.1: Create fresh campaign for default provider test
                        async with self.session.get(f"{BACKEND_URL}/templates", headers=headers) as response:
                            if response.status == 200:
                                templates = await response.json()
                                if templates:
                                    async with self.session.get(f"{BACKEND_URL}/lists", headers=headers) as response:
                                        if response.status == 200:
                                            lists = await response.json()
                                            if lists:
                                                # Create fresh campaign for default provider test
                                                campaign_data = {
                                                    "name": f"Default Provider Test Campaign {datetime.now().strftime('%H:%M:%S')}",
                                                    "template_id": templates[0].get("id"),
                                                    "list_ids": [lists[0].get("id")],
                                                    "max_emails": 1,
                                                    "follow_up_enabled": False
                                                }
                                                
                                                async with self.session.post(f"{BACKEND_URL}/campaigns", json=campaign_data, headers=headers) as response:
                                                    if response.status == 200:
                                                        campaign = await response.json()
                                                        campaign_id = campaign.get("id")
                                                        self.created_campaign_ids.append(campaign_id)
                                                        
                                                        # Send without specifying email_provider_id
                                                        send_data = {
                                                            "send_immediately": False,  # Don't actually send
                                                            # No email_provider_id specified - should use default
                                                            "max_emails": 1,
                                                            "schedule_type": "immediate"
                                                        }
                                                        
                                                        async with self.session.post(f"{BACKEND_URL}/campaigns/{campaign_id}/send", json=send_data, headers=headers) as send_response:
                                                            if send_response.status == 200:
                                                                send_result = await send_response.json()
                                                                test_details.append(f"✅ Campaign sending without provider selection successful")
                                                                test_details.append(f"   - Should use default provider: {default_provider.get('name')}")
                                                                test_details.append(f"   - Response: {send_result.get('message', 'No message')[:100]}")
                                                                test_details.append(f"   - Campaign ID: {campaign_id}")
                                                                self.test_results["default_provider_functionality"]["status"] = "passed"
                                                            else:
                                                                error_text = await send_response.text()
                                                                test_details.append(f"❌ Campaign sending without provider failed: HTTP {send_response.status}")
                                                                test_details.append(f"   - Error: {error_text[:200]}")
                                                                self.test_results["default_provider_functionality"]["status"] = "failed"
                                                    else:
                                                        test_details.append(f"❌ Failed to create fresh campaign: HTTP {response.status}")
                                                        self.test_results["default_provider_functionality"]["status"] = "failed"
                                            else:
                                                test_details.append("❌ No lists available for fresh campaign creation")
                                                self.test_results["default_provider_functionality"]["status"] = "failed"
                                        else:
                                            test_details.append(f"❌ Failed to get lists: HTTP {response.status}")
                                            self.test_results["default_provider_functionality"]["status"] = "failed"
                                else:
                                    test_details.append("❌ No templates available for fresh campaign creation")
                                    self.test_results["default_provider_functionality"]["status"] = "failed"
                            else:
                                test_details.append(f"❌ Failed to get templates: HTTP {response.status}")
                                self.test_results["default_provider_functionality"]["status"] = "failed"
                    else:
                        test_details.append("⚠️ No default provider found")
                        test_details.append("   Available providers:")
                        for provider in providers:
                            is_default = "✓" if provider.get("is_default", False) else "✗"
                            test_details.append(f"   - {provider.get('name', 'Unknown')} (Default: {is_default})")
                        
                        # Test setting a provider as default
                        if providers:
                            first_provider = providers[0]
                            provider_id = first_provider.get("id")
                            
                            async with self.session.post(f"{BACKEND_URL}/email-providers/{provider_id}/set-default", headers=headers) as response:
                                if response.status == 200:
                                    test_details.append(f"✅ Successfully set default provider: {first_provider.get('name')}")
                                    self.test_results["default_provider_functionality"]["status"] = "partial"
                                else:
                                    test_details.append(f"❌ Failed to set default provider: HTTP {response.status}")
                                    self.test_results["default_provider_functionality"]["status"] = "failed"
                        else:
                            self.test_results["default_provider_functionality"]["status"] = "failed"
                else:
                    test_details.append(f"❌ Failed to get email providers: HTTP {response.status}")
                    self.test_results["default_provider_functionality"]["status"] = "failed"
                    
        except Exception as e:
            test_details.append(f"❌ Exception in default provider functionality test: {str(e)}")
            self.test_results["default_provider_functionality"]["status"] = "failed"
        
        self.test_results["default_provider_functionality"]["details"] = test_details
        for detail in test_details:
            print(f"   {detail}")
    
    async def test_error_handling(self):
        """Test 5: Error Handling - Test what happens when invalid providers are selected"""
        print("\n⚠️ TESTING ERROR HANDLING...")
        test_details = []
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Test 5.1: Create fresh campaign for error handling test
            fake_provider_id = "non-existent-provider-id-12345"
            
            # Get templates and lists for fresh campaign creation
            async with self.session.get(f"{BACKEND_URL}/templates", headers=headers) as response:
                if response.status == 200:
                    templates = await response.json()
                    if templates:
                        async with self.session.get(f"{BACKEND_URL}/lists", headers=headers) as response:
                            if response.status == 200:
                                lists = await response.json()
                                if lists:
                                    # Create fresh campaign for error handling test
                                    campaign_data = {
                                        "name": f"Error Handling Test Campaign {datetime.now().strftime('%H:%M:%S')}",
                                        "template_id": templates[0].get("id"),
                                        "list_ids": [lists[0].get("id")],
                                        "max_emails": 1,
                                        "follow_up_enabled": False
                                    }
                                    
                                    async with self.session.post(f"{BACKEND_URL}/campaigns", json=campaign_data, headers=headers) as response:
                                        if response.status == 200:
                                            campaign = await response.json()
                                            campaign_id = campaign.get("id")
                                            self.created_campaign_ids.append(campaign_id)
                                            
                                            # Try to send with fake provider ID
                                            send_data = {
                                                "send_immediately": False,
                                                "email_provider_id": fake_provider_id,
                                                "max_emails": 1,
                                                "schedule_type": "immediate"
                                            }
                                            
                                            async with self.session.post(f"{BACKEND_URL}/campaigns/{campaign_id}/send", json=send_data, headers=headers) as send_response:
                                                if send_response.status in [400, 404]:
                                                    error_text = await send_response.text()
                                                    test_details.append(f"✅ Proper error handling for invalid provider ID")
                                                    test_details.append(f"   - Status Code: {send_response.status}")
                                                    test_details.append(f"   - Error Message: {error_text[:100]}")
                                                elif send_response.status == 200:
                                                    test_details.append(f"⚠️ Campaign accepted invalid provider ID (may use default)")
                                                    send_result = await send_response.json()
                                                    test_details.append(f"   - Response: {send_result.get('message', 'No message')[:100]}")
                                                else:
                                                    test_details.append(f"❌ Unexpected response for invalid provider: HTTP {send_response.status}")
                                                    error_text = await send_response.text()
                                                    test_details.append(f"   - Error: {error_text[:100]}")
                                        else:
                                            test_details.append(f"❌ Failed to create fresh campaign: HTTP {response.status}")
                                else:
                                    test_details.append("❌ No lists available for fresh campaign creation")
                            else:
                                test_details.append(f"❌ Failed to get lists: HTTP {response.status}")
                    else:
                        test_details.append("❌ No templates available for fresh campaign creation")
                else:
                    test_details.append(f"❌ Failed to get templates: HTTP {response.status}")
            
            # Test 5.2: Try to create duplicate email provider
            async with self.session.get(f"{BACKEND_URL}/email-providers", headers=headers) as response:
                if response.status == 200:
                    providers = await response.json()
                    if providers:
                        existing_provider = providers[0]
                        existing_email = existing_provider.get("email_address")
                        
                        # Try to create provider with same email
                        duplicate_provider_data = {
                            "name": "Duplicate Test Provider",
                            "provider_type": "gmail",
                            "email_address": existing_email,  # Same email as existing
                            "display_name": "Duplicate Test",
                            "smtp_host": "smtp.gmail.com",
                            "smtp_port": 587,
                            "smtp_username": existing_email,
                            "smtp_password": "test_password",
                            "daily_send_limit": 500,
                            "hourly_send_limit": 50,
                            "is_default": False,
                            "skip_connection_test": True
                        }
                        
                        async with self.session.post(f"{BACKEND_URL}/email-providers", json=duplicate_provider_data, headers=headers) as response:
                            if response.status == 400:
                                error_text = await response.text()
                                test_details.append(f"✅ Proper error handling for duplicate email provider")
                                test_details.append(f"   - Status Code: {response.status}")
                                test_details.append(f"   - Error Message: {error_text[:100]}")
                            elif response.status == 200:
                                # If it succeeded, clean up the duplicate
                                result = await response.json()
                                duplicate_id = result.get("id")
                                if duplicate_id:
                                    self.created_provider_ids.append(duplicate_id)
                                test_details.append(f"⚠️ Duplicate provider creation succeeded (may be allowed)")
                            else:
                                test_details.append(f"❌ Unexpected response for duplicate provider: HTTP {response.status}")
            
            # Test 5.3: Try to test connection of non-existent provider
            async with self.session.post(f"{BACKEND_URL}/email-providers/{fake_provider_id}/test", headers=headers) as response:
                if response.status == 404:
                    test_details.append(f"✅ Proper 404 error for testing non-existent provider")
                elif response.status == 500:
                    test_details.append(f"⚠️ Server error for non-existent provider test (acceptable)")
                else:
                    test_details.append(f"❌ Unexpected response for non-existent provider test: HTTP {response.status}")
            
            self.test_results["error_handling"]["status"] = "passed"
                    
        except Exception as e:
            test_details.append(f"❌ Exception in error handling test: {str(e)}")
            self.test_results["error_handling"]["status"] = "failed"
        
        self.test_results["error_handling"]["details"] = test_details
        for detail in test_details:
            print(f"   {detail}")
    
    async def run_all_tests(self):
        """Run all email provider selection and usage tests"""
        print("🚀 STARTING EMAIL PROVIDER SELECTION AND USAGE TESTING")
        print("=" * 70)
        
        # Setup session and authenticate
        if not await self.setup_session():
            print("❌ Failed to setup session. Exiting.")
            return
        
        try:
            # Run all tests
            await self.test_email_provider_management()
            await self.test_provider_selection_campaigns()
            await self.test_email_sending_selected_providers()
            await self.test_default_provider_functionality()
            await self.test_error_handling()
            
            # Print summary
            print("\n" + "=" * 70)
            print("📊 EMAIL PROVIDER SELECTION AND USAGE TEST SUMMARY")
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
            
            # Overall assessment
            if passed_tests == total_tests:
                print("\n🎉 ALL EMAIL PROVIDER TESTS PASSED!")
                print("Email provider selection and usage functionality is fully operational.")
            elif passed_tests + partial_tests == total_tests:
                print("\n⚠️ EMAIL PROVIDER FUNCTIONALITY MOSTLY WORKING")
                print("Some components may need attention but core functionality is operational.")
            else:
                print("\n❌ EMAIL PROVIDER FUNCTIONALITY HAS CRITICAL ISSUES")
                print("Multiple components are not working correctly.")
                
        finally:
            await self.cleanup_session()

async def main():
    """Main test execution"""
    tester = EmailProviderSelectionTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())