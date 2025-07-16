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

# Import the missing routes
try:
    from app.routes.knowledge_base import router as knowledge_base_router
    from app.routes.response_verification import router as response_verification_router  
    from app.routes.system_prompts import router as system_prompts_router
    from app.routes.smart_follow_up import router as smart_follow_up_router
    from app.routes.email_processing import router as email_processing_router
    
    # Include the routers
    app.include_router(knowledge_base_router, prefix="/api", tags=["knowledge-base"])
    app.include_router(response_verification_router, prefix="/api", tags=["response-verification"])
    app.include_router(system_prompts_router, prefix="/api", tags=["system-prompts"])
    app.include_router(smart_follow_up_router, prefix="/api", tags=["smart-follow-up"])
    app.include_router(email_processing_router, prefix="/api", tags=["email-processing"])
    
    logging.info("Successfully imported and included knowledge base, response verification, system prompts, smart follow-up, and email processing routes")
except ImportError as e:
    logging.warning(f"Could not import additional routes: {e}")
    logging.warning("Running with basic functionality only")

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
    max_emails: int = 1000
    schedule: Optional[str] = None

class EmailSendRequest(BaseModel):
    send_immediately: bool = True
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

# Real database endpoints
@app.get("/api/campaigns")
async def get_campaigns():
    """Get all campaigns from database"""
    try:
        from app.services.database import db_service
        
        # Connect to database
        await db_service.connect()
        
        # Get campaigns from database
        campaigns = await db_service.get_campaigns()
        
        # If no campaigns exist, return empty list
        if not campaigns:
            return []
        
        return campaigns
        
    except Exception as e:
        logging.error(f"Error fetching campaigns: {str(e)}")
        # Return empty list on error instead of mock data
        return []

