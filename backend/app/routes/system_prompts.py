from fastapi import APIRouter, HTTPException
from app.models import SystemPrompt
from app.services.database import db_service
from app.utils.helpers import generate_id
from typing import Dict, Optional
from datetime import datetime

router = APIRouter()

@router.post("/system-prompts")
async def create_system_prompt(prompt: SystemPrompt):
    """Create a new system prompt"""
    prompt.id = generate_id()
    prompt_dict = prompt.dict()
    
    result = await db_service.create_system_prompt(prompt_dict)
    if not result:
        raise HTTPException(status_code=500, detail="Failed to create system prompt")
    
    return {"id": prompt.id, "message": "System prompt created successfully"}

@router.get("/system-prompts")
async def get_system_prompts():
    """Get all system prompts"""
    prompts = await db_service.get_system_prompts()
    return prompts

@router.get("/system-prompts/{prompt_id}")
async def get_system_prompt(prompt_id: str):
    """Get a specific system prompt by ID"""
    prompt = await db_service.get_system_prompt_by_id(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="System prompt not found")
    return prompt

@router.put("/system-prompts/{prompt_id}")
async def update_system_prompt(prompt_id: str, prompt_data: Dict):
    """Update a system prompt"""
    prompt_data["updated_at"] = datetime.utcnow()
    result = await db_service.update_system_prompt(prompt_id, prompt_data)
    
    if not result:
        raise HTTPException(status_code=404, detail="System prompt not found")
    
    return {"message": "System prompt updated successfully"}

@router.delete("/system-prompts/{prompt_id}")
async def delete_system_prompt(prompt_id: str):
    """Delete a system prompt"""
    result = await db_service.delete_system_prompt(prompt_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="System prompt not found")
    
    return {"message": "System prompt deleted successfully"}

@router.get("/system-prompts/default/{prompt_type}")
async def get_default_system_prompt(prompt_type: str = "general"):
    """Get default system prompt by type"""
    prompt = await db_service.get_default_system_prompt(prompt_type)
    if not prompt:
        raise HTTPException(status_code=404, detail=f"No default system prompt found for type: {prompt_type}")
    return prompt

@router.post("/system-prompts/{prompt_id}/set-default")
async def set_default_system_prompt(prompt_id: str):
    """Set a system prompt as default for its type"""
    # Get the prompt to check its type
    prompt = await db_service.get_system_prompt_by_id(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="System prompt not found")
    
    # Remove default flag from all prompts of the same type
    all_prompts = await db_service.get_system_prompts()
    for p in all_prompts:
        if p["prompt_type"] == prompt["prompt_type"] and p["is_default"]:
            await db_service.update_system_prompt(p["id"], {"is_default": False})
    
    # Set this prompt as default
    result = await db_service.update_system_prompt(prompt_id, {"is_default": True})
    
    if not result:
        raise HTTPException(status_code=500, detail="Failed to set default prompt")
    
    return {"message": "Default system prompt set successfully"}

@router.get("/system-prompts/types/available")
async def get_prompt_types():
    """Get available system prompt types"""
    prompt_types = [
        {
            "type": "general",
            "name": "General AI Behavior",
            "description": "Overall AI assistant behavior and personality"
        },
        {
            "type": "intent_classification",
            "name": "Intent Classification",
            "description": "Prompt for classifying email intents"
        },
        {
            "type": "response_generation",
            "name": "Response Generation",
            "description": "Prompt for generating email responses"
        },
        {
            "type": "verification",
            "name": "Response Verification",
            "description": "Prompt for verifying response quality"
        },
        {
            "type": "personalization",
            "name": "Personalization",
            "description": "Prompt for personalizing responses"
        }
    ]
    return {"prompt_types": prompt_types}

@router.post("/system-prompts/{prompt_id}/test")
async def test_system_prompt(prompt_id: str, test_data: Dict):
    """Test a system prompt with sample input"""
    prompt = await db_service.get_system_prompt_by_id(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="System prompt not found")
    
    test_input = test_data.get("input", "")
    if not test_input:
        raise HTTPException(status_code=400, detail="Test input is required")
    
    try:
        # Import groq service for testing
        from app.services.groq_service_mock import groq_service
        
        # Test the prompt
        response = await groq_service.client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": prompt["prompt_text"]},
                {"role": "user", "content": test_input}
            ],
            temperature=prompt.get("temperature", 0.7),
            max_tokens=prompt.get("max_tokens", 1000)
        )
        
        # Update usage count
        await db_service.update_system_prompt(prompt_id, {
            "usage_count": prompt.get("usage_count", 0) + 1,
            "last_used": datetime.utcnow()
        })
        
        return {
            "prompt_id": prompt_id,
            "test_input": test_input,
            "ai_response": response.choices[0].message.content,
            "prompt_settings": {
                "temperature": prompt.get("temperature", 0.7),
                "max_tokens": prompt.get("max_tokens", 1000)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error testing prompt: {str(e)}")

@router.post("/system-prompts/bulk-create-defaults")
async def create_default_prompts():
    """Create default system prompts for all types"""
    default_prompts = [
        {
            "name": "Default General Behavior",
            "description": "Default AI assistant behavior",
            "prompt_text": "You are a professional and helpful AI email assistant. Always be courteous, clear, and concise in your responses. Focus on being helpful while maintaining a professional tone.",
            "prompt_type": "general",
            "is_default": True,
            "is_active": True
        },
        {
            "name": "Default Intent Classification",
            "description": "Default intent classification prompt",
            "prompt_text": "Analyze the following email and classify its intent. Look for indicators of interest, questions, objections, requests for information, scheduling requests, or other business-related intents. Respond with classified intents and confidence scores.",
            "prompt_type": "intent_classification",
            "is_default": True,
            "is_active": True
        },
        {
            "name": "Default Response Generation",
            "description": "Default response generation prompt",
            "prompt_text": "Generate a professional and personalized email response that addresses the sender's intent. Use the provided context and prospect information to create a helpful and engaging reply.",
            "prompt_type": "response_generation",
            "is_default": True,
            "is_active": True
        },
        {
            "name": "Default Verification",
            "description": "Default response verification prompt",
            "prompt_text": "Verify the quality of the generated email response. Check for professionalism, relevance to the original email, proper personalization, and overall effectiveness.",
            "prompt_type": "verification",
            "is_default": True,
            "is_active": True
        }
    ]
    
    created_prompts = []
    for prompt_data in default_prompts:
        prompt_data["id"] = generate_id()
        prompt_data["created_at"] = datetime.utcnow()
        prompt_data["usage_count"] = 0
        
        result = await db_service.create_system_prompt(prompt_data)
        if result:
            created_prompts.append(prompt_data["id"])
    
    return {
        "message": f"Created {len(created_prompts)} default system prompts",
        "created_prompts": created_prompts
    }