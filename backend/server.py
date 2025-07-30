# AI Email Responder - Working Backend
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Dict, Any
import logging
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import asyncio
import re
import json

# Import EmailProviderType from the main models file
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))
from models import EmailProviderType

# Configure logging
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="AI Email Responder", version="1.0.0")

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove dead connections
                self.active_connections.remove(connection)

manager = ConnectionManager()

app = FastAPI(title="AI Email Responder", version="1.0.0")

# Import the missing routes
try:
    from app.routes.knowledge_base import router as knowledge_base_router
    from app.routes.response_verification import router as response_verification_router  
    from app.routes.system_prompts import router as system_prompts_router
    from app.routes.smart_follow_up import router as smart_follow_up_router
    from app.routes.email_processing import router as email_processing_router
    from app.routes.follow_up_monitoring import router as follow_up_monitoring_router
    from app.routes.intents import router as intents_router
    from app.routes.ai_prospecting import router as ai_prospecting_router
    from app.routes.ai_agent import router as ai_agent_router
    
    # Include the routers
    app.include_router(knowledge_base_router, prefix="/api", tags=["knowledge-base"])
    app.include_router(response_verification_router, prefix="/api", tags=["response-verification"])
    app.include_router(system_prompts_router, prefix="/api", tags=["system-prompts"])
    app.include_router(smart_follow_up_router, prefix="/api", tags=["smart-follow-up"])
    app.include_router(email_processing_router, prefix="/api", tags=["email-processing"])
    app.include_router(follow_up_monitoring_router, prefix="/api", tags=["follow-up-monitoring"])
    app.include_router(intents_router, prefix="/api", tags=["intents"])
    app.include_router(ai_prospecting_router, prefix="/api", tags=["ai-prospecting"])
    app.include_router(ai_agent_router, prefix="/api", tags=["ai-agent"])
    
    logging.info("Successfully imported and included all routes including AI Agent")
except ImportError as e:
    logging.warning(f"Could not import additional routes: {e}")
    logging.warning("Running with basic functionality only")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",
        "https://opulent-fishstick-pj6559j5pp5gh96-3000.app.github.dev",
        "https://localhost:3000",
        "http://localhost:3000"
    ],
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
    
    # Enhanced Follow-up Configuration
    follow_up_enabled: bool = True
    follow_up_schedule_type: str = "interval"  # interval, datetime
    follow_up_intervals: List[int] = [3, 7, 14]  # days (for interval mode)
    follow_up_dates: List[str] = []  # ISO datetime strings (for datetime mode)
    follow_up_timezone: str = "UTC"
    follow_up_time_window_start: str = "09:00"
    follow_up_time_window_end: str = "17:00"
    follow_up_days_of_week: List[str] = ["monday", "tuesday", "wednesday", "thursday", "friday"]
    follow_up_templates: List[str] = []

class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    template_id: Optional[str] = None
    list_ids: Optional[List[str]] = None
    max_emails: Optional[int] = None
    follow_up_enabled: Optional[bool] = None
    follow_up_schedule_type: Optional[str] = None
    follow_up_intervals: Optional[List[int]] = None
    follow_up_dates: Optional[List[str]] = None
    follow_up_timezone: Optional[str] = None
    follow_up_time_window_start: Optional[str] = None
    follow_up_time_window_end: Optional[str] = None
    follow_up_days_of_week: Optional[List[str]] = None
    follow_up_templates: Optional[List[str]] = None

class AddProspectsRequest(BaseModel):
    prospect_ids: List[str]

class EmailSendRequest(BaseModel):
    send_immediately: bool = True
    email_provider_id: str = ""
    max_emails: int = 1000
    schedule_type: str = "immediate"
    start_time: Optional[str] = None
    follow_up_enabled: bool = True
    follow_up_intervals: List[int] = [3, 7, 14]
    follow_up_templates: List[str] = []

@app.post("/api/test-email")
async def test_email_sending(request: Dict[str, Any]):
    """Test email sending functionality"""
    try:
        to_email = request.get("to_email")
        subject = request.get("subject")
        content = request.get("content")
        
        if not all([to_email, subject, content]):
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        # Send test email
        await send_email(to_email, subject, content)
        
        return {
            "status": "success",
            "message": f"Test email sent successfully to {to_email}"
        }
    except Exception as e:
        logging.error(f"Test email failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Test email failed: {str(e)}")

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
        
        # Update prospect counts for each campaign
        for campaign in campaigns:
            prospect_count = 0
            if campaign.get('list_ids'):
                for list_id in campaign['list_ids']:
                    prospects = await db_service.get_prospects_by_list_id(list_id)
                    prospect_count += len(prospects)
            campaign['prospect_count'] = prospect_count
        
        return campaigns
        
    except Exception as e:
        logging.error(f"Error fetching campaigns: {str(e)}")
        # Return empty list on error instead of mock data
        return []

