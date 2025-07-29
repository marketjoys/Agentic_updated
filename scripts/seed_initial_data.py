#!/usr/bin/env python3
"""
Setup script to seed the database with initial data
"""

import asyncio
from datetime import datetime
from app.services.database import db_service
from app.utils.helpers import generate_id

async def seed_database():
    """Seed database with initial data"""
    try:
        # Connect to database
        await db_service.connect()
        
        print("🌱 Seeding database with initial data...")
        
        # Create sample templates
        templates = [
            {
                "id": generate_id(),
                "name": "Welcome Email",
                "subject": "Welcome to Our Service, {{first_name}}!",
                "content": """
                <html>
                <body>
                    <h2>Welcome {{first_name}}!</h2>
                    <p>Thank you for your interest in our service. We're excited to work with {{company}}.</p>
                    <p>Our team will reach out to you soon with more information.</p>
                    <p>Best regards,<br>
                    The Team</p>
                </body>
                </html>
                """,
                "type": "initial",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "id": generate_id(),
                "name": "Follow-up Email",
                "subject": "Following up on our conversation - {{company}}",
                "content": """
                <html>
                <body>
                    <h2>Hi {{first_name}},</h2>
                    <p>I wanted to follow up on our previous conversation about {{company}}.</p>
                    <p>Are you still interested in learning more about our service?</p>
                    <p>Feel free to reply to this email with any questions.</p>
                    <p>Best regards,<br>
                    The Team</p>
                </body>
                </html>
                """,
                "type": "follow_up",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "id": generate_id(),
                "name": "Final Follow-up",
                "subject": "Final follow-up for {{company}}",
                "content": """
                <html>
                <body>
                    <h2>Hi {{first_name}},</h2>
                    <p>This is my final follow-up regarding {{company}}.</p>
                    <p>If you're not interested at this time, I understand and won't reach out again.</p>
                    <p>However, if you have any questions or would like to learn more, please don't hesitate to reply.</p>
                    <p>Best regards,<br>
                    The Team</p>
                </body>
                </html>
                """,
                "type": "follow_up",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        
        # Insert templates
        template_count = 0
        for template in templates:
            result = await db_service.create_template(template)
            if result:
                template_count += 1
                print(f"✅ Created template: {template['name']}")
        
        print(f"📝 Created {template_count} templates")
        
        # Create sample prospect lists
        lists = [
            {
                "id": generate_id(),
                "name": "Tech Startups",
                "description": "Technology startup companies",
                "color": "#3B82F6",
                "tags": ["tech", "startup", "b2b"],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "id": generate_id(),
                "name": "Finance Companies",
                "description": "Financial services companies",
                "color": "#10B981",
                "tags": ["finance", "services", "b2b"],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "id": generate_id(),
                "name": "Healthcare Organizations",
                "description": "Healthcare and medical organizations",
                "color": "#EF4444",
                "tags": ["healthcare", "medical", "b2b"],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        
        # Insert lists
        list_count = 0
        for list_item in lists:
            result = await db_service.create_list(list_item)
            if result:
                list_count += 1
                print(f"✅ Created list: {list_item['name']}")
        
        print(f"📋 Created {list_count} prospect lists")
        
        # Create sample prospects
        prospects = [
            {
                "id": generate_id(),
                "email": "john.doe@techstartup.com",
                "first_name": "John",
                "last_name": "Doe",
                "company": "TechStartup Inc",
                "job_title": "CEO",
                "industry": "Technology",
                "status": "active",
                "list_ids": [lists[0]["id"]],  # Tech Startups
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "id": generate_id(),
                "email": "jane.smith@financegroup.com",
                "first_name": "Jane",
                "last_name": "Smith",
                "company": "Finance Group LLC",
                "job_title": "CFO",
                "industry": "Finance",
                "status": "active",
                "list_ids": [lists[1]["id"]],  # Finance Companies
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "id": generate_id(),
                "email": "mike.johnson@healthcorp.com",
                "first_name": "Mike",
                "last_name": "Johnson",
                "company": "Health Corp",
                "job_title": "Director of Operations",
                "industry": "Healthcare",
                "status": "active",
                "list_ids": [lists[2]["id"]],  # Healthcare Organizations
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        
        # Insert prospects
        prospect_count = 0
        for prospect in prospects:
            result, error = await db_service.create_prospect(prospect)
            if result:
                prospect_count += 1
                print(f"✅ Created prospect: {prospect['first_name']} {prospect['last_name']} ({prospect['email']})")
            else:
                print(f"❌ Failed to create prospect {prospect['email']}: {error}")
        
        print(f"👥 Created {prospect_count} prospects")
        
        # Create sample intents
        intents = [
            {
                "id": generate_id(),
                "name": "Interested",
                "description": "Prospect shows interest in our service",
                "keywords": ["interested", "yes", "tell me more", "sounds good", "want to know more"],
                "auto_respond": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "id": generate_id(),
                "name": "Not Interested",
                "description": "Prospect is not interested",
                "keywords": ["not interested", "no thanks", "remove me", "unsubscribe"],
                "auto_respond": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "id": generate_id(),
                "name": "Request More Info",
                "description": "Prospect requests more information",
                "keywords": ["more info", "details", "information", "tell me more", "explain"],
                "auto_respond": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        
        # Insert intents
        intent_count = 0
        for intent in intents:
            result = await db_service.create_intent(intent)
            if result:
                intent_count += 1
                print(f"✅ Created intent: {intent['name']}")
        
        print(f"🎯 Created {intent_count} intents")
        
        print("\n🎉 Database seeding completed successfully!")
        print(f"📊 Summary:")
        print(f"   - Templates: {template_count}")
        print(f"   - Lists: {list_count}")
        print(f"   - Prospects: {prospect_count}")
        print(f"   - Intents: {intent_count}")
        
    except Exception as e:
        print(f"❌ Error seeding database: {str(e)}")
        
    finally:
        # Disconnect from database
        await db_service.disconnect()

if __name__ == "__main__":
    print("🌱 Starting database seeding...")
    asyncio.run(seed_database())