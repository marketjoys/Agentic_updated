from fastapi import APIRouter, HTTPException
from app.services.enhanced_email_processor import enhanced_email_processor
from app.services.database import db_service
from typing import Dict
from datetime import datetime

router = APIRouter()

@router.post("/enhanced-email-processing/start")
async def start_enhanced_email_processing():
    """Start the enhanced email processing engine"""
    try:
        result = await enhanced_email_processor.start_email_processing()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/enhanced-email-processing/stop")
async def stop_enhanced_email_processing():
    """Stop the enhanced email processing engine"""
    try:
        result = await enhanced_email_processor.stop_email_processing()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/enhanced-email-processing/status")
async def get_enhanced_email_processing_status():
    """Get enhanced email processing status"""
    try:
        stats = await enhanced_email_processor.get_processing_statistics()
        return {
            "status": "running" if enhanced_email_processor.processing else "stopped",
            "statistics": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/enhanced-email-processing/statistics")
async def get_enhanced_email_processing_statistics():
    """Get detailed enhanced email processing statistics"""
    try:
        stats = await enhanced_email_processor.get_processing_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/enhanced-email-processing/process-campaign")
async def process_campaign_with_enhanced_ai(campaign_data: Dict):
    """Process a campaign with enhanced AI capabilities"""
    try:
        campaign_id = campaign_data.get("campaign_id")
        if not campaign_id:
            raise HTTPException(status_code=400, detail="Campaign ID is required")
        
        result = await enhanced_email_processor.process_campaign_emails(campaign_id)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/enhanced-email-processing/real-time-metrics")
async def get_real_time_metrics():
    """Get real-time processing metrics"""
    try:
        # Get current processing metrics
        stats = await enhanced_email_processor.get_processing_statistics()
        
        # Get recent activity
        recent_activity = await db_service.db.emails.find({
            "created_at": {"$gte": datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)}
        }).sort("created_at", -1).limit(10).to_list(length=10)
        
        for activity in recent_activity:
            activity.pop('_id', None)
        
        return {
            "processing_stats": stats,
            "recent_activity": recent_activity,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))