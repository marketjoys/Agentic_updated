import os
from typing import List, Dict, Optional, Tuple
import json
import asyncio
from datetime import datetime
from app.services.database import db_service
from app.services.knowledge_base_service import knowledge_base_service
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MockGroqClient:
    def __init__(self, api_key):
        self.api_key = api_key
        
    class chat:
        class completions:
            @staticmethod
            def create(model, messages, temperature=0.7, max_tokens=1000):
                # Mock response
                class MockResponse:
                    def __init__(self):
                        self.choices = [
                            MockChoice()
                        ]
                
                class MockChoice:
                    def __init__(self):
                        self.message = MockMessage()
                
                class MockMessage:
                    def __init__(self):
                        self.content = '{"intents": [{"intent_id": "test_intent", "intent_name": "Test Intent", "confidence": 0.8, "reasoning": "Mock response for testing"}]}'
                
                return MockResponse()

class GroqService:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY", "mock_key")
        self.client = MockGroqClient(api_key)
        self.model = "llama3-8b-8192"
        
    async def classify_intents(self, email_content: str, subject: str = "", 
                              use_custom_prompt: bool = True) -> List[Dict]:
        """
        Mock intent classification for testing
        """
        try:
            # Get available intents from database
            intents = await db_service.get_intents()
            
            if not intents:
                return []
            
            # Return mock classification
            return [
                {
                    "intent_id": intents[0]["id"] if intents else "mock_intent",
                    "intent_name": intents[0]["name"] if intents else "Mock Intent",
                    "confidence": 0.8,
                    "reasoning": "Mock classification for testing purposes",
                    "keywords_found": ["test", "mock"],
                    "context_strength": "high"
                }
            ]
            
        except Exception as e:
            print(f"Error in mock intent classification: {str(e)}")
            return []
    
    async def generate_response(self, 
                               email_content: str, 
                               subject: str, 
                               classified_intents: List[Dict], 
                               conversation_context: List[Dict] = None,
                               prospect_data: Dict = None,
                               use_knowledge_base: bool = True,
                               use_custom_prompt: bool = True) -> Dict:
        """
        Mock response generation for testing
        """
        try:
            # Mock response
            return {
                "subject": f"Re: {subject}",
                "content": f"Thank you for your email. This is a mock response generated for testing purposes.\n\nBest regards,\nAI Email Responder",
                "intents_addressed": [intent.get("intent_name", "Unknown") for intent in classified_intents],
                "template_used": "mock_template",
                "knowledge_used": [],
                "confidence": 0.85,
                "reasoning": "Mock response generation for testing",
                "conversation_context_used": bool(conversation_context),
                "personalization_elements": ["name", "company"] if prospect_data else []
            }
            
        except Exception as e:
            print(f"Error in mock response generation: {str(e)}")
            return {"error": f"Mock response generation failed: {str(e)}"}
    
    def _make_json_safe(self, data):
        """Convert data to JSON-safe format"""
        if isinstance(data, list):
            return [self._make_json_safe(item) for item in data]
        elif isinstance(data, dict):
            safe_data = {}
            for key, value in data.items():
                if hasattr(value, 'isoformat'):  # datetime object
                    safe_data[key] = value.isoformat()
                else:
                    safe_data[key] = value
            return safe_data
        else:
            return data
    
    async def _get_templates_for_intents(self, classified_intents: List[Dict]) -> List[Dict]:
        """Get templates associated with classified intents"""
        templates = []
        
        for intent in classified_intents:
            # Get intent details from database
            intent_details = await db_service.get_intent_by_id(intent["intent_id"])
            if intent_details:
                # Get primary template
                if intent_details.get("primary_template_id"):
                    template = await db_service.get_template_by_id(intent_details["primary_template_id"])
                    if template:
                        templates.append(template)
        
        # If no specific templates found, get all auto_response templates
        if not templates:
            all_templates = await db_service.get_templates()
            templates = [t for t in all_templates if t.get("type") == "auto_response"]
        
        return templates
    
    def _fallback_intent_parsing(self, response_content: str, intents: List[Dict], email_content: str) -> Dict:
        """Fallback intent parsing when JSON parsing fails"""
        try:
            result = {"intents": []}
            
            # Return first intent as fallback
            if intents:
                result["intents"].append({
                    "intent_id": intents[0]["id"],
                    "intent_name": intents[0]["name"],
                    "confidence": 0.7,
                    "reasoning": "Fallback parsing for testing"
                })
            
            return result
            
        except Exception as e:
            print(f"Error in fallback parsing: {str(e)}")
            return {"intents": []}

# Create global Groq service instance
groq_service = GroqService()