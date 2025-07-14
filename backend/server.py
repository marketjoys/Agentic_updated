# AI Email Responder - Working Backend
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
import logging
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import asyncio
import re

# Configure logging
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="AI Email Responder", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class LoginRequest(BaseModel):
    username: str
    password: str

class EmailProvider(BaseModel):
    name: str
    provider_type: str
    email_address: str
    display_name: str = ""
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_use_tls: bool = True
    imap_host: str = ""
    imap_port: int = 993
    imap_username: str = ""
    imap_password: str = ""
    daily_send_limit: int = 500
    hourly_send_limit: int = 50
    is_default: bool = False
    skip_connection_test: bool = False

class Campaign(BaseModel):
    name: str
    template_id: str
    list_ids: List[str] = []
    email_provider_id: str = ""
    max_emails: int = 1000
    schedule_type: str = "immediate"
    start_time: Optional[str] = None
    follow_up_enabled: bool = True
    follow_up_intervals: List[int] = [3, 7, 14]
    follow_up_templates: List[str] = []

# Basic endpoints
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.post("/api/auth/login")
async def login(request: LoginRequest):
    if request.username == "testuser" and request.password == "testpass123":
        return {"access_token": "test_token_12345", "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/api/auth/register")
async def register(request: LoginRequest):
    if request.username and request.password:
        return {"access_token": "test_token_12345", "token_type": "bearer"}
    raise HTTPException(status_code=400, detail="Registration failed")

@app.get("/api/auth/me")
async def get_me():
    return {
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "is_active": True,
        "created_at": datetime.utcnow()
    }

@app.post("/api/auth/refresh")
async def refresh_token():
    # Return a new token for token refresh
    return {"access_token": "test_token_12345", "token_type": "bearer"}

@app.post("/api/auth/logout")
async def logout():
    # Simple logout endpoint
    return {"message": "Logged out successfully"}

# Mock data endpoints
@app.get("/api/campaigns")
async def get_campaigns():
    return [
        {
            "id": "1",
            "name": "Test Campaign",
            "status": "draft",
            "prospect_count": 10,
            "max_emails": 1000,
            "created_at": datetime.utcnow(),
            "schedule": None
        },
        {
            "id": "2",
            "name": "Welcome Series",
            "status": "active",
            "prospect_count": 50,
            "max_emails": 500,
            "created_at": datetime.utcnow(),
            "schedule": None
        }
    ]

@app.post("/api/campaigns")
async def create_campaign(campaign: Campaign):
    return {
        "id": "new_campaign_id",
        "name": campaign.name,
        "status": "draft",
        "prospect_count": 0,
        "max_emails": campaign.max_emails,
        "created_at": datetime.utcnow(),
        "message": "Campaign created successfully"
    }

@app.get("/api/email-providers")
async def get_email_providers():
    return [
        {
            "id": "1",
            "name": "Test Gmail Provider",
            "provider_type": "gmail",
            "email_address": "test@gmail.com",
            "is_active": True,
            "is_default": True,
            "daily_send_limit": 500,
            "hourly_send_limit": 50,
            "current_daily_count": 0,
            "current_hourly_count": 0,
            "last_sync": datetime.utcnow()
        },
        {
            "id": "2",
            "name": "Test Outlook Provider",
            "provider_type": "outlook",
            "email_address": "test@outlook.com",
            "is_active": True,
            "is_default": False,
            "daily_send_limit": 300,
            "hourly_send_limit": 30,
            "current_daily_count": 0,
            "current_hourly_count": 0,
            "last_sync": datetime.utcnow()
        }
    ]

@app.post("/api/email-providers")
async def create_email_provider(provider: EmailProvider):
    return {
        "id": "new_provider_id",
        "message": "Email provider created successfully",
        **provider.dict()
    }

@app.put("/api/email-providers/{provider_id}")
async def update_email_provider(provider_id: str, provider: EmailProvider):
    return {
        "id": provider_id,
        "message": "Email provider updated successfully",
        **provider.dict()
    }

@app.delete("/api/email-providers/{provider_id}")
async def delete_email_provider(provider_id: str):
    return {
        "id": provider_id,
        "message": "Email provider deleted successfully"
    }

@app.post("/api/email-providers/{provider_id}/test")
async def test_email_provider(provider_id: str):
    return {
        "id": provider_id,
        "message": "Connection test successful",
        "smtp_test": "passed",
        "imap_test": "passed"
    }

@app.post("/api/email-providers/{provider_id}/set-default")
async def set_default_email_provider(provider_id: str):
    return {
        "id": provider_id,
        "message": "Default provider updated successfully"
    }

