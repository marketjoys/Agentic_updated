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
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from ..models import EmailProviderType, FollowUpStatus
except ImportError:
    # Fallback import
    import importlib.util
    spec = importlib.util.spec_from_file_location("models", os.path.join(os.path.dirname(os.path.dirname(__file__)), "models.py"))
    models_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(models_module)
    EmailProviderType = models_module.EmailProviderType
    FollowUpStatus = models_module.FollowUpStatus

__all__ = [
    "ConversationState",
    "ConversationTurn", 
    "EnhancedConversationContext",
    "EndpointMapping",
    "InformationRequest",
    "ConfirmationRequest",
    "EmailProviderType",
    "FollowUpStatus"
]