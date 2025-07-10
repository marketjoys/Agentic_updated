from fastapi import APIRouter, HTTPException
from app.services.response_verification_service import response_verification_service
from app.services.database import db_service
from typing import Dict, List

router = APIRouter()

@router.post("/response-verification/verify")
async def verify_response(verification_request: Dict):
    """Verify an AI-generated response before sending"""
    try:
        message_id = verification_request.get("message_id")
        response_content = verification_request.get("response_content")
        original_email = verification_request.get("original_email")
        classified_intents = verification_request.get("classified_intents", [])
        conversation_context = verification_request.get("conversation_context", [])
        prospect_data = verification_request.get("prospect_data", {})
        
        if not all([message_id, response_content, original_email]):
            raise HTTPException(status_code=400, detail="Missing required fields: message_id, response_content, original_email")
        
        verification_result = await response_verification_service.verify_response(
            message_id, response_content, original_email, 
            classified_intents, conversation_context, prospect_data
        )
        
        return verification_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")

@router.get("/response-verification/pending")
async def get_pending_verifications():
    """Get all pending verifications that need manual review"""
    verifications = await response_verification_service.get_pending_verifications()
    return verifications

@router.get("/response-verification/{verification_id}")
async def get_verification(verification_id: str):
    """Get a specific verification by ID"""
    verification = await response_verification_service.get_verification_by_id(verification_id)
    if not verification:
        raise HTTPException(status_code=404, detail="Verification not found")
    return verification

@router.post("/response-verification/{verification_id}/approve")
async def approve_verification(verification_id: str, approval_data: Dict):
    """Manually approve a verification"""
    reviewer = approval_data.get("reviewer", "unknown")
    notes = approval_data.get("notes", "")
    
    success, error = await response_verification_service.approve_verification(
        verification_id, reviewer, notes
    )
    
    if error:
        raise HTTPException(status_code=400, detail=error)
    
    if not success:
        raise HTTPException(status_code=404, detail="Verification not found")
    
    return {"message": "Verification approved successfully"}

@router.post("/response-verification/{verification_id}/reject")
async def reject_verification(verification_id: str, rejection_data: Dict):
    """Manually reject a verification"""
    reviewer = rejection_data.get("reviewer", "unknown")
    notes = rejection_data.get("notes", "")
    suggested_changes = rejection_data.get("suggested_changes", "")
    
    success, error = await response_verification_service.reject_verification(
        verification_id, reviewer, notes, suggested_changes
    )
    
    if error:
        raise HTTPException(status_code=400, detail=error)
    
    if not success:
        raise HTTPException(status_code=404, detail="Verification not found")
    
    return {"message": "Verification rejected successfully"}

@router.put("/response-verification/{verification_id}/content")
async def update_response_content(verification_id: str, content_data: Dict):
    """Update response content after verification"""
    new_content = content_data.get("content")
    
    if not new_content:
        raise HTTPException(status_code=400, detail="New content is required")
    
    success, error = await response_verification_service.update_response_content(
        verification_id, new_content
    )
    
    if error:
        raise HTTPException(status_code=400, detail=error)
    
    if not success:
        raise HTTPException(status_code=404, detail="Verification not found")
    
    return {"message": "Response content updated successfully"}

@router.get("/response-verification/statistics/overview")
async def get_verification_statistics():
    """Get verification statistics"""
    stats = await response_verification_service.get_verification_statistics()
    return stats

@router.post("/response-verification/batch-process")
async def batch_process_verifications(batch_data: Dict):
    """Process multiple verifications at once"""
    verification_actions = batch_data.get("actions", [])
    reviewer = batch_data.get("reviewer", "unknown")
    
    if not verification_actions:
        raise HTTPException(status_code=400, detail="No verification actions provided")
    
    results = {"successful": [], "failed": []}
    
    for action in verification_actions:
        verification_id = action.get("verification_id")
        action_type = action.get("action")  # approve, reject
        notes = action.get("notes", "")
        
        try:
            if action_type == "approve":
                success, error = await response_verification_service.approve_verification(
                    verification_id, reviewer, notes
                )
            elif action_type == "reject":
                suggested_changes = action.get("suggested_changes", "")
                success, error = await response_verification_service.reject_verification(
                    verification_id, reviewer, notes, suggested_changes
                )
            else:
                results["failed"].append({
                    "verification_id": verification_id,
                    "error": "Invalid action type"
                })
                continue
            
            if success:
                results["successful"].append(verification_id)
            else:
                results["failed"].append({
                    "verification_id": verification_id,
                    "error": error or "Unknown error"
                })
                
        except Exception as e:
            results["failed"].append({
                "verification_id": verification_id,
                "error": str(e)
            })
    
    return {
        "message": f"Processed {len(results['successful'])} verifications successfully, {len(results['failed'])} failed",
        "results": results
    }

@router.get("/response-verification/quality-metrics/dashboard")
async def get_quality_metrics():
    """Get verification quality metrics for dashboard"""
    try:
        stats = await response_verification_service.get_verification_statistics()
        
        # Calculate quality metrics
        total = stats.get("total_verifications", 0)
        approved = stats.get("approved_verifications", 0)
        rejected = stats.get("rejected_verifications", 0)
        pending = stats.get("pending_verifications", 0)
        
        approval_rate = (approved / total * 100) if total > 0 else 0
        rejection_rate = (rejected / total * 100) if total > 0 else 0
        
        # Get recent verifications for trends
        recent_verifications = await response_verification_service.get_pending_verifications()
        
        # Calculate average scores from recent verifications
        avg_context_score = 0
        avg_intent_score = 0
        avg_overall_score = 0
        
        if recent_verifications:
            context_scores = [v.get("context_score", 0) for v in recent_verifications if v.get("context_score")]
            intent_scores = [v.get("intent_alignment_score", 0) for v in recent_verifications if v.get("intent_alignment_score")]
            overall_scores = [v.get("overall_score", 0) for v in recent_verifications if v.get("overall_score")]
            
            avg_context_score = sum(context_scores) / len(context_scores) if context_scores else 0
            avg_intent_score = sum(intent_scores) / len(intent_scores) if intent_scores else 0
            avg_overall_score = sum(overall_scores) / len(overall_scores) if overall_scores else 0
        
        return {
            "total_verifications": total,
            "approval_rate": round(approval_rate, 2),
            "rejection_rate": round(rejection_rate, 2),
            "pending_verifications": pending,
            "quality_scores": {
                "average_context_score": round(avg_context_score, 3),
                "average_intent_score": round(avg_intent_score, 3),
                "average_overall_score": round(avg_overall_score, 3)
            },
            "status_distribution": {
                "approved": approved,
                "rejected": rejected,
                "pending": pending
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting quality metrics: {str(e)}")

@router.post("/response-verification/auto-approve-threshold")
async def set_auto_approve_threshold(threshold_data: Dict):
    """Set automatic approval threshold"""
    threshold = threshold_data.get("threshold", 0.75)
    
    if not 0.0 <= threshold <= 1.0:
        raise HTTPException(status_code=400, detail="Threshold must be between 0.0 and 1.0")
    
    # Update the service threshold
    response_verification_service.verification_thresholds["overall_score"] = threshold
    
    return {
        "message": "Auto-approval threshold updated successfully",
        "new_threshold": threshold
    }