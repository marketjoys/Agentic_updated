#!/usr/bin/env python3
"""
AI Agent Backend Test - Focus on AI Agent functionality
Tests the AI Agent endpoints and related functionality
"""

import asyncio
import aiohttp
import json
from datetime import datetime
import sys

# Backend URL from environment
BACKEND_URL = "https://030d008b-cc85-4bf3-afdd-411b8004d718.preview.emergentagent.com/api"

class AIAgentTester:
    def __init__(self):
        self.session = None
        self.test_results = []
    
    async def setup_session(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession()
    
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    async def test_get_endpoint(self, endpoint, description):
        """Test a GET endpoint"""
        try:
            print(f"\n🔍 Testing {description}...")
            print(f"   URL: {BACKEND_URL}{endpoint}")
            
            async with self.session.get(f"{BACKEND_URL}{endpoint}") as response:
                status_code = response.status
                
                if status_code == 200:
                    data = await response.json()
                    print(f"   ✅ SUCCESS - Status: {status_code}")
                    self.test_results.append({"test": description, "status": "PASS", "code": status_code})
                    return {"success": True, "status_code": status_code, "data": data}
                else:
                    error_text = await response.text()
                    print(f"   ❌ FAILED - Status: {status_code}")
                    print(f"   Error: {error_text}")
                    self.test_results.append({"test": description, "status": "FAIL", "code": status_code, "error": error_text})
                    return {"success": False, "status_code": status_code, "error": error_text}
                    
        except Exception as e:
            print(f"   ❌ EXCEPTION - {str(e)}")
            self.test_results.append({"test": description, "status": "ERROR", "error": str(e)})
            return {"success": False, "error": str(e)}
    
    async def test_post_endpoint(self, endpoint, description, data=None):
        """Test a POST endpoint"""
        try:
            print(f"\n🔍 Testing {description}...")
            print(f"   URL: {BACKEND_URL}{endpoint}")
            
            headers = {'Content-Type': 'application/json'}
            async with self.session.post(f"{BACKEND_URL}{endpoint}", json=data, headers=headers) as response:
                status_code = response.status
                
                if status_code in [200, 201]:
                    response_data = await response.json()
                    print(f"   ✅ SUCCESS - Status: {status_code}")
                    self.test_results.append({"test": description, "status": "PASS", "code": status_code})
                    return {"success": True, "status_code": status_code, "data": response_data}
                else:
                    error_text = await response.text()
                    print(f"   ❌ FAILED - Status: {status_code}")
                    print(f"   Error: {error_text}")
                    self.test_results.append({"test": description, "status": "FAIL", "code": status_code, "error": error_text})
                    return {"success": False, "status_code": status_code, "error": error_text}
                    
        except Exception as e:
            print(f"   ❌ EXCEPTION - {str(e)}")
            self.test_results.append({"test": description, "status": "ERROR", "error": str(e)})
            return {"success": False, "error": str(e)}
    
    async def test_ai_agent_endpoints(self):
        """Test AI Agent specific endpoints"""
        print("=" * 80)
        print("🤖 AI AGENT BACKEND ENDPOINTS TEST")
        print("=" * 80)
        
        # Test industries endpoint (used by AI Agent)
        await self.test_get_endpoint("/industries", "Industries for AI Agent")
        
        # Test intents endpoint (used by AI Agent)
        await self.test_get_endpoint("/intents", "Intents for AI Agent")
        
        # Test campaigns endpoint (AI Agent shows campaigns)
        await self.test_get_endpoint("/campaigns", "Campaigns (AI Agent shows these)")
        
        # Test prospects endpoint (AI Agent shows prospects)
        await self.test_get_endpoint("/prospects", "Prospects (AI Agent shows these)")
        
        # Test auth endpoints (needed for AI Agent to work)
        await self.test_post_endpoint("/auth/login", "Login (required for AI Agent)", {
            "username": "testuser",
            "password": "testpass123"
        })
        
        # Test auth/me endpoint
        await self.test_get_endpoint("/auth/me", "User Info (AI Agent needs this)")
        
        # Test services status (AI Agent shows this)
        await self.test_get_endpoint("/services/status", "Services Status (AI Agent shows this)")
        
        # Test dashboard metrics (AI Agent might use this)
        await self.test_get_endpoint("/real-time/dashboard-metrics", "Dashboard Metrics (AI Agent uses this)")
    
    async def run_tests(self):
        """Run all AI Agent related tests"""
        await self.setup_session()
        
        try:
            await self.test_ai_agent_endpoints()
            
        finally:
            await self.cleanup_session()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("📋 AI AGENT BACKEND TEST SUMMARY")
        print("=" * 80)
        
        passed = len([r for r in self.test_results if r["status"] == "PASS"])
        failed = len([r for r in self.test_results if r["status"] == "FAIL"])
        errors = len([r for r in self.test_results if r["status"] == "ERROR"])
        total = len(self.test_results)
        
        print(f"\n📊 RESULTS:")
        print(f"   ✅ Passed: {passed}")
        print(f"   ❌ Failed: {failed}")
        print(f"   🔥 Errors: {errors}")
        print(f"   📈 Total: {total}")
        
        if failed > 0 or errors > 0:
            print(f"\n❌ FAILED/ERROR TESTS:")
            for result in self.test_results:
                if result["status"] in ["FAIL", "ERROR"]:
                    print(f"   • {result['test']}: {result['status']}")
                    if "error" in result:
                        print(f"     Error: {result['error']}")
        
        success_rate = (passed / total * 100) if total > 0 else 0
        print(f"\n🎯 SUCCESS RATE: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("✅ AI Agent backend endpoints are working well!")
        elif success_rate >= 70:
            print("⚠️ AI Agent backend has some issues but mostly working")
        else:
            print("❌ AI Agent backend has significant issues")
        
        print("=" * 80)

async def main():
    """Main test execution"""
    tester = AIAgentTester()
    await tester.run_tests()

if __name__ == "__main__":
    asyncio.run(main())