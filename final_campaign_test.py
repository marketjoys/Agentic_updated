#!/usr/bin/env python3
"""
Final Campaign Sending Verification Test
"""

import requests
import json
from datetime import datetime
import time

BACKEND_URL = "https://6e3b97c7-cc8d-4c39-9c3f-1f7dfaa69da3.preview.emergentagent.com"

def test_campaign_sending_functionality():
    """Test the complete campaign sending workflow"""
    print("🚀 Final Campaign Sending Functionality Test")
    print("=" * 60)
    
    try:
        # 1. Authentication
        print("\n1. Testing Authentication...")
        login_data = {
            "username": "testuser",
            "password": "testpass123"
        }
        
        response = requests.post(f"{BACKEND_URL}/api/auth/login", json=login_data)
        if response.status_code != 200:
            print(f"❌ Authentication failed: {response.status_code}")
            return False
        
        print("✅ Authentication successful")
        
        # 2. Check Email Providers
        print("\n2. Checking Email Providers...")
        response = requests.get(f"{BACKEND_URL}/api/email-providers")
        if response.status_code != 200:
            print(f"❌ Failed to get email providers: {response.status_code}")
            return False
        
        providers = response.json()
        active_providers = [p for p in providers if p.get('is_active', False)]
        default_providers = [p for p in providers if p.get('is_default', False)]
        
        print(f"✅ Found {len(providers)} providers, {len(active_providers)} active, {len(default_providers)} default")
        
        # 3. Check Templates
        print("\n3. Checking Templates...")
        response = requests.get(f"{BACKEND_URL}/api/templates")
        if response.status_code != 200:
            print(f"❌ Failed to get templates: {response.status_code}")
            return False
        
        templates = response.json()
        print(f"✅ Found {len(templates)} templates")
        
        # 4. Check Prospects
        print("\n4. Checking Prospects...")
        response = requests.get(f"{BACKEND_URL}/api/prospects")
        if response.status_code != 200:
            print(f"❌ Failed to get prospects: {response.status_code}")
            return False
        
        prospects = response.json()
        print(f"✅ Found {len(prospects)} prospects")
        
        # 5. Create Campaign
        print("\n5. Creating Campaign...")
        campaign_data = {
            "name": f"Final Test Campaign {int(time.time())}",
            "template_id": templates[0]['id'],
            "list_ids": [],
            "max_emails": 5,
            "schedule": None
        }
        
        response = requests.post(f"{BACKEND_URL}/api/campaigns", json=campaign_data)
        if response.status_code != 200:
            print(f"❌ Campaign creation failed: {response.status_code} - {response.text}")
            return False
        
        campaign = response.json()
        campaign_id = campaign['id']
        print(f"✅ Campaign created with ID: {campaign_id}")
        
        # 6. Send Campaign (CRITICAL TEST)
        print("\n6. Sending Campaign (CRITICAL)...")
        send_request = {
            "send_immediately": True,
            "email_provider_id": "",  # Use default provider
            "max_emails": 5,
            "schedule_type": "immediate",
            "start_time": None,
            "follow_up_enabled": False,
            "follow_up_intervals": [],
            "follow_up_templates": []
        }
        
        response = requests.post(f"{BACKEND_URL}/api/campaigns/{campaign_id}/send", json=send_request)
        if response.status_code != 200:
            print(f"❌ Campaign sending failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
        
        result = response.json()
        total_sent = result.get('total_sent', 0)
        total_failed = result.get('total_failed', 0)
        
        if total_sent > 0:
            print(f"✅ Campaign sent successfully!")
            print(f"   📧 Emails sent: {total_sent}")
            print(f"   ❌ Emails failed: {total_failed}")
            print(f"   📊 Status: {result.get('status')}")
        else:
            print(f"❌ No emails were sent")
            print(f"   Details: {result}")
            return False
        
        # 7. Check Campaign Status
        print("\n7. Checking Campaign Status...")
        response = requests.get(f"{BACKEND_URL}/api/campaigns/{campaign_id}/status")
        if response.status_code != 200:
            print(f"❌ Failed to get campaign status: {response.status_code}")
            return False
        
        status = response.json()
        print(f"✅ Campaign status: {status.get('status')}")
        print(f"   📧 Total sent: {status.get('total_sent')}")
        print(f"   ❌ Total failed: {status.get('total_failed')}")
        
        # 8. Check Analytics
        print("\n8. Checking Analytics...")
        response = requests.get(f"{BACKEND_URL}/api/analytics")
        if response.status_code != 200:
            print(f"❌ Failed to get analytics: {response.status_code}")
            return False
        
        analytics = response.json()
        print(f"✅ Analytics retrieved:")
        print(f"   📊 Total campaigns: {analytics.get('total_campaigns')}")
        print(f"   📧 Total emails sent: {analytics.get('total_emails_sent')}")
        print(f"   👥 Total prospects: {analytics.get('total_prospects')}")
        
        # 9. Check Campaign-Specific Analytics
        print("\n9. Checking Campaign Analytics...")
        response = requests.get(f"{BACKEND_URL}/api/analytics/campaign/{campaign_id}")
        if response.status_code != 200:
            print(f"❌ Failed to get campaign analytics: {response.status_code}")
            return False
        
        campaign_analytics = response.json()
        print(f"✅ Campaign analytics:")
        print(f"   📧 Total sent: {campaign_analytics.get('total_sent')}")
        print(f"   📖 Open rate: {campaign_analytics.get('open_rate')}%")
        print(f"   💬 Reply rate: {campaign_analytics.get('reply_rate')}%")
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED - CAMPAIGN SENDING IS FULLY FUNCTIONAL!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with exception: {str(e)}")
        return False

def main():
    """Main function"""
    success = test_campaign_sending_functionality()
    
    if success:
        print("\n✅ FINAL RESULT: Email campaign sending functionality is working correctly")
        print("   - Authentication system operational")
        print("   - Email providers configured and active")
        print("   - Templates and prospects available")
        print("   - Campaign creation working")
        print("   - Email sending successful")
        print("   - Campaign status tracking functional")
        print("   - Analytics system operational")
    else:
        print("\n❌ FINAL RESULT: Issues detected with campaign sending functionality")
    
    return success

if __name__ == "__main__":
    main()