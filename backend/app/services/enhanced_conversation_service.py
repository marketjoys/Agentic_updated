# Enhanced Conversation Context Service with Confirmation Flow
import logging
import re
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from app.models.conversation_models import (
    ConversationState, ConversationTurn, EnhancedConversationContext,
    InformationRequest, ConfirmationRequest
)
from app.services.database import db_service
from app.utils.helpers import generate_id

logger = logging.getLogger(__name__)

class EnhancedConversationService:
    """Enhanced conversation service with state management and confirmation flow"""
    
    def __init__(self):
        self.db = db_service
        self.active_contexts: Dict[str, EnhancedConversationContext] = {}
        self.default_max_turns = 10  # Default turn limit
    
    async def get_conversation_context(self, session_id: str, user_id: str = "default") -> EnhancedConversationContext:
        """Get or create conversation context"""
        try:
            # Check in-memory cache first
            if session_id in self.active_contexts:
                context = self.active_contexts[session_id]
                context.last_activity = datetime.utcnow()
                return context
            
            # Connect to database
            await self.db.connect()
            
            # Try to get from database
            context_data = await self.db.db.enhanced_conversations.find_one({"session_id": session_id})
            
            if context_data:
                # Convert to model
                context = self._convert_db_to_context(context_data)
                self.active_contexts[session_id] = context
                return context
            
            # Create new context
            context = EnhancedConversationContext(
                session_id=session_id,
                user_id=user_id,
                current_state=ConversationState.ANALYZING,
                turns=[],
                max_turns=self.default_max_turns,
                pending_action=None,
                extracted_params={},
                missing_params=[],
                endpoint_mapping=None,
                context_variables={},
                user_preferences={},
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                last_activity=datetime.utcnow()
            )
            
            # Save to database
            await self._save_context(context)
            self.active_contexts[session_id] = context
            
            return context
            
        except Exception as e:
            logger.error(f"Error getting conversation context: {e}")
            # Return minimal context on error
            return EnhancedConversationContext(
                session_id=session_id,
                user_id=user_id,
                current_state=ConversationState.ANALYZING,
                turns=[],
                max_turns=self.default_max_turns,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                last_activity=datetime.utcnow()
            )
    
    async def add_conversation_turn(self, 
                                 session_id: str, 
                                 user_message: str, 
                                 agent_response: str,
                                 state: ConversationState,
                                 intent: Optional[str] = None,
                                 extracted_params: Dict[str, Any] = None,
                                 missing_params: List[str] = None,
                                 action_taken: Optional[str] = None,
                                 data: Optional[Dict[str, Any]] = None) -> None:
        """Add a new conversation turn"""
        try:
            context = await self.get_conversation_context(session_id)
            
            # Create new turn
            turn = ConversationTurn(
                turn_id=generate_id(),
                timestamp=datetime.utcnow(),
                user_message=user_message,
                agent_response=agent_response,
                state=state,
                intent=intent,
                extracted_params=extracted_params or {},
                missing_params=missing_params or [],
                action_taken=action_taken,
                data=data
            )
            
            # Add turn to context
            context.turns.append(turn)
            context.updated_at = datetime.utcnow()
            context.last_activity = datetime.utcnow()
            
            # Manage turn limit
            if len(context.turns) > context.max_turns:
                # Keep only the most recent turns
                context.turns = context.turns[-context.max_turns:]
            
            # Update context variables using regex analysis
            await self._update_context_with_regex_analysis(context, user_message, agent_response)
            
            # Save to database and cache
            await self._save_context(context)
            self.active_contexts[session_id] = context
            
            logger.info(f"Added conversation turn for session {session_id}")
            
        except Exception as e:
            logger.error(f"Error adding conversation turn: {e}")
    
    async def update_conversation_state(self, session_id: str, new_state: ConversationState) -> None:
        """Update the conversation state"""
        try:
            context = await self.get_conversation_context(session_id)
            context.current_state = new_state
            context.updated_at = datetime.utcnow()
            context.last_activity = datetime.utcnow()
            
            await self._save_context(context)
            self.active_contexts[session_id] = context
            
        except Exception as e:
            logger.error(f"Error updating conversation state: {e}")
    
    async def set_pending_action(self, session_id: str, action_data: Dict[str, Any]) -> None:
        """Set the pending action for confirmation"""
        try:
            context = await self.get_conversation_context(session_id)
            context.pending_action = action_data
            context.updated_at = datetime.utcnow()
            
            await self._save_context(context)
            self.active_contexts[session_id] = context
            
        except Exception as e:
            logger.error(f"Error setting pending action: {e}")
    
    async def clear_pending_action(self, session_id: str) -> None:
        """Clear the pending action after execution"""
        try:
            context = await self.get_conversation_context(session_id)
            context.pending_action = None
            context.extracted_params = {}
            context.missing_params = []
            context.endpoint_mapping = None
            context.current_state = ConversationState.ANALYZING
            context.updated_at = datetime.utcnow()
            
            await self._save_context(context)
            self.active_contexts[session_id] = context
            
        except Exception as e:
            logger.error(f"Error clearing pending action: {e}")
    
    async def update_extracted_params(self, session_id: str, params: Dict[str, Any]) -> None:
        """Update extracted parameters"""
        try:
            context = await self.get_conversation_context(session_id)
            context.extracted_params.update(params)
            context.updated_at = datetime.utcnow()
            
            await self._save_context(context)
            self.active_contexts[session_id] = context
            
        except Exception as e:
            logger.error(f"Error updating extracted params: {e}")
    
    async def set_missing_params(self, session_id: str, missing_params: List[str]) -> None:
        """Set missing parameters that need to be collected"""
        try:
            context = await self.get_conversation_context(session_id)
            context.missing_params = missing_params
            context.updated_at = datetime.utcnow()
            
            await self._save_context(context)
            self.active_contexts[session_id] = context
            
        except Exception as e:
            logger.error(f"Error setting missing params: {e}")
    
    async def set_turn_limit(self, session_id: str, max_turns: int) -> None:
        """Set the maximum number of turns to keep in context"""
        try:
            context = await self.get_conversation_context(session_id)
            context.max_turns = max_turns
            
            # Trim existing turns if necessary
            if len(context.turns) > max_turns:
                context.turns = context.turns[-max_turns:]
            
            context.updated_at = datetime.utcnow()
            
            await self._save_context(context)
            self.active_contexts[session_id] = context
            
        except Exception as e:
            logger.error(f"Error setting turn limit: {e}")
    
    async def get_conversation_history(self, session_id: str, limit: Optional[int] = None) -> List[ConversationTurn]:
        """Get conversation history with optional limit"""
        try:
            context = await self.get_conversation_context(session_id)
            turns = context.turns
            
            if limit and len(turns) > limit:
                return turns[-limit:]
            
            return turns
            
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []
    
    async def _update_context_with_regex_analysis(self, context: EnhancedConversationContext, 
                                                user_message: str, agent_response: str) -> None:
        """Update context variables using regex analysis"""
        try:
            variables = context.context_variables
            
            # Extract entities using regex patterns
            entity_patterns = {
                'campaigns': r'\b(?:campaign|campaigns?)\s+(?:named|called)?\s*["\']?([^"\']+)["\']?',
                'prospects': r'\b(?:prospect|contact|person)\s+(?:named|called)?\s*["\']?([^"\']+)["\']?',
                'templates': r'\b(?:template|templates?)\s+(?:named|called)?\s*["\']?([^"\']+)["\']?',
                'lists': r'\b(?:list|lists?)\s+(?:named|called)?\s*["\']?([^"\']+)["\']?',
                'companies': r'\b(?:from|at|company)\s+([A-Z][A-Za-z\s&\.]+)',
                'emails': r'\b([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b',
                'names': r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                'numbers': r'\b(\d+)\b'
            }
            
            message_combined = f"{user_message} {agent_response}".lower()
            
            # Extract entities and store them
            for entity_type, pattern in entity_patterns.items():
                matches = re.findall(pattern, message_combined, re.IGNORECASE)
                if matches:
                    if entity_type not in variables:
                        variables[entity_type] = []
                    
                    # Add new matches, avoiding duplicates
                    for match in matches:
                        if isinstance(match, tuple):
                            match = match[0]  # Take first capture group
                        if match not in variables[entity_type]:
                            variables[entity_type].append(match)
                    
                    # Keep only recent items (last 10)
                    variables[entity_type] = variables[entity_type][-10:]
            
            # Track intent patterns
            intent_patterns = {
                'create_intent': r'\b(?:create|make|add|new)\b',
                'delete_intent': r'\b(?:delete|remove|destroy)\b',
                'show_intent': r'\b(?:show|display|list|view|see)\b',
                'send_intent': r'\b(?:send|launch|start|execute)\b',
                'update_intent': r'\b(?:update|change|modify|edit)\b',
                'help_intent': r'\b(?:help|assist|guide)\b'
            }
            
            # Count intent occurrences
            for intent, pattern in intent_patterns.items():
                if re.search(pattern, user_message.lower()):
                    variables[f'{intent}_count'] = variables.get(f'{intent}_count', 0) + 1
            
            # Track confirmation patterns
            confirmation_patterns = {
                'positive': r'\b(?:yes|yeah|yep|sure|okay|ok|proceed|go ahead|confirm|do it)\b',
                'negative': r'\b(?:no|nope|cancel|stop|abort|don\'t|never mind)\b'
            }
            
            for conf_type, pattern in confirmation_patterns.items():
                if re.search(pattern, user_message.lower()):
                    variables[f'last_{conf_type}_response'] = datetime.utcnow().isoformat()
            
            # Update context variables
            variables['last_updated'] = datetime.utcnow().isoformat()
            variables['total_messages'] = variables.get('total_messages', 0) + 1
            
            context.context_variables = variables
            
        except Exception as e:
            logger.error(f"Error updating context with regex analysis: {e}")
    
    async def _save_context(self, context: EnhancedConversationContext) -> None:
        """Save context to database"""
        try:
            await self.db.connect()
            
            # Convert to dictionary for MongoDB
            context_dict = {
                "session_id": context.session_id,
                "user_id": context.user_id,
                "current_state": context.current_state.value,
                "turns": [turn.dict() for turn in context.turns],
                "max_turns": context.max_turns,
                "pending_action": context.pending_action,
                "extracted_params": context.extracted_params,
                "missing_params": context.missing_params,
                "endpoint_mapping": context.endpoint_mapping.dict() if context.endpoint_mapping else None,
                "context_variables": context.context_variables,
                "user_preferences": context.user_preferences,
                "created_at": context.created_at,
                "updated_at": context.updated_at,
                "last_activity": context.last_activity
            }
            
            # Upsert to database
            await self.db.db.enhanced_conversations.update_one(
                {"session_id": context.session_id},
                {"$set": context_dict},
                upsert=True
            )
            
        except Exception as e:
            logger.error(f"Error saving context to database: {e}")
    
    def _convert_db_to_context(self, context_data: Dict[str, Any]) -> EnhancedConversationContext:
        """Convert database document to context model"""
        try:
            # Convert turns
            turns = []
            for turn_data in context_data.get('turns', []):
                turn = ConversationTurn(**turn_data)
                turns.append(turn)
            
            # Convert endpoint mapping if present
            endpoint_mapping = None
            if context_data.get('endpoint_mapping'):
                from app.models.conversation_models import EndpointMapping
                endpoint_mapping = EndpointMapping(**context_data['endpoint_mapping'])
            
            return EnhancedConversationContext(
                session_id=context_data['session_id'],
                user_id=context_data.get('user_id', 'default'),
                current_state=ConversationState(context_data.get('current_state', 'analyzing')),
                turns=turns,
                max_turns=context_data.get('max_turns', self.default_max_turns),
                pending_action=context_data.get('pending_action'),
                extracted_params=context_data.get('extracted_params', {}),
                missing_params=context_data.get('missing_params', []),
                endpoint_mapping=endpoint_mapping,
                context_variables=context_data.get('context_variables', {}),
                user_preferences=context_data.get('user_preferences', {}),
                created_at=context_data.get('created_at', datetime.utcnow()),
                updated_at=context_data.get('updated_at', datetime.utcnow()),
                last_activity=context_data.get('last_activity', datetime.utcnow())
            )
            
        except Exception as e:
            logger.error(f"Error converting DB data to context: {e}")
            # Return minimal context on error
            return EnhancedConversationContext(
                session_id=context_data.get('session_id', generate_id()),
                user_id=context_data.get('user_id', 'default'),
                current_state=ConversationState.ANALYZING,
                turns=[],
                max_turns=self.default_max_turns,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                last_activity=datetime.utcnow()
            )
    
    async def clear_session(self, session_id: str) -> None:
        """Clear a conversation session"""
        try:
            # Remove from cache
            if session_id in self.active_contexts:
                del self.active_contexts[session_id]
            
            # Remove from database
            await self.db.connect()
            await self.db.db.enhanced_conversations.delete_one({"session_id": session_id})
            
            logger.info(f"Cleared enhanced session {session_id}")
            
        except Exception as e:
            logger.error(f"Error clearing enhanced session: {e}")
    
    async def cleanup_old_sessions(self, days_old: int = 7) -> int:
        """Clean up old conversation sessions"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            await self.db.connect()
            result = await self.db.db.enhanced_conversations.delete_many({
                "last_activity": {"$lt": cutoff_date}
            })
            
            # Clean up in-memory cache
            sessions_to_remove = []
            for session_id, context in self.active_contexts.items():
                if context.last_activity < cutoff_date:
                    sessions_to_remove.append(session_id)
            
            for session_id in sessions_to_remove:
                del self.active_contexts[session_id]
            
            logger.info(f"Cleaned up {result.deleted_count} old enhanced sessions")
            return result.deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up old enhanced sessions: {e}")
            return 0

# Global instance
enhanced_conversation_service = EnhancedConversationService()