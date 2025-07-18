#!/usr/bin/env python3
"""
Script to set up real data for the email responder application.
This script will:
1. Clear existing mock data
2. Set up real Gmail provider with provided credentials
3. Add real prospects (amits.joys@gmail.com, ronsmith.joys@gmail.com)
4. Create a real campaign for testing
"""

import asyncio
import os
import sys
from datetime import datetime

# Add the backend directory to the path
sys.path.append('/app/backend')

from app.services.database import db_service
from app.utils.helpers import generate_id

async def clear_existing_data():
    """Clear existing mock data"""
    print("🧹 Clearing existing mock data...")
    
    await db_service.connect()
    
    # Clear collections
    await db_service.db.prospects.delete_many({})
    await db_service.db.campaigns.delete_many({})
    await db_service.db.email_providers.delete_many({})
    await db_service.db.templates.delete_many({})
    await db_service.db.prospect_lists.delete_many({})
    await db_service.db.emails.delete_many({})
    await db_service.db.intents.delete_many({})
    
    print("✅ Cleared all existing data")

async def setup_gmail_provider():
    """Set up real Gmail provider with provided credentials"""
    print("📧 Setting up Gmail provider...")
    
    gmail_provider = {
        "id": generate_id(),
        "name": "Production Gmail Provider",
        "provider_type": "gmail",
        "email_address": "kasargovinda@gmail.com",
        "display_name": "Govinda Kasar",
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
        "skip_connection_test": False,  # We want to test the connection
        "current_daily_count": 0,
        "current_hourly_count": 0,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "last_sync": datetime.utcnow()
    }
    
    result = await db_service.create_email_provider(gmail_provider)
    print(f"✅ Created Gmail provider: {gmail_provider['name']}")
    return gmail_provider

