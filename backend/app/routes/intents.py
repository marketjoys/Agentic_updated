from fastapi import APIRouter
from app.models import IntentConfig
from app.services.database import db_service
from app.utils.helpers import generate_id

router = APIRouter()

@router.post("/intents")
async def create_intent(intent: IntentConfig):
    """Create a new intent configuration"""
    intent.id = generate_id()
    intent_dict = intent.dict()
    result = await db_service.create_intent(intent_dict)
    intent_dict.pop('_id', None)
    return intent_dict

@router.get("/intents")
async def get_intents():
    """Get all intent configurations"""
    intents = await db_service.get_intents()
    return intents