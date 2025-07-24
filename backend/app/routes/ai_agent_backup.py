# Enhanced AI Agent Conversational Interface with Confirmation Flow
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List, Dict, Optional, Any, Union
import logging
from datetime import datetime
import json
import asyncio
from bson import ObjectId
from app.services.enhanced_ai_agent_service import enhanced_ai_agent_service
from app.services.enhanced_conversation_service import enhanced_conversation_service
from app.services.ai_agent_service import ai_agent_service  # Keep for backward compatibility
from app.services.conversation_context_service import conversation_context_service  # Keep for backward compatibility
from app.utils.helpers import generate_id

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Helper function to convert ObjectId to string
def convert_objectid_to_str(data):
    """Convert MongoDB ObjectIds to strings for JSON serialization"""
    if isinstance(data, dict):
        return {key: convert_objectid_to_str(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_objectid_to_str(item) for item in data]
    elif isinstance(data, ObjectId):
        return str(data)
    else:
        return data

router = APIRouter()

# Request/Response Models
class ConversationRequest(BaseModel):
    message: str
    user_id: Optional[str] = "default"
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = {}
    use_enhanced_flow: Optional[bool] = True  # Use enhanced confirmation flow by default

class ConversationResponse(BaseModel):
    response: str
    action_taken: Optional[str] = None
    data: Optional[Union[Dict[str, Any], List[Any]]] = None
    suggestions: Optional[List[str]] = []
    session_id: str
    timestamp: str
    conversation_state: Optional[str] = None  # Current conversation state
    pending_action: Optional[Dict[str, Any]] = None  # Action waiting for confirmation
    context_info: Optional[Dict[str, Any]] = None  # Additional context information

class SetTurnLimitRequest(BaseModel):
    session_id: str
    max_turns: int  # Number of turns to keep in context (10-100)

class ConversationResponse(BaseModel):
    response: str
    action_taken: Optional[str] = None
    data: Optional[Union[Dict[str, Any], List[Any]]] = None
    suggestions: Optional[List[str]] = []
    session_id: str
    timestamp: str

class VoiceRequest(BaseModel):
    audio_data: str  # Base64 encoded audio
    user_id: Optional[str] = "default"
    session_id: Optional[str] = None

# Active WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

manager = ConnectionManager()

# Main Conversational Endpoints
@router.post("/ai-agent/chat", response_model=ConversationResponse)
async def chat_with_agent(request: ConversationRequest):
    """
    Main conversational endpoint - handles text-based conversation with enhanced confirmation flow
    """
    try:
        logger.info(f"AI Agent chat request: {request.message} (Enhanced: {request.use_enhanced_flow})")
        
        # Generate session ID if not provided
        if not request.session_id:
            request.session_id = generate_id()
        
        # Choose service based on request
        if request.use_enhanced_flow:
            # Use enhanced service with confirmation flow
            result = await enhanced_ai_agent_service.process_conversation(
                message=request.message,
                user_id=request.user_id,
                session_id=request.session_id,
                context=request.context or {}
            )
            
            # Get additional context info
            conv_context = await enhanced_conversation_service.get_conversation_context(
                request.session_id, request.user_id
            )
            
            context_info = {
                "turn_count": len(conv_context.turns),
                "max_turns": conv_context.max_turns,
                "state": conv_context.current_state.value,
                "extracted_params": conv_context.extracted_params,
                "missing_params": conv_context.missing_params
            }
            
            return ConversationResponse(
                response=result['response'],
                action_taken=result.get('action_taken'),
                data=convert_objectid_to_str(result.get('data')),
                suggestions=result.get('suggestions', []),
                session_id=request.session_id,
                timestamp=datetime.utcnow().isoformat(),
                conversation_state=result.get('conversation_state'),
                pending_action=conv_context.pending_action,
                context_info=context_info
            )
        
        else:
            # Use original service for backward compatibility
            result = await ai_agent_service.process_conversation(
                message=request.message,
                user_id=request.user_id,
                session_id=request.session_id,
                context=request.context or {}
            )
            
            # Save conversation to old context system
            await conversation_context_service.save_conversation_turn(
                session_id=request.session_id,
                user_message=request.message,
                agent_response=result['response'],
                action_taken=result.get('action_taken'),
                data=convert_objectid_to_str(result.get('data'))
            )
            
            return ConversationResponse(
                response=result['response'],
                action_taken=result.get('action_taken'),
                data=convert_objectid_to_str(result.get('data')),
                suggestions=result.get('suggestions', []),
                session_id=request.session_id,
                timestamp=datetime.utcnow().isoformat(),
                conversation_state="legacy",
                pending_action=None,
                context_info={"mode": "legacy"}
            )
        
    except Exception as e:
        logger.error(f"Error in AI agent chat: {e}")
        raise HTTPException(status_code=500, detail=f"AI agent error: {str(e)}")

@router.post("/ai-agent/voice")
async def voice_interaction(request: VoiceRequest):
    """
    Voice-based interaction endpoint
    """
    try:
        logger.info("AI Agent voice request received")
        
        # Generate session ID if not provided
        if not request.session_id:
            request.session_id = generate_id()
        
        # Process voice input (for now, we'll simulate voice-to-text)
        # In production, you'd integrate with speech-to-text service
        text_message = "I want to see all my campaigns"  # Placeholder
        
        # Process the conversation
        result = await ai_agent_service.process_conversation(
            message=text_message,
            user_id=request.user_id,
            session_id=request.session_id,
            context={}
        )
        
        return {
            "transcribed_text": text_message,
            "response": result['response'],
            "action_taken": result.get('action_taken'),
            "data": result.get('data'),
            "session_id": request.session_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in AI agent voice: {e}")
        raise HTTPException(status_code=500, detail=f"Voice processing error: {str(e)}")

@router.websocket("/ai-agent/ws/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str, enhanced: bool = True):
    """
    WebSocket endpoint for real-time conversation with enhanced flow support
    """
    await manager.connect(websocket)
    logger.info(f"WebSocket connection established for session: {session_id} (Enhanced: {enhanced})")
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            user_message = message_data.get('message', '')
            user_id = message_data.get('user_id', 'default')
            use_enhanced = message_data.get('use_enhanced_flow', enhanced)
            
            logger.info(f"WebSocket message: {user_message} (Enhanced: {use_enhanced})")
            
            if use_enhanced:
                # Use enhanced service
                result = await enhanced_ai_agent_service.process_conversation(
                    message=user_message,
                    user_id=user_id,
                    session_id=session_id,
                    context=message_data.get('context', {})
                )
                
                # Get additional context
                conv_context = await enhanced_conversation_service.get_conversation_context(session_id, user_id)
                
                # Send response back to client
                response = {
                    "response": result['response'],
                    "action_taken": result.get('action_taken'),
                    "data": convert_objectid_to_str(result.get('data')),
                    "suggestions": result.get('suggestions', []),
                    "conversation_state": result.get('conversation_state'),
                    "pending_action": conv_context.pending_action,
                    "context_info": {
                        "turn_count": len(conv_context.turns),
                        "max_turns": conv_context.max_turns,
                        "state": conv_context.current_state.value,
                        "extracted_params": conv_context.extracted_params,
                        "missing_params": conv_context.missing_params
                    },
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            else:
                # Use original service
                result = await ai_agent_service.process_conversation(
                    message=user_message,
                    user_id=user_id,
                    session_id=session_id,
                    context=message_data.get('context', {})
                )
                
                # Save conversation
                await conversation_context_service.save_conversation_turn(
                    session_id=session_id,
                    user_message=user_message,
                    agent_response=result['response'],
                    action_taken=result.get('action_taken'),
                    data=result.get('data')
                )
                
                # Send response back to client
                response = {
                    "response": result['response'],
                    "action_taken": result.get('action_taken'),
                    "data": convert_objectid_to_str(result.get('data')),
                    "suggestions": result.get('suggestions', []),
                    "conversation_state": "legacy",
                    "pending_action": None,
                    "context_info": {"mode": "legacy"},
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            await manager.send_personal_message(json.dumps(response), websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f"WebSocket connection closed for session: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close(code=1000)

# Context Management Endpoints
@router.get("/ai-agent/sessions/{session_id}/context")
async def get_conversation_context(session_id: str):
    """
    Get conversation context for a session
    """
    try:
        context = await conversation_context_service.get_session_context(session_id)
        return {
            "session_id": session_id,
            "context": context,
            "message_count": len(context.get('messages', [])),
            "created_at": context.get('created_at'),
            "updated_at": context.get('updated_at')
        }
        
    except Exception as e:
        logger.error(f"Error getting conversation context: {e}")
        raise HTTPException(status_code=500, detail=f"Context retrieval error: {str(e)}")

@router.delete("/ai-agent/sessions/{session_id}")
async def clear_conversation_session(session_id: str):
    """
    Clear conversation session and context
    """
    try:
        await conversation_context_service.clear_session(session_id)
        return {
            "message": f"Session {session_id} cleared successfully",
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error clearing session: {e}")
        raise HTTPException(status_code=500, detail=f"Session clear error: {str(e)}")

@router.get("/ai-agent/sessions")
async def get_active_sessions(user_id: str = "default"):
    """
    Get all active conversation sessions for a user
    """
    try:
        sessions = await conversation_context_service.get_user_sessions(user_id)
        return {
            "user_id": user_id,
            "sessions": sessions,
            "session_count": len(sessions),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting sessions: {e}")
        raise HTTPException(status_code=500, detail=f"Sessions retrieval error: {str(e)}")

# Agent Capabilities Endpoints
@router.get("/ai-agent/capabilities")
async def get_agent_capabilities():
    """
    Get AI agent capabilities and available actions
    """
    try:
        capabilities = await ai_agent_service.get_agent_capabilities()
        return {
            "capabilities": capabilities,
            "supported_actions": list(capabilities.keys()),
            "examples": [
                "Show me all my campaigns",
                "Create a new prospect named John Doe from TechCorp",
                "Send the Summer Sale campaign to Technology Companies list",
                "What are my analytics for this month?",
                "Upload prospects from CSV data",
                "Create a new email template for welcome messages",
                "Add prospects to my VIP list",
                "Start email monitoring",
                "Show me recent email activity"
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting capabilities: {e}")
        raise HTTPException(status_code=500, detail=f"Capabilities error: {str(e)}")

@router.post("/ai-agent/set-turn-limit")
async def set_conversation_turn_limit(request: SetTurnLimitRequest):
    """
    Set the maximum number of conversation turns to keep in context
    """
    try:
        if request.max_turns < 1 or request.max_turns > 1000:
            raise HTTPException(status_code=400, detail="Turn limit must be between 1 and 1000")
        
        await enhanced_conversation_service.set_turn_limit(request.session_id, request.max_turns)
        
        return {
            "message": f"Turn limit set to {request.max_turns} for session {request.session_id}",
            "session_id": request.session_id,
            "max_turns": request.max_turns,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error setting turn limit: {e}")
        raise HTTPException(status_code=500, detail=f"Turn limit error: {str(e)}")

@router.get("/ai-agent/enhanced-capabilities")
async def get_enhanced_agent_capabilities():
    """
    Get enhanced AI agent capabilities and available actions
    """
    try:
        capabilities = await enhanced_ai_agent_service.get_agent_capabilities()
        
        return {
            "capabilities": capabilities,
            "conversation_flow": {
                "description": "Multi-turn conversation with explicit confirmation",
                "steps": [
                    "1. User inputs query/task",
                    "2. Agent checks which backend endpoint to use",
                    "3. Agent checks required payloads for API call",
                    "4. If missing info, ask user for remaining info",
                    "5. Confirm with user before proceeding", 
                    "6. Execute the task",
                    "7. Handle changes/confirmations"
                ],
                "states": ["analyzing", "gathering_info", "confirming", "executing", "completed", "error"]
            },
            "context_features": [
                "Configurable turn limits (10-100 turns)",
                "Regex-based context extraction",
                "State persistence across sessions",
                "Parameter validation and information gathering",
                "Explicit user confirmation before actions"
            ],
            "examples": [
                "Show me all my campaigns",
                "Create a new campaign named Summer Sale",
                "Add John Smith from TechCorp to my database",
                "Send Test Campaign to VIP list",
                "What are my analytics for this month?",
                "Upload prospects from CSV data"
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting enhanced capabilities: {e}")
        raise HTTPException(status_code=500, detail=f"Enhanced capabilities error: {str(e)}")

@router.get("/ai-agent/conversation-history/{session_id}")
async def get_conversation_history(session_id: str, limit: Optional[int] = None):
    """
    Get conversation history for a session with optional limit
    """
    try:
        history = await enhanced_conversation_service.get_conversation_history(session_id, limit)
        
        # Convert to serializable format
        history_data = []
        for turn in history:
            history_data.append({
                "turn_id": turn.turn_id,
                "timestamp": turn.timestamp.isoformat(),
                "user_message": turn.user_message,
                "agent_response": turn.agent_response,
                "state": turn.state.value,
                "intent": turn.intent,
                "extracted_params": turn.extracted_params,
                "missing_params": turn.missing_params,
                "action_taken": turn.action_taken,
                "data": convert_objectid_to_str(turn.data)
            })
        
        return {
            "session_id": session_id,
            "history": history_data,
            "turn_count": len(history_data),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        raise HTTPException(status_code=500, detail=f"History retrieval error: {str(e)}")

@router.get("/ai-agent/conversation-context/{session_id}")
async def get_enhanced_conversation_context(session_id: str):
    """
    Get enhanced conversation context with state and parameters
    """
    try:
        context = await enhanced_conversation_service.get_conversation_context(session_id)
        
        return {
            "session_id": context.session_id,
            "user_id": context.user_id,
            "current_state": context.current_state.value,
            "turn_count": len(context.turns),
            "max_turns": context.max_turns,
            "pending_action": context.pending_action,
            "extracted_params": context.extracted_params,
            "missing_params": context.missing_params,
            "context_variables": context.context_variables,
            "user_preferences": context.user_preferences,
            "created_at": context.created_at.isoformat(),
            "updated_at": context.updated_at.isoformat(),
            "last_activity": context.last_activity.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting enhanced conversation context: {e}")
        raise HTTPException(status_code=500, detail=f"Enhanced context retrieval error: {str(e)}")

@router.post("/ai-agent/test")
async def test_agent_functionality(request: Dict[str, Any]):
    """
    Test agent functionality with sample inputs (supports both legacy and enhanced modes)
    """
    try:
        test_message = request.get('message', 'Show me all campaigns')
        use_enhanced = request.get('use_enhanced_flow', True)
        session_id = request.get('session_id', 'test_session')
        user_id = request.get('user_id', 'test_user')
        
        if use_enhanced:
            result = await enhanced_ai_agent_service.process_conversation(
                message=test_message,
                user_id=user_id,
                session_id=session_id,
                context={}
            )
            
            # Get context info
            conv_context = await enhanced_conversation_service.get_conversation_context(session_id, user_id)
            
            return {
                "test_message": test_message,
                "agent_response": result['response'],
                "action_taken": result.get('action_taken'),
                "data": convert_objectid_to_str(result.get('data')),
                "suggestions": result.get('suggestions', []),
                "conversation_state": result.get('conversation_state'),
                "context_info": {
                    "turn_count": len(conv_context.turns),
                    "max_turns": conv_context.max_turns,
                    "state": conv_context.current_state.value
                },
                "mode": "enhanced",
                "status": "success",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        else:
            result = await ai_agent_service.process_conversation(
                message=test_message,
                user_id=user_id,
                session_id=session_id,
                context={}
            )
            
            return {
                "test_message": test_message,
                "agent_response": result['response'],
                "action_taken": result.get('action_taken'),
                "data": convert_objectid_to_str(result.get('data')),
                "suggestions": result.get('suggestions', []),
                "mode": "legacy",
                "status": "success",
                "timestamp": datetime.utcnow().isoformat()
            }
        
    except Exception as e:
        logger.error(f"Error in agent test: {e}")
        raise HTTPException(status_code=500, detail=f"Agent test error: {str(e)}")

# Analytics for AI Agent Usage
@router.get("/ai-agent/analytics")
async def get_agent_analytics():
    """
    Get AI agent usage analytics (supports both legacy and enhanced systems)
    """
    try:
        # Get legacy analytics
        legacy_analytics = await conversation_context_service.get_usage_analytics()
        
        # Try to get enhanced analytics
        try:
            enhanced_sessions = []  # Would implement if needed
            enhanced_analytics = {
                "period": "last_30_days",
                "enhanced_sessions": len(enhanced_sessions),
                "confirmation_flow_usage": "available",
                "avg_confirmation_rate": 0.85,  # Mock data
                "state_distribution": {
                    "analyzing": 0.4,
                    "gathering_info": 0.2,
                    "confirming": 0.3,
                    "executing": 0.1
                }
            }
        except Exception:
            enhanced_analytics = {"error": "Enhanced analytics not available"}
        
        return {
            "legacy_analytics": legacy_analytics,
            "enhanced_analytics": enhanced_analytics,
            "combined_insights": {
                "total_conversations": legacy_analytics.get("total_sessions", 0),
                "enhanced_flow_available": True,
                "confirmation_based_actions": True
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting agent analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Analytics error: {str(e)}")

# Update the original capabilities endpoint to include enhanced features
@router.get("/ai-agent/capabilities")
async def get_agent_capabilities():
    """
    Get AI agent capabilities (includes both legacy and enhanced features)
    """
    try:
        # Get legacy capabilities
        legacy_capabilities = await ai_agent_service.get_agent_capabilities()
        
        # Get enhanced capabilities
        enhanced_capabilities = await enhanced_ai_agent_service.get_agent_capabilities()
        
        return {
            "legacy_capabilities": legacy_capabilities,
            "enhanced_capabilities": enhanced_capabilities,
            "conversation_modes": {
                "legacy": {
                    "description": "Direct execution mode (original behavior)",
                    "features": ["Immediate action execution", "Basic context retention"]
                },
                "enhanced": {
                    "description": "Confirmation-based flow with multi-turn conversations",
                    "features": [
                        "Parameter validation and information gathering",
                        "Explicit user confirmation before actions",
                        "Configurable conversation context (10-100 turns)",
                        "Regex-based context analysis",
                        "State-based conversation management"
                    ]
                }
            },
            "supported_actions": list(enhanced_capabilities.keys()) if isinstance(enhanced_capabilities, dict) else [],
            "examples": [
                "Show me all my campaigns",
                "Create a new prospect named John Doe from TechCorp",
                "Send the Summer Sale campaign to Technology Companies list",
                "What are my analytics for this month?",
                "Upload prospects from CSV data",
                "Create a new email template for welcome messages",
                "Add prospects to my VIP list",
                "Start email monitoring",
                "Show me recent email activity"
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting capabilities: {e}")
        raise HTTPException(status_code=500, detail=f"Capabilities error: {str(e)}")

async def test_agent_functionality(request: Dict[str, Any]):
    """
    Test agent functionality with sample inputs
    """
    try:
        test_message = request.get('message', 'Show me all campaigns')
        
        result = await ai_agent_service.process_conversation(
            message=test_message,
            user_id="test_user",
            session_id="test_session",
            context={}
        )
        
        return {
            "test_message": test_message,
            "agent_response": result['response'],
            "action_taken": result.get('action_taken'),
            "data": result.get('data'),
            "suggestions": result.get('suggestions', []),
            "status": "success",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in agent test: {e}")
        raise HTTPException(status_code=500, detail=f"Agent test error: {str(e)}")

# Analytics for AI Agent Usage
@router.get("/ai-agent/analytics")
async def get_agent_analytics():
    """
    Get AI agent usage analytics
    """
    try:
        analytics = await conversation_context_service.get_usage_analytics()
        return {
            "analytics": analytics,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting agent analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Analytics error: {str(e)}")

# Help and Guidance
@router.get("/ai-agent/help")
async def get_agent_help():
    """
    Get help information for using the AI agent
    """
    return {
        "help": {
            "overview": "AI Agent allows you to control the entire application through natural language conversation.",
            "supported_operations": [
                "Campaign Management: 'Show campaigns', 'Create campaign', 'Send campaign'",
                "Prospect Management: 'Add prospect', 'Show prospects', 'Upload CSV'",
                "Template Management: 'Create template', 'Show templates', 'Update template'",
                "List Management: 'Create list', 'Add prospects to list', 'Show lists'",
                "Analytics: 'Show analytics', 'Campaign performance', 'Dashboard metrics'",
                "Email Processing: 'Start monitoring', 'Stop monitoring', 'Process status'"
            ],
            "voice_commands": "You can use voice commands by sending audio to the /voice endpoint",
            "websocket": "Use WebSocket connection for real-time conversation",
            "examples": [
                "Natural: 'I want to create a new campaign for summer promotion'",
                "Specific: 'Create campaign named Summer Sale using Welcome template for Technology list'",
                "Question: 'How many prospects do I have in my database?'",
                "Action: 'Send the Q4 Campaign to all VIP customers'"
            ]
        },
        "endpoints": {
            "chat": "POST /ai-agent/chat - Text-based conversation",
            "voice": "POST /ai-agent/voice - Voice-based interaction",
            "websocket": "WS /ai-agent/ws/{session_id} - Real-time chat",
            "context": "GET /ai-agent/sessions/{session_id}/context - Get conversation context",
            "capabilities": "GET /ai-agent/capabilities - Get agent capabilities"
        },
        "timestamp": datetime.utcnow().isoformat()
    }