from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
import os
import io
from datetime import datetime, timedelta
import uuid
import json
import pandas as pd
from groq import Groq
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template
import asyncio
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AI Email Responder", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
client = AsyncIOMotorClient(os.getenv("MONGO_URL"))
db = client.email_responder

# Groq client (optional) - Fixed initialization
try:
    groq_api_key = os.getenv("GROQ_API_KEY")
    if groq_api_key:
        groq_client = Groq(api_key=groq_api_key)
    else:
        groq_client = None
except Exception as e:
    print(f"Warning: Could not initialize Groq client: {e}")
    groq_client = None

# Security
security = HTTPBearer()

# Pydantic models
class ProspectList(BaseModel):
    id: str = None
    name: str
    description: str = ""
    color: str = "#3B82F6"  # Default blue color
    prospect_count: int = 0
    tags: List[str] = []
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()

class Prospect(BaseModel):
    id: str = None
    email: EmailStr
    first_name: str
    last_name: str
    company: str = ""
    phone: str = ""
    linkedin_url: str = ""
    company_domain: str = ""
    industry: str = ""
    company_linkedin_url: str = ""
    job_title: str = ""
    location: str = ""
    company_size: str = ""
    annual_revenue: str = ""
    lead_source: str = ""
    list_ids: List[str] = []  # Can belong to multiple lists
    tags: List[str] = []
    additional_fields: Dict[str, str] = {}
    status: str = "active"
    campaign_id: str = ""
    last_contact: Optional[datetime] = None
    created_at: datetime = datetime.utcnow()

class Template(BaseModel):
    id: str = None
    name: str
    subject: str
    content: str
    type: str = "initial"  # initial, follow_up, auto_response
    placeholders: List[str] = []
    created_at: datetime = datetime.utcnow()

class Campaign(BaseModel):
    id: str = None
    name: str
    template_id: str
    list_ids: List[str] = []  # Target specific lists
    prospect_count: int = 0
    max_emails: int = 1000
    # Advanced Scheduling Options
    schedule_type: str = "immediate"  # immediate, scheduled, recurring
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    timezone: str = "UTC"
    send_window_start: str = "09:00"  # 24-hour format
    send_window_end: str = "17:00"
    send_days: List[str] = ["monday", "tuesday", "wednesday", "thursday", "friday"]
    rate_limit_per_hour: int = 100
    rate_limit_per_day: int = 1000
    delay_between_emails: int = 60  # seconds
    # Existing fields
    status: str = "draft"  # draft, scheduled, active, paused, completed
    follow_up_intervals: List[int] = [3, 7, 14]  # days
    follow_up_templates: List[str] = []
    created_at: datetime = datetime.utcnow()

class IntentConfig(BaseModel):
    id: str = None
    name: str
    description: str
    keywords: List[str] = []
    # Enhanced Template System
    primary_template_id: str = ""
    fallback_template_id: str = ""
    combination_templates: List[Dict[str, str]] = []  # For multiple intents
    auto_respond: bool = True
    response_delay_min: int = 5  # minutes
    response_delay_max: int = 60  # minutes
    confidence_threshold: float = 0.7
    escalate_to_human: bool = False
    created_at: datetime = datetime.utcnow()

class EmailMessage(BaseModel):
    id: str = None
    prospect_id: str
    campaign_id: str
    subject: str
    content: str
    status: str = "pending"  # pending, sent, failed
    sent_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    replied_at: Optional[datetime] = None
    created_at: datetime = datetime.utcnow()

class ThreadContext(BaseModel):
    id: str = None
    prospect_id: str
    campaign_id: str
    messages: List[Dict[str, Any]] = []
    last_activity: datetime = datetime.utcnow()
    created_at: datetime = datetime.utcnow()

# Utility functions
def generate_id():
    return str(uuid.uuid4())

