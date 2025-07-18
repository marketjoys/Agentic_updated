#!/usr/bin/env python3
"""
Script to fix the intents in the database to enable automatic responses
"""
import asyncio
from app.services.database import db_service

async def fix_intents():
    """Fix the intents by adding auto_respond flags and other necessary fields"""
    try:
        await db_service.connect()
        
        # Get all intents
        intents = await db_service.get_intents()
        print(f"Found {len(intents)} intents to fix")
        
        # Update each intent with proper auto_respond configuration
        for intent in intents:
            intent_id = intent["id"]
            intent_name = intent["name"]
            
            # Determine if this intent should auto-respond
            auto_respond = True  # Enable auto-response for all intents for now
            
            # Enhanced intent configuration
            updated_intent = {
                "auto_respond": auto_respond,
                "primary_template_id": None,  # Will be set later
                "combination_templates": [],
                "response_type": "single",  # or "multiple"
                "priority": 1 if "positive" in intent_name.lower() else 2,
                "is_active": True,
                "updated_at": await db_service.get_current_timestamp()
            }
            
            # Update the intent
            result = await db_service.update_intent(intent_id, updated_intent)
            print(f"✅ Updated intent '{intent_name}' - auto_respond: {auto_respond}")
        
        # Verify updates
        updated_intents = await db_service.get_intents()
        print("\n🔍 Verification:")
        for intent in updated_intents:
            print(f"- {intent['name']}: auto_respond = {intent.get('auto_respond', False)}")
        
        await db_service.disconnect()
        print("\n🎉 Successfully fixed all intents!")
        
    except Exception as e:
        print(f"❌ Error fixing intents: {str(e)}")
        await db_service.disconnect()

if __name__ == "__main__":
    asyncio.run(fix_intents())