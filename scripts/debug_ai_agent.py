#!/usr/bin/env python3
"""
Debug AI Agent Parameter Extraction
Testing the specific parameter extraction patterns to identify the issue
"""

import requests
import json
from datetime import datetime

# Get backend URL from frontend .env file
BACKEND_URL = "https://ae48834a-85ee-471e-b115-ca275e953d9f.preview.emergentagent.com"

def test_single_command(message, expected_name):
    """Test a single command and show detailed extraction results"""
    print(f"\n🧪 Testing: '{message}'")
    print(f"Expected: '{expected_name}'")
    
    try:
        # Authenticate
        login_data = {"username": "testuser", "password": "testpass123"}
        response = requests.post(f"{BACKEND_URL}/api/auth/login", json=login_data)
        
        if response.status_code != 200:
            print(f"❌ Authentication failed: {response.status_code}")
            return
        
        auth_result = response.json()
        headers = {"Authorization": f"Bearer {auth_result['access_token']}"}
        
        # Send chat request
        chat_request = {
            "message": message,
            "context": {
                "user_id": "testuser",
                "session_id": f"debug_session_{int(datetime.now().timestamp())}"
            }
        }
        
        response = requests.post(f"{BACKEND_URL}/api/ai-agent/chat", json=chat_request, headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Chat request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return
        
        chat_response = response.json()
        
        print(f"✅ Response received")
        print(f"Action taken: {chat_response.get('action_taken', 'None')}")
        print(f"Response text: {chat_response.get('response', 'None')}")
        
        if 'data' in chat_response and chat_response['data']:
            data = chat_response['data']
            print(f"Data returned: {json.dumps(data, indent=2, default=str)}")
            
            # Check extracted name
            extracted_name = data.get('name', 'Not found')
            print(f"Extracted name: '{extracted_name}'")
            
            if expected_name in extracted_name:
                print("✅ Name extraction: CORRECT")
            else:
                print("❌ Name extraction: INCORRECT")
                print(f"   Expected: '{expected_name}'")
                print(f"   Got: '{extracted_name}'")
        else:
            print("❌ No data returned")
        
        # Clean up if resource was created
        if 'data' in chat_response and chat_response['data'] and 'id' in chat_response['data']:
            resource_id = chat_response['data']['id']
            if 'list' in message.lower():
                cleanup_response = requests.delete(f"{BACKEND_URL}/api/lists/{resource_id}", headers=headers)
                print(f"🧹 Cleanup: {'✅' if cleanup_response.status_code == 200 else '❌'}")
            elif 'prospect' in message.lower():
                cleanup_response = requests.delete(f"{BACKEND_URL}/api/prospects/{resource_id}", headers=headers)
                print(f"🧹 Cleanup: {'✅' if cleanup_response.status_code == 200 else '❌'}")
        
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

def main():
    """Test specific commands that are failing"""
    print("🔍 AI Agent Parameter Extraction Debug")
    print("=" * 60)
    
    # Test list creation commands
    test_single_command("Create a new list called Test Marketing List", "Test Marketing List")
    test_single_command("Make a new list named VIP Customers", "VIP Customers")
    test_single_command("Add a list called Technology Companies", "Technology Companies")
    
    # Test prospect creation commands
    test_single_command("Add prospect Mike Davis at DataScience AI", "Mike Davis")

if __name__ == "__main__":
    main()