@app.get("/api/lists")
async def get_lists():
    return [
        {
            "id": "1",
            "name": "Tech Startups",
            "description": "Technology startup companies",
            "color": "#3B82F6",
            "prospect_count": 5,
            "tags": ["tech", "startup", "b2b"],
            "created_at": datetime.utcnow()
        },
        {
            "id": "2",
            "name": "Finance Companies",
            "description": "Financial services companies",
            "color": "#10B981",
            "prospect_count": 3,
            "tags": ["finance", "services", "b2b"],
            "created_at": datetime.utcnow()
        },
        {
            "id": "3",
            "name": "Healthcare Organizations",
            "description": "Healthcare and medical organizations",
            "color": "#EF4444",
            "prospect_count": 2,
            "tags": ["healthcare", "medical", "b2b"],
            "created_at": datetime.utcnow()
        }
    ]

@app.get("/api/templates")
async def get_templates():
    return [
        {
            "id": "1",
            "name": "Welcome Email",
            "subject": "Welcome to Our Service, {{first_name}}!",
            "content": "Hello {{first_name}}, welcome to our service!",
            "type": "initial",
            "created_at": datetime.utcnow()
        },
        {
            "id": "2",
            "name": "Follow-up Day 3",
            "subject": "Quick follow-up regarding {{company}}",
            "content": "Hi {{first_name}}, I wanted to follow up about {{company}}...",
            "type": "follow_up",
            "created_at": datetime.utcnow()
        },
        {
            "id": "3",
            "name": "Follow-up Day 7",
            "subject": "Final follow-up for {{company}}",
            "content": "Hi {{first_name}}, this is my final follow-up about {{company}}...",
            "type": "follow_up",
            "created_at": datetime.utcnow()
        }
    ]

@app.get("/api/prospects")
async def get_prospects(skip: int = 0, limit: int = 100):
    return [
        {
            "id": "1",
            "email": "john.doe@techstartup.com",
            "first_name": "John",
            "last_name": "Doe",
            "company": "TechStartup Inc",
            "job_title": "CEO",
            "industry": "Technology",
            "status": "active",
            "created_at": datetime.utcnow()
        },
        {
            "id": "2",
            "email": "jane.smith@financegroup.com",
            "first_name": "Jane",
            "last_name": "Smith",
            "company": "Finance Group LLC",
            "job_title": "CFO",
            "industry": "Finance",
            "status": "active",
            "created_at": datetime.utcnow()
        },
        {
            "id": "3",
            "email": "mike.johnson@healthcorp.com",
            "first_name": "Mike",
            "last_name": "Johnson",
            "company": "Health Corp",
            "job_title": "Director of Operations",
            "industry": "Healthcare",
            "status": "active",
            "created_at": datetime.utcnow()
        }
    ]

@app.get("/api/intents")
async def get_intents():
    return [
        {
            "id": "1",
            "name": "Interested",
            "description": "Prospect shows interest in our service",
            "keywords": ["interested", "yes", "tell me more", "sounds good"],
            "auto_respond": True,
            "created_at": datetime.utcnow()
        },
        {
            "id": "2",
            "name": "Not Interested",
            "description": "Prospect is not interested",
            "keywords": ["not interested", "no thanks", "remove me"],
            "auto_respond": True,
            "created_at": datetime.utcnow()
        }
    ]

@app.get("/api/analytics/campaign/{campaign_id}")
async def get_campaign_analytics(campaign_id: str):
    return {
        "total_sent": 45,
        "total_failed": 2,
        "total_opened": 23,
        "total_replied": 5,
        "open_rate": 51.1,
        "reply_rate": 11.1,
        "campaign_id": campaign_id
    }

# Real-time endpoints
@app.get("/api/real-time/dashboard-metrics")
async def get_dashboard_metrics():
    return {
        "metrics": {
            "overview": {
                "total_prospects": 10,
                "total_campaigns": 2,
                "total_emails_sent": 47,
                "emails_today": 12,
                "active_campaigns": 1
            },
            "provider_stats": {
                "Test Gmail Provider": {
                    "type": "gmail",
                    "status": "active",
                    "emails_sent_today": 8,
                    "daily_limit": 500
                },
                "Test Outlook Provider": {
                    "type": "outlook",
                    "status": "active",
                    "emails_sent_today": 4,
                    "daily_limit": 300
                }
            },
            "recent_activity": [
                {
                    "id": "1",
                    "subject": "Welcome to Our Service",
                    "recipient": "john.doe@techstartup.com",
                    "status": "sent",
                    "created_at": datetime.utcnow().isoformat()
                }
            ]
        },
        "last_updated": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)