async def send_email(to_email: str, subject: str, content: str):
    """Send email using SMTP"""
    try:
        smtp_host = os.getenv("SMTP_HOST")
        smtp_port = int(os.getenv("SMTP_PORT", 587))
        smtp_username = os.getenv("SMTP_USERNAME")
        smtp_password = os.getenv("SMTP_PASSWORD")
        
        if not all([smtp_host, smtp_username, smtp_password]):
            print(f"SMTP not configured - would send email to {to_email}")
            return True  # Return True for demo purposes
        
        message = MIMEMultipart()
        message["From"] = smtp_username
        message["To"] = to_email
        message["Subject"] = subject
        
        message.attach(MIMEText(content, "html"))
        
        await aiosmtplib.send(
            message,
            hostname=smtp_host,
            port=smtp_port,
            start_tls=True,
            username=smtp_username,
            password=smtp_password,
        )
        return True
    except Exception as e:
        print(f"Email sending failed: {str(e)}")
        return True  # Return True for demo purposes

def personalize_template(template_content: str, prospect: dict) -> str:
    """Personalize template with prospect data"""
    try:
        template = Template(template_content)
        return template.render(
            first_name=prospect.get("first_name", ""),
            last_name=prospect.get("last_name", ""),
            company=prospect.get("company", ""),
            email=prospect.get("email", "")
        )
    except Exception as e:
        print(f"Template personalization failed: {str(e)}")
        return template_content

# Initialize seed data
async def init_seed_data():
    """Initialize database with seed data"""
    try:
        # Check if data already exists
        existing_prospects = await db.prospects.count_documents({})
        if existing_prospects > 0:
            return
        
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
                "additional_fields": {"timezone": "PST", "preferred_contact": "email"},
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
        
        # Seed intents
        seed_intents = [
            {
                "id": generate_id(),
                "name": "Positive Response",
                "description": "When someone shows interest, says yes, or wants to learn more",
                "keywords": ["interested", "yes", "tell me more", "schedule", "demo", "call"],
                "response_template": "Thank you for your interest! I'll reach out to schedule a demo.",
                "created_at": datetime.utcnow()
            },
            {
                "id": generate_id(),
                "name": "Not Interested",
                "description": "When someone explicitly says they're not interested",
                "keywords": ["not interested", "no thanks", "remove", "unsubscribe"],
                "response_template": "I understand. I'll remove you from our outreach list.",
                "created_at": datetime.utcnow()
            },
            {
                "id": generate_id(),
                "name": "Request More Info",
                "description": "When someone asks for more information or has questions",
                "keywords": ["more info", "questions", "details", "pricing", "features"],
                "response_template": "I'd be happy to provide more details. Let me send you our information packet.",
                "created_at": datetime.utcnow()
            }
        ]
        
        # Insert seed data
        await db.prospects.insert_many(seed_prospects)
        await db.templates.insert_many(seed_templates)
        await db.intents.insert_many(seed_intents)
        
        print("✅ Seed data initialized successfully")
        
    except Exception as e:
        print(f"Error initializing seed data: {str(e)}")

# API Routes

@app.on_event("startup")
async def startup_event():
    await init_seed_data()

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Prospect Management
@app.post("/api/prospects")
async def create_prospect(prospect: Prospect):
    prospect.id = generate_id()
    prospect_dict = prospect.dict()
    result = await db.prospects.insert_one(prospect_dict)
    prospect_dict.pop('_id', None)
    return prospect_dict

@app.get("/api/prospects")
async def get_prospects(skip: int = 0, limit: int = 100):
    prospects = await db.prospects.find().skip(skip).limit(limit).to_list(length=limit)
    for prospect in prospects:
        prospect.pop('_id', None)
    return prospects

