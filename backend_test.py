#!/usr/bin/env python3
"""
Comprehensive Backend Test for Email Campaign System
Tests the current state of email providers, lists, prospects, campaigns, and services
"""

import asyncio
import aiohttp
import json
from datetime import datetime
import sys
import os

# Backend URL from environment
BACKEND_URL = "https://030d008b-cc85-4bf3-afdd-411b8004d718.preview.emergentagent.com/api"

class EmailCampaignSystemTester:
    def __init__(self):
        self.session = None
        self.results = {
            "email_providers": {"count": 0, "data": [], "status": "unknown"},
            "lists": {"count": 0, "data": [], "status": "unknown"},
            "prospects": {"count": 0, "data": [], "status": "unknown"},
            "campaigns": {"count": 0, "data": [], "status": "unknown"},
            "templates": {"count": 0, "data": [], "status": "unknown"},
            "services": {"status": "unknown", "data": {}},
            "overall_status": "unknown"
        }
    
    async def setup_session(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession()
    
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    async def test_endpoint(self, endpoint, description):
        """Test a single endpoint and return results"""
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
    
    async def test_email_providers(self):
        """Test email providers endpoint"""
        result = await self.test_endpoint("/email-providers", "Email Providers")
        
        if result["success"]:
            providers = result["data"]
            self.results["email_providers"]["count"] = len(providers)
            self.results["email_providers"]["data"] = providers
            self.results["email_providers"]["status"] = "working"
            
            print(f"   📊 Found {len(providers)} email providers")
            for provider in providers:
                print(f"      - {provider.get('name', 'Unknown')} ({provider.get('provider_type', 'Unknown')})")
                print(f"        Email: {provider.get('email_address', 'N/A')}")
                print(f"        Active: {provider.get('is_active', False)}")
                print(f"        Default: {provider.get('is_default', False)}")
        else:
            self.results["email_providers"]["status"] = "failed"
    
    async def test_lists(self):
        """Test prospect lists endpoint"""
        result = await self.test_endpoint("/lists", "Prospect Lists")
        
        if result["success"]:
            lists = result["data"]
            self.results["lists"]["count"] = len(lists)
            self.results["lists"]["data"] = lists
            self.results["lists"]["status"] = "working"
            
            print(f"   📊 Found {len(lists)} prospect lists")
            for list_item in lists:
                print(f"      - {list_item.get('name', 'Unknown')}")
                print(f"        Prospects: {list_item.get('prospect_count', 0)}")
                print(f"        Description: {list_item.get('description', 'N/A')}")
        else:
            self.results["lists"]["status"] = "failed"
    
    async def test_prospects(self):
        """Test prospects endpoint"""
        result = await self.test_endpoint("/prospects", "Prospects")
        
        if result["success"]:
            prospects = result["data"]
            self.results["prospects"]["count"] = len(prospects)
            self.results["prospects"]["data"] = prospects
            self.results["prospects"]["status"] = "working"
            
            print(f"   📊 Found {len(prospects)} prospects")
            for prospect in prospects[:5]:  # Show first 5
                print(f"      - {prospect.get('first_name', '')} {prospect.get('last_name', '')}")
                print(f"        Email: {prospect.get('email', 'N/A')}")
                print(f"        Company: {prospect.get('company', 'N/A')}")
        else:
            self.results["prospects"]["status"] = "failed"
    
    async def test_campaigns(self):
        """Test campaigns endpoint"""
        result = await self.test_endpoint("/campaigns", "Campaigns")
        
        if result["success"]:
            campaigns = result["data"]
            self.results["campaigns"]["count"] = len(campaigns)
            self.results["campaigns"]["data"] = campaigns
            self.results["campaigns"]["status"] = "working"
            
            print(f"   📊 Found {len(campaigns)} campaigns")
            for campaign in campaigns:
                print(f"      - {campaign.get('name', 'Unknown')}")
                print(f"        Status: {campaign.get('status', 'N/A')}")
                print(f"        Prospects: {campaign.get('prospect_count', 0)}")
                print(f"        Follow-up enabled: {campaign.get('follow_up_enabled', False)}")
        else:
            self.results["campaigns"]["status"] = "failed"
    
    async def test_templates(self):
        """Test templates endpoint"""
        result = await self.test_endpoint("/templates", "Email Templates")
        
        if result["success"]:
            templates = result["data"]
            self.results["templates"]["count"] = len(templates)
            self.results["templates"]["data"] = templates
            self.results["templates"]["status"] = "working"
            
            print(f"   📊 Found {len(templates)} email templates")
            for template in templates:
                print(f"      - {template.get('name', 'Unknown')}")
                print(f"        Type: {template.get('type', 'N/A')}")
        else:
            self.results["templates"]["status"] = "failed"
    
    async def test_services_status(self):
        """Test services status endpoint"""
        result = await self.test_endpoint("/services/status", "Services Status")
        
        if result["success"]:
            services = result["data"]
            self.results["services"]["data"] = services
            self.results["services"]["status"] = "working"
            
            print(f"   📊 Services Status:")
            if "services" in services:
                for service_name, service_info in services["services"].items():
                    status = service_info.get("status", "unknown")
                    description = service_info.get("description", "")
                    print(f"      - {service_name}: {status}")
                    print(f"        Description: {description}")
                    
                    # Show monitored providers for email processor
                    if service_name == "email_processor" and "monitored_providers" in service_info:
                        providers = service_info["monitored_providers"]
                        print(f"        Monitored providers: {len(providers)}")
                        for provider in providers:
                            print(f"          * {provider.get('name', 'Unknown')} ({provider.get('provider_type', 'Unknown')})")
            
            print(f"   Overall Status: {services.get('overall_status', 'unknown')}")
        else:
            self.results["services"]["status"] = "failed"
    
    async def test_health_check(self):
        """Test basic health check"""
        result = await self.test_endpoint("/health", "Health Check")
        return result["success"] if result else False
    
    async def run_comprehensive_test(self):
        """Run all tests and provide comprehensive overview"""
        print("=" * 80)
        print("🚀 COMPREHENSIVE EMAIL CAMPAIGN SYSTEM TEST")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        
        await self.setup_session()
        
        try:
            # Test basic connectivity first
            health_ok = await self.test_health_check()
            if not health_ok:
                print("\n❌ CRITICAL: Backend health check failed!")
                self.results["overall_status"] = "failed"
                return
            
            # Run all endpoint tests
            await self.test_email_providers()
            await self.test_lists()
            await self.test_prospects()
            await self.test_campaigns()
            await self.test_templates()
            await self.test_services_status()
            
            # Determine overall status
            failed_tests = [k for k, v in self.results.items() 
                          if isinstance(v, dict) and v.get("status") == "failed"]
            
            if not failed_tests:
                self.results["overall_status"] = "healthy"
            elif len(failed_tests) <= 2:
                self.results["overall_status"] = "degraded"
            else:
                self.results["overall_status"] = "failed"
            
        finally:
            await self.cleanup_session()
        
        # Print comprehensive summary
        self.print_summary()
    
    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("📋 COMPREHENSIVE SYSTEM OVERVIEW")
        print("=" * 80)
        
        # System Status
        status_emoji = {
            "healthy": "✅",
            "degraded": "⚠️",
            "failed": "❌",
            "unknown": "❓"
        }
        
        overall_status = self.results["overall_status"]
        print(f"\n🎯 OVERALL SYSTEM STATUS: {status_emoji.get(overall_status, '❓')} {overall_status.upper()}")
        
        # Component Summary
        print(f"\n📊 COMPONENT SUMMARY:")
        print(f"   • Email Providers: {self.results['email_providers']['count']} configured")
        print(f"   • Prospect Lists: {self.results['lists']['count']} created")
        print(f"   • Prospects: {self.results['prospects']['count']} total")
        print(f"   • Campaigns: {self.results['campaigns']['count']} created")
        print(f"   • Templates: {self.results['templates']['count']} available")
        
        # Services Status
        print(f"\n🔧 BACKGROUND SERVICES:")
        services_data = self.results["services"]["data"]
        if "services" in services_data:
            for service_name, service_info in services_data["services"].items():
                status = service_info.get("status", "unknown")
                emoji = "✅" if status == "running" else "❌" if status == "stopped" else "❓"
                print(f"   • {service_name}: {emoji} {status}")
        
        # Detailed Analysis
        print(f"\n🔍 DETAILED ANALYSIS:")
        
        # Email Providers Analysis
        providers = self.results["email_providers"]["data"]
        if providers:
            active_providers = [p for p in providers if p.get("is_active", False)]
            default_providers = [p for p in providers if p.get("is_default", False)]
            print(f"   • Active Email Providers: {len(active_providers)}/{len(providers)}")
            print(f"   • Default Provider Set: {'Yes' if default_providers else 'No'}")
            
            for provider in providers:
                imap_enabled = provider.get("imap_enabled", False)
                print(f"     - {provider.get('name', 'Unknown')}: IMAP {'✅' if imap_enabled else '❌'}")
        
        # Campaign Analysis
        campaigns = self.results["campaigns"]["data"]
        if campaigns:
            active_campaigns = [c for c in campaigns if c.get("status") == "active"]
            follow_up_campaigns = [c for c in campaigns if c.get("follow_up_enabled", False)]
            print(f"   • Active Campaigns: {len(active_campaigns)}/{len(campaigns)}")
            print(f"   • Follow-up Enabled: {len(follow_up_campaigns)}/{len(campaigns)}")
        
        # System Readiness
        print(f"\n🎯 SYSTEM READINESS:")
        readiness_score = 0
        total_checks = 6
        
        if self.results["email_providers"]["count"] > 0:
            readiness_score += 1
            print("   ✅ Email providers configured")
        else:
            print("   ❌ No email providers configured")
        
        if self.results["prospects"]["count"] > 0:
            readiness_score += 1
            print("   ✅ Prospects available")
        else:
            print("   ❌ No prospects available")
        
        if self.results["templates"]["count"] > 0:
            readiness_score += 1
            print("   ✅ Email templates available")
        else:
            print("   ❌ No email templates available")
        
        if self.results["lists"]["count"] > 0:
            readiness_score += 1
            print("   ✅ Prospect lists created")
        else:
            print("   ❌ No prospect lists created")
        
        # Check if services are running
        services_data = self.results["services"]["data"]
        if "services" in services_data:
            follow_up_running = services_data["services"].get("smart_follow_up_engine", {}).get("status") == "running"
            email_proc_running = services_data["services"].get("email_processor", {}).get("status") == "running"
            
            if follow_up_running:
                readiness_score += 1
                print("   ✅ Follow-up engine running")
            else:
                print("   ❌ Follow-up engine not running")
            
            if email_proc_running:
                readiness_score += 1
                print("   ✅ Email processor running")
            else:
                print("   ❌ Email processor not running")
        
        readiness_percentage = (readiness_score / total_checks) * 100
        print(f"\n📈 SYSTEM READINESS: {readiness_percentage:.1f}% ({readiness_score}/{total_checks})")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if self.results["email_providers"]["count"] == 0:
            print("   • Configure at least one email provider to send campaigns")
        if self.results["prospects"]["count"] == 0:
            print("   • Import prospects to start email campaigns")
        if self.results["templates"]["count"] == 0:
            print("   • Create email templates for campaigns")
        if self.results["campaigns"]["count"] == 0:
            print("   • Create campaigns to start email outreach")
        
        services_data = self.results["services"]["data"]
        if "services" in services_data:
            if services_data["services"].get("smart_follow_up_engine", {}).get("status") != "running":
                print("   • Start the follow-up engine for automated follow-ups")
            if services_data["services"].get("email_processor", {}).get("status") != "running":
                print("   • Start the email processor for auto-responses")
        
        print("\n" + "=" * 80)
        print("✅ COMPREHENSIVE TEST COMPLETED")
        print("=" * 80)

async def main():
    """Main test execution"""
    tester = EmailCampaignSystemTester()
    await tester.run_comprehensive_test()

if __name__ == "__main__":
    asyncio.run(main())