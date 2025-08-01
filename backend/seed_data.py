"""
Seed data script for AI Email Responder
Creates test credentials and initial data for the application
"""
import asyncio
import sys
import os
from datetime import datetime, timedelta
from typing import List, Dict

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.database import db_service
from app.middleware.security import get_password_hash
from app.utils.helpers import generate_id

async def create_test_user():
    """Create test user credentials"""
    try:
        # Check if user already exists
        existing_user = await db_service.db.users.find_one({"username": "testuser"})
        if existing_user:
            print("✅ Test user already exists")
            return
        
        # Create test user
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "full_name": "Test User",
            "hashed_password": get_password_hash("testpass123"),
            "is_active": True,
            "created_at": datetime.utcnow(),
            "last_login": None
        }
        
        await db_service.db.users.insert_one(user_data)
        print("✅ Test user created successfully")
        print("   Username: testuser")
        print("   Password: testpass123")
        print("   Email: test@example.com")
        
    except Exception as e:
        print(f"❌ Error creating test user: {e}")

async def create_test_email_providers():
    """Create test email providers"""
    try:
        # Check if providers already exist
        existing_providers = await db_service.get_email_providers()
        if existing_providers:
            print("✅ Email providers already exist")
            return
        
        # Create test Gmail provider
        gmail_provider = {
            "id": generate_id(),
            "name": "Test Gmail Provider",
            "provider_type": "gmail",
            "email_address": "test@gmail.com",
            "display_name": "Test Gmail",
            "smtp_host": "smtp.gmail.com",
            "smtp_port": 587,
            "smtp_username": "test@gmail.com",
            "smtp_password": "app_password_here",
            "smtp_use_tls": True,
            "imap_host": "imap.gmail.com",
            "imap_port": 993,
            "imap_username": "test@gmail.com",
            "imap_password": "app_password_here",
            "imap_use_ssl": True,
            "is_active": True,
            "is_default": True,
            "daily_send_limit": 500,
            "hourly_send_limit": 50,
            "current_daily_count": 0,
            "current_hourly_count": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "skip_connection_test": True  # Skip test for demo
        }
        
        await db_service.create_email_provider(gmail_provider)
        
        # Create test Outlook provider
        outlook_provider = {
            "id": generate_id(),
            "name": "Test Outlook Provider",
            "provider_type": "outlook",
            "email_address": "test@outlook.com",
            "display_name": "Test Outlook",
            "smtp_host": "smtp-mail.outlook.com",
            "smtp_port": 587,
            "smtp_username": "test@outlook.com",
            "smtp_password": "app_password_here",
            "smtp_use_tls": True,
            "imap_host": "outlook.office365.com",
            "imap_port": 993,
            "imap_username": "test@outlook.com",
            "imap_password": "app_password_here",
            "imap_use_ssl": True,
            "is_active": True,
            "is_default": False,
            "daily_send_limit": 300,
            "hourly_send_limit": 30,
            "current_daily_count": 0,
            "current_hourly_count": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "skip_connection_test": True  # Skip test for demo
        }
        
        await db_service.create_email_provider(outlook_provider)
        
        print("✅ Test email providers created successfully")
        
    except Exception as e:
        print(f"❌ Error creating email providers: {e}")

