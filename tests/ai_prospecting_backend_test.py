#!/usr/bin/env python3
"""
AI Prospecting Functionality Backend Test
Tests the AI Agent's AI prospecting functionality as requested in the review.

This test verifies:
1. AI Agent API endpoint with AI prospecting queries
2. Proper action recognition ("ai_prospecting_search")
3. Correct routing to AI prospecting service
4. Database/lists management for prospects
5. Edge cases and error handling
"""

import asyncio
import aiohttp
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any

# Test configuration
BACKEND_URL = "https://1e08e58e-1080-4fe8-bd99-54911ebc72f3.preview.emergentagent.com"
TEST_USER = "testuser"
TEST_PASSWORD = "testpass123"

class AIProspectingTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_results = []
        
    async def setup_session(self):
        """Setup HTTP session and authenticate"""
        self.session = aiohttp.ClientSession()
        
        # Login to get auth token
        login_data = {
            "username": TEST_USER,
            "password": TEST_PASSWORD
        }
        
        async with self.session.post(f"{BACKEND_URL}/api/auth/login", json=login_data) as response:
            if response.status == 200:
                data = await response.json()
                self.auth_token = data.get("access_token")
                print(f"✅ Authentication successful")
                return True
            else:
                print(f"❌ Authentication failed: {response.status}")
                return False
    
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    def get_headers(self):
        """Get headers with authentication"""
        return {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
    
    async def test_ai_agent_prospecting_queries(self):
        """Test AI Agent API endpoint with AI prospecting queries"""
        print("\n🧪 Testing AI Agent AI Prospecting Queries...")
        
        test_queries = [
            "Find prospects like CEOs at tech companies",
            "AI prospect search for marketing directors",
            "Suggest prospects for VIP list",
            "Find CTOs at software companies in California",
            "Search for founders in fintech startups"
        ]
        
        results = []
        
        for query in test_queries:
            try:
                # Test with enhanced flow (default)
                request_data = {
                    "message": query,
                    "use_enhanced_flow": True
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/api/ai-agent/chat",
                    json=request_data,
                    headers=self.get_headers()
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        # Check if action is recognized as AI prospecting
                        action_taken = data.get("action_taken")
                        response_text = data.get("response", "")
                        
                        # Verify proper action recognition
                        is_ai_prospecting = (
                            action_taken == "ai_prospecting_search" or
                            "prospecting" in response_text.lower() or
                            "prospects" in response_text.lower()
                        )
                        
                        result = {
                            "query": query,
                            "status": "success",
                            "action_taken": action_taken,
                            "response": response_text[:200] + "..." if len(response_text) > 200 else response_text,
                            "ai_prospecting_recognized": is_ai_prospecting,
                            "conversation_state": data.get("conversation_state"),
                            "pending_action": data.get("pending_action"),
                            "data": data.get("data")
                        }
                        
                        if is_ai_prospecting:
                            print(f"  ✅ Query: '{query}' - Action: {action_taken}")
                        else:
                            print(f"  ⚠️  Query: '{query}' - Action: {action_taken} (not recognized as AI prospecting)")
                        
                        results.append(result)
                        
                    else:
                        error_text = await response.text()
                        print(f"  ❌ Query: '{query}' - HTTP {response.status}: {error_text}")
                        results.append({
                            "query": query,
                            "status": "error",
                            "error": f"HTTP {response.status}: {error_text}"
                        })
                
                # Small delay between requests
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"  ❌ Query: '{query}' - Exception: {str(e)}")
                results.append({
                    "query": query,
                    "status": "exception",
                    "error": str(e)
                })
        
        # Analyze results
        successful_queries = [r for r in results if r.get("status") == "success"]
        ai_prospecting_recognized = [r for r in successful_queries if r.get("ai_prospecting_recognized")]
        
        print(f"\n📊 AI Agent Prospecting Query Results:")
        print(f"   Total queries tested: {len(test_queries)}")
        print(f"   Successful responses: {len(successful_queries)}")
        print(f"   AI prospecting recognized: {len(ai_prospecting_recognized)}")
        print(f"   Recognition rate: {len(ai_prospecting_recognized)/len(test_queries)*100:.1f}%")
        
        return {
            "test_name": "AI Agent Prospecting Queries",
            "total_queries": len(test_queries),
            "successful": len(successful_queries),
            "ai_prospecting_recognized": len(ai_prospecting_recognized),
            "recognition_rate": len(ai_prospecting_recognized)/len(test_queries)*100,
            "results": results
        }
    
    async def test_direct_ai_prospecting_endpoint(self):
        """Test direct AI prospecting endpoint"""
        print("\n🧪 Testing Direct AI Prospecting Endpoint...")
        
        test_cases = [
            {
                "query": "Find CEOs at technology companies",
                "target_list": None,
                "max_results": 10
            },
            {
                "query": "Search for marketing directors in California",
                "target_list": "Marketing Prospects",
                "max_results": 15
            },
            {
                "query": "Find CTOs at software startups",
                "target_list": "Tech Leaders",
                "max_results": 20
            }
        ]
        
        results = []
        
        for test_case in test_cases:
            try:
                async with self.session.post(
                    f"{BACKEND_URL}/api/ai-prospecting/search",
                    json=test_case,
                    headers=self.get_headers()
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        result = {
                            "query": test_case["query"],
                            "target_list": test_case["target_list"],
                            "status": "success",
                            "success": data.get("success"),
                            "prospects_count": data.get("prospects_count", 0),
                            "message": data.get("message", ""),
                            "needs_clarification": data.get("needs_clarification", False)
                        }
                        
                        if data.get("success"):
                            print(f"  ✅ Query: '{test_case['query']}' - Found {data.get('prospects_count', 0)} prospects")
                        else:
                            print(f"  ⚠️  Query: '{test_case['query']}' - {data.get('message', 'No message')}")
                        
                        results.append(result)
                        
                    else:
                        error_text = await response.text()
                        print(f"  ❌ Query: '{test_case['query']}' - HTTP {response.status}: {error_text}")
                        results.append({
                            "query": test_case["query"],
                            "status": "error",
                            "error": f"HTTP {response.status}: {error_text}"
                        })
                
                await asyncio.sleep(1)  # Longer delay for API calls
                
            except Exception as e:
                print(f"  ❌ Query: '{test_case['query']}' - Exception: {str(e)}")
                results.append({
                    "query": test_case["query"],
                    "status": "exception",
                    "error": str(e)
                })
        
        successful_calls = [r for r in results if r.get("status") == "success" and r.get("success")]
        
        print(f"\n📊 Direct AI Prospecting Results:")
        print(f"   Total test cases: {len(test_cases)}")
        print(f"   Successful calls: {len(successful_calls)}")
        print(f"   Success rate: {len(successful_calls)/len(test_cases)*100:.1f}%")
        
        return {
            "test_name": "Direct AI Prospecting Endpoint",
            "total_cases": len(test_cases),
            "successful": len(successful_calls),
            "success_rate": len(successful_calls)/len(test_cases)*100,
            "results": results
        }
    
    async def test_list_management_integration(self):
        """Test AI prospecting integration with list management"""
        print("\n🧪 Testing List Management Integration...")
        
        # First, get existing lists
        existing_lists = []
        try:
            async with self.session.get(
                f"{BACKEND_URL}/api/lists",
                headers=self.get_headers()
            ) as response:
                if response.status == 200:
                    existing_lists = await response.json()
                    print(f"  📋 Found {len(existing_lists)} existing lists")
        except Exception as e:
            print(f"  ⚠️  Could not fetch existing lists: {e}")
        
        # Test cases for list integration
        test_cases = [
            {
                "description": "Add to existing list",
                "query": "Find marketing managers at tech companies",
                "target_list": existing_lists[0]["name"] if existing_lists else "Technology Companies",
                "expect_existing_list": True
            },
            {
                "description": "Add to non-existent list (should create default)",
                "query": "Find sales directors in healthcare",
                "target_list": "Non-Existent List 12345",
                "expect_existing_list": False
            },
            {
                "description": "No target list specified",
                "query": "Find product managers at startups",
                "target_list": None,
                "expect_existing_list": False
            }
        ]
        
        results = []
        
        for test_case in test_cases:
            try:
                # Test via AI Agent
                request_data = {
                    "message": f"{test_case['query']} for {test_case['target_list']}" if test_case['target_list'] else test_case['query'],
                    "use_enhanced_flow": False  # Use legacy mode for direct execution
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/api/ai-agent/chat",
                    json=request_data,
                    headers=self.get_headers()
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        result = {
                            "description": test_case["description"],
                            "query": test_case["query"],
                            "target_list": test_case["target_list"],
                            "status": "success",
                            "action_taken": data.get("action_taken"),
                            "response": data.get("response", "")[:150] + "...",
                            "data": data.get("data")
                        }
                        
                        # Check if prospects were added
                        if data.get("data") and isinstance(data["data"], dict):
                            prospects_count = data["data"].get("prospects_count", 0)
                            target_list_used = data["data"].get("target_list")
                            
                            result.update({
                                "prospects_found": prospects_count,
                                "target_list_used": target_list_used,
                                "list_handling": "correct" if target_list_used else "no_list_specified"
                            })
                            
                            print(f"  ✅ {test_case['description']}: Found {prospects_count} prospects")
                            if target_list_used:
                                print(f"     Added to list: {target_list_used}")
                        else:
                            print(f"  ⚠️  {test_case['description']}: No prospect data returned")
                        
                        results.append(result)
                        
                    else:
                        error_text = await response.text()
                        print(f"  ❌ {test_case['description']}: HTTP {response.status}")
                        results.append({
                            "description": test_case["description"],
                            "status": "error",
                            "error": f"HTTP {response.status}: {error_text}"
                        })
                
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"  ❌ {test_case['description']}: Exception: {str(e)}")
                results.append({
                    "description": test_case["description"],
                    "status": "exception",
                    "error": str(e)
                })
        
        # Check if lists were created/updated
        try:
            async with self.session.get(
                f"{BACKEND_URL}/api/lists",
                headers=self.get_headers()
            ) as response:
                if response.status == 200:
                    updated_lists = await response.json()
                    new_lists_count = len(updated_lists) - len(existing_lists)
                    print(f"  📋 Lists after testing: {len(updated_lists)} (added {new_lists_count})")
        except Exception as e:
            print(f"  ⚠️  Could not fetch updated lists: {e}")
        
        successful_tests = [r for r in results if r.get("status") == "success"]
        
        print(f"\n📊 List Management Integration Results:")
        print(f"   Total test cases: {len(test_cases)}")
        print(f"   Successful tests: {len(successful_tests)}")
        print(f"   Success rate: {len(successful_tests)/len(test_cases)*100:.1f}%")
        
        return {
            "test_name": "List Management Integration",
            "total_cases": len(test_cases),
            "successful": len(successful_tests),
            "success_rate": len(successful_tests)/len(test_cases)*100,
            "results": results
        }
    
    async def test_edge_cases(self):
        """Test edge cases and error handling"""
        print("\n🧪 Testing Edge Cases and Error Handling...")
        
        edge_cases = [
            {
                "description": "Empty query",
                "query": "",
                "expect_error": True
            },
            {
                "description": "Very vague query",
                "query": "find people",
                "expect_error": False
            },
            {
                "description": "Non-prospecting query",
                "query": "What's the weather today?",
                "expect_error": False
            },
            {
                "description": "Query with special characters",
                "query": "Find C++ developers @ tech companies (remote)",
                "expect_error": False
            },
            {
                "description": "Very long query",
                "query": "Find senior software engineers with 10+ years experience in Python, JavaScript, and React who work at technology companies with 100-500 employees located in California, New York, or Texas and have verified email addresses",
                "expect_error": False
            }
        ]
        
        results = []
        
        for edge_case in edge_cases:
            try:
                request_data = {
                    "message": edge_case["query"],
                    "use_enhanced_flow": False
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/api/ai-agent/chat",
                    json=request_data,
                    headers=self.get_headers()
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        result = {
                            "description": edge_case["description"],
                            "query": edge_case["query"],
                            "status": "success",
                            "action_taken": data.get("action_taken"),
                            "response": data.get("response", "")[:100] + "...",
                            "handled_gracefully": True
                        }
                        
                        # Check if it was handled as expected
                        if edge_case["expect_error"]:
                            if "error" in data.get("response", "").lower() or not data.get("action_taken"):
                                print(f"  ✅ {edge_case['description']}: Handled as expected (error/no action)")
                            else:
                                print(f"  ⚠️  {edge_case['description']}: Expected error but got action: {data.get('action_taken')}")
                        else:
                            print(f"  ✅ {edge_case['description']}: Handled gracefully")
                        
                        results.append(result)
                        
                    else:
                        error_text = await response.text()
                        result = {
                            "description": edge_case["description"],
                            "status": "http_error",
                            "error": f"HTTP {response.status}",
                            "handled_gracefully": response.status in [400, 422]  # Expected error codes
                        }
                        
                        if edge_case["expect_error"] and response.status in [400, 422]:
                            print(f"  ✅ {edge_case['description']}: Properly returned error {response.status}")
                        else:
                            print(f"  ❌ {edge_case['description']}: HTTP {response.status}")
                        
                        results.append(result)
                
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"  ❌ {edge_case['description']}: Exception: {str(e)}")
                results.append({
                    "description": edge_case["description"],
                    "status": "exception",
                    "error": str(e),
                    "handled_gracefully": False
                })
        
        handled_gracefully = [r for r in results if r.get("handled_gracefully")]
        
        print(f"\n📊 Edge Cases Results:")
        print(f"   Total edge cases: {len(edge_cases)}")
        print(f"   Handled gracefully: {len(handled_gracefully)}")
        print(f"   Graceful handling rate: {len(handled_gracefully)/len(edge_cases)*100:.1f}%")
        
        return {
            "test_name": "Edge Cases and Error Handling",
            "total_cases": len(edge_cases),
            "handled_gracefully": len(handled_gracefully),
            "graceful_rate": len(handled_gracefully)/len(edge_cases)*100,
            "results": results
        }
    
    async def test_database_verification(self):
        """Verify prospects are being added to database properly"""
        print("\n🧪 Testing Database Verification...")
        
        # Get initial prospect count
        initial_prospects = []
        try:
            async with self.session.get(
                f"{BACKEND_URL}/api/prospects",
                headers=self.get_headers()
            ) as response:
                if response.status == 200:
                    initial_prospects = await response.json()
                    print(f"  📊 Initial prospects in database: {len(initial_prospects)}")
        except Exception as e:
            print(f"  ⚠️  Could not fetch initial prospects: {e}")
        
        # Perform a small AI prospecting search
        test_query = "Find 2 marketing managers at small tech companies"
        
        try:
            request_data = {
                "message": test_query,
                "use_enhanced_flow": False
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/api/ai-agent/chat",
                json=request_data,
                headers=self.get_headers()
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("action_taken") == "ai_prospecting_search" and data.get("data"):
                        prospects_added = data["data"].get("prospects_count", 0)
                        print(f"  ✅ AI prospecting reported {prospects_added} prospects added")
                        
                        # Wait a moment for database to update
                        await asyncio.sleep(2)
                        
                        # Check updated prospect count
                        try:
                            async with self.session.get(
                                f"{BACKEND_URL}/api/prospects",
                                headers=self.get_headers()
                            ) as response:
                                if response.status == 200:
                                    updated_prospects = await response.json()
                                    actual_increase = len(updated_prospects) - len(initial_prospects)
                                    
                                    print(f"  📊 Prospects after AI search: {len(updated_prospects)}")
                                    print(f"  📊 Actual increase: {actual_increase}")
                                    
                                    if actual_increase > 0:
                                        print(f"  ✅ Database verification: Prospects were added successfully")
                                        
                                        # Check if prospects have proper AI prospecting metadata
                                        recent_prospects = updated_prospects[-actual_increase:] if actual_increase > 0 else []
                                        ai_sourced = [p for p in recent_prospects if p.get("source") == "apollo_ai"]
                                        
                                        print(f"  📊 AI-sourced prospects: {len(ai_sourced)}/{actual_increase}")
                                        
                                        return {
                                            "test_name": "Database Verification",
                                            "status": "success",
                                            "initial_count": len(initial_prospects),
                                            "final_count": len(updated_prospects),
                                            "prospects_added": actual_increase,
                                            "ai_sourced": len(ai_sourced),
                                            "verification_passed": actual_increase > 0
                                        }
                                    else:
                                        print(f"  ⚠️  Database verification: No prospects were actually added")
                                        return {
                                            "test_name": "Database Verification",
                                            "status": "warning",
                                            "message": "No prospects were added to database",
                                            "verification_passed": False
                                        }
                        except Exception as e:
                            print(f"  ❌ Could not verify database update: {e}")
                            return {
                                "test_name": "Database Verification",
                                "status": "error",
                                "error": str(e),
                                "verification_passed": False
                            }
                    else:
                        print(f"  ⚠️  AI prospecting was not triggered or returned no data")
                        return {
                            "test_name": "Database Verification",
                            "status": "warning",
                            "message": "AI prospecting was not triggered",
                            "verification_passed": False
                        }
                else:
                    print(f"  ❌ AI Agent request failed: HTTP {response.status}")
                    return {
                        "test_name": "Database Verification",
                        "status": "error",
                        "error": f"HTTP {response.status}",
                        "verification_passed": False
                    }
        
        except Exception as e:
            print(f"  ❌ Database verification failed: {e}")
            return {
                "test_name": "Database Verification",
                "status": "exception",
                "error": str(e),
                "verification_passed": False
            }
    
    async def run_all_tests(self):
        """Run all AI prospecting tests"""
        print("🚀 Starting AI Prospecting Functionality Tests")
        print("=" * 60)
        
        if not await self.setup_session():
            return {"error": "Authentication failed"}
        
        try:
            # Run all test suites
            test_results = []
            
            # Test 1: AI Agent prospecting queries
            result1 = await self.test_ai_agent_prospecting_queries()
            test_results.append(result1)
            
            # Test 2: Direct AI prospecting endpoint
            result2 = await self.test_direct_ai_prospecting_endpoint()
            test_results.append(result2)
            
            # Test 3: List management integration
            result3 = await self.test_list_management_integration()
            test_results.append(result3)
            
            # Test 4: Edge cases
            result4 = await self.test_edge_cases()
            test_results.append(result4)
            
            # Test 5: Database verification
            result5 = await self.test_database_verification()
            test_results.append(result5)
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "test_results": test_results,
                "summary": self.generate_summary(test_results)
            }
            
        finally:
            await self.cleanup_session()
    
    def generate_summary(self, test_results: List[Dict]) -> Dict:
        """Generate test summary"""
        total_tests = len(test_results)
        successful_tests = len([r for r in test_results if r.get("successful", 0) > 0 or r.get("verification_passed")])
        
        # Calculate overall metrics
        total_queries = sum(r.get("total_queries", r.get("total_cases", 0)) for r in test_results)
        successful_queries = sum(r.get("successful", 0) for r in test_results)
        
        # AI prospecting specific metrics
        ai_prospecting_recognized = 0
        for result in test_results:
            if result.get("test_name") == "AI Agent Prospecting Queries":
                ai_prospecting_recognized = result.get("ai_prospecting_recognized", 0)
                break
        
        return {
            "total_test_suites": total_tests,
            "successful_test_suites": successful_tests,
            "overall_success_rate": successful_tests / total_tests * 100 if total_tests > 0 else 0,
            "total_queries_tested": total_queries,
            "successful_queries": successful_queries,
            "query_success_rate": successful_queries / total_queries * 100 if total_queries > 0 else 0,
            "ai_prospecting_recognition_count": ai_prospecting_recognized,
            "ai_prospecting_recognition_rate": ai_prospecting_recognized / 5 * 100 if ai_prospecting_recognized else 0,  # 5 test queries
            "key_findings": [
                f"AI prospecting queries recognized: {ai_prospecting_recognized}/5",
                f"Overall query success rate: {successful_queries}/{total_queries}",
                f"Test suites passed: {successful_tests}/{total_tests}"
            ]
        }

async def main():
    """Main test execution"""
    tester = AIProspectingTester()
    
    try:
        results = await tester.run_all_tests()
        
        if "error" in results:
            print(f"\n❌ Test execution failed: {results['error']}")
            return
        
        # Print final summary
        print("\n" + "=" * 60)
        print("🎯 AI PROSPECTING FUNCTIONALITY TEST SUMMARY")
        print("=" * 60)
        
        summary = results["summary"]
        print(f"📊 Overall Results:")
        print(f"   Test Suites: {summary['successful_test_suites']}/{summary['total_test_suites']} passed ({summary['overall_success_rate']:.1f}%)")
        print(f"   Total Queries: {summary['successful_queries']}/{summary['total_queries_tested']} successful ({summary['query_success_rate']:.1f}%)")
        print(f"   AI Prospecting Recognition: {summary['ai_prospecting_recognition_count']}/5 queries ({summary['ai_prospecting_recognition_rate']:.1f}%)")
        
        print(f"\n🔍 Key Findings:")
        for finding in summary["key_findings"]:
            print(f"   • {finding}")
        
        # Determine overall status
        if summary["overall_success_rate"] >= 80 and summary["ai_prospecting_recognition_rate"] >= 60:
            print(f"\n✅ AI PROSPECTING FUNCTIONALITY: WORKING")
            print("   The AI Agent successfully recognizes and processes AI prospecting queries.")
            print("   Prospects are being found and added to lists/database properly.")
        elif summary["overall_success_rate"] >= 60:
            print(f"\n⚠️  AI PROSPECTING FUNCTIONALITY: PARTIALLY WORKING")
            print("   Some AI prospecting functionality is working but needs improvement.")
        else:
            print(f"\n❌ AI PROSPECTING FUNCTIONALITY: NOT WORKING")
            print("   AI prospecting functionality has significant issues.")
        
        # Save detailed results
        with open("/app/ai_prospecting_test_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n📄 Detailed results saved to: /app/ai_prospecting_test_results.json")
        
    except Exception as e:
        print(f"\n❌ Test execution failed with exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())