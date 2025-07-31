#!/usr/bin/env python3
"""
Simple AI Prospecting Test - Direct API calls to understand the current state
"""

import asyncio
import aiohttp
import json

BACKEND_URL = "https://6b79b9a6-93ed-4a33-b1a5-f766f54ddce0.preview.emergentagent.com"

async def test_ai_prospecting():
    """Test AI prospecting functionality directly"""
    
    # Login first
    async with aiohttp.ClientSession() as session:
        # Login
        login_data = {"username": "testuser", "password": "testpass123"}
        async with session.post(f"{BACKEND_URL}/api/auth/login", json=login_data) as response:
            if response.status != 200:
                print("❌ Login failed")
                return
            
            data = await response.json()
            auth_token = data.get("access_token")
            headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
            print("✅ Login successful")
        
        # Test 1: Direct AI prospecting endpoint
        print("\n🧪 Testing Direct AI Prospecting Endpoint...")
        test_data = {
            "query": "Find CEOs at technology companies",
            "max_results": 5
        }
        
        async with session.post(f"{BACKEND_URL}/api/ai-prospecting/search", json=test_data, headers=headers) as response:
            print(f"Status: {response.status}")
            data = await response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        
        # Test 2: AI Agent with different queries
        print("\n🧪 Testing AI Agent with Different Queries...")
        
        test_queries = [
            "ai prospecting for CEOs",  # Should match existing pattern
            "find prospects using ai",  # Should match existing pattern  
            "find prospects like CEOs at tech companies",  # Should NOT match (missing pattern)
            "suggest prospects for my campaign"  # Should match existing pattern
        ]
        
        for query in test_queries:
            print(f"\n📝 Testing query: '{query}'")
            request_data = {"message": query, "use_enhanced_flow": False}
            
            async with session.post(f"{BACKEND_URL}/api/ai-agent/chat", json=request_data, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    action = data.get("action_taken", "none")
                    response_text = data.get("response", "")[:100] + "..."
                    print(f"   Action: {action}")
                    print(f"   Response: {response_text}")
                else:
                    print(f"   ❌ HTTP {response.status}")

if __name__ == "__main__":
    asyncio.run(test_ai_prospecting())