async def setup_real_prospects():
    """Set up real prospects for testing"""
    print("👥 Setting up real prospects...")
    
    real_prospects = [
        {
            "id": generate_id(),
            "email": "amits.joys@gmail.com",
            "first_name": "Amit",
            "last_name": "Joys",
            "company": "Emergent Inc",
            "job_title": "Software Engineer",
            "industry": "Technology",
            "phone": "",
            "status": "active",
            "list_ids": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": generate_id(),
            "email": "ronsmith.joys@gmail.com",
            "first_name": "Ron",
            "last_name": "Smith",
            "company": "Emergent Inc",
            "job_title": "Product Manager",
            "industry": "Technology",
            "phone": "",
            "status": "active",
            "list_ids": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    created_prospects = []
    for prospect in real_prospects:
        result, error = await db_service.create_prospect(prospect)
        if result:
            created_prospects.append(prospect)
            print(f"✅ Created prospect: {prospect['first_name']} {prospect['last_name']} ({prospect['email']})")
        else:
            print(f"❌ Failed to create prospect {prospect['email']}: {error}")
    
    return created_prospects

async def setup_real_templates():
    """Set up real email templates"""
    print("📝 Setting up real email templates...")
    
    templates = [
        {
            "id": generate_id(),
            "name": "Initial Outreach",
            "subject": "Partnership Opportunity with {{company}}",
            "content": """Hi {{first_name}},

I hope this email finds you well! I came across {{company}} and was impressed by your work in the {{industry}} industry.

I'd love to connect and explore potential collaboration opportunities that could benefit both our organizations.

Would you be open to a brief 15-minute call next week to discuss this further?

Best regards,
Govinda Kasar
kasargovinda@gmail.com""",
            "type": "initial",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": generate_id(),
            "name": "Follow-up Email",
            "subject": "Following up - {{company}}",
            "content": """Hi {{first_name}},

I wanted to follow up on my previous email regarding potential collaboration opportunities.

I understand you're likely busy, but I believe there could be significant value in a brief conversation about how we can work together.

Would you have 10-15 minutes available this week for a quick call?

Looking forward to hearing from you.

Best regards,
Govinda Kasar
kasargovinda@gmail.com""",
            "type": "follow_up",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    created_templates = []
    for template in templates:
        result = await db_service.create_template(template)
        if result:
            created_templates.append(template)
            print(f"✅ Created template: {template['name']}")
        else:
            print(f"❌ Failed to create template: {template['name']}")
    
    return created_templates

async def setup_prospect_list(prospects):
    """Set up a prospect list with real prospects"""
    print("📋 Setting up prospect list...")
    
    prospect_list = {
        "id": generate_id(),
        "name": "Real Prospects - Test Campaign",
        "description": "Real prospects for testing email campaign functionality",
        "color": "#3B82F6",
        "prospect_count": len(prospects),
        "tags": ["real", "test", "production"],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await db_service.create_list(prospect_list)
    if result:
        print(f"✅ Created prospect list: {prospect_list['name']}")
        
        # Add prospects to the list
        for prospect in prospects:
            prospect["list_ids"] = [prospect_list["id"]]
            await db_service.update_prospect(prospect["id"], {"list_ids": prospect["list_ids"]})
        
        print(f"✅ Added {len(prospects)} prospects to the list")
        return prospect_list
    else:
        print(f"❌ Failed to create prospect list")
        return None

async def setup_real_campaign(templates, prospect_list, gmail_provider):
    """Set up a real campaign for testing"""
    print("🚀 Setting up real campaign...")
    
    if not templates or not prospect_list:
        print("❌ Cannot create campaign: missing templates or prospect list")
        return None
    
    campaign = {
        "id": generate_id(),
        "name": "Test Campaign - Real Email Integration",
        "template_id": templates[0]["id"],
        "list_ids": [prospect_list["id"]],
        "max_emails": 10,
        "schedule": None,
        "status": "draft",
        "prospect_count": prospect_list["prospect_count"],
        "email_provider_id": gmail_provider["id"],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await db_service.create_campaign(campaign)
    if result:
        print(f"✅ Created campaign: {campaign['name']}")
        return campaign
    else:
        print(f"❌ Failed to create campaign")
        return None

async def setup_intents():
    """Set up basic intents for AI responses"""
    print("🧠 Setting up intents...")
    
    intents = [
        {
            "id": generate_id(),
            "name": "Positive Response",
            "description": "Prospect is interested and wants to learn more",
            "keywords": ["interested", "yes", "tell me more", "sounds good", "let's talk", "sure", "okay"],
            "response_template": "Thank you for your interest! I'll reach out to schedule a call.",
            "confidence_threshold": 0.7,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": generate_id(),
            "name": "Not Interested",
            "description": "Prospect is not interested at this time",
            "keywords": ["not interested", "no thanks", "remove me", "unsubscribe", "not now"],
            "response_template": "Thank you for your time. I'll remove you from our outreach list.",
            "confidence_threshold": 0.8,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    created_intents = []
    for intent in intents:
        result = await db_service.create_intent(intent)
        if result:
            created_intents.append(intent)
            print(f"✅ Created intent: {intent['name']}")
        else:
            print(f"❌ Failed to create intent: {intent['name']}")
    
    return created_intents

async def main():
    """Main function to set up all real data"""
    print("🚀 Setting up real data for email responder application...")
    print("=" * 60)
    
    try:
        # Connect to database
        await db_service.connect()
        
        # Step 1: Clear existing data
        await clear_existing_data()
        
        # Step 2: Set up Gmail provider
        gmail_provider = await setup_gmail_provider()
        
        # Step 3: Set up real prospects
        prospects = await setup_real_prospects()
        
        # Step 4: Set up templates
        templates = await setup_real_templates()
        
        # Step 5: Set up prospect list
        prospect_list = await setup_prospect_list(prospects)
        
        # Step 6: Set up campaign
        campaign = await setup_real_campaign(templates, prospect_list, gmail_provider)
        
        # Step 7: Set up intents
        intents = await setup_intents()
        
        print("\n" + "=" * 60)
        print("🎉 Real data setup completed successfully!")
        print(f"✅ Gmail Provider: {gmail_provider['name']}")
        print(f"✅ Prospects: {len(prospects)} real prospects")
        print(f"✅ Templates: {len(templates)} email templates")
        print(f"✅ Prospect List: {prospect_list['name'] if prospect_list else 'Failed'}")
        print(f"✅ Campaign: {campaign['name'] if campaign else 'Failed'}")
        print(f"✅ Intents: {len(intents)} AI intents")
        
        print("\n📧 Ready to send real emails!")
        print("Login to the application with testuser/testpass123 to test email sending.")
        
    except Exception as e:
        print(f"❌ Error setting up real data: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await db_service.disconnect()

if __name__ == "__main__":
    asyncio.run(main())