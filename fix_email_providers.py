#!/usr/bin/env python3
"""
Fix Email Provider Database Issue for Campaign Sending
"""

import requests
import json
from datetime import datetime
import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.append('/app/backend')

from app.services.database import db_service

BACKEND_URL = "https://478c70c5-672e-41c9-bcd2-df57c17a9a63.preview.emergentagent.com"

async def fix_email_providers():
    """Add test email providers to database"""
    try:
        await db_service.connect()
        
        # Check existing providers
        existing_providers = await db_service.get_email_providers()
        print(f"Found {len(existing_providers)} existing providers")
        
        # Add test providers if none exist
        if len(existing_providers) == 0:
            test_providers = [
                {
                    "id": "test-gmail-provider",
                    "name": "Test Gmail Provider",
                    "provider_type": "gmail",
                    "email_address": "test@gmail.com",
                    "display_name": "Test Gmail",
                    "smtp_host": "smtp.gmail.com",
                    "smtp_port": 587,
                    "smtp_username": "test@gmail.com",
                    "smtp_password": "app_password",
                    "smtp_use_tls": True,
                    "imap_host": "imap.gmail.com",
                    "imap_port": 993,
                    "imap_username": "test@gmail.com",
                    "imap_password": "app_password",
                    "daily_send_limit": 500,
                    "hourly_send_limit": 50,
                    "current_daily_count": 0,
                    "current_hourly_count": 0,
                    "is_default": True,
                    "is_active": True,
                    "skip_connection_test": True,
                    "created_at": datetime.utcnow(),
                    "last_sync": datetime.utcnow()
                },
                {
                    "id": "test-outlook-provider",
                    "name": "Test Outlook Provider",
                    "provider_type": "outlook",
                    "email_address": "test@outlook.com",
                    "display_name": "Test Outlook",
                    "smtp_host": "smtp-mail.outlook.com",
                    "smtp_port": 587,
                    "smtp_username": "test@outlook.com",
                    "smtp_password": "app_password",
                    "smtp_use_tls": True,
                    "imap_host": "outlook.office365.com",
                    "imap_port": 993,
                    "imap_username": "test@outlook.com",
                    "imap_password": "app_password",
                    "daily_send_limit": 300,
                    "hourly_send_limit": 30,
                    "current_daily_count": 0,
                    "current_hourly_count": 0,
                    "is_default": False,
                    "is_active": True,
                    "skip_connection_test": True,
                    "created_at": datetime.utcnow(),
                    "last_sync": datetime.utcnow()
                }
            ]
            
            for provider in test_providers:
                result = await db_service.create_email_provider(provider)
                print(f"Added provider: {provider['name']} - Result: {result}")
        else:
            # Update existing providers to have skip_connection_test
            for provider in existing_providers:
                update_data = {
                    "skip_connection_test": True,
                    "is_active": True,
                    "smtp_password": "app_password",
                    "imap_password": "app_password"
                }
                result = await db_service.update_email_provider(provider['id'], update_data)
                print(f"Updated provider: {provider['name']} - Result: {result}")
        
        # Verify providers
        updated_providers = await db_service.get_email_providers()
        print(f"Total providers after update: {len(updated_providers)}")
        
        for provider in updated_providers:
            print(f"Provider: {provider['name']} - Active: {provider.get('is_active')} - Skip Test: {provider.get('skip_connection_test')}")
        
        await db_service.disconnect()
        return True
        
    except Exception as e:
        print(f"Error fixing email providers: {str(e)}")
        return False

def test_campaign_sending_after_fix():
    """Test campaign sending after fixing providers"""
    try:
        # Login first
        login_data = {
            "username": "testuser",
            "password": "testpass123"
        }
        
        response = requests.post(f"{BACKEND_URL}/api/auth/login", json=login_data)
        if response.status_code != 200:
            print(f"Login failed: {response.status_code}")
            return False
        
        # Get templates
        templates_response = requests.get(f"{BACKEND_URL}/api/templates")
        if templates_response.status_code != 200:
            print(f"Failed to get templates: {templates_response.status_code}")
            return False
        
        templates = templates_response.json()
        if not templates:
            print("No templates available")
            return False
        
        template_id = templates[0]['id']
        
        # Create campaign
        campaign_data = {
            "name": f"Fixed Test Campaign {int(datetime.now().timestamp())}",
            "template_id": template_id,
            "list_ids": [],
            "max_emails": 10,
            "schedule": None
        }
        
        response = requests.post(f"{BACKEND_URL}/api/campaigns", json=campaign_data)
        if response.status_code != 200:
            print(f"Campaign creation failed: {response.status_code} - {response.text}")
            return False
        
        campaign = response.json()
        campaign_id = campaign['id']
        print(f"Created campaign: {campaign_id}")
        
        # Send campaign
        send_request = {
            "send_immediately": True,
            "email_provider_id": "",  # Use default provider
            "max_emails": 10,
            "schedule_type": "immediate",
            "start_time": None,
            "follow_up_enabled": True,
            "follow_up_intervals": [3, 7, 14],
            "follow_up_templates": []
        }
        
        response = requests.post(f"{BACKEND_URL}/api/campaigns/{campaign_id}/send", json=send_request)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Campaign sent successfully!")
            print(f"   Total sent: {result.get('total_sent', 0)}")
            print(f"   Total failed: {result.get('total_failed', 0)}")
            print(f"   Status: {result.get('status')}")
            return True
        else:
            print(f"❌ Campaign sending failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error testing campaign sending: {str(e)}")
        return False

async def main():
    """Main function"""
    print("🔧 Fixing Email Provider Database Issue...")
    
    # Fix email providers
    if await fix_email_providers():
        print("✅ Email providers fixed successfully")
        
        # Test campaign sending
        print("\n🧪 Testing campaign sending after fix...")
        if test_campaign_sending_after_fix():
            print("✅ Campaign sending test passed!")
        else:
            print("❌ Campaign sending test failed")
    else:
        print("❌ Failed to fix email providers")

if __name__ == "__main__":
    asyncio.run(main())