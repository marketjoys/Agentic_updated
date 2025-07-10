from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
import os
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

# Groq client (optional)
try:
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY")) if os.getenv("GROQ_API_KEY") else None
except Exception as e:
    print(f"Warning: Could not initialize Groq client: {e}")
    groq_client = None

# Security
security = HTTPBearer()

# Pydantic models
class Prospect(BaseModel):
    id: str = None
    email: EmailStr
    first_name: str
    last_name: str
    company: str = ""
    phone: str = ""
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
    prospect_count: int = 0
    max_emails: int = 1000
    schedule: Optional[datetime] = None
    status: str = "draft"  # draft, active, paused, completed
    follow_up_intervals: List[int] = [3, 7, 14]  # days
    follow_up_templates: List[str] = []
    created_at: datetime = datetime.utcnow()

class IntentConfig(BaseModel):
    id: str = None
    name: str
    description: str
    keywords: List[str] = []
    response_template: str = ""
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
            raise HTTPException(status_code=500, detail="SMTP configuration incomplete")
        
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
        return False

def personalize_template(template_content: str, prospect: dict) -> str:
    """Personalize template with prospect data"""
    template = Template(template_content)
    return template.render(
        first_name=prospect.get("first_name", ""),
        last_name=prospect.get("last_name", ""),
        company=prospect.get("company", ""),
        email=prospect.get("email", "")
    )

# API Routes

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Prospect Management
@app.post("/api/prospects")
async def create_prospect(prospect: Prospect):
    prospect.id = generate_id()
    prospect_dict = prospect.dict()
    result = await db.prospects.insert_one(prospect_dict)
    # Remove MongoDB's _id field and return our custom id
    prospect_dict.pop('_id', None)
    return prospect_dict

@app.get("/api/prospects")
async def get_prospects(skip: int = 0, limit: int = 100):
    prospects = await db.prospects.find().skip(skip).limit(limit).to_list(length=limit)
    # Remove MongoDB's _id field from all prospects
    for prospect in prospects:
        prospect.pop('_id', None)
    return prospects

@app.post("/api/prospects/upload")
async def upload_prospects(file: UploadFile = File(...)):
    """Upload prospects from CSV file"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be CSV format")
    
    content = await file.read()
    df = pd.read_csv(content)
    
    required_columns = ['email', 'first_name', 'last_name']
    if not all(col in df.columns for col in required_columns):
        raise HTTPException(status_code=400, detail=f"CSV must contain columns: {required_columns}")
    
    prospects = []
    for _, row in df.iterrows():
        prospect = Prospect(
            id=generate_id(),
            email=row['email'],
            first_name=row['first_name'],
            last_name=row['last_name'],
            company=row.get('company', ''),
            phone=row.get('phone', '')
        )
        prospects.append(prospect.dict())
    
    if prospects:
        await db.prospects.insert_many(prospects)
    
    return {"message": f"Uploaded {len(prospects)} prospects", "count": len(prospects)}

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
    
    # Get prospects for this campaign
    prospects = await db.prospects.find({"campaign_id": campaign_id}).to_list(length=campaign["max_emails"])
    
    # Schedule email sending
    background_tasks.add_task(process_campaign_emails, campaign_id, prospects, template)
    
    # Update campaign status
    await db.campaigns.update_one(
        {"id": campaign_id},
        {"$set": {"status": "active"}}
    )
    
    return {"message": f"Campaign started. Sending to {len(prospects)} prospects"}

async def process_campaign_emails(campaign_id: str, prospects: List[dict], template: dict):
    """Process campaign emails in background"""
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
            
            # Update prospect last contact
            await db.prospects.update_one(
                {"id": prospect["id"]},
                {"$set": {"last_contact": datetime.utcnow()}}
            )
            
            # Small delay to avoid overwhelming SMTP server
            await asyncio.sleep(1)
            
        except Exception as e:
            print(f"Error sending email to {prospect['email']}: {str(e)}")
            continue

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)