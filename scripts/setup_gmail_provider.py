#!/usr/bin/env python3
"""
Setup script to add real Gmail provider to the database
"""

import asyncio
import os
from datetime import datetime
from app.services.database import db_service
from app.utils.helpers import generate_id

async def setup_gmail_provider():
    """Setup Gmail provider with real credentials"""
    try:
        # Connect to database
        await db_service.connect()
        
        # Clear existing providers to avoid duplicates
        await db_service.db.email_providers.delete_many({})
        
        # Gmail provider configuration
        gmail_provider = {
            "id": generate_id(),
            "name": "Gmail Provider",
            "provider_type": "gmail",
            "email_address": "kasargovinda@gmail.com",
            "display_name": "Kasargovinda",
            "smtp_host": "smtp.gmail.com",
            "smtp_port": 587,
            "smtp_username": "kasargovinda@gmail.com",
            "smtp_password": "urvsdfvrzfabvykm",
            "smtp_use_tls": True,
            "imap_host": "imap.gmail.com",
            "imap_port": 993,
            "imap_username": "kasargovinda@gmail.com",
            "imap_password": "urvsdfvrzfabvykm",
            "daily_send_limit": 500,
            "hourly_send_limit": 50,
            "is_default": True,
            "is_active": True,
            "skip_connection_test": False,  # Enable real connection testing
            "current_daily_count": 0,
            "current_hourly_count": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_sync": datetime.utcnow()
        }
        
        # Insert Gmail provider
        result = await db_service.create_email_provider(gmail_provider)
        
        if result:
            print(f"✅ Gmail provider created successfully with ID: {gmail_provider['id']}")
            print(f"📧 Email: {gmail_provider['email_address']}")
            print(f"🔧 SMTP: {gmail_provider['smtp_host']}:{gmail_provider['smtp_port']}")
            print(f"📬 IMAP: {gmail_provider['imap_host']}:{gmail_provider['imap_port']}")
            print(f"⚡ Daily limit: {gmail_provider['daily_send_limit']}")
            print(f"⏱️ Hourly limit: {gmail_provider['hourly_send_limit']}")
            print(f"🔒 TLS enabled: {gmail_provider['smtp_use_tls']}")
        else:
            print("❌ Failed to create Gmail provider")
            
    except Exception as e:
        print(f"❌ Error setting up Gmail provider: {str(e)}")
        
    finally:
        # Disconnect from database
        await db_service.disconnect()

if __name__ == "__main__":
    print("🚀 Setting up Gmail provider...")
    asyncio.run(setup_gmail_provider())