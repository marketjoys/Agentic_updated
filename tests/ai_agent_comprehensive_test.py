#!/usr/bin/env python3
"""
AI Agent Functionality Testing - Comprehensive Test Suite
Testing the specific scenarios mentioned in the review request
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AIAgentTester:
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.session = None
        self.auth_token = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        await self.authenticate()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def authenticate(self):
        """Authenticate and get access token"""
        try:
            login_data = {
                "username": self.username,
                "password": self.password
            }
            
            async with self.session.post(f"{self.base_url}/api/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data.get("access_token")
                    logger.info("✅ Authentication successful")
                    return True
                else:
                    logger.error(f"❌ Authentication failed: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            return False
    
    async def make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """Make authenticated API request"""
        headers = {}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        try:
            url = f"{self.base_url}{endpoint}"
            
            if method.upper() == "GET":
                async with self.session.get(url, headers=headers) as response:
                    return {
                        "status": response.status,
                        "data": await response.json() if response.content_type == 'application/json' else await response.text()
                    }
            elif method.upper() == "POST":
                async with self.session.post(url, json=data, headers=headers) as response:
                    return {
                        "status": response.status,
                        "data": await response.json() if response.content_type == 'application/json' else await response.text()
                    }
            elif method.upper() == "PUT":
                async with self.session.put(url, json=data, headers=headers) as response:
                    return {
                        "status": response.status,
                        "data": await response.json() if response.content_type == 'application/json' else await response.text()
                    }
            elif method.upper() == "DELETE":
                async with self.session.delete(url, headers=headers) as response:
                    return {
                        "status": response.status,
                        "data": await response.json() if response.content_type == 'application/json' else await response.text()
                    }
        except Exception as e:
            logger.error(f"❌ Request error for {method} {endpoint}: {e}")
            return {"status": 500, "data": {"error": str(e)}}
    
    async def test_ai_agent_chat(self, message: str, test_name: str) -> Dict:
        """Test AI Agent chat functionality"""
        logger.info(f"\n🤖 Testing AI Agent: {test_name}")
        logger.info(f"📝 Message: '{message}'")
        
        chat_data = {
            "message": message,
            "user_id": "testuser",
            "session_id": f"test_session_{datetime.now().timestamp()}",
            "context": {}
        }
        
        result = await self.make_request("POST", "/api/ai-agent/chat", chat_data)
        
        if result["status"] == 200:
            response_data = result["data"]
            logger.info(f"✅ AI Agent Response: {response_data.get('response', 'No response')}")
            logger.info(f"🎯 Action Taken: {response_data.get('action_taken', 'None')}")
            
            if response_data.get('data'):
                data = response_data['data']
                if isinstance(data, list):
                    logger.info(f"📊 Data Count: {len(data)} items")
                elif isinstance(data, dict):
                    logger.info(f"📊 Data Keys: {list(data.keys())}")
            
            return {
                "success": True,
                "response": response_data.get('response', ''),
                "action_taken": response_data.get('action_taken', ''),
                "data": response_data.get('data'),
                "suggestions": response_data.get('suggestions', [])
            }
        else:
            logger.error(f"❌ AI Agent Error: {result['status']} - {result['data']}")
            return {
                "success": False,
                "error": result['data'],
                "status": result['status']
            }
    
    async def test_backend_endpoints(self):
        """Test backend endpoints to ensure they're working"""
        logger.info("\n🔧 Testing Backend Endpoints...")
        
        endpoints_to_test = [
            ("GET", "/api/campaigns", "Campaigns"),
            ("GET", "/api/prospects", "Prospects"),
            ("GET", "/api/lists", "Lists"),
            ("GET", "/api/templates", "Templates"),
            ("GET", "/api/ai-agent/capabilities", "AI Agent Capabilities"),
            ("GET", "/api/ai-agent/help", "AI Agent Help")
        ]
        
        for method, endpoint, name in endpoints_to_test:
            result = await self.make_request(method, endpoint)
            if result["status"] == 200:
                logger.info(f"✅ {name} endpoint working")
            else:
                logger.error(f"❌ {name} endpoint failed: {result['status']}")
    
    async def run_comprehensive_tests(self):
        """Run all AI Agent tests as specified in the review request"""
        logger.info("🚀 Starting Comprehensive AI Agent Testing")
        logger.info("=" * 80)
        
        # Test backend endpoints first
        await self.test_backend_endpoints()
        
        test_results = {}
        
        # 1. PROSPECT CREATION TESTS (Previously Failing)
        logger.info("\n" + "=" * 50)
        logger.info("1️⃣ PROSPECT CREATION TESTS (Previously Failing)")
        logger.info("=" * 50)
        
        prospect_tests = [
            ("Add a prospect named John Smith from TechCorp", "prospect_john_smith"),
            ("Create a prospect Mike Davis at DataScience AI", "prospect_mike_davis"),
            ("Add Sarah Johnson from InnovateSoft", "prospect_sarah_johnson"),
            ("Create prospect Michael O'Connor from Global Tech Solutions Inc", "prospect_michael_oconnor")
        ]
        
        for message, test_key in prospect_tests:
            result = await self.test_ai_agent_chat(message, f"Prospect Creation - {test_key}")
            test_results[test_key] = result
            await asyncio.sleep(1)  # Brief pause between tests
        
        # 2. LIST CREATION TESTS (Should continue working)
        logger.info("\n" + "=" * 50)
        logger.info("2️⃣ LIST CREATION TESTS (Should continue working)")
        logger.info("=" * 50)
        
        list_tests = [
            ("Create a new list called Test Marketing List", "list_test_marketing"),
            ("Make a list named VIP Customers", "list_vip_customers"),
            ("Create a list called Technology Companies", "list_technology_companies")
        ]
        
        for message, test_key in list_tests:
            result = await self.test_ai_agent_chat(message, f"List Creation - {test_key}")
            test_results[test_key] = result
            await asyncio.sleep(1)
        
        # 3. SHOW COMMANDS TESTS (Should continue working)
        logger.info("\n" + "=" * 50)
        logger.info("3️⃣ SHOW COMMANDS TESTS (Should continue working)")
        logger.info("=" * 50)
        
        show_tests = [
            ("Show me all my prospects", "show_prospects"),
            ("Show me all my lists", "show_lists"),
            ("Show me all my campaigns", "show_campaigns")
        ]
        
        for message, test_key in show_tests:
            result = await self.test_ai_agent_chat(message, f"Show Command - {test_key}")
            test_results[test_key] = result
            await asyncio.sleep(1)
        
        # 4. SEARCH/FIND TESTS (New functionality)
        logger.info("\n" + "=" * 50)
        logger.info("4️⃣ SEARCH/FIND TESTS (New functionality)")
        logger.info("=" * 50)
        
        search_tests = [
            ("Find prospects from TechCorp", "search_techcorp"),
            ("Search prospects named John", "search_john"),
            ("Find prospects in technology industry", "search_technology_industry")
        ]
        
        for message, test_key in search_tests:
            result = await self.test_ai_agent_chat(message, f"Search - {test_key}")
            test_results[test_key] = result
            await asyncio.sleep(1)
        
        # 5. ADD TO LIST TESTS
        logger.info("\n" + "=" * 50)
        logger.info("5️⃣ ADD TO LIST TESTS")
        logger.info("=" * 50)
        
        add_to_list_tests = [
            ("Add John Smith to VIP Customers list", "add_john_to_vip")
        ]
        
        for message, test_key in add_to_list_tests:
            result = await self.test_ai_agent_chat(message, f"Add to List - {test_key}")
            test_results[test_key] = result
            await asyncio.sleep(1)
        
        # Generate comprehensive test report
        await self.generate_test_report(test_results)
        
        return test_results
    
    async def generate_test_report(self, test_results: Dict):
        """Generate comprehensive test report"""
        logger.info("\n" + "=" * 80)
        logger.info("📊 COMPREHENSIVE AI AGENT TEST REPORT")
        logger.info("=" * 80)
        
        # Categorize results
        categories = {
            "Prospect Creation": ["prospect_john_smith", "prospect_mike_davis", "prospect_sarah_johnson", "prospect_michael_oconnor"],
            "List Creation": ["list_test_marketing", "list_vip_customers", "list_technology_companies"],
            "Show Commands": ["show_prospects", "show_lists", "show_campaigns"],
            "Search/Find": ["search_techcorp", "search_john", "search_technology_industry"],
            "Add to List": ["add_john_to_vip"]
        }
        
        overall_stats = {"total": 0, "passed": 0, "failed": 0}
        
        for category, test_keys in categories.items():
            logger.info(f"\n🔍 {category} Tests:")
            category_stats = {"total": 0, "passed": 0, "failed": 0}
            
            for test_key in test_keys:
                if test_key in test_results:
                    result = test_results[test_key]
                    category_stats["total"] += 1
                    overall_stats["total"] += 1
                    
                    if result.get("success"):
                        status = "✅ PASS"
                        category_stats["passed"] += 1
                        overall_stats["passed"] += 1
                        
                        # Check if action was taken
                        action = result.get("action_taken", "None")
                        if action and action != "None" and action != "help":
                            logger.info(f"  {status} - {test_key} (Action: {action})")
                        else:
                            logger.info(f"  ⚠️  PARTIAL - {test_key} (No specific action taken)")
                    else:
                        status = "❌ FAIL"
                        category_stats["failed"] += 1
                        overall_stats["failed"] += 1
                        error = result.get("error", "Unknown error")
                        logger.info(f"  {status} - {test_key} (Error: {error})")
            
            # Category summary
            pass_rate = (category_stats["passed"] / category_stats["total"] * 100) if category_stats["total"] > 0 else 0
            logger.info(f"  📈 {category} Summary: {category_stats['passed']}/{category_stats['total']} passed ({pass_rate:.1f}%)")
        
        # Overall summary
        overall_pass_rate = (overall_stats["passed"] / overall_stats["total"] * 100) if overall_stats["total"] > 0 else 0
        logger.info(f"\n🎯 OVERALL TEST RESULTS:")
        logger.info(f"   Total Tests: {overall_stats['total']}")
        logger.info(f"   Passed: {overall_stats['passed']}")
        logger.info(f"   Failed: {overall_stats['failed']}")
        logger.info(f"   Pass Rate: {overall_pass_rate:.1f}%")
        
        # Detailed analysis
        logger.info(f"\n🔬 DETAILED ANALYSIS:")
        
        # Check for specific issues mentioned in review request
        prospect_creation_issues = []
        for test_key in ["prospect_john_smith", "prospect_mike_davis", "prospect_sarah_johnson", "prospect_michael_oconnor"]:
            if test_key in test_results:
                result = test_results[test_key]
                if not result.get("success") or result.get("action_taken") in ["help", "None", None]:
                    prospect_creation_issues.append(test_key)
        
        if prospect_creation_issues:
            logger.info(f"   ⚠️  Prospect Creation Issues: {len(prospect_creation_issues)} tests failed")
            logger.info(f"      Failed tests: {', '.join(prospect_creation_issues)}")
        else:
            logger.info(f"   ✅ Prospect Creation: All tests passed")
        
        # Check list creation
        list_creation_issues = []
        for test_key in ["list_test_marketing", "list_vip_customers", "list_technology_companies"]:
            if test_key in test_results:
                result = test_results[test_key]
                if not result.get("success") or result.get("action_taken") not in ["create_list"]:
                    list_creation_issues.append(test_key)
        
        if list_creation_issues:
            logger.info(f"   ⚠️  List Creation Issues: {len(list_creation_issues)} tests failed")
        else:
            logger.info(f"   ✅ List Creation: All tests passed")
        
        # Check show commands
        show_command_issues = []
        for test_key in ["show_prospects", "show_lists", "show_campaigns"]:
            if test_key in test_results:
                result = test_results[test_key]
                expected_actions = ["list_prospects", "list_lists", "list_campaigns"]
                if not result.get("success") or result.get("action_taken") not in expected_actions:
                    show_command_issues.append(test_key)
        
        if show_command_issues:
            logger.info(f"   ⚠️  Show Commands Issues: {len(show_command_issues)} tests failed")
        else:
            logger.info(f"   ✅ Show Commands: All tests passed")
        
        # Final recommendations
        logger.info(f"\n💡 RECOMMENDATIONS:")
        if overall_pass_rate >= 80:
            logger.info(f"   ✅ AI Agent functionality is mostly working well")
        elif overall_pass_rate >= 60:
            logger.info(f"   ⚠️  AI Agent has some issues that need attention")
        else:
            logger.info(f"   ❌ AI Agent has significant issues requiring immediate fixes")
        
        if prospect_creation_issues:
            logger.info(f"   🔧 Fix prospect creation parameter extraction (regex patterns)")
        if list_creation_issues:
            logger.info(f"   🔧 Fix list creation functionality")
        if show_command_issues:
            logger.info(f"   🔧 Fix show command routing")
        
        logger.info("=" * 80)

async def main():
    """Main test execution"""
    # Use the backend URL from frontend/.env
    BASE_URL = "https://9875c261-7164-46da-a66e-4f7aea2c987d.preview.emergentagent.com"
    USERNAME = "testuser"
    PASSWORD = "testpass123"
    
    logger.info("🚀 AI Agent Functionality Testing Started")
    logger.info(f"🌐 Backend URL: {BASE_URL}")
    logger.info(f"👤 Test User: {USERNAME}")
    
    try:
        async with AIAgentTester(BASE_URL, USERNAME, PASSWORD) as tester:
            test_results = await tester.run_comprehensive_tests()
            
        logger.info("\n✅ AI Agent Testing Completed Successfully")
        
    except Exception as e:
        logger.error(f"❌ Testing failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())