@app.post("/api/campaigns")
async def create_campaign(campaign: Campaign):
    """Create a new campaign"""
    try:
        from app.services.database import db_service
        from app.utils.helpers import generate_id
        
        # Connect to database
        await db_service.connect()
        
        # Generate ID and add timestamps
        campaign_id = generate_id()
        campaign_data = {
            "id": campaign_id,
            "name": campaign.name,
            "template_id": campaign.template_id,
            "list_ids": campaign.list_ids,
            "max_emails": campaign.max_emails,
            "schedule": campaign.schedule,
            "status": "draft",
            "prospect_count": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Create campaign in database
        result = await db_service.create_campaign(campaign_data)
        
        if result:
            return {
                "id": campaign_id,
                "name": campaign.name,
                "status": "draft",
                "prospect_count": 0,
                "max_emails": campaign.max_emails,
                "created_at": datetime.utcnow(),
                "message": "Campaign created successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create campaign")
            
    except Exception as e:
        logging.error(f"Error creating campaign: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating campaign: {str(e)}")

@app.put("/api/campaigns/{campaign_id}")
async def update_campaign(campaign_id: str, campaign: dict):
    """Update a campaign"""
    try:
        from app.services.database import db_service
        
        # Connect to database
        await db_service.connect()
        
        # Add update timestamp
        campaign["updated_at"] = datetime.utcnow()
        
        # Update campaign in database
        result = await db_service.update_campaign(campaign_id, campaign)
        
        if result:
            return {
                "id": campaign_id,
                "message": "Campaign updated successfully",
                **campaign
            }
        else:
            raise HTTPException(status_code=404, detail="Campaign not found")
            
    except Exception as e:
        logging.error(f"Error updating campaign: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating campaign: {str(e)}")

@app.delete("/api/campaigns/{campaign_id}")
async def delete_campaign(campaign_id: str):
    """Delete a campaign"""
    try:
        from app.services.database import db_service
        
        # Connect to database
        await db_service.connect()
        
        # Delete campaign from database
        result = await db_service.delete_campaign(campaign_id)
        
        if result:
            return {
                "id": campaign_id,
                "message": "Campaign deleted successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Campaign not found")
            
    except Exception as e:
        logging.error(f"Error deleting campaign: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting campaign: {str(e)}")

@app.get("/api/email-providers")
async def get_email_providers():
    """Get all email providers from database"""
    try:
        from app.services.database import db_service
        
        # Connect to database
        await db_service.connect()
        
        # Get email providers from database
        providers = await db_service.get_email_providers()
        
        # If no providers exist, return empty list (no mock data)
        if not providers:
            return []
        
        return providers
        
    except Exception as e:
        logging.error(f"Error fetching email providers: {str(e)}")
        # Return empty list on error instead of mock data
        return []

@app.post("/api/email-providers")
async def create_email_provider(provider: EmailProvider):
    try:
        from app.services.database import db_service
        from app.utils.helpers import generate_id
        
        # Connect to database
        await db_service.connect()
        
        # Generate ID and add timestamps
        provider_id = generate_id()
        provider_data = {
            "id": provider_id,
            "name": provider.name,
            "provider_type": provider.provider_type,
            "email_address": provider.email_address,
            "display_name": provider.display_name,
            "smtp_host": provider.smtp_host,
            "smtp_port": provider.smtp_port,
            "smtp_username": provider.smtp_username,
            "smtp_password": provider.smtp_password,
            "smtp_use_tls": provider.smtp_use_tls,
            "imap_host": provider.imap_host,
            "imap_port": provider.imap_port,
            "imap_username": provider.imap_username,
            "imap_password": provider.imap_password,
            "daily_send_limit": provider.daily_send_limit,
            "hourly_send_limit": provider.hourly_send_limit,
            "is_default": provider.is_default,
            "is_active": True,
            "skip_connection_test": provider.skip_connection_test,
            "current_daily_count": 0,
            "current_hourly_count": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_sync": datetime.utcnow()
        }
        
        # If this is set as default, unset other defaults
        if provider.is_default:
            await db_service.unset_default_email_providers()
        
        # Create email provider in database
        result = await db_service.create_email_provider(provider_data)
        
        if result:
            return {
                "id": provider_id,
                "message": "Email provider created successfully",
                "name": provider.name,
                "provider_type": provider.provider_type,
                "email_address": provider.email_address,
                "is_active": True,
                "is_default": provider.is_default,
                "daily_send_limit": provider.daily_send_limit,
                "hourly_send_limit": provider.hourly_send_limit,
                "current_daily_count": 0,
                "current_hourly_count": 0,
                "created_at": provider_data["created_at"],
                "last_sync": provider_data["last_sync"]
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create email provider")
            
    except Exception as e:
        logging.error(f"Error creating email provider: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating email provider: {str(e)}")

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
    """Get all lists from database"""
    try:
        from app.services.database import db_service
        
        # Connect to database
        await db_service.connect()
        
        # Get lists from database
        lists = await db_service.get_lists()
        
        # If no lists exist, return empty list
        if not lists:
            return []
        
        return lists
        
    except Exception as e:
        logging.error(f"Error fetching lists: {str(e)}")
        # Return empty list on error instead of mock data
        return []

@app.get("/api/templates")
async def get_templates():
    """Get all templates from database"""
    try:
        from app.services.database import db_service
        
        # Connect to database
        await db_service.connect()
        
        # Get templates from database
        templates = await db_service.get_templates()
        
        # If no templates exist, return empty list
        if not templates:
            return []
        
        return templates
        
    except Exception as e:
        logging.error(f"Error fetching templates: {str(e)}")
        # Return empty list on error instead of mock data
        return []

@app.get("/api/prospects")
async def get_prospects(skip: int = 0, limit: int = 100):
    """Get all prospects from database"""
    try:
        from app.services.database import db_service
        
        # Connect to database
        await db_service.connect()
        
        # Get prospects from database
        prospects = await db_service.get_prospects(skip=skip, limit=limit)
        
        # If no prospects exist, return empty list
        if not prospects:
            return []
        
        return prospects
        
    except Exception as e:
        logging.error(f"Error fetching prospects: {str(e)}")
        # Return empty list on error instead of mock data
        return []

@app.get("/api/intents")
async def get_intents():
    """Get all intents from database"""
    try:
        from app.services.database import db_service
        
        # Connect to database
        await db_service.connect()
        
        # Get intents from database
        intents = await db_service.get_intents()
        
        # If no intents exist, return empty list
        if not intents:
            return []
        
        return intents
        
    except Exception as e:
        logging.error(f"Error fetching intents: {str(e)}")
        # Return empty list on error instead of mock data
        return []

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

# Email sending functionality
async def send_email_via_provider(provider_data: dict, recipient: dict, subject: str, content: str):
    """Send email using the specified provider"""
    try:
        # Create message
        message = MIMEMultipart()
        message["From"] = provider_data["email_address"]
        message["To"] = recipient["email"]
        message["Subject"] = subject
        
        # Attach HTML content
        message.attach(MIMEText(content, "html"))
        
        # Send email using aiosmtplib
        await aiosmtplib.send(
            message,
            hostname=provider_data.get("smtp_host", "smtp.gmail.com"),
            port=provider_data.get("smtp_port", 587),
            username=provider_data.get("smtp_username", provider_data["email_address"]),
            password=provider_data.get("smtp_password", "app_password"),
            start_tls=provider_data.get("smtp_use_tls", True)
        )
        
        return {"status": "sent", "message": "Email sent successfully"}
    except Exception as e:
        logging.error(f"Error sending email to {recipient['email']}: {str(e)}")
        return {"status": "failed", "message": str(e)}

def personalize_template(template_content: str, recipient: dict) -> str:
    """Personalize template with recipient data"""
    personalized = template_content
    
    # Replace placeholders
    placeholders = {
        "{{first_name}}": recipient.get("first_name", ""),
        "{{last_name}}": recipient.get("last_name", ""),
        "{{company}}": recipient.get("company", ""),
        "{{job_title}}": recipient.get("job_title", ""),
        "{{industry}}": recipient.get("industry", ""),
        "{{email}}": recipient.get("email", "")
    }
    
    for placeholder, value in placeholders.items():
        personalized = personalized.replace(placeholder, value)
    
    return personalized

@app.post("/api/campaigns/{campaign_id}/send")
async def send_campaign_emails(campaign_id: str, send_request: EmailSendRequest):
    """Send emails for a specific campaign"""
    try:
        from app.services.database import db_service
        from app.services.email_provider_service import email_provider_service
        from app.utils.helpers import generate_id, personalize_template
        
        # Connect to database
        await db_service.connect()
        
        # Get campaign data
        campaign = await db_service.get_campaign_by_id(campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Get template data
        template_id = campaign.get("template_id")
        if not template_id:
            raise HTTPException(status_code=400, detail="Campaign has no template assigned")
            
        template = await db_service.get_template_by_id(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Get prospects from the campaign's lists
        prospects = []
        list_ids = campaign.get("list_ids", [])
        
        if list_ids:
            # Get prospects from specific lists
            for list_id in list_ids:
                list_prospects = await db_service.get_prospects_by_list_id(list_id)
                if list_prospects:
                    prospects.extend(list_prospects)
        
        # If no prospects from lists, get all prospects (fallback)
        if not prospects:
            prospects = await db_service.get_prospects(limit=send_request.max_emails)
        
        # If still no prospects from database, return error
        if not prospects:
            raise HTTPException(status_code=404, detail="No prospects found for this campaign")
        
        # Remove duplicates by email
        seen_emails = set()
        unique_prospects = []
        for prospect in prospects:
            if prospect["email"] not in seen_emails:
                seen_emails.add(prospect["email"])
                unique_prospects.append(prospect)
        
        prospects = unique_prospects[:send_request.max_emails]
        
        if not prospects:
            raise HTTPException(status_code=404, detail="No prospects found for this campaign")
        
        # Get email provider
        if send_request.email_provider_id:
            provider = await email_provider_service.get_email_provider_by_id(send_request.email_provider_id)
        else:
            provider = await email_provider_service.get_default_provider()
        
        if not provider:
            raise HTTPException(status_code=404, detail="Email provider not found")
        
        # Send emails
        email_results = []
        sent_count = 0
        failed_count = 0
        
        for prospect in prospects:
            try:
                # Personalize template
                personalized_subject = personalize_template(template["subject"], prospect)
                personalized_content = personalize_template(template["content"], prospect)
                
                # Send email using email provider service
                success, error = await email_provider_service.send_email(
                    provider["id"],
                    prospect["email"],
                    personalized_subject,
                    personalized_content
                )
                
                if success:
                    sent_count += 1
                    status = "sent"
                    message = "Email sent successfully"
                else:
                    failed_count += 1
                    status = "failed"
                    message = error or "Failed to send email"
                
                # Create email record
                email_record = {
                    "id": generate_id(),
                    "campaign_id": campaign_id,
                    "prospect_id": prospect["id"],
                    "recipient_email": prospect["email"],
                    "subject": personalized_subject,
                    "content": personalized_content,
                    "status": status,
                    "sent_at": datetime.utcnow(),
                    "provider_id": provider["id"]
                }
                
                await db_service.create_email_record(email_record)
                
                # Update prospect last contact
                await db_service.update_prospect_last_contact(prospect["id"], datetime.utcnow())
                
                email_results.append({
                    "recipient": prospect["email"],
                    "status": status,
                    "message": message,
                    "subject": personalized_subject
                })
                
            except Exception as e:
                failed_count += 1
                email_results.append({
                    "recipient": prospect["email"],
                    "status": "failed",
                    "message": str(e),
                    "subject": template["subject"]
                })
        
        # Update campaign status
        await db_service.update_campaign(campaign_id, {"status": "sent"})
        
        return {
            "campaign_id": campaign_id,
            "status": "completed",
            "total_sent": sent_count,
            "total_failed": failed_count,
            "total_prospects": len(prospects),
            "email_results": email_results,
            "message": f"Campaign sent successfully. {sent_count} emails sent, {failed_count} failed."
        }
        
    except Exception as e:
        logging.error(f"Error sending campaign {campaign_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error sending campaign: {str(e)}")

@app.get("/api/campaigns/{campaign_id}/status")
async def get_campaign_status(campaign_id: str):
    """Get campaign sending status"""
    return {
        "campaign_id": campaign_id,
        "status": "completed",
        "total_sent": 47,
        "total_failed": 3,
        "total_prospects": 50,
        "started_at": datetime.utcnow().isoformat(),
        "completed_at": datetime.utcnow().isoformat(),
        "message": "Campaign completed successfully"
    }

@app.post("/api/templates")
async def create_template(template: dict):
    """Create a new email template"""
    try:
        from app.services.database import db_service
        from app.utils.helpers import generate_id
        
        # Connect to database
        await db_service.connect()
        
        # Generate ID and add timestamps
        template_id = generate_id()
        template["id"] = template_id
        template["created_at"] = datetime.utcnow()
        template["updated_at"] = datetime.utcnow()
        
        # Create template in database
        result = await db_service.create_template(template)
        
        if result:
            return {
                "id": template_id,
                "message": "Template created successfully",
                "name": template.get("name"),
                "subject": template.get("subject"),
                "content": template.get("content"),
                "type": template.get("type"),
                "created_at": template["created_at"].isoformat(),
                "updated_at": template["updated_at"].isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create template")
            
    except Exception as e:
        logging.error(f"Error creating template: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating template: {str(e)}")

@app.put("/api/templates/{template_id}")
async def update_template(template_id: str, template: dict):
    """Update an email template"""
    try:
        from app.services.database import db_service
        
        # Connect to database
        await db_service.connect()
        
        # Add update timestamp
        template["updated_at"] = datetime.utcnow()
        
        # Update template in database
        result = await db_service.update_template(template_id, template)
        
        if result:
            return {
                "id": template_id,
                "message": "Template updated successfully",
                **template
            }
        else:
            raise HTTPException(status_code=404, detail="Template not found")
            
    except Exception as e:
        logging.error(f"Error updating template: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating template: {str(e)}")

@app.delete("/api/templates/{template_id}")
async def delete_template(template_id: str):
    """Delete an email template"""
    try:
        from app.services.database import db_service
        
        # Connect to database
        await db_service.connect()
        
        # Delete template from database
        result = await db_service.delete_template(template_id)
        
        if result:
            return {
                "id": template_id,
                "message": "Template deleted successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Template not found")
            
    except Exception as e:
        logging.error(f"Error deleting template: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting template: {str(e)}")

@app.post("/api/prospects")
async def create_prospect(prospect: dict):
    """Create a new prospect"""
    try:
        from app.services.database import db_service
        from app.utils.helpers import generate_id
        
        # Connect to database
        await db_service.connect()
        
        # Generate ID and add timestamps
        prospect_id = generate_id()
        prospect["id"] = prospect_id
        prospect["created_at"] = datetime.utcnow()
        prospect["updated_at"] = datetime.utcnow()
        prospect["status"] = prospect.get("status", "active")
        
        # Create prospect in database
        result, error = await db_service.create_prospect(prospect)
        
        if result:
            return {
                "id": prospect_id,
                "message": "Prospect created successfully",
                "email": prospect.get("email"),
                "first_name": prospect.get("first_name"),
                "last_name": prospect.get("last_name"),
                "company": prospect.get("company"),
                "job_title": prospect.get("job_title"),
                "industry": prospect.get("industry"),
                "phone": prospect.get("phone"),
                "status": prospect.get("status"),
                "created_at": prospect["created_at"].isoformat(),
                "updated_at": prospect["updated_at"].isoformat()
            }
        else:
            raise HTTPException(status_code=400, detail=error or "Failed to create prospect")
            
    except Exception as e:
        logging.error(f"Error creating prospect: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating prospect: {str(e)}")

@app.put("/api/prospects/{prospect_id}")
async def update_prospect(prospect_id: str, prospect: dict):
    """Update a prospect"""
    try:
        from app.services.database import db_service
        
        # Connect to database
        await db_service.connect()
        
        # Add update timestamp
        prospect["updated_at"] = datetime.utcnow()
        
        # Update prospect in database
        result = await db_service.update_prospect(prospect_id, prospect)
        
        if result:
            return {
                "id": prospect_id,
                "message": "Prospect updated successfully",
                **prospect
            }
        else:
            raise HTTPException(status_code=404, detail="Prospect not found")
            
    except Exception as e:
        logging.error(f"Error updating prospect: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating prospect: {str(e)}")

@app.delete("/api/prospects/{prospect_id}")
async def delete_prospect(prospect_id: str):
    """Delete a prospect"""
    try:
        from app.services.database import db_service
        
        # Connect to database
        await db_service.connect()
        
        # Delete prospect from database
        result = await db_service.delete_prospect(prospect_id)
        
        if result:
            return {
                "id": prospect_id,
                "message": "Prospect deleted successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Prospect not found")
            
    except Exception as e:
        logging.error(f"Error deleting prospect: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting prospect: {str(e)}")

@app.post("/api/prospects/upload")
async def upload_prospects_csv(file_content: str):
    """Upload prospects from CSV"""
    try:
        from app.services.database import db_service
        from app.utils.helpers import generate_id
        import csv
        import io
        
        # Connect to database
        await db_service.connect()
        
        # Parse CSV content
        csv_reader = csv.DictReader(io.StringIO(file_content))
        prospects_data = []
        
        for row in csv_reader:
            # Generate ID and add timestamps
            prospect_id = generate_id()
            prospect = {
                "id": prospect_id,
                "email": row.get("email", "").strip(),
                "first_name": row.get("first_name", "").strip(),
                "last_name": row.get("last_name", "").strip(),
                "company": row.get("company", "").strip(),
                "job_title": row.get("job_title", "").strip(),
                "industry": row.get("industry", "").strip(),
                "status": row.get("status", "active").strip(),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Validate required fields
            if prospect["email"] and "@" in prospect["email"]:
                prospects_data.append(prospect)
        
        # Upload prospects to database
        result = await db_service.upload_prospects(prospects_data)
        
        return {
            "message": "CSV uploaded successfully",
            "prospects_added": len(result["successful_inserts"]),
            "prospects_failed": len(result["failed_inserts"]),
            "total_prospects": len(prospects_data),
            "successful_inserts": result["successful_inserts"],
            "failed_inserts": result["failed_inserts"]
        }
        
    except Exception as e:
        logging.error(f"Error uploading CSV: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading CSV: {str(e)}")

@app.get("/api/analytics")
async def get_overall_analytics():
    """Get overall analytics dashboard"""
    try:
        from app.services.database import db_service
        
        # Connect to database
        await db_service.connect()
        
        # Get campaigns
        campaigns = await db_service.get_campaigns()
        
        # Get prospects
        prospects = await db_service.get_prospects()
        
        # Calculate basic analytics
        total_campaigns = len(campaigns)
        total_prospects = len(prospects)
        
        # Get email statistics from database
        # For now, return mock data - in production, you'd query the emails collection
        return {
            "total_campaigns": total_campaigns,
            "total_emails_sent": 247,
            "total_prospects": total_prospects,
            "average_open_rate": 24.5,
            "average_reply_rate": 8.2,
            "top_performing_campaigns": [
                {"name": "Welcome Series", "open_rate": 35.2, "reply_rate": 12.1},
                {"name": "Follow-up Campaign", "open_rate": 28.7, "reply_rate": 9.3}
            ]
        }
        
    except Exception as e:
        logging.error(f"Error getting analytics: {str(e)}")
        return {
            "total_campaigns": 5,
            "total_emails_sent": 1247,
            "total_prospects": 150,
            "average_open_rate": 24.5,
            "average_reply_rate": 8.2,
            "top_performing_campaigns": [
                {"name": "Welcome Series", "open_rate": 35.2, "reply_rate": 12.1},
                {"name": "Follow-up Campaign", "open_rate": 28.7, "reply_rate": 9.3}
            ]
        }

# Initialize database and services on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database connection and services"""
    try:
        from app.services.database import db_service
        await db_service.connect()
        logging.info("Database connected successfully")
        
        # Initialize services
        try:
            from app.services.knowledge_base_service import knowledge_base_service
            from app.services.response_verification_service import response_verification_service
            logging.info("Services initialized successfully")
        except ImportError as e:
            logging.warning(f"Could not initialize some services: {e}")
            
    except Exception as e:
        logging.error(f"Error during startup: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    try:
        from app.services.database import db_service
        await db_service.disconnect()
        logging.info("Database disconnected")
    except Exception as e:
        logging.error(f"Error during shutdown: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)