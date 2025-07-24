from fastapi import APIRouter, HTTPException
from app.services.database import db_service
from app.services.email_processor import email_processor
from app.services.smart_follow_up_engine import smart_follow_up_engine
from datetime import datetime, timedelta
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/follow-up-monitoring/dashboard")
async def get_follow_up_dashboard():
    """Get comprehensive follow-up monitoring dashboard"""
    try:
        # Get IMAP monitoring stats
        imap_stats = await db_service.get_imap_monitoring_stats()
        
        # Get follow-up statistics
        follow_up_stats = await smart_follow_up_engine.get_follow_up_statistics()
        
        # Get active campaigns with follow-up enabled
        active_campaigns = await db_service.get_active_follow_up_campaigns()
        
        # Get prospects needing follow-up
        prospects_needing_follow_up = await db_service.get_prospects_needing_follow_up()
        
        # Get recent responses
        recent_responses = await _get_recent_prospect_responses()
        
        return {
            "imap_monitoring": imap_stats,
            "follow_up_stats": follow_up_stats,
            "active_campaigns": len(active_campaigns),
            "prospects_needing_follow_up": len(prospects_needing_follow_up),
            "recent_responses": recent_responses,
            "system_status": {
                "email_processor_running": email_processor.processing,
                "follow_up_engine_running": smart_follow_up_engine.processing,
                "last_updated": datetime.utcnow()
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting follow-up dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/follow-up-monitoring/imap-scan-status")
async def get_last_imap_scan_status():
    """Get the status of the last IMAP scan with detailed information"""
    try:
        # Get the most recent IMAP scan log
        recent_logs = await db_service.db.imap_scan_logs.find().sort("timestamp", -1).limit(1).to_list(1)
        last_scan = recent_logs[0] if recent_logs else None
        
        # Get overall IMAP statistics
        cutoff_24h = datetime.utcnow() - timedelta(hours=24)
        logs_24h = await db_service.db.imap_scan_logs.find({
            "timestamp": {"$gte": cutoff_24h}
        }).to_list(100)
        
        # Calculate statistics
        total_scans_24h = len(logs_24h)
        total_emails_found_24h = sum(log.get("new_emails_found", 0) for log in logs_24h)
        total_emails_processed_24h = sum(log.get("emails_processed", 0) for log in logs_24h)
        total_errors_24h = sum(len(log.get("errors", [])) for log in logs_24h)
        
        # Get email processor status
        from app.services.email_processor import email_processor
        processor_running = email_processor.processing
        
        return {
            "last_scan": {
                "timestamp": last_scan["timestamp"] if last_scan else None,
                "new_emails_found": last_scan.get("new_emails_found", 0) if last_scan else 0,
                "emails_processed": last_scan.get("emails_processed", 0) if last_scan else 0,
                "scan_duration_seconds": last_scan.get("scan_duration_seconds", 0) if last_scan else 0,
                "errors": last_scan.get("errors", []) if last_scan else [],
                "success": len(last_scan.get("errors", [])) == 0 if last_scan else False
            },
            "statistics_24h": {
                "total_scans": total_scans_24h,
                "total_emails_found": total_emails_found_24h,
                "total_emails_processed": total_emails_processed_24h,
                "total_errors": total_errors_24h,
                "avg_emails_per_scan": round(total_emails_found_24h / max(total_scans_24h, 1), 2),
                "success_rate": round((total_scans_24h - total_errors_24h) / max(total_scans_24h, 1) * 100, 2) if total_scans_24h > 0 else 100
            },
            "processor_status": {
                "running": processor_running,
                "last_check": datetime.utcnow(),
                "next_scan_in_seconds": 30 if processor_running else None
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting IMAP scan status: {str(e)}")
        return {
            "last_scan": None,
            "statistics_24h": {
                "total_scans": 0,
                "total_emails_found": 0,
                "total_emails_processed": 0,
                "total_errors": 0,
                "avg_emails_per_scan": 0,
                "success_rate": 100
            },
            "processor_status": {
                "running": False,
                "last_check": datetime.utcnow(),
                "next_scan_in_seconds": None,
                "error": str(e)
            }
        }

@router.get("/follow-up-monitoring/imap-logs")
async def get_imap_scan_logs(hours: int = 24):
    """Get IMAP scan logs for the last N hours"""
    try:
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        logs = await db_service.db.imap_scan_logs.find({
            "timestamp": {"$gte": cutoff_time}
        }).sort("timestamp", -1).limit(100).to_list(100)
        
        return {
            "logs": logs,
            "total_scans": len(logs),
            "time_range_hours": hours
        }
        
    except Exception as e:
        logger.error(f"Error getting IMAP logs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/follow-up-monitoring/prospect-responses")
async def get_prospect_responses(days: int = 7):
    """Get prospect responses for the last N days"""
    try:
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        
        # Get prospects who responded recently
        responded_prospects = await db_service.db.prospects.find({
            "responded_at": {"$gte": cutoff_time}
        }).to_list(100)
        
        # Get their follow-up history
        response_data = []
        for prospect in responded_prospects:
            follow_up_history = await db_service.get_prospect_follow_up_history(prospect["id"])
            response_data.append({
                "prospect": prospect,
                "follow_up_history": follow_up_history,
                "response_type": prospect.get("response_type", "unknown")
            })
        
        return {
            "responses": response_data,
            "total_responses": len(responded_prospects),
            "time_range_days": days
        }
        
    except Exception as e:
        logger.error(f"Error getting prospect responses: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/follow-up-monitoring/thread-analysis/{prospect_id}")
async def analyze_prospect_thread(prospect_id: str):
    """Analyze a prospect's thread for follow-up effectiveness"""
    try:
        # Get prospect
        prospect = await db_service.get_prospect_by_id(prospect_id)
        if not prospect:
            raise HTTPException(status_code=404, detail="Prospect not found")
        
        # Get thread
        thread = await db_service.get_thread_by_prospect_id(prospect_id)
        if not thread:
            return {
                "prospect_id": prospect_id,
                "thread_found": False,
                "analysis": "No thread found for this prospect"
            }
        
        # Analyze thread messages
        messages = thread.get("messages", [])
        sent_messages = [m for m in messages if m.get("sent_by_us", False)]
        received_messages = [m for m in messages if m.get("type") == "received"]
        
        # Get follow-up history
        follow_up_history = await db_service.get_prospect_follow_up_history(prospect_id)
        
        # Calculate response metrics
        response_time = None
        if sent_messages and received_messages:
            last_sent = max(sent_messages, key=lambda x: x.get("timestamp", datetime.min))
            first_response = min(
                [m for m in received_messages if m.get("timestamp") > last_sent.get("timestamp", datetime.min)],
                key=lambda x: x.get("timestamp", datetime.max),
                default=None
            )
            if first_response:
                response_time = (first_response["timestamp"] - last_sent["timestamp"]).total_seconds()
        
        return {
            "prospect_id": prospect_id,
            "prospect": prospect,
            "thread_found": True,
            "analysis": {
                "total_messages": len(messages),
                "sent_by_us": len(sent_messages),
                "received_from_prospect": len(received_messages),
                "follow_up_count": len(follow_up_history),
                "response_time_seconds": response_time,
                "follow_up_status": prospect.get("follow_up_status", "unknown"),
                "response_type": prospect.get("response_type", "none")
            },
            "messages": messages,
            "follow_up_history": follow_up_history
        }
        
    except Exception as e:
        logger.error(f"Error analyzing prospect thread: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/follow-up-monitoring/force-stop-follow-up/{prospect_id}")
async def force_stop_follow_up(prospect_id: str):
    """Force stop follow-ups for a prospect"""
    try:
        # Check if prospect exists
        prospect = await db_service.get_prospect_by_id(prospect_id)
        if not prospect:
            raise HTTPException(status_code=404, detail="Prospect not found")
        
        # Stop follow-ups
        success = await db_service.mark_prospect_as_responded(prospect_id, "manual_stop")
        
        if success:
            # Cancel pending follow-ups
            await db_service.cancel_pending_follow_ups(prospect_id)
            
            return {
                "message": f"Follow-ups stopped for prospect {prospect_id}",
                "prospect_id": prospect_id,
                "action": "force_stopped"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to stop follow-ups")
        
    except Exception as e:
        logger.error(f"Error force stopping follow-up: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/follow-up-monitoring/restart-follow-up/{prospect_id}")
async def restart_follow_up(prospect_id: str):
    """Restart follow-ups for a prospect"""
    try:
        # Check if prospect exists
        prospect = await db_service.get_prospect_by_id(prospect_id)
        if not prospect:
            raise HTTPException(status_code=404, detail="Prospect not found")
        
        # Restart follow-ups
        success = await db_service.update_prospect(prospect_id, {
            "follow_up_status": "active",
            "responded_at": None,
            "response_type": "",
            "follow_up_count": 0,
            "last_follow_up": None
        })
        
        if success:
            return {
                "message": f"Follow-ups restarted for prospect {prospect_id}",
                "prospect_id": prospect_id,
                "action": "restarted"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to restart follow-ups")
        
    except Exception as e:
        logger.error(f"Error restarting follow-up: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/follow-up-monitoring/health-check")
async def health_check():
    """Health check for follow-up monitoring system"""
    try:
        # Check database connection
        await db_service.connect()
        
        # Check recent IMAP activity
        recent_logs = await db_service.db.imap_scan_logs.find().sort("timestamp", -1).limit(1).to_list(1)
        last_scan = recent_logs[0] if recent_logs else None
        
        # Check if systems are running
        health_status = {
            "database_connected": True,
            "email_processor_running": email_processor.processing,
            "follow_up_engine_running": smart_follow_up_engine.processing,
            "last_imap_scan": last_scan["timestamp"] if last_scan else None,
            "system_time": datetime.utcnow()
        }
        
        # Determine overall health
        overall_health = (
            health_status["database_connected"] and
            health_status["email_processor_running"] and
            health_status["follow_up_engine_running"]
        )
        
        return {
            "status": "healthy" if overall_health else "unhealthy",
            "details": health_status
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

async def _get_recent_prospect_responses(hours: int = 24):
    """Get recent prospect responses"""
    try:
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        responses = await db_service.db.prospects.find({
            "responded_at": {"$gte": cutoff_time}
        }).sort("responded_at", -1).limit(10).to_list(10)
        
        return [
            {
                "prospect_id": r["id"],
                "email": r["email"],
                "responded_at": r["responded_at"],
                "response_type": r.get("response_type", "unknown"),
                "follow_up_count": r.get("follow_up_count", 0)
            }
            for r in responses
        ]
        
    except Exception as e:
        logger.error(f"Error getting recent responses: {str(e)}")
        return []