from fastapi import APIRouter
from app.services.database import db_service

router = APIRouter()

@router.get("/analytics/campaign/{campaign_id}")
async def get_campaign_analytics(campaign_id: str):
    """Get analytics for a specific campaign"""
    analytics = await db_service.get_campaign_analytics(campaign_id)
    return analytics