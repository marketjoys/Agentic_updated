# Conversation Models for Enhanced AI Agent
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from datetime import datetime

class ConversationState(Enum):
    """States of a conversation flow"""
    ANALYZING = "analyzing"           # Analyzing user intent and mapping endpoints
    GATHERING_INFO = "gathering_info" # Asking user for missing information
    CONFIRMING = "confirming"         # Confirming action with user before execution
    EXECUTING = "executing"           # Executing the confirmed action
    COMPLETED = "completed"           # Action completed successfully
    ERROR = "error"                   # Error occurred during process

class EndpointMapping(BaseModel):
    """Maps user intents to backend endpoints"""
    endpoint: str
    method: str
    required_params: List[str]
    optional_params: List[str] = []
    description: str
    examples: List[str] = []

class ConversationTurn(BaseModel):
    """Individual conversation turn"""
    turn_id: str
    timestamp: datetime
    user_message: str
    agent_response: str
    state: ConversationState
    intent: Optional[str] = None
    extracted_params: Dict[str, Any] = {}
    missing_params: List[str] = []
    action_taken: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class EnhancedConversationContext(BaseModel):
    """Enhanced conversation context with state management"""
    session_id: str
    user_id: str = "default"
    current_state: ConversationState = ConversationState.ANALYZING
    turns: List[ConversationTurn] = []
    max_turns: int = 10  # Configurable turn limit
    
    # Current action being processed
    pending_action: Optional[Dict[str, Any]] = None
    extracted_params: Dict[str, Any] = {}
    missing_params: List[str] = []
    endpoint_mapping: Optional[EndpointMapping] = None
    
    # Context variables for continuity
    context_variables: Dict[str, Any] = {}
    user_preferences: Dict[str, Any] = {}
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    last_activity: datetime

class InformationRequest(BaseModel):
    """Request for missing information from user"""
    parameter: str
    question: str
    example: Optional[str] = None
    validation_pattern: Optional[str] = None
    required: bool = True

class ConfirmationRequest(BaseModel):
    """Request for user confirmation before action execution"""
    action_summary: str
    endpoint: str
    method: str
    parameters: Dict[str, Any]
    estimated_impact: str
    confirm_question: str