# Conversation Context Service - Manages conversation state and context
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from app.services.database import db_service
from app.utils.helpers import generate_id

logger = logging.getLogger(__name__)

class ConversationContextService:
    def __init__(self):
        self.db = db_service
        self.active_sessions = {}  # In-memory cache for active sessions
    
    async def get_session_context(self, session_id: str) -> Dict[str, Any]:
        """
        Get conversation context for a session
        """
        try:
            # First check in-memory cache
            if session_id in self.active_sessions:
                return self.active_sessions[session_id]
            
            # Connect to database
            await self.db.connect()
            
            # Get from database
            context = await self.db.db.conversation_sessions.find_one({"session_id": session_id})
            
            if context:
                # Cache it
                self.active_sessions[session_id] = context
                return context
            else:
                # Create new session context
                new_context = {
                    "session_id": session_id,
                    "messages": [],
                    "context_variables": {},
                    "user_preferences": {},
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                    "last_activity": datetime.utcnow()
                }
                
                await self.db.db.conversation_sessions.insert_one(new_context)
                self.active_sessions[session_id] = new_context
                return new_context
                
        except Exception as e:
            logger.error(f"Error getting session context: {e}")
            return {
                "session_id": session_id,
                "messages": [],
                "context_variables": {},
                "user_preferences": {},
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "last_activity": datetime.utcnow()
            }
    
    async def save_conversation_turn(self, session_id: str, user_message: str, agent_response: str, action_taken: Optional[str] = None, data: Optional[Dict] = None):
        """
        Save a conversation turn (user message + agent response)
        """
        try:
            # Get current context
            context = await self.get_session_context(session_id)
            
            # Create conversation turn
            turn = {
                "turn_id": generate_id(),
                "timestamp": datetime.utcnow(),
                "user_message": user_message,
                "agent_response": agent_response,
                "action_taken": action_taken,
                "data": data
            }
            
            # Add to messages
            context["messages"].append(turn)
            context["updated_at"] = datetime.utcnow()
            context["last_activity"] = datetime.utcnow()
            
            # Update context variables based on the conversation
            await self.update_context_variables(context, user_message, action_taken, data)
            
            # Save to database
            await self.db.connect()
            await self.db.db.conversation_sessions.update_one(
                {"session_id": session_id},
                {"$set": context},
                upsert=True
            )
            
            # Update cache
            self.active_sessions[session_id] = context
            
            logger.info(f"Saved conversation turn for session {session_id}")
            
        except Exception as e:
            logger.error(f"Error saving conversation turn: {e}")
    
    async def update_context_variables(self, context: Dict[str, Any], user_message: str, action_taken: Optional[str], data: Optional[Dict]):
        """
        Update context variables based on conversation content
        """
        try:
            variables = context.get("context_variables", {})
            
            # Track user preferences
            message_lower = user_message.lower()
            
            # Track frequently mentioned entities
            if 'campaign' in message_lower:
                variables['last_discussed_entity'] = 'campaign'
                variables['campaign_mentions'] = variables.get('campaign_mentions', 0) + 1
            elif 'prospect' in message_lower:
                variables['last_discussed_entity'] = 'prospect'
                variables['prospect_mentions'] = variables.get('prospect_mentions', 0) + 1
            elif 'template' in message_lower:
                variables['last_discussed_entity'] = 'template'
                variables['template_mentions'] = variables.get('template_mentions', 0) + 1
            
            # Track successful actions
            if action_taken and data:
                variables['last_successful_action'] = action_taken
                variables['successful_actions'] = variables.get('successful_actions', [])
                variables['successful_actions'].append({
                    "action": action_taken,
                    "timestamp": datetime.utcnow().isoformat(),
                    "success": data is not None
                })
                
                # Keep only last 10 successful actions
                if len(variables['successful_actions']) > 10:
                    variables['successful_actions'] = variables['successful_actions'][-10:]
            
            # Track user communication style
            if any(word in message_lower for word in ['please', 'thank you', 'thanks']):
                variables['polite_user'] = True
            
            if len(user_message.split()) < 5:
                variables['prefers_brief_commands'] = variables.get('prefers_brief_commands', 0) + 1
            else:
                variables['prefers_detailed_commands'] = variables.get('prefers_detailed_commands', 0) + 1
            
            # Update timestamp
            variables['last_updated'] = datetime.utcnow().isoformat()
            
            context["context_variables"] = variables
            
        except Exception as e:
            logger.error(f"Error updating context variables: {e}")
    
    async def clear_session(self, session_id: str):
        """
        Clear a conversation session
        """
        try:
            # Remove from cache
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
            
            # Remove from database
            await self.db.connect()
            await self.db.db.conversation_sessions.delete_one({"session_id": session_id})
            
            logger.info(f"Cleared session {session_id}")
            
        except Exception as e:
            logger.error(f"Error clearing session: {e}")
    
    async def get_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all sessions for a user
        """
        try:
            await self.db.connect()
            
            # For now, we'll get all recent sessions (in production, you'd filter by user_id)
            sessions = await self.db.db.conversation_sessions.find({
                "last_activity": {"$gte": datetime.utcnow() - timedelta(days=7)}
            }).sort("last_activity", -1).to_list(length=20)
            
            # Convert ObjectId to string and clean up
            for session in sessions:
                if '_id' in session:
                    session['_id'] = str(session['_id'])
                
                # Add summary info
                messages = session.get('messages', [])
                session['message_count'] = len(messages)
                session['last_message'] = messages[-1]['user_message'] if messages else ''
                session['duration'] = (session.get('updated_at', session.get('created_at')) - session.get('created_at')).total_seconds() if session.get('updated_at') and session.get('created_at') else 0
            
            return sessions
            
        except Exception as e:
            logger.error(f"Error getting user sessions: {e}")
            return []
    
    async def get_conversation_summary(self, session_id: str) -> Dict[str, Any]:
        """
        Get a summary of the conversation
        """
        try:
            context = await self.get_session_context(session_id)
            messages = context.get('messages', [])
            variables = context.get('context_variables', {})
            
            if not messages:
                return {
                    "session_id": session_id,
                    "summary": "No conversation yet",
                    "message_count": 0,
                    "topics": [],
                    "actions_taken": []
                }
            
            # Analyze conversation topics
            topics = []
            actions_taken = []
            
            for message in messages:
                if message.get('action_taken'):
                    actions_taken.append({
                        "action": message['action_taken'],
                        "timestamp": message['timestamp'].isoformat(),
                        "success": message.get('data') is not None
                    })
            
            # Extract topics from context variables
            if variables.get('last_discussed_entity'):
                topics.append(variables['last_discussed_entity'])
            
            return {
                "session_id": session_id,
                "summary": f"Conversation with {len(messages)} turns focusing on {', '.join(topics) if topics else 'general topics'}",
                "message_count": len(messages),
                "topics": topics,
                "actions_taken": actions_taken,
                "duration": (context.get('updated_at') - context.get('created_at')).total_seconds() if context.get('updated_at') and context.get('created_at') else 0,
                "last_activity": context.get('last_activity').isoformat() if context.get('last_activity') else None
            }
            
        except Exception as e:
            logger.error(f"Error getting conversation summary: {e}")
            return {
                "session_id": session_id,
                "summary": "Error retrieving summary",
                "message_count": 0,
                "topics": [],
                "actions_taken": []
            }
    
    async def get_usage_analytics(self) -> Dict[str, Any]:
        """
        Get usage analytics for the AI agent
        """
        try:
            await self.db.connect()
            
            # Get recent sessions (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_sessions = await self.db.db.conversation_sessions.find({
                "created_at": {"$gte": thirty_days_ago}
            }).to_list(length=1000)
            
            # Calculate analytics
            total_sessions = len(recent_sessions)
            total_messages = sum(len(session.get('messages', [])) for session in recent_sessions)
            
            # Count actions
            action_counts = {}
            successful_actions = 0
            
            for session in recent_sessions:
                for message in session.get('messages', []):
                    action = message.get('action_taken')
                    if action:
                        action_counts[action] = action_counts.get(action, 0) + 1
                        if message.get('data'):
                            successful_actions += 1
            
            # Calculate average session length
            avg_session_length = total_messages / total_sessions if total_sessions > 0 else 0
            
            # Get most active days
            daily_usage = {}
            for session in recent_sessions:
                date_key = session.get('created_at').date().isoformat()
                daily_usage[date_key] = daily_usage.get(date_key, 0) + 1
            
            return {
                "period": "last_30_days",
                "total_sessions": total_sessions,
                "total_messages": total_messages,
                "average_session_length": round(avg_session_length, 1),
                "successful_actions": successful_actions,
                "action_breakdown": action_counts,
                "most_popular_actions": sorted(action_counts.items(), key=lambda x: x[1], reverse=True)[:5],
                "daily_usage": daily_usage,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting usage analytics: {e}")
            return {
                "period": "last_30_days",
                "total_sessions": 0,
                "total_messages": 0,
                "average_session_length": 0,
                "successful_actions": 0,
                "action_breakdown": {},
                "most_popular_actions": [],
                "daily_usage": {},
                "error": str(e),
                "generated_at": datetime.utcnow().isoformat()
            }
    
    async def cleanup_old_sessions(self, days_old: int = 30):
        """
        Clean up old conversation sessions
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            await self.db.connect()
            result = await self.db.db.conversation_sessions.delete_many({
                "last_activity": {"$lt": cutoff_date}
            })
            
            # Also clean up in-memory cache
            sessions_to_remove = []
            for session_id, context in self.active_sessions.items():
                if context.get('last_activity', datetime.utcnow()) < cutoff_date:
                    sessions_to_remove.append(session_id)
            
            for session_id in sessions_to_remove:
                del self.active_sessions[session_id]
            
            logger.info(f"Cleaned up {result.deleted_count} old sessions")
            return result.deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up old sessions: {e}")
            return 0

# Global instance
conversation_context_service = ConversationContextService()