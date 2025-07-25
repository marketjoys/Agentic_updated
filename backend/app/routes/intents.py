from fastapi import APIRouter, HTTPException
from datetime import datetime
from app.models import IntentConfig
from app.services.database import db_service
from app.utils.helpers import generate_id

router = APIRouter()

@router.post("/intents")
async def create_intent(intent: IntentConfig):
    """Create a new intent configuration"""
    try:
        # Connect to database
        await db_service.connect()
        
        # Generate ID if not provided
        if not intent.id:
            intent.id = generate_id()
        
        # Add timestamps
        intent_dict = intent.dict()
        intent_dict["created_at"] = datetime.utcnow()
        intent_dict["updated_at"] = datetime.utcnow()
        
        # Create intent in database
        result = await db_service.create_intent(intent_dict)
        
        if result:
            # Clean up response
            intent_dict.pop('_id', None)
            return {
                "id": intent.id,
                "message": "Intent created successfully",
                **intent_dict
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create intent")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating intent: {str(e)}")

@router.get("/intents")
async def get_intents():
    """Get all intent configurations"""
    try:
        # Connect to database
        await db_service.connect()
        
        # Get intents from database
        intents = await db_service.get_intents()
        return intents
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching intents: {str(e)}")

@router.get("/intents/{intent_id}")
async def get_intent(intent_id: str):
    """Get specific intent by ID"""
    try:
        # Connect to database
        await db_service.connect()
        
        # Get intent from database
        intent = await db_service.get_intent_by_id(intent_id)
        if not intent:
            raise HTTPException(status_code=404, detail="Intent not found")
        return intent
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching intent: {str(e)}")

@router.put("/intents/{intent_id}")
async def update_intent(intent_id: str, intent: IntentConfig):
    """Update an intent configuration"""
    try:
        # Connect to database
        await db_service.connect()
        
        # Prepare update data
        intent_dict = intent.dict()
        intent_dict.pop('id', None)  # Remove ID from update data
        intent_dict["updated_at"] = datetime.utcnow()
        
        # Update intent in database
        result = await db_service.update_intent(intent_id, intent_dict)
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Intent not found")
        
        return {
            "id": intent_id,
            "message": "Intent updated successfully",
            **intent_dict
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating intent: {str(e)}")

@router.delete("/intents/{intent_id}")
async def delete_intent(intent_id: str):
    """Delete an intent configuration"""
    try:
        # Connect to database
        await db_service.connect()
        
        # Delete intent from database
        result = await db_service.delete_intent(intent_id)
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Intent not found")
        
        return {
            "id": intent_id,
            "message": "Intent deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting intent: {str(e)}")