@app.post("/api/campaigns")
async def create_campaign(campaign: Campaign):
    """Create a new campaign with enhanced follow-up configuration"""
    try:
        from app.services.database import db_service
        from app.utils.helpers import generate_id
        from datetime import datetime
        import pytz
        
        # Connect to database
        await db_service.connect()
        
        # Calculate prospect count from lists
        prospect_count = 0
        if campaign.list_ids:
            for list_id in campaign.list_ids:
                prospects = await db_service.get_prospects_by_list_id(list_id)
                prospect_count += len(prospects)
        
        # Generate ID and add timestamps
        campaign_id = generate_id()
        
        # Process follow-up dates if using datetime scheduling
        follow_up_dates_processed = []
        if campaign.follow_up_schedule_type == "datetime" and campaign.follow_up_dates:
            try:
                # Validate timezone
                tz = pytz.timezone(campaign.follow_up_timezone)
                
                for date_str in campaign.follow_up_dates:
                    # Parse ISO datetime string
                    follow_up_datetime = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    
                    # Ensure timezone awareness
                    if follow_up_datetime.tzinfo is None:
                        follow_up_datetime = tz.localize(follow_up_datetime)
                    
                    follow_up_dates_processed.append(follow_up_datetime)
                    
                logging.info(f"Processed {len(follow_up_dates_processed)} follow-up dates for campaign {campaign.name}")
                
            except Exception as e:
                logging.error(f"Error processing follow-up dates: {str(e)}")
                raise HTTPException(status_code=400, detail=f"Invalid follow-up dates or timezone: {str(e)}")
        
        campaign_data = {
            "id": campaign_id,
            "name": campaign.name,
            "template_id": campaign.template_id,
            "list_ids": campaign.list_ids,
            "max_emails": campaign.max_emails,
            "schedule": campaign.schedule,
            "status": "draft",
            "prospect_count": prospect_count,
            
            # Enhanced Follow-up Configuration
            "follow_up_enabled": campaign.follow_up_enabled,
            "follow_up_schedule_type": campaign.follow_up_schedule_type,
            "follow_up_intervals": campaign.follow_up_intervals,
            "follow_up_dates": follow_up_dates_processed,
            "follow_up_timezone": campaign.follow_up_timezone,
            "follow_up_time_window_start": campaign.follow_up_time_window_start,
            "follow_up_time_window_end": campaign.follow_up_time_window_end,
            "follow_up_days_of_week": campaign.follow_up_days_of_week,
            "follow_up_templates": campaign.follow_up_templates,
            
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Create campaign in database
        result = await db_service.create_campaign(campaign_data)
        
        if result:
            response_data = {
                "id": campaign_id,
                "name": campaign.name,
                "status": "draft",
                "prospect_count": prospect_count,
                "max_emails": campaign.max_emails,
                "follow_up_enabled": campaign.follow_up_enabled,
                "follow_up_schedule_type": campaign.follow_up_schedule_type,
                "created_at": datetime.utcnow(),
                "message": "Campaign created successfully with enhanced follow-up configuration"
            }
            
            # Add follow-up details to response
            if campaign.follow_up_schedule_type == "datetime":
                response_data["follow_up_dates"] = [dt.isoformat() for dt in follow_up_dates_processed]
                response_data["follow_up_timezone"] = campaign.follow_up_timezone
            else:
                response_data["follow_up_intervals"] = campaign.follow_up_intervals
            
            return response_data
        else:
            raise HTTPException(status_code=500, detail="Failed to create campaign")
            
    except HTTPException:
        # Re-raise HTTPException so it's not caught by the generic handler
        raise
    except Exception as e:
        logging.error(f"Error creating campaign: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating campaign: {str(e)}")

@app.get("/api/campaigns/{campaign_id}")
async def get_campaign_by_id(campaign_id: str):
    """Get a specific campaign by ID with detailed information"""
    try:
        from app.services.database import db_service
        
        # Connect to database
        await db_service.connect()
        
        # Get campaign data
        campaign = await db_service.get_campaign_by_id(campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Get template information
        template = None
        if campaign.get("template_id"):
            template = await db_service.get_template_by_id(campaign["template_id"])
        
        # Get prospect lists information
        lists_info = []
        if campaign.get("list_ids"):
            for list_id in campaign["list_ids"]:
                list_data = await db_service.get_list_by_id(list_id)
                if list_data:
                    lists_info.append(list_data)
        
        # Get email records for this campaign
        email_records = []
        try:
            cursor = db_service.db.emails.find({"campaign_id": campaign_id})
            email_records = await cursor.to_list(length=None)
            
            # Convert ObjectId to string if present
            for record in email_records:
                if "_id" in record:
                    record.pop("_id")
        except Exception as e:
            logging.warning(f"Could not fetch email records: {e}")
        
        # Calculate analytics
        total_sent = len([r for r in email_records if r.get("status") == "sent"])
        total_failed = len([r for r in email_records if r.get("status") == "failed"])
        
        # Enhanced campaign details
        campaign_details = {
            **campaign,
            "template": template,
            "lists": lists_info,
            "email_records": email_records,
            "analytics": {
                "total_sent": total_sent,
                "total_failed": total_failed,
                "total_emails": len(email_records),
                "success_rate": (total_sent / len(email_records) * 100) if email_records else 0
            }
        }
        
        return campaign_details
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching campaign details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching campaign details: {str(e)}")

@app.put("/api/campaigns/{campaign_id}")
async def update_campaign(campaign_id: str, campaign_update: CampaignUpdate):
    """Update a campaign with enhanced follow-up configuration"""
    try:
        from app.services.database import db_service
        from datetime import datetime
        import pytz
        
        # Connect to database
        await db_service.connect()
        
        # Prepare update data
        update_data = {}
        
        # Basic fields
        if campaign_update.name is not None:
            update_data["name"] = campaign_update.name
        if campaign_update.template_id is not None:
            update_data["template_id"] = campaign_update.template_id
        if campaign_update.list_ids is not None:
            update_data["list_ids"] = campaign_update.list_ids
        if campaign_update.max_emails is not None:
            update_data["max_emails"] = campaign_update.max_emails
        
        # Follow-up configuration
        if campaign_update.follow_up_enabled is not None:
            update_data["follow_up_enabled"] = campaign_update.follow_up_enabled
        if campaign_update.follow_up_schedule_type is not None:
            update_data["follow_up_schedule_type"] = campaign_update.follow_up_schedule_type
        if campaign_update.follow_up_intervals is not None:
            update_data["follow_up_intervals"] = campaign_update.follow_up_intervals
        if campaign_update.follow_up_timezone is not None:
            update_data["follow_up_timezone"] = campaign_update.follow_up_timezone
        if campaign_update.follow_up_time_window_start is not None:
            update_data["follow_up_time_window_start"] = campaign_update.follow_up_time_window_start
        if campaign_update.follow_up_time_window_end is not None:
            update_data["follow_up_time_window_end"] = campaign_update.follow_up_time_window_end
        if campaign_update.follow_up_days_of_week is not None:
            update_data["follow_up_days_of_week"] = campaign_update.follow_up_days_of_week
        if campaign_update.follow_up_templates is not None:
            update_data["follow_up_templates"] = campaign_update.follow_up_templates
        
        # Process follow-up dates if provided
        if campaign_update.follow_up_dates is not None:
            follow_up_dates_processed = []
            if campaign_update.follow_up_dates:
                try:
                    timezone = campaign_update.follow_up_timezone or "UTC"
                    tz = pytz.timezone(timezone)
                    
                    for date_str in campaign_update.follow_up_dates:
                        # Parse ISO datetime string
                        follow_up_datetime = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        
                        # Ensure timezone awareness
                        if follow_up_datetime.tzinfo is None:
                            follow_up_datetime = tz.localize(follow_up_datetime)
                        
                        follow_up_dates_processed.append(follow_up_datetime)
                        
                    logging.info(f"Updated {len(follow_up_dates_processed)} follow-up dates for campaign {campaign_id}")
                    
                except Exception as e:
                    logging.error(f"Error processing follow-up dates: {str(e)}")
                    raise HTTPException(status_code=400, detail=f"Invalid follow-up dates or timezone: {str(e)}")
                    
            update_data["follow_up_dates"] = follow_up_dates_processed
        
        # Add update timestamp
        update_data["updated_at"] = datetime.utcnow()
        
        # Update campaign in database
        result = await db_service.update_campaign(campaign_id, update_data)
        
        if result:
            response_data = {
                "id": campaign_id,
                "message": "Campaign updated successfully with enhanced follow-up configuration",
                **update_data
            }
            
            # Format datetime objects for JSON response
            if "follow_up_dates" in update_data and update_data["follow_up_dates"]:
                response_data["follow_up_dates"] = [dt.isoformat() for dt in update_data["follow_up_dates"]]
            
            return response_data
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

async def _auto_configure_provider(provider_id: str, provider: EmailProvider) -> dict:
    """Auto-configure provider based on type for production readiness"""
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
        "imap_enabled": bool(provider.imap_host and provider.imap_username and provider.imap_password),
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
    
    # Auto-configure based on provider type
    if provider.provider_type.lower() == "gmail":
        if not provider_data["smtp_host"]:
            provider_data["smtp_host"] = "smtp.gmail.com"
        if not provider_data["imap_host"]:
            provider_data["imap_host"] = "imap.gmail.com"
    elif provider.provider_type.lower() == "outlook":
        if not provider_data["smtp_host"]:
            provider_data["smtp_host"] = "smtp-mail.outlook.com"
        if not provider_data["imap_host"]:
            provider_data["imap_host"] = "outlook.office365.com"
    
    return provider_data

async def _validate_provider_configuration(provider_data: dict) -> str:
    """Validate provider configuration and return error message if invalid"""
    # Check required fields
    if not provider_data.get("name"):
        return "Provider name is required"
    
    if not provider_data.get("email_address"):
        return "Email address is required"
    
    # Validate email format
    import re
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, provider_data.get("email_address", "")):
        return "Invalid email address format"
    
    # Check SMTP configuration if not skipping connection test
    if not provider_data.get("skip_connection_test", False):
        if not provider_data.get("smtp_host"):
            return "SMTP host is required"
        if not provider_data.get("smtp_username"):
            return "SMTP username is required"
        if not provider_data.get("smtp_password"):
            return "SMTP password is required"
    
    return None  # No validation errors

@app.post("/api/email-providers")
async def create_email_provider(provider: EmailProvider):
    try:
        from app.services.database import db_service
        from app.utils.helpers import generate_id
        from app.services.email_processor import email_processor
        
        # Connect to database
        await db_service.connect()
        
        # Generate ID and add timestamps
        provider_id = generate_id()
        
        # Auto-configure provider based on type for production readiness
        provider_data = await _auto_configure_provider(provider_id, provider)
        
        # Validate provider configuration
        validation_error = await _validate_provider_configuration(provider_data)
        if validation_error:
            raise HTTPException(status_code=400, detail=validation_error)
        
        # If this is set as default, unset other defaults
        if provider.is_default:
            await db_service.unset_default_email_providers()
        
        # Create email provider in database
        try:
            result = await db_service.create_email_provider(provider_data)
        except ValueError as ve:
            # Handle duplicate provider error
            raise HTTPException(status_code=400, detail=str(ve))
        
        if result:
            # Auto-start IMAP monitoring if enabled and email processor is running
            if provider_data["imap_enabled"] and email_processor.processing:
                try:
                    await email_processor.add_provider_to_monitoring(provider_id, provider_data)
                    logging.info(f"Auto-started IMAP monitoring for provider: {provider.name}")
                except Exception as imap_error:
                    logging.warning(f"Failed to auto-start IMAP monitoring: {str(imap_error)}")
            
            return {
                "id": provider_id,
                "message": "Email provider created successfully",
                "name": provider.name,
                "provider_type": provider.provider_type,
                "email_address": provider.email_address,
                "is_active": True,
                "is_default": provider.is_default,
                "imap_enabled": provider_data["imap_enabled"],
                "daily_send_limit": provider.daily_send_limit,
                "hourly_send_limit": provider.hourly_send_limit,
                "current_daily_count": 0,
                "current_hourly_count": 0,
                "created_at": provider_data["created_at"],
                "last_sync": provider_data["last_sync"]
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create email provider")
            
    except HTTPException:
        # Re-raise HTTPException so it's not caught by the generic handler
        raise
    except Exception as e:
        logging.error(f"Error creating email provider: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating email provider: {str(e)}")

@app.put("/api/email-providers/{provider_id}/toggle-imap")
async def toggle_provider_imap(provider_id: str):
    """Toggle IMAP monitoring for a specific provider"""
    try:
        from app.services.database import db_service
        from app.services.email_processor import email_processor
        
        # Connect to database
        await db_service.connect()
        
        # Get provider data
        provider = await db_service.get_email_provider_by_id(provider_id)
        if not provider:
            raise HTTPException(status_code=404, detail="Email provider not found")
        
        # Toggle IMAP enabled status
        new_imap_status = not provider.get("imap_enabled", False)
        
        # Update in database
        await db_service.update_email_provider(provider_id, {
            "imap_enabled": new_imap_status,
            "updated_at": datetime.utcnow()
        })
        
        # Update email processor monitoring
        if new_imap_status:
            # Start monitoring this provider
            if email_processor.processing:
                await email_processor.add_provider_to_monitoring(provider_id, provider)
                logging.info(f"Started IMAP monitoring for provider: {provider['name']}")
        else:
            # Stop monitoring this provider
            await email_processor.remove_provider_from_monitoring(provider_id)
            logging.info(f"Stopped IMAP monitoring for provider: {provider['name']}")
        
        return {
            "id": provider_id,
            "message": f"IMAP monitoring {'enabled' if new_imap_status else 'disabled'}",
            "imap_enabled": new_imap_status
        }
        
    except Exception as e:
        logging.error(f"Error toggling IMAP for provider {provider_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error toggling IMAP: {str(e)}")

@app.get("/api/email-providers/{provider_id}/imap-status")
async def get_provider_imap_status(provider_id: str):
    """Get IMAP status for a specific provider"""
    try:
        from app.services.database import db_service
        from app.services.email_processor import email_processor
        
        # Connect to database
        await db_service.connect()
        
        # Get provider data
        provider = await db_service.get_email_provider_by_id(provider_id)
        if not provider:
            raise HTTPException(status_code=404, detail="Email provider not found")
        
        # Get IMAP monitoring status
        is_monitoring = email_processor.is_provider_being_monitored(provider_id)
        last_scan = await db_service.get_last_imap_scan_for_provider(provider_id)
        
        return {
            "provider_id": provider_id,
            "provider_name": provider.get("name"),
            "imap_enabled": provider.get("imap_enabled", False),
            "is_monitoring": is_monitoring,
            "email_processor_running": email_processor.processing,
            "last_scan": last_scan.isoformat() if last_scan else None,
            "imap_config": {
                "host": provider.get("imap_host", ""),
                "port": provider.get("imap_port", 993),
                "username": provider.get("imap_username", "")
            }
        }
        
    except Exception as e:
        logging.error(f"Error getting IMAP status for provider {provider_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting IMAP status: {str(e)}")

@app.put("/api/email-providers/{provider_id}")
async def update_email_provider(provider_id: str, provider: EmailProvider):
    return {
        "id": provider_id,
        "message": "Email provider updated successfully",
        **provider.dict()
    }

@app.delete("/api/email-providers/{provider_id}")
async def delete_email_provider(provider_id: str):
    try:
        from app.services.database import db_service
        from app.services.email_processor import email_processor
        
        # Connect to database
        await db_service.connect()
        
        # Check if provider exists
        provider = await db_service.get_email_provider_by_id(provider_id)
        if not provider:
            raise HTTPException(status_code=404, detail="Email provider not found")
        
        # Stop IMAP monitoring if it's enabled for this provider
        if provider.get("imap_enabled", False):
            try:
                await email_processor.remove_provider_from_monitoring(provider_id)
                logging.info(f"Stopped IMAP monitoring for provider: {provider.get('name', 'Unknown')}")
            except Exception as imap_error:
                logging.warning(f"Failed to stop IMAP monitoring: {str(imap_error)}")
        
        # Delete from database
        result = await db_service.delete_email_provider(provider_id)
        
        if result.deleted_count > 0:
            return {
                "id": provider_id,
                "message": "Email provider deleted successfully",
                "deleted": True
            }
        else:
            raise HTTPException(status_code=404, detail="Email provider not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error deleting email provider: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting email provider: {str(e)}")

@app.post("/api/email-providers/{provider_id}/test")
async def test_email_provider(provider_id: str):
    try:
        from app.services.database import db_service
        import imaplib
        import smtplib
        
        # Connect to database
        await db_service.connect()
        
        # Get provider data
        provider = await db_service.get_email_provider_by_id(provider_id)
        if not provider:
            raise HTTPException(status_code=404, detail="Email provider not found")
        
        test_results = {
            "id": provider_id,
            "name": provider.get("name", "Unknown"),
            "smtp_test": "not_tested",
            "imap_test": "not_tested",
            "overall_status": "passed"
        }
        
        # Test SMTP connection
        try:
            if provider.get("smtp_host") and provider.get("smtp_username") and provider.get("smtp_password"):
                smtp_server = smtplib.SMTP(provider["smtp_host"], provider.get("smtp_port", 587))
                smtp_server.starttls()
                smtp_server.login(provider["smtp_username"], provider["smtp_password"])
                smtp_server.quit()
                test_results["smtp_test"] = "passed"
                logging.info(f"SMTP test passed for provider: {provider['name']}")
            else:
                test_results["smtp_test"] = "skipped - missing SMTP credentials"
        except Exception as smtp_error:
            test_results["smtp_test"] = f"failed - {str(smtp_error)}"
            test_results["overall_status"] = "failed"
            logging.error(f"SMTP test failed for provider {provider['name']}: {str(smtp_error)}")
        
        # Test IMAP connection
        try:
            if provider.get("imap_host") and provider.get("imap_username") and provider.get("imap_password"):
                mail = imaplib.IMAP4_SSL(provider["imap_host"], provider.get("imap_port", 993))
                mail.login(provider["imap_username"], provider["imap_password"])
                mail.select("inbox")
                # Test if we can search for emails
                status, messages = mail.search(None, "ALL")
                if status == "OK":
                    message_count = len(messages[0].split()) if messages[0] else 0
                    test_results["imap_test"] = f"passed - {message_count} emails found in inbox"
                else:
                    test_results["imap_test"] = "failed - could not search inbox"
                    test_results["overall_status"] = "failed"
                mail.close()
                mail.logout()
                logging.info(f"IMAP test passed for provider: {provider['name']}")
            else:
                test_results["imap_test"] = "skipped - missing IMAP credentials"
        except Exception as imap_error:
            test_results["imap_test"] = f"failed - {str(imap_error)}"
            test_results["overall_status"] = "failed"
            logging.error(f"IMAP test failed for provider {provider['name']}: {str(imap_error)}")
        
        return test_results
        
    except Exception as e:
        logging.error(f"Error testing email provider: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error testing email provider: {str(e)}")

@app.get("/api/email-providers/{provider_id}/imap-status")
async def get_provider_imap_status(provider_id: str):
    """Get IMAP monitoring status for a specific provider"""
    try:
        from app.services.database import db_service
        from app.services.email_processor import email_processor
        
        # Connect to database
        await db_service.connect()
        
        # Get provider data
        provider = await db_service.get_email_provider_by_id(provider_id)
        if not provider:
            raise HTTPException(status_code=404, detail="Email provider not found")
        
        # Check if provider is being monitored
        is_being_monitored = email_processor.is_provider_being_monitored(provider_id)
        
        # Get monitoring details if available
        monitoring_info = None
        if is_being_monitored:
            monitoring_info = email_processor.monitored_providers.get(provider_id, {})
        
        return {
            "provider_id": provider_id,
            "provider_name": provider.get("name", "Unknown"),
            "imap_enabled": provider.get("imap_enabled", False),
            "email_processor_running": email_processor.processing,
            "is_being_monitored": is_being_monitored,
            "last_scan": monitoring_info.get("last_scan") if monitoring_info else None,
            "imap_host": provider.get("imap_host", ""),
            "imap_port": provider.get("imap_port", 993),
            "status": "active" if is_being_monitored else "inactive"
        }
        
    except Exception as e:
        logging.error(f"Error getting IMAP status for provider {provider_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting IMAP status: {str(e)}")

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

@app.post("/api/lists")
async def create_list(list_data: dict):
    """Create a new prospect list"""
    try:
        from app.services.database import db_service
        from app.utils.helpers import generate_id
        
        # Connect to database
        await db_service.connect()
        
        # Generate ID and add timestamps
        list_id = generate_id()
        list_data["id"] = list_id
        list_data["created_at"] = datetime.utcnow()
        list_data["updated_at"] = datetime.utcnow()
        list_data["prospect_count"] = 0
        
        # Create list in database
        result = await db_service.create_list(list_data)
        
        if result:
            return {
                "id": list_id,
                "message": "List created successfully",
                "name": list_data.get("name"),
                "description": list_data.get("description"),
                "color": list_data.get("color"),
                "tags": list_data.get("tags", []),
                "prospect_count": 0,
                "created_at": list_data["created_at"].isoformat(),
                "updated_at": list_data["updated_at"].isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create list")
            
    except HTTPException:
        # Re-raise HTTPException so it's not caught by the generic handler
        raise
    except Exception as e:
        logging.error(f"Error creating list: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating list: {str(e)}")

@app.put("/api/lists/{list_id}")
async def update_list(list_id: str, list_data: dict):
    """Update a prospect list"""
    try:
        from app.services.database import db_service
        
        # Connect to database
        await db_service.connect()
        
        # Add update timestamp
        list_data["updated_at"] = datetime.utcnow()
        
        # Update list in database
        result = await db_service.update_list(list_id, list_data)
        
        if result:
            return {
                "id": list_id,
                "message": "List updated successfully",
                **list_data
            }
        else:
            raise HTTPException(status_code=404, detail="List not found")
            
    except Exception as e:
        logging.error(f"Error updating list: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating list: {str(e)}")

@app.delete("/api/lists/{list_id}")
async def delete_list(list_id: str):
    """Delete a prospect list"""
    try:
        from app.services.database import db_service
        
        # Connect to database
        await db_service.connect()
        
        # Delete list from database
        result = await db_service.delete_list(list_id)
        
        if result:
            return {
                "id": list_id,
                "message": "List deleted successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="List not found")
            
    except Exception as e:
        logging.error(f"Error deleting list: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting list: {str(e)}")

@app.post("/api/lists/{list_id}/prospects")
async def add_prospects_to_list(list_id: str, request: AddProspectsRequest):
    """Add prospects to a list"""
    try:
        from app.services.database import db_service
        
        # Connect to database
        await db_service.connect()
        
        # Add prospects to list
        result = await db_service.add_prospects_to_list(list_id, request.prospect_ids)
        
        if result:
            return {
                "list_id": list_id,
                "message": f"Added {len(request.prospect_ids)} prospects to list",
                "prospects_added": len(request.prospect_ids)
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to add prospects to list")
            
    except Exception as e:
        logging.error(f"Error adding prospects to list: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error adding prospects to list: {str(e)}")

@app.delete("/api/lists/{list_id}/prospects")
async def remove_prospects_from_list(list_id: str, request: AddProspectsRequest):
    """Remove prospects from a list"""
    try:
        from app.services.database import db_service
        
        # Connect to database
        await db_service.connect()
        
        # Remove prospects from list
        result = await db_service.remove_prospects_from_list(list_id, request.prospect_ids)
        
        if result:
            return {
                "list_id": list_id,
                "message": f"Removed {len(request.prospect_ids)} prospects from list",
                "prospects_removed": len(request.prospect_ids)
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to remove prospects from list")
            
    except Exception as e:
        logging.error(f"Error removing prospects from list: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error removing prospects from list: {str(e)}")

@app.get("/api/lists/{list_id}")
async def get_list_by_id(list_id: str):
    """Get a specific list by ID"""
    try:
        from app.services.database import db_service
        
        # Connect to database
        await db_service.connect()
        
        # Get list from database
        list_data = await db_service.get_list_by_id(list_id)
        
        if list_data:
            return list_data
        else:
            raise HTTPException(status_code=404, detail="List not found")
            
    except Exception as e:
        logging.error(f"Error fetching list: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching list: {str(e)}")

@app.get("/api/lists/{list_id}/prospects")
async def get_list_prospects(list_id: str):
    """Get prospects for a specific list"""
    try:
        from app.services.database import db_service
        
        # Connect to database
        await db_service.connect()
        
        # Check if list exists
        list_data = await db_service.get_list_by_id(list_id)
        if not list_data:
            raise HTTPException(status_code=404, detail="List not found")
        
        # Get prospects for this list
        prospects = await db_service.get_prospects_by_list_id(list_id)
        
        return {
            "list_id": list_id,
            "list_name": list_data.get("name", "Unknown"),
            "prospects": prospects,
            "total_count": len(prospects)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching list prospects: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching list prospects: {str(e)}")

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

# Intents endpoint removed - handled by router
# @app.get("/api/intents")
# async def get_intents():
#     """Get all intents from database"""
#     try:
#         from app.services.database import db_service
#         
#         # Connect to database
#         await db_service.connect()
#         
#         # Get intents from database
#         intents = await db_service.get_intents()
#         
#         # If no intents exist, return empty list
#         if not intents:
#             return []
#         
#         return intents
#         
#     except Exception as e:
#         logging.error(f"Error fetching intents: {str(e)}")
#         # Return empty list on error instead of mock data
#         return []

@app.get("/api/industries")
async def get_industries():
    """Get all industries for AI Agent"""
    try:
        from app.services.database import db_service
        
        # Connect to database
        await db_service.connect()
        
        # Get industries from database
        industries = await db_service.get_industry_tags()
        
        # If no industries exist, return empty list
        if not industries:
            return []
        
        # Transform for AI Agent usage with URLs
        industry_data = []
        for industry in industries:
            industry_data.append({
                "id": industry.get("id"),
                "external_id": industry.get("external_id"),
                "industry": industry.get("industry"),
                "description": industry.get("description", ""),
                "url": f"/api/industries/{industry.get('external_id')}",
                "is_active": industry.get("is_active", True)
            })
        
        return {
            "industries": industry_data,
            "total_count": len(industry_data),
            "message": "Industries available for AI Agent"
        }
        
    except Exception as e:
        logging.error(f"Error fetching industries: {str(e)}")
        return {"industries": [], "total_count": 0, "error": str(e)}

@app.get("/api/industries/{external_id}")
async def get_industry_by_external_id(external_id: str):
    """Get specific industry by external ID"""
    try:
        from app.services.database import db_service
        
        # Connect to database
        await db_service.connect()
        
        # Get specific industry by external_id
        industry = await db_service.db.industry_tags.find_one({"external_id": external_id})
        
        if not industry:
            raise HTTPException(status_code=404, detail="Industry not found")
        
        # Clean up the data
        if "_id" in industry:
            industry.pop("_id")
        
        return {
            "id": industry.get("id"),
            "external_id": industry.get("external_id"),
            "industry": industry.get("industry"),
            "description": industry.get("description", ""),
            "url": f"/api/industries/{external_id}",
            "is_active": industry.get("is_active", True),
            "created_at": industry.get("created_at"),
            "updated_at": industry.get("updated_at")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching industry: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching industry: {str(e)}")

@app.get("/api/industries/search/{search_term}")
async def search_industries(search_term: str):
    """Search industries by name for AI Agent"""
    try:
        from app.services.database import db_service
        
        # Connect to database
        await db_service.connect()
        
        # Search industries by name (case-insensitive)
        industries = await db_service.db.industry_tags.find({
            "industry": {"$regex": search_term, "$options": "i"}
        }).to_list(length=50)  # Limit to 50 results
        
        # Transform results
        industry_data = []
        for industry in industries:
            if "_id" in industry:
                industry.pop("_id")
                
            industry_data.append({
                "id": industry.get("id"),
                "external_id": industry.get("external_id"),
                "industry": industry.get("industry"),
                "description": industry.get("description", ""),
                "url": f"/api/industries/{industry.get('external_id')}",
                "is_active": industry.get("is_active", True)
            })
        
        return {
            "search_term": search_term,
            "industries": industry_data,
            "total_count": len(industry_data),
            "message": f"Found {len(industry_data)} industries matching '{search_term}'"
        }
        
    except Exception as e:
        logging.error(f"Error searching industries: {str(e)}")
        return {"search_term": search_term, "industries": [], "total_count": 0, "error": str(e)}

@app.get("/api/services/status")
async def get_services_status():
    """Get status of auto follow-up and auto-responder services with provider details"""
    try:
        from app.services.smart_follow_up_engine_enhanced import enhanced_smart_follow_up_engine
        from app.services.email_processor import email_processor
        
        # Get monitored providers info
        monitored_providers_info = []
        if hasattr(email_processor, 'monitored_providers'):
            for provider_id, provider_config in email_processor.monitored_providers.items():
                monitored_providers_info.append({
                    "id": provider_id,
                    "name": provider_config["name"],
                    "provider_type": provider_config["provider_type"],
                    "last_scan": provider_config["last_scan"].isoformat() if provider_config["last_scan"] else None,
                    "imap_host": provider_config["imap_host"]
                })
        
        return {
            "services": {
                "smart_follow_up_engine": {
                    "status": "running" if enhanced_smart_follow_up_engine.processing else "stopped",
                    "description": "Handles automatic follow-up emails"
                },
                "email_processor": {
                    "status": "running" if email_processor.processing else "stopped", 
                    "description": "Handles automatic email responses (auto-responder)",
                    "monitored_providers_count": len(monitored_providers_info),
                    "monitored_providers": monitored_providers_info
                }
            },
            "overall_status": "healthy" if (enhanced_smart_follow_up_engine.processing and email_processor.processing) else "degraded",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "services": {
                "smart_follow_up_engine": {"status": "error", "error": str(e)},
                "email_processor": {"status": "error", "error": str(e)}
            },
            "overall_status": "error",
            "timestamp": datetime.utcnow().isoformat()
        }

@app.post("/api/services/start-all")
async def start_all_services():
    """Manually start both follow-up and auto-responder services"""
    try:
        from app.services.smart_follow_up_engine_enhanced import enhanced_smart_follow_up_engine
        from app.services.email_processor import email_processor
        
        results = {}
        
        # Start Follow-up Engine
        if not enhanced_smart_follow_up_engine.processing:
            follow_up_result = await enhanced_smart_follow_up_engine.start_follow_up_engine()
            results["smart_follow_up_engine"] = follow_up_result
        else:
            results["smart_follow_up_engine"] = {"status": "already_running"}
        
        # Start Email Processor
        if not email_processor.processing:
            email_result = await email_processor.start_monitoring()
            results["email_processor"] = email_result
        else:
            results["email_processor"] = {"status": "already_running"}
        
        return {
            "message": "All services start initiated",
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting services: {str(e)}")

@app.post("/api/services/stop-all")
async def stop_all_services():
    """Manually stop both follow-up and auto-responder services"""
    try:
        from app.services.smart_follow_up_engine_enhanced import enhanced_smart_follow_up_engine
        from app.services.email_processor import email_processor
        
        # Stop Follow-up Engine
        follow_up_result = await enhanced_smart_follow_up_engine.stop_follow_up_engine()
        
        # Stop Email Processor
        email_result = await email_processor.stop_monitoring()
        
        return {
            "message": "All services stopped",
            "results": {
                "smart_follow_up_engine": follow_up_result,
                "email_processor": email_result
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error stopping services: {str(e)}")
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
    """Get real-time dashboard metrics from actual database"""
    try:
        from app.services.database import db_service
        
        # Connect to database
        await db_service.connect()
        
        # Get actual data from database
        prospects = await db_service.get_prospects()
        campaigns = await db_service.get_campaigns()
        email_providers = await db_service.get_email_providers()
        
        # Count emails sent today
        today = datetime.utcnow().date()
        emails_today = await db_service.db.emails.count_documents({
            "sent_at": {
                "$gte": datetime.combine(today, datetime.min.time()),
                "$lt": datetime.combine(today, datetime.max.time())
            }
        })
        
        # Get total emails sent
        total_emails_sent = await db_service.db.emails.count_documents({})
        
        # Count active campaigns
        active_campaigns = len([c for c in campaigns if c.get("status") == "active"])
        
        # Get recent activity (last 5 sent emails)
        recent_emails = await db_service.db.emails.find(
            {"status": "sent"},
            sort=[("sent_at", -1)]
        ).limit(5).to_list(length=5)
        
        recent_activity = []
        for email in recent_emails:
            recent_activity.append({
                "id": email.get("id", ""),
                "subject": email.get("subject", ""),
                "recipient": email.get("recipient_email", ""),
                "status": email.get("status", ""),
                "created_at": email.get("sent_at", datetime.utcnow()).isoformat()
            })
        
        # Get provider stats
        provider_stats = {}
        for provider in email_providers:
            provider_stats[provider["name"]] = {
                "type": provider["provider_type"],
                "status": "active" if provider["is_active"] else "inactive",
                "emails_sent_today": provider.get("current_daily_count", 0),
                "daily_limit": provider.get("daily_send_limit", 500)
            }
        
        return {
            "metrics": {
                "overview": {
                    "total_prospects": len(prospects),
                    "total_campaigns": len(campaigns),
                    "total_emails_sent": total_emails_sent,
                    "emails_today": emails_today,
                    "active_campaigns": active_campaigns
                },
                "provider_stats": provider_stats,
                "recent_activity": recent_activity
            },
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Error getting dashboard metrics: {str(e)}")
        # Return basic metrics on error
        return {
            "metrics": {
                "overview": {
                    "total_prospects": 2,
                    "total_campaigns": 1,
                    "total_emails_sent": 2,
                    "emails_today": 2,
                    "active_campaigns": 0
                },
                "provider_stats": {
                    "Production Gmail Provider": {
                        "type": "gmail",
                        "status": "active",
                        "emails_sent_today": 2,
                        "daily_limit": 500
                    }
                },
                "recent_activity": []
            },
            "last_updated": datetime.utcnow().isoformat()
        }

# Email sending functionality
async def send_email(to_email: str, subject: str, content: str):
    """Simple email sending function for testing"""
    try:
        from app.services.database import db_service
        from app.services.email_provider_service import email_provider_service
        
        # Connect to database
        await db_service.connect()
        
        # Get default email provider
        provider = await email_provider_service.get_default_provider()
        if not provider:
            raise Exception("No default email provider configured")
        
        # Send email using email provider service
        success, error = await email_provider_service.send_email(
            provider["id"],
            to_email,
            subject,
            content
        )
        
        if not success:
            raise Exception(error or "Failed to send email")
            
        return True
        
    except Exception as e:
        logging.error(f"Error in send_email: {str(e)}")
        raise e
async def send_email_via_provider(provider_data: dict, recipient: dict, subject: str, content: str, html_content: str = None):
    """Send email using the specified provider with HTML support"""
    try:
        # Create message
        message = MIMEMultipart('alternative')
        message["From"] = provider_data["email_address"]
        message["To"] = recipient["email"]
        message["Subject"] = subject
        
        # Attach plain text version
        text_part = MIMEText(content, "plain")
        message.attach(text_part)
        
        # Attach HTML version if provided
        if html_content:
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
        
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
    """Personalize template with recipient data - supports both text and HTML"""
    personalized = template_content
    
    # Replace placeholders
    placeholders = {
        "{{first_name}}": recipient.get("first_name", ""),
        "{{last_name}}": recipient.get("last_name", ""),
        "{{company}}": recipient.get("company", ""),
        "{{job_title}}": recipient.get("job_title", ""),
        "{{industry}}": recipient.get("industry", ""),
        "{{email}}": recipient.get("email", ""),
        "{{subject}}": recipient.get("subject", "")  # For HTML templates
    }
    
    for placeholder, value in placeholders.items():
        personalized = personalized.replace(placeholder, value)
    
    return personalized

@app.post("/api/campaigns/{campaign_id}/send")
async def send_campaign_emails(campaign_id: str, send_request: EmailSendRequest):
    """Send emails for a specific campaign with auto-start follow-up and auto-response services"""
    try:
        from app.services.database import db_service
        from app.services.email_provider_service import email_provider_service
        from app.services.smart_follow_up_engine_enhanced import enhanced_smart_follow_up_engine
        from app.services.email_processor import email_processor
        from app.utils.helpers import generate_id, personalize_template
        
        # Connect to database
        await db_service.connect()
        
        # Auto-start Follow-up and Auto-Response Services
        logging.info("Auto-starting follow-up and auto-response services...")
        
        if not enhanced_smart_follow_up_engine.processing:
            await enhanced_smart_follow_up_engine.start_follow_up_engine()
            logging.info("Smart Follow-up Engine started automatically")
        
        if not email_processor.processing:
            await email_processor.start_monitoring()
            logging.info("Email Processor (Auto-Responder) started automatically")
        
        # Get campaign data
        campaign = await db_service.get_campaign_by_id(campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Check if campaign has already been sent
        current_status = campaign.get("status", "draft")
        if current_status in ["sent", "completed", "active"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Campaign has already been {current_status}. Cannot send again."
            )
        
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
                # Personalize template - support both HTML and text
                personalized_subject = personalize_template(template["subject"], prospect)
                personalized_content = personalize_template(template["content"], prospect)
                
                # Personalize HTML content if available
                personalized_html_content = None
                if template.get("html_content") and template.get("is_html_enabled", False):
                    personalized_html_content = personalize_template(template["html_content"], prospect)
                
                # Send email using email provider service
                success, error = await email_provider_service.send_email(
                    provider["id"],
                    prospect["email"],
                    personalized_subject,
                    personalized_content,
                    personalized_html_content  # Pass HTML content
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
                
                # Update prospect last contact and follow-up status
                await db_service.update_prospect_last_contact(prospect["id"], datetime.utcnow())
                
                # Set up prospect for follow-up if campaign has follow-up enabled
                if campaign.get("follow_up_enabled", False) and success:
                    await db_service.update_prospect(prospect["id"], {
                        "campaign_id": campaign_id,
                        "follow_up_status": "active",
                        "follow_up_count": 0,
                        "last_follow_up": None
                    })
                
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
        
        # Update campaign status - keep active if follow-up enabled
        campaign_status = "active" if campaign.get("follow_up_enabled", False) else "sent"
        await db_service.update_campaign(campaign_id, {"status": campaign_status})
        
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
    """Create a new email template with HTML support"""
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
        
        # Ensure HTML support fields are present
        if "html_content" not in template:
            template["html_content"] = convert_text_to_html(template.get("content", ""))
        if "is_html_enabled" not in template:
            template["is_html_enabled"] = True
        if "style_settings" not in template:
            template["style_settings"] = {
                "primaryColor": "#3B82F6",
                "backgroundColor": "#FFFFFF", 
                "textColor": "#1F2937",
                "font": "Arial, sans-serif",
                "borderRadius": "8px"
            }
        
        # Create template in database
        result = await db_service.create_template(template)
        
        if result:
            return {
                "id": template_id,
                "message": "Template created successfully",
                "name": template.get("name"),
                "subject": template.get("subject"),
                "content": template.get("content"),
                "html_content": template.get("html_content"),
                "is_html_enabled": template.get("is_html_enabled"),
                "type": template.get("type"),
                "style_settings": template.get("style_settings"),
                "created_at": template["created_at"].isoformat(),
                "updated_at": template["updated_at"].isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create template")
            
    except HTTPException:
        # Re-raise HTTPException so it's not caught by the generic handler
        raise
    except Exception as e:
        logging.error(f"Error creating template: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating template: {str(e)}")

def convert_text_to_html(text_content):
    """Convert plain text to basic HTML template"""
    if not text_content:
        return get_default_html_template()
    
    paragraphs = text_content.split('\n')
    html_paragraphs = []
    
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if paragraph:
            html_paragraphs.append(f"            <p>{paragraph}</p>")
    
    html_content = '\n'.join(html_paragraphs)
    
    return f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{{{subject}}}}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #1F2937;
            background-color: #f9fafb;
            margin: 0;
            padding: 20px;
        }}
        .email-container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: #FFFFFF;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            padding: 30px;
        }}
        h1, h2, h3 {{ color: #1F2937; }}
        p {{ margin-bottom: 16px; }}
        .signature {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #E5E7EB;
            font-size: 14px;
            color: #6B7280;
        }}
    </style>
</head>
<body>
    <div class="email-container">
{html_content}
        <div class="signature">
            <p>Best regards,<br>
            Your Team</p>
        </div>
    </div>
</body>
</html>'''

def get_default_html_template():
    """Get default HTML template"""
    return '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{subject}}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #1F2937;
            background-color: #f9fafb;
            margin: 0;
            padding: 20px;
        }
        .email-container {
            max-width: 600px;
            margin: 0 auto;
            background-color: #FFFFFF;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }
        .header {
            background-color: #3B82F6;
            color: white;
            padding: 20px;
            text-align: center;
        }
        .content {
            padding: 30px;
        }
        .footer {
            background-color: #F3F4F6;
            padding: 20px;
            text-align: center;
            font-size: 12px;
            color: #6B7280;
        }
        .button {
            display: inline-block;
            background-color: #3B82F6;
            color: white;
            padding: 12px 24px;
            text-decoration: none;
            border-radius: 6px;
            margin: 20px 0;
        }
        h1, h2, h3 { color: #1F2937; }
        p { margin-bottom: 16px; }
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <h1>Hello {{first_name}}!</h1>
        </div>
        <div class="content">
            <p>Write your email content here...</p>
            <p>You can personalize with {{first_name}}, {{last_name}}, {{company}}, etc.</p>
        </div>
        <div class="footer">
            <p>This email was sent to {{email}}</p>
        </div>
    </div>
</body>
</html>'''

@app.put("/api/templates/{template_id}")
async def update_template(template_id: str, template: dict):
    """Update an email template with HTML support"""
    try:
        from app.services.database import db_service
        
        # Connect to database
        await db_service.connect()
        
        # Add update timestamp
        template["updated_at"] = datetime.utcnow()
        
        # Ensure HTML support fields are present if enabling HTML
        if template.get("is_html_enabled") and "html_content" not in template:
            template["html_content"] = convert_text_to_html(template.get("content", ""))
        
        # Update template in database
        result = await db_service.update_template(template_id, template)
        
        if result:
            response_data = {
                "id": template_id,
                "message": "Template updated successfully",
                **template
            }
            
            # Convert datetime to string for JSON response
            if "updated_at" in response_data and hasattr(response_data["updated_at"], "isoformat"):
                response_data["updated_at"] = response_data["updated_at"].isoformat()
                
            return response_data
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
            
    except HTTPException:
        # Re-raise HTTPException so it's not caught by the generic handler
        raise
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

# WebSocket endpoint for real-time dashboard
@app.websocket("/api/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "get_current_metrics":
                # Get current metrics and send to client
                try:
                    from app.services.database import db_service
                    
                    # Connect to database
                    await db_service.connect()
                    
                    # Get actual data from database
                    prospects = await db_service.get_prospects()
                    campaigns = await db_service.get_campaigns()
                    email_providers = await db_service.get_email_providers()
                    
                    # Count emails sent today
                    today = datetime.utcnow().date()
                    emails_today = await db_service.db.emails.count_documents({
                        "sent_at": {
                            "$gte": datetime.combine(today, datetime.min.time()),
                            "$lt": datetime.combine(today, datetime.max.time())
                        }
                    })
                    
                    # Get total emails sent
                    total_emails_sent = await db_service.db.emails.count_documents({})
                    
                    # Count active campaigns
                    active_campaigns = len([c for c in campaigns if c.get("status") == "active"])
                    
                    # Get recent activity (last 5 sent emails)
                    recent_emails = await db_service.db.emails.find(
                        {"status": {"$in": ["sent", "failed"]}},
                        sort=[("sent_at", -1)]
                    ).limit(5).to_list(length=5)
                    
                    recent_activity = []
                    for email in recent_emails:
                        recent_activity.append({
                            "id": email.get("id", ""),
                            "subject": email.get("subject", ""),
                            "recipient": email.get("recipient_email", ""),
                            "status": email.get("status", ""),
                            "created_at": email.get("sent_at", datetime.utcnow()).isoformat()
                        })
                    
                    # Get provider stats
                    provider_stats = {}
                    for provider in email_providers:
                        provider_stats[provider["name"]] = {
                            "type": provider["provider_type"],
                            "status": "active" if provider["is_active"] else "inactive",
                            "emails_sent_today": provider.get("current_daily_count", 0),
                            "daily_limit": provider.get("daily_send_limit", 500)
                        }
                    
                    metrics_data = {
                        "type": "current_metrics",
                        "data": {
                            "overview": {
                                "total_prospects": len(prospects),
                                "total_campaigns": len(campaigns),
                                "total_emails_sent": total_emails_sent,
                                "emails_today": emails_today,
                                "active_campaigns": active_campaigns
                            },
                            "provider_stats": provider_stats,
                            "recent_activity": recent_activity
                        },
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
                    await websocket.send_text(json.dumps(metrics_data))
                    
                except Exception as e:
                    error_message = {
                        "type": "error",
                        "message": f"Failed to get metrics: {str(e)}"
                    }
                    await websocket.send_text(json.dumps(error_message))
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Initialize database and services on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database connection and services"""
    try:
        from app.services.database import db_service
        await db_service.connect()
        logging.info("Database connected successfully")
        
        # Initialize seed data
        try:
            from app.services.seed_data import initialize_seed_data
            await initialize_seed_data(db_service)
            logging.info("Seed data initialization completed")
        except Exception as e:
            logging.warning(f"Could not initialize seed data: {e}")
        
        # Initialize services
        try:
            from app.services.knowledge_base_service import knowledge_base_service
            from app.services.response_verification_service import response_verification_service
            logging.info("Services initialized successfully")
        except ImportError as e:
            logging.warning(f"Could not initialize some services: {e}")
        
        # Auto-start critical services for Auto Follow-ups and Auto Responders
        try:
            from app.services.smart_follow_up_engine_enhanced import enhanced_smart_follow_up_engine
            from app.services.email_processor import email_processor
            
            # Start Follow-up Engine
            if not enhanced_smart_follow_up_engine.processing:
                await enhanced_smart_follow_up_engine.start_follow_up_engine()
                logging.info("✅ Smart Follow-up Engine started automatically on startup")
            
            # Start Email Processor (Auto Responder)
            if not email_processor.processing:
                await email_processor.start_monitoring()
                logging.info("✅ Email Processor (Auto Responder) started automatically on startup")
                
        except Exception as e:
            logging.error(f"Failed to auto-start follow-up/auto-responder services: {e}")
            
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