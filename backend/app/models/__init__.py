# Models package initialization
from .conversation_models import (
    ConversationState,
    ConversationTurn,
    EnhancedConversationContext,
    EndpointMapping,
    InformationRequest,
    ConfirmationRequest
)

# Import from the main models.py file (one level up)
import os
import sys

# Add the parent directory to sys.path to import from models.py
parent_dir = os.path.dirname(os.path.dirname(__file__))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from models import (
        EmailProviderType, FollowUpStatus, EmailProvider, KnowledgeBase, 
        SystemPrompt, FollowUpRule, ProspectList, Prospect, Template, 
        Campaign, IntentConfig, EmailMessage, ThreadContext, ResponseVerification
    )
except ImportError as e:
    print(f"Warning: Could not import from models.py: {e}")
    # Create minimal enum as fallback
    from enum import Enum
    
    class EmailProviderType(str, Enum):
        GMAIL = "gmail"
        OUTLOOK = "outlook"
        YAHOO = "yahoo"
        CUSTOM_SMTP = "custom_smtp"
    
    class FollowUpStatus(str, Enum):
        ACTIVE = "active"
        PAUSED = "paused"
        COMPLETED = "completed"
        STOPPED = "stopped"
    
    # Minimal fallback classes
    KnowledgeBase = None
    SystemPrompt = None
    FollowUpRule = None
    ProspectList = None
    Prospect = None
    Template = None
    Campaign = None
    IntentConfig = None
    EmailMessage = None
    ThreadContext = None
    ResponseVerification = None
    EmailProvider = None

__all__ = [
    "ConversationState",
    "ConversationTurn", 
    "EnhancedConversationContext",
    "EndpointMapping",
    "InformationRequest",
    "ConfirmationRequest",
    "EmailProviderType",
    "FollowUpStatus",
    "EmailProvider",
    "KnowledgeBase",
    "SystemPrompt",
    "FollowUpRule",
    "ProspectList",
    "Prospect",
    "Template",
    "Campaign",
    "IntentConfig",
    "EmailMessage",
    "ThreadContext",
    "ResponseVerification"
]