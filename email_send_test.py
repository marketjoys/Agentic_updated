#!/usr/bin/env python3
"""
Simple test for email sending functionality
"""

import requests
import json

BACKEND_URL = "https://f8668367-46b0-4e7a-833d-996816e709b0.preview.emergentagent.com"

def test_email_sending():
    # Authenticate
    login_data = {"username": "testuser", "password": "testpass123"}
    response = requests.post(f"{BACKEND_URL}/api/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"❌ Authentication failed: {response.status_code}")
        return
    
    auth_token = response.json().get('access_token')
    headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
    
    # Get email providers
    response = requests.get(f"{BACKEND_URL}/api/email-providers", headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to get email providers: {response.status_code}")
        return
    
    providers = response.json()
    print(f"✅ Found {len(providers)} email providers")
    for provider in providers:
        print(f"   - {provider['name']} (ID: {provider['id']}, Default: {provider.get('is_default', False)})")
    
    if not providers:
        print("❌ No email providers available")
        return
    
    # Use the first provider
    provider_id = providers[0]['id']
    
    # Get campaigns
    response = requests.get(f"{BACKEND_URL}/api/campaigns", headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to get campaigns: {response.status_code}")
        return
    
    campaigns = response.json()
    print(f"✅ Found {len(campaigns)} campaigns")
    
    if not campaigns:
        print("❌ No campaigns available")
        return
    
    # Use the first campaign
    campaign_id = campaigns[0]['id']
    print(f"✅ Testing email sending for campaign: {campaign_id}")
    
    # Test email sending
    send_request = {
        "send_immediately": True,
        "email_provider_id": provider_id,
        "max_emails": 3,
        "schedule_type": "immediate",
        "start_time": None,
        "follow_up_enabled": False,
        "follow_up_intervals": [],
        "follow_up_templates": []
    }
    
    response = requests.post(f"{BACKEND_URL}/api/campaigns/{campaign_id}/send", 
                           json=send_request, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Email sending successful!")
        print(f"   Total sent: {result.get('total_sent', 0)}")
        print(f"   Total failed: {result.get('total_failed', 0)}")
        print(f"   Message: {result.get('message', 'No message')}")
    else:
        print(f"❌ Email sending failed: {response.status_code}")
        print(f"   Response: {response.text}")

if __name__ == "__main__":
    test_email_sending()