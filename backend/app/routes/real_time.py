from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from app.services.real_time_service import real_time_service
from app.services.database import db_service
from typing import Dict
import json
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time communications"""
    if not client_id:
        client_id = str(uuid.uuid4())
    
    await real_time_service.manager.connect(websocket, client_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                await handle_websocket_message(client_id, message)
            except json.JSONDecodeError:
                await real_time_service.manager.send_personal_json(
                    {"error": "Invalid JSON format"}, client_id
                )
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {e}")
                await real_time_service.manager.send_personal_json(
                    {"error": "Internal server error"}, client_id
                )
                
    except WebSocketDisconnect:
        real_time_service.manager.disconnect(client_id)
        logger.info(f"Client {client_id} disconnected")

async def handle_websocket_message(client_id: str, message: Dict):
    """Handle incoming WebSocket messages"""
    message_type = message.get("type")
    
    if message_type == "subscribe":
        # Subscribe to event types
        event_types = message.get("event_types", [])
        for event_type in event_types:
            real_time_service.manager.subscribe_to_event(client_id, event_type)
        
        await real_time_service.manager.send_personal_json(
            {
                "type": "subscription_confirmed",
                "subscribed_to": event_types,
                "client_id": client_id
            },
            client_id
        )
    
    elif message_type == "unsubscribe":
        # Unsubscribe from event types
        event_types = message.get("event_types", [])
        for event_type in event_types:
            real_time_service.manager.unsubscribe_from_event(client_id, event_type)
        
        await real_time_service.manager.send_personal_json(
            {
                "type": "unsubscription_confirmed",
                "unsubscribed_from": event_types,
                "client_id": client_id
            },
            client_id
        )
    
    elif message_type == "get_current_metrics":
        # Send current metrics to the client
        await real_time_service.manager.send_personal_json(
            {
                "type": "current_metrics",
                "data": real_time_service.metrics_cache,
                "timestamp": real_time_service.last_metrics_update.isoformat() if real_time_service.last_metrics_update else None
            },
            client_id
        )
    
    elif message_type == "ping":
        # Respond to ping with pong
        await real_time_service.manager.send_personal_json(
            {
                "type": "pong",
                "timestamp": message.get("timestamp")
            },
            client_id
        )
    
    else:
        await real_time_service.manager.send_personal_json(
            {"error": f"Unknown message type: {message_type}"}, client_id
        )

@router.get("/real-time/dashboard-metrics")
async def get_dashboard_metrics():
    """Get current dashboard metrics"""
    try:
        # Update metrics if cache is old or empty
        if not real_time_service.metrics_cache or not real_time_service.last_metrics_update:
            await real_time_service._update_dashboard_metrics()
        
        return {
            "metrics": real_time_service.metrics_cache,
            "last_updated": real_time_service.last_metrics_update.isoformat() if real_time_service.last_metrics_update else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/real-time/active-connections")
async def get_active_connections():
    """Get information about active WebSocket connections"""
    try:
        connections_info = {}
        for client_id, subscriptions in real_time_service.manager.connection_subscriptions.items():
            connections_info[client_id] = {
                "subscriptions": list(subscriptions),
                "connected": client_id in real_time_service.manager.active_connections
            }
        
        return {
            "total_connections": len(real_time_service.manager.active_connections),
            "connections": connections_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/real-time/broadcast")
async def broadcast_message(message_data: Dict):
    """Broadcast a message to all connected clients"""
    try:
        event_type = message_data.get("event_type", "general")
        message = message_data.get("message", {})
        
        await real_time_service.manager.broadcast_to_subscribed(
            {
                "type": "broadcast",
                "data": message,
                "event_type": event_type
            },
            event_type
        )
        
        return {"success": True, "message": "Message broadcasted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/real-time/send-notification")
async def send_notification(notification_data: Dict):
    """Send a notification to all subscribed clients"""
    try:
        notification = {
            "type": notification_data.get("type", "info"),
            "title": notification_data.get("title", "Notification"),
            "message": notification_data.get("message", ""),
            "timestamp": notification_data.get("timestamp")
        }
        
        await real_time_service.manager.broadcast_to_subscribed(
            {
                "type": "notification",
                "data": notification
            },
            "notifications"
        )
        
        return {"success": True, "message": "Notification sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/real-time/system-status")
async def get_system_status():
    """Get comprehensive system status"""
    try:
        # Database status
        db_healthy = True
        try:
            await db_service.db.command("ping")
        except Exception:
            db_healthy = False
        
        # Email provider status
        providers = await db_service.db.email_providers.find({}).to_list(length=None)
        provider_status = {}
        for provider in providers:
            provider_status[provider['name']] = {
                "status": provider.get('status', 'unknown'),
                "last_tested": provider.get('last_tested'),
                "daily_usage": provider.get('emails_sent_today', 0),
                "daily_limit": provider.get('daily_limit', 0)
            }
        
        # Campaign status
        active_campaigns = await db_service.db.campaigns.count_documents({"status": "active"})
        failed_campaigns = await db_service.db.campaigns.count_documents({"status": "failed"})
        
        return {
            "database": {
                "healthy": db_healthy,
                "status": "connected" if db_healthy else "disconnected"
            },
            "email_providers": provider_status,
            "campaigns": {
                "active": active_campaigns,
                "failed": failed_campaigns
            },
            "websocket_connections": len(real_time_service.manager.active_connections),
            "timestamp": real_time_service.last_metrics_update.isoformat() if real_time_service.last_metrics_update else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/real-time/force-metrics-update")
async def force_metrics_update():
    """Force update of dashboard metrics"""
    try:
        await real_time_service._update_dashboard_metrics()
        return {
            "success": True,
            "message": "Metrics updated successfully",
            "last_updated": real_time_service.last_metrics_update.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))