async def create_test_templates():
    """Create test email templates"""
    try:
        # Check if templates already exist
        existing_templates = await db_service.get_templates()
        if existing_templates:
            print("✅ Templates already exist")
            return
        
        # Initial template
        initial_template = {
            "id": generate_id(),
            "name": "Welcome Email",
            "subject": "Welcome to Our Service, {{first_name}}!",
            "content": """
            <html>
            <body>
                <h2>Welcome {{first_name}}!</h2>
                <p>Thank you for your interest in our service. We're excited to connect with you.</p>
                <p>Here at {{company}}, we specialize in helping businesses like yours grow and succeed.</p>
                <p>Would you be interested in a quick 15-minute call to discuss how we can help {{company}}?</p>
                <p>Best regards,<br>
                The Team</p>
            </body>
            </html>
            """,
            "type": "initial",
            "placeholders": ["first_name", "last_name", "company"],
            "created_at": datetime.utcnow()
        }
        
        await db_service.create_template(initial_template)
        
        # Follow-up template 1
        followup_template_1 = {
            "id": generate_id(),
            "name": "Follow-up Day 3",
            "subject": "Quick follow-up regarding {{company}}",
            "content": """
            <html>
            <body>
                <h2>Hi {{first_name}},</h2>
                <p>I wanted to follow up on my previous email about helping {{company}} with our services.</p>
                <p>Many companies in the {{industry}} industry have seen great results working with us.</p>
                <p>Would you be available for a brief call this week?</p>
                <p>Best regards,<br>
                The Team</p>
            </body>
            </html>
            """,
            "type": "follow_up",
            "placeholders": ["first_name", "company", "industry"],
            "created_at": datetime.utcnow()
        }
        
        await db_service.create_template(followup_template_1)
        
        # Follow-up template 2
        followup_template_2 = {
            "id": generate_id(),
            "name": "Follow-up Day 7",
            "subject": "Final follow-up for {{company}}",
            "content": """
            <html>
            <body>
                <h2>Hi {{first_name}},</h2>
                <p>This is my final follow-up regarding our conversation about {{company}}.</p>
                <p>I understand you're busy, but I wanted to make sure you didn't miss this opportunity.</p>
                <p>If you're not interested, just let me know and I'll remove you from our list.</p>
                <p>Otherwise, I'd love to chat for just 10 minutes about how we can help.</p>
                <p>Best regards,<br>
                The Team</p>
            </body>
            </html>
            """,
            "type": "follow_up",
            "placeholders": ["first_name", "company"],
            "created_at": datetime.utcnow()
        }
        
        await db_service.create_template(followup_template_2)
        
        print("✅ Test templates created successfully")
        
    except Exception as e:
        print(f"❌ Error creating templates: {e}")

