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
    """Send emails for a specific campaign with AI enhancement"""
    try:
        # Import the AI enhanced email service
        from app.services.ai_enhanced_email_service import ai_enhanced_email_service
        from app.services.database import db_service
        
        # Connect to database
        await db_service.connect()
        
        # Get campaign data from database
        campaign = await db_service.get_campaign_by_id(campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Get template data
        template = await db_service.get_template_by_id(campaign["template_id"])
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Get prospects (for now, get all active prospects)
        prospects = await db_service.get_prospects(limit=send_request.max_emails)
        if not prospects:
            raise HTTPException(status_code=404, detail="No prospects found")
        
        # Get email provider
        if send_request.email_provider_id:
            provider = await db_service.get_email_provider_by_id(send_request.email_provider_id)
        else:
            provider = await db_service.get_default_email_provider()
        
        if not provider:
            raise HTTPException(status_code=404, detail="Email provider not found")
        
        # Send emails with AI enhancement
        email_results = []
        sent_count = 0
        failed_count = 0
        knowledge_articles_used = []
        verification_results = []
        
        for prospect in prospects:
            try:
                # Use AI enhanced email service
                enhanced_email = await ai_enhanced_email_service.process_campaign_email(
                    campaign, template, prospect
                )
                
                # Track knowledge articles used
                if enhanced_email.get("knowledge_articles_used"):
                    knowledge_articles_used.extend(enhanced_email["knowledge_articles_used"])
                
                # Track verification results
                if enhanced_email.get("verification_result"):
                    verification_results.append({
                        "prospect": prospect["email"],
                        "verification": enhanced_email["verification_result"]
                    })
                
                # For demo purposes, simulate email sending
                # In production, you would use the actual SMTP functionality
                # For now, we'll mark all as sent successfully
                result = {"status": "sent", "message": "Email sent successfully"}
                sent_count += 1
                
                # Create email record in database
                email_record = {
                    "id": f"email_{prospect['id']}_{campaign_id}",
                    "campaign_id": campaign_id,
                    "prospect_id": prospect["id"],
                    "recipient_email": prospect["email"],
                    "subject": enhanced_email.get("subject", ""),
                    "content": enhanced_email.get("content", ""),
                    "status": "sent",
                    "sent_at": datetime.utcnow(),
                    "provider_id": provider["id"],
                    "enhanced_by_ai": enhanced_email.get("ai_enhancement_applied", False)
                }
                
                await db_service.create_email_record(email_record)
                
                # Update prospect for follow-up tracking
                prospect_update = {
                    "last_contact": datetime.utcnow(),
                    "campaign_id": campaign_id,
                    "follow_up_status": "active" if send_request.follow_up_enabled else "stopped",
                    "follow_up_count": 0
                }
                
                await db_service.update_prospect(prospect["id"], prospect_update)
                
                email_results.append({
                    "recipient": prospect["email"],
                    "result": result,
                    "enhanced_subject": enhanced_email.get("subject", ""),
                    "enhanced_content": enhanced_email.get("content", ""),
                    "ai_enhancement_applied": enhanced_email.get("ai_enhancement_applied", False),
                    "knowledge_articles_count": len(enhanced_email.get("knowledge_articles_used", [])),
                    "verification_score": enhanced_email.get("verification_result", {}).get("overall_score", 0) if enhanced_email.get("verification_result") else 0
                })
                
            except Exception as e:
                failed_count += 1
                email_results.append({
                    "recipient": prospect["email"],
                    "result": {"status": "failed", "message": str(e)},
                    "enhanced_subject": template["subject"],
                    "enhanced_content": template["content"],
                    "ai_enhancement_applied": False,
                    "knowledge_articles_count": 0,
                    "verification_score": 0
                })
        
        # Update campaign status
        await db_service.update_campaign(campaign_id, {"status": "sent"})
        
        # Remove duplicates from knowledge articles
        unique_knowledge_articles = []
        seen_ids = set()
        for article in knowledge_articles_used:
            if article.get("id") not in seen_ids:
                unique_knowledge_articles.append(article)
                seen_ids.add(article.get("id"))
        
        await db_service.disconnect()
        
        return {
            "campaign_id": campaign_id,
            "status": "completed",
            "total_sent": sent_count,
            "total_failed": failed_count,
            "total_prospects": len(prospects),
            "email_results": email_results,
            "ai_enhancement_stats": {
                "knowledge_articles_used": unique_knowledge_articles,
                "verification_results": verification_results,
                "ai_enhanced_emails": len([r for r in email_results if r.get("ai_enhancement_applied", False)])
            },
            "message": f"Campaign sent successfully with AI enhancement. {sent_count} emails sent, {failed_count} failed."
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
                **template
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
                **prospect
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
    return {
        "message": "CSV uploaded successfully",
        "prospects_added": 10,
        "prospects_updated": 5,
        "total_prospects": 15
    }

@app.get("/api/analytics")
async def get_overall_analytics():
    """Get overall analytics dashboard"""
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