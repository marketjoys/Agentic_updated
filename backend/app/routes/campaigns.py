from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.models import Campaign, EmailMessage
from app.services.database import db_service
from app.services.email_provider_service import email_provider_service
from app.utils.helpers import generate_id, personalize_template
from datetime import datetime
import asyncio
import logging
from typing import List

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/campaigns")
async def create_campaign(campaign: Campaign):
    """Create a new campaign"""
    campaign.id = generate_id()
    campaign_dict = campaign.dict()
    result = await db_service.create_campaign(campaign_dict)
    campaign_dict.pop('_id', None)
    return campaign_dict

@router.get("/campaigns")
async def get_campaigns():
    """Get all campaigns"""
    campaigns = await db_service.get_campaigns()
    return campaigns

@router.get("/campaigns/{campaign_id}")
async def get_campaign(campaign_id: str):
    """Get a specific campaign by ID"""
    campaign = await db_service.get_campaign_by_id(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign

@router.post("/campaigns/{campaign_id}/send")
async def send_campaign(campaign_id: str, background_tasks: BackgroundTasks, send_data: dict = {}):
    """Send campaign emails with enhanced follow-up provider tracking and duplicate prevention"""
    campaign = await db_service.get_campaign_by_id(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    template = await db_service.get_template_by_id(campaign["template_id"])
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # CRITICAL FIX: Check if campaign has already been sent
    existing_emails = await db_service.db.emails.find({
        "campaign_id": campaign_id,
        "is_follow_up": False,
        "status": "sent"
    }).to_list(length=None)
    
    if existing_emails:
        logger.warning(f"Campaign {campaign_id} has already been sent to {len(existing_emails)} prospects")
        # Check if force resend is requested
        if not send_data.get("force_resend", False):
            raise HTTPException(
                status_code=400, 
                detail=f"Campaign has already been sent to {len(existing_emails)} prospects. Use 'force_resend': true to resend."
            )
    
    # Determine email provider to use
    provider_id = send_data.get("email_provider_id") or campaign.get("email_provider_id")
    if not provider_id:
        # Get default provider
        default_provider = await email_provider_service.get_default_provider()
        if not default_provider:
            raise HTTPException(status_code=400, detail="No email provider available")
        provider_id = default_provider["id"]
    
    # Validate provider exists
    provider = await email_provider_service.get_email_provider_by_id(provider_id)
    if not provider:
        raise HTTPException(status_code=400, detail="Email provider not found")
    
    # Update campaign with provider information for follow-ups
    await db_service.update_campaign(campaign_id, {
        "email_provider_id": provider_id,
        "status": "sending",  # Keep as sending initially, will become active after first emails
        "updated_at": datetime.utcnow()
    })
    
    # Get prospects from campaign lists
    prospects = []
    for list_id in campaign.get("list_ids", []):
        list_prospects = await db_service.get_prospects_by_list_id(list_id)
        prospects.extend(list_prospects)
    
    # Remove duplicates
    seen_emails = set()
    unique_prospects = []
    for prospect in prospects:
        if prospect["email"] not in seen_emails:
            seen_emails.add(prospect["email"])
            unique_prospects.append(prospect)
    
    # CRITICAL FIX: Filter out prospects who have already received this campaign
    if not send_data.get("force_resend", False):
        already_sent_emails = {email.get("recipient_email") for email in existing_emails}
        filtered_prospects = [
            prospect for prospect in unique_prospects 
            if prospect["email"] not in already_sent_emails
        ]
        logger.info(f"Filtered out {len(unique_prospects) - len(filtered_prospects)} prospects who already received this campaign")
        unique_prospects = filtered_prospects
    
    # Limit to max_emails
    max_emails = send_data.get("max_emails") or campaign.get("max_emails", 100)
    prospects = unique_prospects[:max_emails]
    
    if not prospects:
        logger.warning(f"No prospects to send to for campaign {campaign_id}")
        return {
            "campaign_id": campaign_id,
            "status": "completed",
            "email_provider_id": provider_id,
            "email_provider_name": provider.get("name"),
            "total_prospects": 0,
            "message": "No prospects to send to (all have already received this campaign)"
        }
    
    logger.info(f"Starting campaign {campaign_id} with provider {provider['name']} for {len(prospects)} prospects")
    
    # Schedule email sending with enhanced provider tracking
    background_tasks.add_task(
        process_campaign_emails_with_follow_up_tracking, 
        campaign_id, 
        prospects, 
        template, 
        provider_id,
        send_data
    )
    
    return {
        "campaign_id": campaign_id,
        "status": "sending",
        "email_provider_id": provider_id,
        "email_provider_name": provider.get("name"),
        "total_prospects": len(prospects),
        "message": f"Campaign started with provider {provider.get('name')}. Sending to {len(prospects)} prospects"
    }

async def process_campaign_emails_with_follow_up_tracking(
    campaign_id: str, 
    prospects: List[dict], 
    template: dict, 
    provider_id: str,
    send_data: dict = {}
):
    """Process campaign emails with enhanced follow-up and provider tracking - FIXED VERSION"""
    sent_count = 0
    failed_count = 0
    skipped_count = 0
    
    # Get provider details
    provider = await email_provider_service.get_email_provider_by_id(provider_id)
    if not provider:
        logger.error(f"Provider {provider_id} not found for campaign {campaign_id}")
        return
    
    logger.info(f"Processing campaign {campaign_id} emails with provider: {provider.get('name')}")
    
    for prospect in prospects:
        try:
            # CRITICAL FIX: Double-check if email already sent to this prospect for this campaign
            existing_email = await db_service.db.emails.find_one({
                "campaign_id": campaign_id,
                "prospect_id": prospect["id"],
                "is_follow_up": False
            })
            
            if existing_email and not send_data.get("force_resend", False):
                logger.info(f"Skipping {prospect['email']} - already sent for campaign {campaign_id}")
                skipped_count += 1
                continue
            
            # Personalize email content
            personalized_content = personalize_template(template["content"], prospect)
            personalized_subject = personalize_template(template["subject"], prospect)
            
            # Send email using the specific provider
            success, error = await email_provider_service.send_email(
                provider_id,
                prospect["email"],
                personalized_subject,
                personalized_content
            )
            
            if not success and error:
                logger.error(f"Email sending failed to {prospect['email']}: {error}")
            
            # Create enhanced email record with proper tracking
            email_id = generate_id()
            email_record = {
                "id": email_id,
                "prospect_id": prospect["id"],
                "campaign_id": campaign_id,
                "email_provider_id": provider_id,  # CRITICAL: Store provider for follow-ups
                "recipient_email": prospect["email"],
                "subject": personalized_subject,
                "content": personalized_content,
                "status": "sent" if success else "failed",
                "sent_at": datetime.utcnow() if success else None,
                "created_at": datetime.utcnow(),
                "is_follow_up": False,
                "follow_up_sequence": 0,
                "sent_by_us": True,  # Mark as sent by our system
                "thread_id": f"thread_{prospect['id']}",  # CONSISTENT THREADING
                "template_id": template["id"],
                "provider_name": provider.get("name")
            }
            
            await db_service.create_email_record(email_record)
            
            if success:
                sent_count += 1
                
                # Update prospect with campaign and follow-up tracking
                await db_service.update_prospect(prospect["id"], {
                    "last_contact": datetime.utcnow(),
                    "campaign_id": campaign_id,
                    "follow_up_status": "active" if send_data.get("follow_up_enabled", True) else "inactive",
                    "follow_up_count": 0,
                    "email_provider_id": provider_id,  # Track which provider was used
                    "updated_at": datetime.utcnow()
                })
                
                # FIXED: Create or update thread context with consistent thread ID
                thread_id = f"thread_{prospect['id']}"
                await db_service.create_or_update_thread_context(
                    prospect["id"], 
                    campaign_id, 
                    provider_id,
                    {
                        "type": "sent",
                        "recipient": prospect["email"],
                        "subject": personalized_subject,
                        "content": personalized_content,
                        "timestamp": datetime.utcnow(),
                        "email_id": email_id,
                        "template_id": template["id"],
                        "provider_id": provider_id,
                        "sent_by_us": True,
                        "is_follow_up": False,
                        "thread_id": thread_id  # ENSURE CONSISTENT THREAD ID
                    }
                )
                
                logger.info(f"Email sent successfully to {prospect['email']} via {provider.get('name')}")
            else:
                failed_count += 1
            
            # Small delay to avoid overwhelming SMTP server
            await asyncio.sleep(0.1)
            
        except Exception as e:
            logger.error(f"Error sending email to {prospect['email']}: {str(e)}")
            failed_count += 1
            continue
    
    # Update campaign status - CRITICAL: Keep as 'active' for follow-ups, not 'completed'
    campaign_status = "active" if send_data.get("follow_up_enabled", True) else "completed"
    
    await db_service.update_campaign(campaign_id, {
        "status": campaign_status,  # Keep active for follow-ups
        "sent_count": sent_count,
        "prospect_count": len(prospects),
        "last_sent_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })
    
    logger.info(f"Campaign {campaign_id} send completed: {sent_count} sent, {failed_count} failed, {skipped_count} skipped. Status: {campaign_status}")
    
    return {
        "sent_count": sent_count,
        "failed_count": failed_count,
        "skipped_count": skipped_count,
        "total_prospects": len(prospects),
        "status": campaign_status
    }