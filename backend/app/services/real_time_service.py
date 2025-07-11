from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Set
import json
import asyncio
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_subscriptions: Dict[str, Set[str]] = {}
        
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.connection_subscriptions[client_id] = set()
        logger.info(f"Client {client_id} connected")
        
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self.connection_subscriptions:
            del self.connection_subscriptions[client_id]
        logger.info(f"Client {client_id} disconnected")
        
    async def send_personal_message(self, message: str, client_id: str):
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(message)
            except Exception as e:
                logger.error(f"Error sending message to {client_id}: {e}")
                self.disconnect(client_id)
    
    async def send_personal_json(self, data: dict, client_id: str):
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json(data)
            except Exception as e:
                logger.error(f"Error sending JSON to {client_id}: {e}")
                self.disconnect(client_id)
                
    async def broadcast_to_subscribed(self, message: dict, event_type: str):
        """Broadcast message to all clients subscribed to a specific event type"""
        disconnected_clients = []
        
        for client_id, websocket in self.active_connections.items():
            if event_type in self.connection_subscriptions.get(client_id, set()):
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to {client_id}: {e}")
                    disconnected_clients.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)
    
    def subscribe_to_event(self, client_id: str, event_type: str):
        """Subscribe client to specific event type"""
        if client_id in self.connection_subscriptions:
            self.connection_subscriptions[client_id].add(event_type)
            logger.info(f"Client {client_id} subscribed to {event_type}")
    
    def unsubscribe_from_event(self, client_id: str, event_type: str):
        """Unsubscribe client from specific event type"""
        if client_id in self.connection_subscriptions:
            self.connection_subscriptions[client_id].discard(event_type)
            logger.info(f"Client {client_id} unsubscribed from {event_type}")

class RealTimeService:
    def __init__(self):
        self.manager = ConnectionManager()
        self.metrics_cache = {}
        self.last_metrics_update = None
        
    async def start_real_time_monitoring(self):
        """Start background tasks for real-time monitoring"""
        asyncio.create_task(self._metrics_updater())
        asyncio.create_task(self._notification_handler())
        
    async def _metrics_updater(self):
        """Background task to update metrics every 10 seconds"""
        while True:
            try:
                # Update metrics
                await self._update_dashboard_metrics()
                
                # Broadcast to subscribed clients
                await self.manager.broadcast_to_subscribed(
                    {
                        "type": "metrics_update",
                        "data": self.metrics_cache,
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    "dashboard_metrics"
                )
                
                await asyncio.sleep(10)  # Update every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in metrics updater: {e}")
                await asyncio.sleep(30)  # Wait longer on error
    
    async def _notification_handler(self):
        """Background task to handle notifications"""
        while True:
            try:
                # Check for important notifications
                await self._check_for_notifications()
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in notification handler: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _update_dashboard_metrics(self):
        """Update dashboard metrics cache"""
        from app.services.database import db_service
        
        try:
            # Get basic counts
            total_prospects = await db_service.db.prospects.count_documents({})
            total_campaigns = await db_service.db.campaigns.count_documents({})
            total_emails_sent = await db_service.db.emails.count_documents({})
            
            # Get today's activity
            today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            emails_today = await db_service.db.emails.count_documents({
                "created_at": {"$gte": today}
            })
            
            # Get active campaigns
            active_campaigns = await db_service.db.campaigns.count_documents({
                "status": "active"
            })
            
            # Get email provider stats
            providers = await db_service.db.email_providers.find({}).to_list(length=None)
            provider_stats = {}
            for provider in providers:
                provider_stats[provider['name']] = {
                    "type": provider['provider_type'],
                    "status": provider['status'],
                    "emails_sent_today": provider.get('emails_sent_today', 0),
                    "daily_limit": provider.get('daily_limit', 0)
                }
            
            # Get recent activity
            recent_emails = await db_service.db.emails.find({}).sort("created_at", -1).limit(10).to_list(length=10)
            recent_activity = []
            for email in recent_emails:
                recent_activity.append({
                    "id": str(email.get('_id')),
                    "subject": email.get('subject', 'No Subject'),
                    "recipient": email.get('recipient', 'Unknown'),
                    "status": email.get('status', 'Unknown'),
                    "created_at": email.get('created_at').isoformat() if email.get('created_at') else None
                })
            
            # Update cache
            self.metrics_cache = {
                "overview": {
                    "total_prospects": total_prospects,
                    "total_campaigns": total_campaigns,
                    "total_emails_sent": total_emails_sent,
                    "emails_today": emails_today,
                    "active_campaigns": active_campaigns
                },
                "provider_stats": provider_stats,
                "recent_activity": recent_activity,
                "last_updated": datetime.utcnow().isoformat()
            }
            
            self.last_metrics_update = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Error updating dashboard metrics: {e}")
    
    async def _check_for_notifications(self):
        """Check for important notifications to send"""
        from app.services.database import db_service
        
        try:
            notifications = []
            
            # Check for provider limits
            providers = await db_service.db.email_providers.find({}).to_list(length=None)
            for provider in providers:
                emails_sent = provider.get('emails_sent_today', 0)
                daily_limit = provider.get('daily_limit', 0)
                
                if daily_limit > 0:
                    usage_percent = (emails_sent / daily_limit) * 100
                    if usage_percent >= 80:
                        notifications.append({
                            "type": "warning",
                            "title": "Email Provider Limit Warning",
                            "message": f"Provider '{provider['name']}' has used {usage_percent:.1f}% of daily limit",
                            "timestamp": datetime.utcnow().isoformat()
                        })
            
            # Check for failed campaigns
            failed_campaigns = await db_service.db.campaigns.find({
                "status": "failed",
                "updated_at": {"$gte": datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)}
            }).to_list(length=None)
            
            for campaign in failed_campaigns:
                notifications.append({
                    "type": "error",
                    "title": "Campaign Failed",
                    "message": f"Campaign '{campaign['name']}' has failed",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            # Send notifications
            if notifications:
                await self.manager.broadcast_to_subscribed(
                    {
                        "type": "notifications",
                        "data": notifications,
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    "notifications"
                )
                
        except Exception as e:
            logger.error(f"Error checking for notifications: {e}")
    
    async def send_campaign_progress_update(self, campaign_id: str, progress_data: dict):
        """Send campaign progress update to subscribed clients"""
        message = {
            "type": "campaign_progress",
            "campaign_id": campaign_id,
            "data": progress_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.manager.broadcast_to_subscribed(message, "campaign_progress")
    
    async def send_provider_status_update(self, provider_id: str, status_data: dict):
        """Send provider status update to subscribed clients"""
        message = {
            "type": "provider_status",
            "provider_id": provider_id,
            "data": status_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.manager.broadcast_to_subscribed(message, "provider_status")

# Global instance
real_time_service = RealTimeService()