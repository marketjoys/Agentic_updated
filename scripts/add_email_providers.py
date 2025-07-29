#!/usr/bin/env python3
"""
Add email providers to database
"""

import asyncio
import sys
import os
sys.path.append('/app/backend')

from app.services.database import db_service
from datetime import datetime

async def add_email_providers():
    """Add email providers to database"""
    try:
        await db_service.connect()
        
        # Check if providers already exist
        existing_providers = await db_service.get_email_providers()
        if len(existing_providers) > 0:
            print(f"✅ Found {len(existing_providers)} existing email providers")
            for provider in existing_providers:
                print(f"   - {provider['name']} (ID: {provider['id']})")
            return
        
        # Add email providers
        providers = [
            {
                "id": "1",
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
                "updated_at": datetime.utcnow(),
                "last_sync": datetime.utcnow()
            },
            {
                "id": "2",
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
                "updated_at": datetime.utcnow(),
                "last_sync": datetime.utcnow()
            }
        ]
        
        for provider in providers:
            result = await db_service.create_email_provider(provider)
            if result:
                print(f"✅ Added email provider: {provider['name']}")
            else:
                print(f"❌ Failed to add email provider: {provider['name']}")
        
        print("✅ Email providers setup complete!")
        
    except Exception as e:
        print(f"❌ Error adding email providers: {str(e)}")

if __name__ == "__main__":
    asyncio.run(add_email_providers())