async def create_test_prospect_lists():
    """Create test prospect lists"""
    try:
        # Check if lists already exist
        existing_lists = await db_service.get_lists()
        if existing_lists:
            print("✅ Prospect lists already exist")
            return
        
        # Create test lists
        tech_list = {
            "id": generate_id(),
            "name": "Tech Startups",
            "description": "Technology startup companies",
            "color": "#3B82F6",
            "prospect_count": 0,
            "tags": ["tech", "startup", "b2b"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db_service.create_list(tech_list)
        
        finance_list = {
            "id": generate_id(),
            "name": "Finance Companies",
            "description": "Financial services companies",
            "color": "#10B981",
            "prospect_count": 0,
            "tags": ["finance", "services", "b2b"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db_service.create_list(finance_list)
        
        healthcare_list = {
            "id": generate_id(),
            "name": "Healthcare Organizations",
            "description": "Healthcare and medical organizations",
            "color": "#EF4444",
            "prospect_count": 0,
            "tags": ["healthcare", "medical", "b2b"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db_service.create_list(healthcare_list)
        
        print("✅ Test prospect lists created successfully")
        
    except Exception as e:
        print(f"❌ Error creating prospect lists: {e}")

async def create_test_prospects():
    """Create test prospects"""
    try:
        # Check if prospects already exist
        existing_prospects = await db_service.get_prospects(0, 10)
        if existing_prospects:
            print("✅ Prospects already exist")
            return
        
        # Get list IDs
        lists = await db_service.get_lists()
        tech_list_id = None
        finance_list_id = None
        healthcare_list_id = None
        
        for list_item in lists:
            if list_item["name"] == "Tech Startups":
                tech_list_id = list_item["id"]
            elif list_item["name"] == "Finance Companies":
                finance_list_id = list_item["id"]
            elif list_item["name"] == "Healthcare Organizations":
                healthcare_list_id = list_item["id"]
        
        # Create test prospects
        prospects = [
            {
                "id": generate_id(),
                "email": "john.doe@techstartup.com",
                "first_name": "John",
                "last_name": "Doe",
                "company": "TechStartup Inc",
                "job_title": "CEO",
                "industry": "Technology",
                "location": "San Francisco, CA",
                "company_size": "10-50",
                "list_ids": [tech_list_id] if tech_list_id else [],
                "tags": ["tech", "ceo", "high-priority"],
                "status": "active",
                "created_at": datetime.utcnow()
            },
            {
                "id": generate_id(),
                "email": "jane.smith@financegroup.com",
                "first_name": "Jane",
                "last_name": "Smith",
                "company": "Finance Group LLC",
                "job_title": "CFO",
                "industry": "Finance",
                "location": "New York, NY",
                "company_size": "50-100",
                "list_ids": [finance_list_id] if finance_list_id else [],
                "tags": ["finance", "cfo", "decision-maker"],
                "status": "active",
                "created_at": datetime.utcnow()
            },
            {
                "id": generate_id(),
                "email": "mike.johnson@healthcorp.com",
                "first_name": "Mike",
                "last_name": "Johnson",
                "company": "Health Corp",
                "job_title": "Director of Operations",
                "industry": "Healthcare",
                "location": "Chicago, IL",
                "company_size": "100-500",
                "list_ids": [healthcare_list_id] if healthcare_list_id else [],
                "tags": ["healthcare", "operations", "director"],
                "status": "active",
                "created_at": datetime.utcnow()
            },
            {
                "id": generate_id(),
                "email": "sarah.wilson@innovation.com",
                "first_name": "Sarah",
                "last_name": "Wilson",
                "company": "Innovation Labs",
                "job_title": "VP of Marketing",
                "industry": "Technology",
                "location": "Austin, TX",
                "company_size": "20-50",
                "list_ids": [tech_list_id] if tech_list_id else [],
                "tags": ["tech", "marketing", "vp"],
                "status": "active",
                "created_at": datetime.utcnow()
            },
            {
                "id": generate_id(),
                "email": "david.brown@medicalgroup.com",
                "first_name": "David",
                "last_name": "Brown",
                "company": "Medical Group Associates",
                "job_title": "Practice Manager",
                "industry": "Healthcare",
                "location": "Los Angeles, CA",
                "company_size": "50-100",
                "list_ids": [healthcare_list_id] if healthcare_list_id else [],
                "tags": ["healthcare", "manager", "practice"],
                "status": "active",
                "created_at": datetime.utcnow()
            }
        ]
        
        for prospect in prospects:
            await db_service.create_prospect(prospect)
        
        print("✅ Test prospects created successfully")
        
    except Exception as e:
        print(f"❌ Error creating prospects: {e}")

async def create_test_intents():
    """Create test intent configurations"""
    try:
        # Check if intents already exist
        existing_intents = await db_service.get_intents()
        if existing_intents:
            print("✅ Intents already exist")
            return
        
        # Create test intents
        interested_intent = {
            "id": generate_id(),
            "name": "Interested",
            "description": "Prospect shows interest in our service",
            "keywords": ["interested", "yes", "tell me more", "sounds good", "I'd like to know", "call me"],
            "auto_respond": True,
            "response_delay_min": 5,
            "response_delay_max": 30,
            "confidence_threshold": 0.7,
            "created_at": datetime.utcnow()
        }
        
        await db_service.create_intent(interested_intent)
        
        not_interested_intent = {
            "id": generate_id(),
            "name": "Not Interested",
            "description": "Prospect is not interested",
            "keywords": ["not interested", "no thanks", "remove me", "unsubscribe", "don't contact"],
            "auto_respond": True,
            "response_delay_min": 2,
            "response_delay_max": 10,
            "confidence_threshold": 0.8,
            "created_at": datetime.utcnow()
        }
        
        await db_service.create_intent(not_interested_intent)
        
        out_of_office_intent = {
            "id": generate_id(),
            "name": "Out of Office",
            "description": "Automatic out of office reply",
            "keywords": ["out of office", "vacation", "away", "automatic reply", "currently out"],
            "auto_respond": False,
            "response_delay_min": 0,
            "response_delay_max": 0,
            "confidence_threshold": 0.9,
            "created_at": datetime.utcnow()
        }
        
        await db_service.create_intent(out_of_office_intent)
        
        print("✅ Test intents created successfully")
        
    except Exception as e:
        print(f"❌ Error creating intents: {e}")

async def main():
    """Main function to run all seed operations"""
    print("🌱 Starting database seeding process...")
    print("=" * 50)
    
    # Create test user
    await create_test_user()
    
    # Create email providers
    await create_test_email_providers()
    
    # Create templates
    await create_test_templates()
    
    # Create prospect lists
    await create_test_prospect_lists()
    
    # Create prospects
    await create_test_prospects()
    
    # Create intents
    await create_test_intents()
    
    print("=" * 50)
    print("🎉 Database seeding completed successfully!")
    print()
    print("🔑 TEST CREDENTIALS:")
    print("   Username: testuser")
    print("   Password: testpass123")
    print("   Email: test@example.com")
    print()
    print("📊 CREATED DATA:")
    print("   - 1 test user")
    print("   - 2 email providers (Gmail, Outlook)")
    print("   - 3 email templates (1 initial, 2 follow-ups)")
    print("   - 3 prospect lists (Tech, Finance, Healthcare)")
    print("   - 5 test prospects")
    print("   - 3 intent configurations")
    print()
    print("🚀 You can now login and test the application!")

if __name__ == "__main__":
    asyncio.run(main())