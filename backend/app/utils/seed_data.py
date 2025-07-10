from app.services.database import db_service
from app.utils.helpers import generate_id
from datetime import datetime

async def init_seed_data():
    """Initialize database with seed data"""
    try:
        # Check if data already exists
        existing_prospects = await db_service.get_prospects()
        if len(existing_prospects) > 0:
            return
        
        # Seed prospect lists
        seed_lists = [
            {
                "id": "list_1",
                "name": "Technology Companies",
                "description": "Tech companies and startups",
                "color": "#3B82F6",
                "tags": ["tech", "software", "startup"],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "id": "list_2", 
                "name": "Enterprise Clients",
                "description": "Large enterprise clients",
                "color": "#10B981",
                "tags": ["enterprise", "large", "corporate"],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "id": "list_3",
                "name": "Warm Leads",
                "description": "Prospects who have shown interest",
                "color": "#F59E0B",
                "tags": ["warm", "interested", "engaged"],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        
        # Seed prospects
        seed_prospects = [
            {
                "id": generate_id(),
                "email": "john.doe@techcorp.com",
                "first_name": "John",
                "last_name": "Doe",
                "company": "TechCorp Inc",
                "phone": "+1-555-0123",
                "linkedin_url": "https://linkedin.com/in/john-doe",
                "company_domain": "techcorp.com",
                "industry": "Technology",
                "company_linkedin_url": "https://linkedin.com/company/techcorp",
                "job_title": "CEO",
                "location": "San Francisco, CA",
                "company_size": "500-1000",
                "annual_revenue": "$50M-$100M",
                "lead_source": "Website",
                "list_ids": ["list_1", "list_3"],  # Technology + Warm
                "tags": ["ceo", "tech", "decision-maker"],
                "status": "active",
                "created_at": datetime.utcnow()
            },
            {
                "id": generate_id(),
                "email": "sarah.smith@innovatesoft.com",
                "first_name": "Sarah",
                "last_name": "Smith",
                "company": "InnovateSoft",
                "phone": "+1-555-0456",
                "linkedin_url": "https://linkedin.com/in/sarah-smith",
                "company_domain": "innovatesoft.com",
                "industry": "Software",
                "company_linkedin_url": "https://linkedin.com/company/innovatesoft",
                "job_title": "CTO",
                "location": "New York, NY",
                "company_size": "100-500",
                "annual_revenue": "$10M-$50M",
                "lead_source": "LinkedIn",
                "list_ids": ["list_1", "list_2"],  # Technology + Enterprise
                "tags": ["cto", "tech", "decision-maker"],
                "additional_fields": {"timezone": "EST", "preferred_contact": "phone"},
                "status": "active",
                "created_at": datetime.utcnow()
            },
            {
                "id": generate_id(),
                "email": "mike.johnson@datascience.ai",
                "first_name": "Mike",
                "last_name": "Johnson",
                "company": "DataScience AI",
                "phone": "+1-555-0789",
                "linkedin_url": "https://linkedin.com/in/mike-johnson",
                "company_domain": "datascience.ai",
                "industry": "Artificial Intelligence",
                "company_linkedin_url": "https://linkedin.com/company/datascience-ai",
                "job_title": "Head of AI",
                "location": "Austin, TX",
                "company_size": "50-100",
                "annual_revenue": "$5M-$10M",
                "lead_source": "Conference",
                "list_ids": ["list_1"],  # Technology
                "tags": ["ai", "tech", "innovation"],
                "additional_fields": {"timezone": "CST", "preferred_contact": "email"},
                "status": "active",
                "created_at": datetime.utcnow()
            },
            {
                "id": generate_id(),
                "email": "lisa.brown@cloudtech.io",
                "first_name": "Lisa",
                "last_name": "Brown",
                "company": "CloudTech Solutions",
                "phone": "+1-555-0321",
                "linkedin_url": "https://linkedin.com/in/lisa-brown",
                "company_domain": "cloudtech.io",
                "industry": "Cloud Computing",
                "company_linkedin_url": "https://linkedin.com/company/cloudtech-solutions",
                "job_title": "VP of Engineering",
                "location": "Seattle, WA",
                "company_size": "200-500",
                "annual_revenue": "$25M-$50M",
                "lead_source": "Referral",
                "list_ids": ["list_2", "list_3"],  # Enterprise + Warm
                "tags": ["cloud", "engineering", "vp"],
                "additional_fields": {"timezone": "PST", "preferred_contact": "email"},
                "status": "active",
                "created_at": datetime.utcnow()
            },
            {
                "id": generate_id(),
                "email": "david.wilson@startupxyz.com",
                "first_name": "David",
                "last_name": "Wilson",
                "company": "StartupXYZ",
                "phone": "+1-555-0654",
                "linkedin_url": "https://linkedin.com/in/david-wilson",
                "company_domain": "startupxyz.com",
                "industry": "Startup",
                "company_linkedin_url": "https://linkedin.com/company/startupxyz",
                "job_title": "Founder",
                "location": "Boston, MA",
                "company_size": "10-50",
                "annual_revenue": "$1M-$5M",
                "lead_source": "Social Media",
                "list_ids": ["list_1"],  # Technology
                "tags": ["startup", "founder", "early-stage"],
                "additional_fields": {"timezone": "EST", "preferred_contact": "phone"},
                "status": "active",
                "created_at": datetime.utcnow()
            }
        ]
        
        # Seed templates
        seed_templates = [
            {
                "id": generate_id(),
                "name": "Welcome Email",
                "subject": "Welcome to our AI Email Solution, {{first_name}}!",
                "content": """
                <html>
                <body>
                    <h2>Hi {{first_name}},</h2>
                    <p>I hope this email finds you well. I'm reaching out from our AI Email Responder team.</p>
                    <p>We've helped companies like {{company}} increase their email engagement by 300% using our AI-powered email automation platform.</p>
                    <p>Would you be interested in a 15-minute demo to see how we can help {{company}} streamline your email outreach?</p>
                    <p>Best regards,<br>AI Email Team</p>
                </body>
                </html>
                """,
                "type": "initial",
                "placeholders": ["{{first_name}}", "{{company}}"],
                "created_at": datetime.utcnow()
            },
            {
                "id": generate_id(),
                "name": "Follow-up Email",
                "subject": "Quick follow-up for {{company}}",
                "content": """
                <html>
                <body>
                    <h2>Hi {{first_name}},</h2>
                    <p>I wanted to follow up on my previous email about our AI Email Responder solution.</p>
                    <p>I understand you're busy, but I believe our platform could really benefit {{company}}.</p>
                    <p>Would you have 10 minutes this week for a quick call?</p>
                    <p>Best regards,<br>AI Email Team</p>
                </body>
                </html>
                """,
                "type": "follow_up",
                "placeholders": ["{{first_name}}", "{{company}}"],
                "created_at": datetime.utcnow()
            },
            {
                "id": generate_id(),
                "name": "Auto Response - Positive",
                "subject": "Great to hear from you!",
                "content": """
                <html>
                <body>
                    <h2>Hi {{first_name}},</h2>
                    <p>Thank you for your interest! I'm excited to learn more about how we can help {{company}}.</p>
                    <p>I'll reach out shortly to schedule a personalized demo.</p>
                    <p>Best regards,<br>AI Email Team</p>
                </body>
                </html>
                """,
                "type": "auto_response",
                "placeholders": ["{{first_name}}", "{{company}}"],
                "created_at": datetime.utcnow()
            }
        ]
        
        # Store template IDs for intent linking
        template_ids = [t["id"] for t in seed_templates]
        auto_response_template_id = template_ids[2]  # "Auto Response - Positive"
        
        # Seed intents with correct template references
        seed_intents = [
            {
                "id": generate_id(),
                "name": "Positive Response",
                "description": "When someone shows interest, says yes, or wants to learn more",
                "keywords": ["interested", "yes", "tell me more", "schedule", "demo", "call"],
                "primary_template_id": auto_response_template_id,
                "fallback_template_id": auto_response_template_id,
                "combination_templates": [],
                "auto_respond": True,
                "response_delay_min": 5,
                "response_delay_max": 30,
                "confidence_threshold": 0.8,
                "escalate_to_human": False,
                "created_at": datetime.utcnow()
            },
            {
                "id": generate_id(),
                "name": "Not Interested",
                "description": "When someone explicitly says they're not interested",
                "keywords": ["not interested", "no thanks", "remove", "unsubscribe"],
                "primary_template_id": auto_response_template_id,
                "fallback_template_id": auto_response_template_id,
                "combination_templates": [],
                "auto_respond": True,
                "response_delay_min": 10,
                "response_delay_max": 60,
                "confidence_threshold": 0.9,
                "escalate_to_human": False,
                "created_at": datetime.utcnow()
            },
            {
                "id": generate_id(),
                "name": "Request More Info",
                "description": "When someone asks for more information or has questions",
                "keywords": ["more info", "questions", "details", "pricing", "features"],
                "primary_template_id": auto_response_template_id,
                "fallback_template_id": auto_response_template_id,
                "combination_templates": [],
                "auto_respond": True,
                "response_delay_min": 15,
                "response_delay_max": 45,
                "confidence_threshold": 0.7,
                "escalate_to_human": True,
                "created_at": datetime.utcnow()
            }
        ]
        
        # Insert seed data
        for seed_list in seed_lists:
            await db_service.create_list(seed_list)
        
        for seed_prospect in seed_prospects:
            await db_service.db.prospects.insert_one(seed_prospect)
            
        for seed_template in seed_templates:
            await db_service.create_template(seed_template)
            
        for seed_intent in seed_intents:
            await db_service.create_intent(seed_intent)
        
        print("✅ Seed data initialized successfully")
        
    except Exception as e:
        print(f"Error initializing seed data: {str(e)}")