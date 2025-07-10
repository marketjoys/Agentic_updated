from fastapi import APIRouter, HTTPException
from app.services.email_processor import email_processor
from app.services.groq_service import groq_service
from app.services.database import db_service
from app.models import ThreadContext
from app.utils.helpers import generate_id
from typing import Dict, List
from datetime import datetime

router = APIRouter()

@router.post("/email-processing/start")
async def start_email_monitoring():
    """Start email monitoring service"""
    try:
        result = await email_processor.start_monitoring()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/email-processing/stop")
async def stop_email_monitoring():
    """Stop email monitoring service"""
    try:
        result = await email_processor.stop_monitoring()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/email-processing/status")
async def get_processing_status():
    """Get email processing status"""
    return {
        "status": "running" if email_processor.processing else "stopped",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.post("/email-processing/test-classification")
async def test_intent_classification(request: Dict):
    """Test intent classification with sample email"""
    try:
        email_content = request.get("content", "")
        subject = request.get("subject", "")
        
        if not email_content:
            raise HTTPException(status_code=400, detail="Email content is required")
        
        # Classify intents
        classified_intents = await groq_service.classify_intents(email_content, subject)
        
        # Analyze sentiment
        sentiment_analysis = await groq_service.analyze_email_sentiment(email_content)
        
        return {
            "email_content": email_content,
            "subject": subject,
            "classified_intents": classified_intents,
            "sentiment_analysis": sentiment_analysis,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/email-processing/test-response")
async def test_response_generation(request: Dict):
    """Test response generation with sample data"""
    try:
        email_content = request.get("content", "")
        subject = request.get("subject", "")
        prospect_id = request.get("prospect_id", "")
        
        if not email_content or not prospect_id:
            raise HTTPException(status_code=400, detail="Email content and prospect ID are required")
        
        # Get prospect data
        prospect = await db_service.get_prospect_by_id(prospect_id)
        if not prospect:
            raise HTTPException(status_code=404, detail="Prospect not found")
        
        # Classify intents
        classified_intents = await groq_service.classify_intents(email_content, subject)
        
        # Generate response
        response_data = await groq_service.generate_response(
            email_content, 
            subject, 
            classified_intents, 
            [], 
            prospect
        )
        
        return {
            "email_content": email_content,
            "subject": subject,
            "prospect": prospect,
            "classified_intents": classified_intents,
            "generated_response": response_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/threads")
async def get_threads():
    """Get all conversation threads"""
    try:
        threads = await db_service.get_threads()
        return threads
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/threads/{thread_id}")
async def get_thread(thread_id: str):
    """Get specific thread by ID"""
    try:
        thread = await db_service.get_thread_by_id(thread_id)
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")
        return thread
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/threads/prospect/{prospect_id}")
async def get_thread_by_prospect(prospect_id: str):
    """Get thread by prospect ID"""
    try:
        thread = await db_service.get_thread_by_prospect_id(prospect_id)
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")
        return thread
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/threads/{thread_id}/messages")
async def add_message_to_thread(thread_id: str, message_data: Dict):
    """Add message to thread"""
    try:
        await db_service.add_message_to_thread(thread_id, message_data)
        return {"message": "Message added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/email-processing/analytics")
async def get_processing_analytics():
    """Get email processing analytics"""
    try:
        # Get threads count
        threads = await db_service.get_threads()
        
        # Get processed emails count
        processed_emails = 0
        auto_responses_sent = 0
        
        for thread in threads:
            messages = thread.get("messages", [])
            processed_emails += len([m for m in messages if m.get("type") == "received"])
            auto_responses_sent += len([m for m in messages if m.get("type") == "sent" and m.get("ai_generated")])
        
        return {
            "total_threads": len(threads),
            "processed_emails": processed_emails,
            "auto_responses_sent": auto_responses_sent,
            "processing_status": "running" if email_processor.processing else "stopped",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))