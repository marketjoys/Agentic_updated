from fastapi import APIRouter, HTTPException
from app.services.context_aware_ai import context_aware_ai
from app.services.database import db_service
from typing import Dict
from datetime import datetime

router = APIRouter()

@router.post("/context-aware-ai/generate-response")
async def generate_context_aware_response(request_data: Dict):
    """Generate a context-aware AI response"""
    try:
        prospect_id = request_data.get("prospect_id")
        email_content = request_data.get("email_content")
        subject = request_data.get("subject", "")
        enhanced_context = request_data.get("enhanced_context", True)
        
        if not all([prospect_id, email_content]):
            raise HTTPException(
                status_code=400, 
                detail="Missing required fields: prospect_id, email_content"
            )
        
        result = await context_aware_ai.generate_context_aware_response(
            prospect_id, email_content, subject, enhanced_context
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/context-aware-ai/conversation-summary/{prospect_id}")
async def get_conversation_summary(prospect_id: str):
    """Get conversation summary for a prospect"""
    try:
        summary = await context_aware_ai.get_conversation_summary(prospect_id)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/context-aware-ai/update-conversation-memory")
async def update_conversation_memory(request_data: Dict):
    """Update conversation memory for a prospect"""
    try:
        prospect_id = request_data.get("prospect_id")
        message_data = request_data.get("message_data")
        
        if not all([prospect_id, message_data]):
            raise HTTPException(
                status_code=400, 
                detail="Missing required fields: prospect_id, message_data"
            )
        
        await context_aware_ai.update_conversation_memory(prospect_id, message_data)
        return {"message": "Conversation memory updated successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/context-aware-ai/prospect-insights/{prospect_id}")
async def get_prospect_insights(prospect_id: str):
    """Get AI-generated insights about a prospect"""
    try:
        # Get prospect data
        prospect = await db_service.get_prospect_by_id(prospect_id)
        if not prospect:
            raise HTTPException(status_code=404, detail="Prospect not found")
        
        # Get conversation history
        thread = await db_service.get_thread_by_prospect_id(prospect_id)
        conversation_history = thread.get("messages", []) if thread else []
        
        # Generate insights
        insights = await context_aware_ai._get_prospect_insights(prospect)
        
        # Add conversation analysis
        if conversation_history:
            conversation_patterns = await context_aware_ai._analyze_conversation_patterns(conversation_history)
            insights["conversation_patterns"] = conversation_patterns
        
        return {
            "prospect_id": prospect_id,
            "insights": insights,
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/context-aware-ai/system-analytics")
async def get_context_aware_analytics():
    """Get analytics for context-aware AI system"""
    try:
        # Get recent AI-generated responses
        recent_responses = await db_service.db.emails.find({
            "ai_generated": True,
            "created_at": {"$gte": datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)}
        }).to_list(length=100)
        
        # Get verification statistics
        verification_stats = await db_service.get_verification_statistics()
        
        # Calculate context usage statistics
        context_enhanced_count = len([r for r in recent_responses if r.get("enhanced_with_context", False)])
        
        analytics = {
            "daily_ai_responses": len(recent_responses),
            "context_enhanced_responses": context_enhanced_count,
            "verification_stats": verification_stats,
            "context_enhancement_rate": (context_enhanced_count / len(recent_responses) * 100) if recent_responses else 0,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return analytics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/context-aware-ai/batch-process")
async def batch_process_conversations(request_data: Dict):
    """Batch process multiple conversations for context analysis"""
    try:
        prospect_ids = request_data.get("prospect_ids", [])
        if not prospect_ids:
            raise HTTPException(status_code=400, detail="No prospect IDs provided")
        
        results = []
        for prospect_id in prospect_ids:
            try:
                summary = await context_aware_ai.get_conversation_summary(prospect_id)
                results.append({
                    "prospect_id": prospect_id,
                    "summary": summary,
                    "status": "success"
                })
            except Exception as e:
                results.append({
                    "prospect_id": prospect_id,
                    "error": str(e),
                    "status": "failed"
                })
        
        return {
            "total_processed": len(prospect_ids),
            "successful": len([r for r in results if r["status"] == "success"]),
            "failed": len([r for r in results if r["status"] == "failed"]),
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))