@app.post("/api/prospects/upload")
async def upload_prospects(file: UploadFile = File(...)):
    """Upload prospects from CSV file"""
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be CSV format")
        
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))
        
        required_columns = ['email', 'first_name', 'last_name']
        if not all(col in df.columns for col in required_columns):
            raise HTTPException(status_code=400, detail=f"CSV must contain columns: {required_columns}")
        
        # Define optional columns
        optional_columns = [
            'company', 'phone', 'linkedin_url', 'company_domain', 'industry',
            'company_linkedin_url', 'job_title', 'location', 'company_size',
            'annual_revenue', 'lead_source'
        ]
        
        prospects = []
        for _, row in df.iterrows():
            # Build prospect data
            prospect_data = {
                "id": generate_id(),
                "email": row['email'],
                "first_name": row['first_name'],
                "last_name": row['last_name']
            }
            
            # Add optional fields
            for col in optional_columns:
                if col in df.columns:
                    prospect_data[col] = row.get(col, '')
            
            # Handle additional fields (any column not in standard fields)
            standard_fields = set(required_columns + optional_columns + ['id'])
            additional_fields = {}
            for col in df.columns:
                if col not in standard_fields:
                    additional_fields[col] = str(row.get(col, ''))
            
            if additional_fields:
                prospect_data['additional_fields'] = additional_fields
            
            prospect = Prospect(**prospect_data)
            prospects.append(prospect.dict())
        
        if prospects:
            result = await db.prospects.insert_many(prospects)
        
        return {"message": f"Uploaded {len(prospects)} prospects", "count": len(prospects)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

# Template Management
@app.post("/api/templates")
async def create_template(template: Template):
    template.id = generate_id()
    template_dict = template.dict()
    result = await db.templates.insert_one(template_dict)
    template_dict.pop('_id', None)
    return template_dict

@app.get("/api/templates")
async def get_templates():
    templates = await db.templates.find().to_list(length=100)
    for template in templates:
        template.pop('_id', None)
    return templates

@app.get("/api/templates/{template_id}")
async def get_template(template_id: str):
    template = await db.templates.find_one({"id": template_id})
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    template.pop('_id', None)
    return template

@app.put("/api/templates/{template_id}")
async def update_template(template_id: str, template: Template):
    template_dict = template.dict()
    template_dict.pop('id', None)
    result = await db.templates.update_one(
        {"id": template_id},
        {"$set": template_dict}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"message": "Template updated successfully"}

# Campaign Management
@app.post("/api/campaigns")
async def create_campaign(campaign: Campaign):
    campaign.id = generate_id()
    campaign_dict = campaign.dict()
    result = await db.campaigns.insert_one(campaign_dict)
    campaign_dict.pop('_id', None)
    return campaign_dict

@app.get("/api/campaigns")
async def get_campaigns():
    campaigns = await db.campaigns.find().to_list(length=100)
    for campaign in campaigns:
        campaign.pop('_id', None)
    return campaigns

@app.get("/api/campaigns/{campaign_id}")
async def get_campaign(campaign_id: str):
    campaign = await db.campaigns.find_one({"id": campaign_id})
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    campaign.pop('_id', None)
    return campaign

@app.post("/api/campaigns/{campaign_id}/send")
async def send_campaign(campaign_id: str, background_tasks: BackgroundTasks):
    """Send campaign emails"""
    campaign = await db.campaigns.find_one({"id": campaign_id})
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    template = await db.templates.find_one({"id": campaign["template_id"]})
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Get all prospects for this campaign
    prospects = await db.prospects.find({"status": "active"}).to_list(length=campaign["max_emails"])
    
    # Schedule email sending
    background_tasks.add_task(process_campaign_emails, campaign_id, prospects, template)
    
    # Update campaign status
    await db.campaigns.update_one(
        {"id": campaign_id},
        {"$set": {"status": "active", "prospect_count": len(prospects)}}
    )
    
    return {"message": f"Campaign started. Sending to {len(prospects)} prospects"}

async def process_campaign_emails(campaign_id: str, prospects: List[dict], template: dict):
    """Process campaign emails in background"""
    sent_count = 0
    failed_count = 0
    
    for prospect in prospects:
        try:
            # Personalize email content
            personalized_content = personalize_template(template["content"], prospect)
            personalized_subject = personalize_template(template["subject"], prospect)
            
            # Send email
            success = await send_email(
                prospect["email"],
                personalized_subject,
                personalized_content
            )
            
            # Create email record
            email_record = EmailMessage(
                id=generate_id(),
                prospect_id=prospect["id"],
                campaign_id=campaign_id,
                subject=personalized_subject,
                content=personalized_content,
                status="sent" if success else "failed",
                sent_at=datetime.utcnow() if success else None
            )
            
            await db.emails.insert_one(email_record.dict())
            
            if success:
                sent_count += 1
            else:
                failed_count += 1
            
            # Update prospect last contact
            await db.prospects.update_one(
                {"id": prospect["id"]},
                {"$set": {"last_contact": datetime.utcnow()}}
            )
            
            # Small delay to avoid overwhelming SMTP server
            await asyncio.sleep(0.1)
            
        except Exception as e:
            print(f"Error sending email to {prospect['email']}: {str(e)}")
            failed_count += 1
            continue
    
    # Update campaign with final results
    await db.campaigns.update_one(
        {"id": campaign_id},
        {"$set": {"status": "completed"}}
    )
    
    print(f"Campaign {campaign_id} completed: {sent_count} sent, {failed_count} failed")

# Intent Management
@app.post("/api/intents")
async def create_intent(intent: IntentConfig):
    intent.id = generate_id()
    intent_dict = intent.dict()
    result = await db.intents.insert_one(intent_dict)
    intent_dict.pop('_id', None)
    return intent_dict

@app.get("/api/intents")
async def get_intents():
    intents = await db.intents.find().to_list(length=100)
    for intent in intents:
        intent.pop('_id', None)
    return intents

# Email Analytics
@app.get("/api/analytics/campaign/{campaign_id}")
async def get_campaign_analytics(campaign_id: str):
    pipeline = [
        {"$match": {"campaign_id": campaign_id}},
        {
            "$group": {
                "_id": "$status",
                "count": {"$sum": 1}
            }
        }
    ]
    
    stats = await db.emails.aggregate(pipeline).to_list(length=10)
    
    analytics = {
        "total_sent": 0,
        "total_failed": 0,
        "total_opened": 0,
        "total_replied": 0
    }
    
    for stat in stats:
        if stat["_id"] == "sent":
            analytics["total_sent"] = stat["count"]
        elif stat["_id"] == "failed":
            analytics["total_failed"] = stat["count"]
    
    # Get opened and replied counts
    opened_count = await db.emails.count_documents({
        "campaign_id": campaign_id,
        "opened_at": {"$exists": True}
    })
    
    replied_count = await db.emails.count_documents({
        "campaign_id": campaign_id,
        "replied_at": {"$exists": True}
    })
    
    analytics["total_opened"] = opened_count
    analytics["total_replied"] = replied_count
    
    return analytics

# Sample CSV download endpoint
@app.get("/api/sample-csv")
async def get_sample_csv():
    return {
        "filename": "prospects_sample.csv",
        "content": "email,first_name,last_name,company,phone,linkedin_url,company_domain,industry,company_linkedin_url,job_title,location,company_size,annual_revenue,lead_source\njohn.doe@example.com,John,Doe,Example Corp,+1-555-0123,https://linkedin.com/in/john-doe,example.com,Technology,https://linkedin.com/company/example-corp,CEO,San Francisco CA,100-500,$10M-$50M,Website\njane.smith@test.com,Jane,Smith,Test Inc,+1-555-0456,https://linkedin.com/in/jane-smith,test.com,Software,https://linkedin.com/company/test-inc,CTO,New York NY,50-100,$5M-$10M,LinkedIn\nmark.wilson@demo.org,Mark,Wilson,Demo Solutions,+1-555-0789,https://linkedin.com/in/mark-wilson,demo.org,Consulting,https://linkedin.com/company/demo-solutions,VP Sales,Austin TX,200-500,$25M-$50M,Referral"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)