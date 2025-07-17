"""
Seed data initialization for the email responder application
"""
from datetime import datetime
from app.utils.helpers import generate_id

async def initialize_seed_data(db_service):
    """Initialize the database with sample data for testing"""
    try:
        # Check if data already exists
        existing_templates = await db_service.get_templates()
        existing_lists = await db_service.get_lists()
        
        if existing_templates and existing_lists:
            print("Seed data already exists, skipping initialization")
            return
        
        print("🌱 Initializing seed data...")
        
        # Sample templates
        templates = [
            {
                "id": generate_id(),
                "name": "Welcome Email",
                "subject": "Welcome to {{company}} - Let's Connect!",
                "content": """Hi {{first_name}},

I hope this email finds you well! I came across {{company}} and was impressed by your work in the {{industry}} industry.

I'd love to connect and explore potential collaboration opportunities that could benefit both our organizations.

Would you be open to a brief 15-minute call next week to discuss this further?

Best regards,
[Your Name]""",
                "type": "initial",
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "id": generate_id(),
                "name": "Follow-up Email",
                "subject": "Following up on our conversation - {{company}}",
                "content": """Hi {{first_name}},

I wanted to follow up on my previous email regarding potential collaboration opportunities between our companies.

I understand you're likely busy, but I believe there could be significant value in a brief conversation about how we can work together.

Would you have 10-15 minutes available this week for a quick call?

Looking forward to hearing from you.

Best regards,
[Your Name]""",
                "type": "follow_up",
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "id": generate_id(),
                "name": "Auto Response - Interest",
                "subject": "Re: Thank you for your interest!",
                "content": """Hi {{first_name}},

Thank you for expressing interest in our collaboration proposal!

I'm excited to learn more about {{company}} and explore how we can work together to achieve mutual success.

I'll reach out within the next 24 hours to schedule a convenient time for our conversation.

Best regards,
[Your Name]""",
                "type": "auto_response",
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        
        # Sample prospects
        prospects = [
            {
                "id": generate_id(),
                "email": "john.doe@techcorp.com",
                "first_name": "John",
                "last_name": "Doe",
                "company": "TechCorp Inc",
                "job_title": "CEO",
                "industry": "Technology",
                "phone": "+1-555-0101",
                "status": "active",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "id": generate_id(),
                "email": "sarah.smith@innovatesoft.com",
                "first_name": "Sarah",
                "last_name": "Smith",
                "company": "InnovateSoft",
                "job_title": "CTO",
                "industry": "Software Development",
                "phone": "+1-555-0102",
                "status": "active",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "id": generate_id(),
                "email": "mike.johnson@datascienceai.com",
                "first_name": "Mike",
                "last_name": "Johnson",
                "company": "DataScience AI",
                "job_title": "VP of Engineering",
                "industry": "Artificial Intelligence",
                "phone": "+1-555-0103",
                "status": "active",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        
        # Sample email providers
        email_providers = [
            {
                "id": generate_id(),
                "name": "Test Gmail Provider",
                "provider_type": "gmail",
                "email_address": "test@gmail.com",
                "display_name": "Test User",
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
                "is_default": True,
                "is_active": True,
                "skip_connection_test": True,
                "current_daily_count": 0,
                "current_hourly_count": 0,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "last_sync": datetime.utcnow()
            }
        ]
        
        # Sample intents
        intents = [
            {
                "id": generate_id(),
                "name": "Positive Response",
                "description": "Prospect is interested and wants to learn more",
                "keywords": ["interested", "yes", "tell me more", "sounds good", "let's talk"],
                "response_template": "Thank you for your interest! I'll reach out to schedule a call.",
                "confidence_threshold": 0.7,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "id": generate_id(),
                "name": "Not Interested",
                "description": "Prospect is not interested at this time",
                "keywords": ["not interested", "no thanks", "remove me", "unsubscribe"],
                "response_template": "Thank you for your time. I'll remove you from our outreach list.",
                "confidence_threshold": 0.8,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        
        # Only create templates if they don't exist
        if not existing_templates:
            # Create templates
            for template in templates:
                await db_service.create_template(template)
            print(f"✅ Created {len(templates)} sample templates")
        else:
            print("✅ Templates already exist, skipping template creation")
            
        # Only create prospects if they don't exist
        existing_prospects = await db_service.get_prospects()
        if not existing_prospects:
            # Create prospects
            for prospect in prospects:
                await db_service.create_prospect(prospect)
            print(f"✅ Created {len(prospects)} sample prospects")
        else:
            print("✅ Prospects already exist, skipping prospect creation")
            prospects = existing_prospects
            
        # Only create email providers if they don't exist
        existing_providers = await db_service.get_email_providers()
        if not existing_providers:
            # Create email providers
            for provider in email_providers:
                await db_service.create_email_provider(provider)
            print(f"✅ Created {len(email_providers)} sample email providers")
        else:
            print("✅ Email providers already exist, skipping provider creation")
            
        # Only create intents if they don't exist
        existing_intents = await db_service.get_intents()
        if not existing_intents:
            # Create intents
            for intent in intents:
                await db_service.create_intent(intent)
            print(f"✅ Created {len(intents)} sample intents")
        else:
            print("✅ Intents already exist, skipping intent creation")
        
        # Sample prospect lists
        prospect_lists = [
            {
                "id": generate_id(),
                "name": "Technology Companies",
                "description": "CEOs and CTOs from tech startups and established companies",
                "color": "#3B82F6",
                "prospect_count": 0,
                "tags": ["tech", "startup", "enterprise"],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "id": generate_id(),
                "name": "AI & Machine Learning",
                "description": "Companies working with AI, ML, and data science",
                "color": "#10B981",
                "prospect_count": 0,
                "tags": ["ai", "ml", "data-science"],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "id": generate_id(),
                "name": "Software Development",
                "description": "Software development companies and service providers",
                "color": "#F59E0B",
                "prospect_count": 0,
                "tags": ["software", "development", "services"],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        
        # Create prospect lists
        for prospect_list in prospect_lists:
            await db_service.create_list(prospect_list)
        print(f"✅ Created {len(prospect_lists)} sample prospect lists")
        
        # Add prospects to lists based on their industry
        if prospect_lists and prospects:
            # Add all prospects to the first list (Technology Companies)
            tech_list_id = prospect_lists[0]["id"]
            prospect_ids = [p["id"] for p in prospects]
            await db_service.add_prospects_to_list(tech_list_id, prospect_ids)
            print(f"✅ Added {len(prospect_ids)} prospects to Technology Companies list")
            
            # Add AI-related prospects to AI & ML list
            ai_list_id = prospect_lists[1]["id"]
            ai_prospects = [p["id"] for p in prospects if "ai" in p.get("industry", "").lower() or "data" in p.get("industry", "").lower()]
            if ai_prospects:
                await db_service.add_prospects_to_list(ai_list_id, ai_prospects)
                print(f"✅ Added {len(ai_prospects)} prospects to AI & ML list")
        
        # Now create a sample campaign using the first template and lists
        if templates and prospect_lists:
            campaign = {
                "id": generate_id(),
                "name": "Q1 2025 Outreach Campaign",
                "template_id": templates[0]["id"],  # Use the actual template ID
                "list_ids": [prospect_lists[0]["id"]],  # Use the first list
                "max_emails": 1000,
                "schedule": None,
                "status": "draft",
                "prospect_count": len(prospects),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            await db_service.create_campaign(campaign)
            print(f"✅ Created sample campaign linked to prospect list")
        
        print("🎉 Seed data initialization completed successfully!")
        
    except Exception as e:
        print(f"❌ Error initializing seed data: {e}")
        import traceback
        traceback.print_exc()