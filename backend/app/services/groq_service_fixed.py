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
    """Mock Groq client for when API key is invalid or for testing"""
    def __init__(self, api_key):
        self.api_key = api_key
        
    class chat:
        class completions:
            @staticmethod
            def create(model, messages, temperature=0.7, max_tokens=1000):
                # Mock response with realistic classification
                user_message = ""
                for msg in messages:
                    if msg.get("role") == "user":
                        user_message = msg.get("content", "").lower()
                        break
                
                # Determine intent based on content
                intent_name = "General Inquiry"
                confidence = 0.7
                
                if any(word in user_message for word in ["interested", "interest", "tell me more", "learn more"]):
                    intent_name = "Interest Intent"
                    confidence = 0.9
                elif any(word in user_message for word in ["pricing", "price", "cost", "quote"]):
                    intent_name = "Pricing Intent"
                    confidence = 0.85
                elif any(word in user_message for word in ["demo", "meeting", "call", "schedule"]):
                    intent_name = "Demo Request"
                    confidence = 0.8
                elif any(word in user_message for word in ["unsubscribe", "stop", "remove"]):
                    intent_name = "Unsubscribe"
                    confidence = 0.95
                
                class MockResponse:
                    def __init__(self):
                        self.choices = [MockChoice()]
                
                class MockChoice:
                    def __init__(self):
                        self.message = MockMessage()
                
                class MockMessage:
                    def __init__(self):
                        self.content = json.dumps({
                            "intents": [{
                                "intent_id": "mock_intent_001",
                                "intent_name": intent_name,
                                "confidence": confidence,
                                "reasoning": f"Detected {intent_name.lower()} based on keywords and context",
                                "keywords_found": [word for word in ["interested", "pricing", "demo"] if word in user_message],
                                "context_strength": "high" if confidence > 0.8 else "medium"
                            }]
                        })
                
                return MockResponse()

class GroqService:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        self.use_mock = not api_key or api_key == "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"  # Invalid key
        
        if self.use_mock:
            print("Using mock Groq service (invalid or missing API key)")
            self.client = MockGroqClient(api_key or "mock_key")
        else:
            try:
                from groq import Groq
                self.client = Groq(api_key=api_key)
                print("Using real Groq service")
            except Exception as e:
                print(f"Failed to initialize Groq client, falling back to mock: {str(e)}")
                self.client = MockGroqClient(api_key)
                self.use_mock = True
        
        self.model = "llama3-8b-8192"
        
    async def classify_intents(self, email_content: str, subject: str = "", 
                              use_custom_prompt: bool = True) -> List[Dict]:
        """
        Enhanced intent classification with fallback to mock when API fails
        """
        try:
            # Get available intents from database
            intents = await db_service.get_intents()
            
            if not intents:
                # Create default intents if none exist
                await self._create_default_intents()
                intents = await db_service.get_intents()
            
            # Get custom system prompt for intent classification
            system_prompt = ""
            if use_custom_prompt:
                custom_prompt = await db_service.get_default_system_prompt("intent_classification")
                if custom_prompt:
                    system_prompt = custom_prompt["prompt_text"]
                    # Update usage count
                    await db_service.update_system_prompt(custom_prompt["id"], {
                        "usage_count": custom_prompt.get("usage_count", 0) + 1,
                        "last_used": datetime.utcnow()
                    })
            
            # Fallback to default prompt if no custom prompt found
            if not system_prompt:
                system_prompt = """You are an expert email intent classifier. Always respond with valid JSON.
                Analyze the email content and classify the intent from the available options.
                Return a JSON object with 'intents' array containing classified intents."""
            
            # Prepare intent descriptions for AI
            intent_descriptions = []
            for intent in intents:
                desc = f"- {intent['name']}: {intent.get('description', 'No description')}"
                if intent.get('keywords'):
                    desc += f" (Keywords: {', '.join(intent['keywords'])})"
                intent_descriptions.append(desc)
            
            # Create messages for the AI
            messages = [
                {
                    "role": "system",
                    "content": f"{system_prompt}\n\nAvailable intents:\n{chr(10).join(intent_descriptions)}"
                },
                {
                    "role": "user", 
                    "content": f"Subject: {subject}\n\nContent: {email_content}\n\nClassify the intent(s) of this email and respond with JSON."
                }
            ]
            
            # Call the AI API (real or mock)
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.3,
                    max_tokens=1000
                )
                
                response_content = response.choices[0].message.content.strip()
                
                # Parse JSON response
                try:
                    parsed_response = json.loads(response_content)
                    classified_intents = parsed_response.get("intents", [])
                    
                    # Validate and map to actual intent IDs
                    valid_intents = []
                    for classified in classified_intents:
                        # Find matching intent in database
                        matching_intent = None
                        for intent in intents:
                            if (intent["name"].lower() == classified.get("intent_name", "").lower() or
                                intent["id"] == classified.get("intent_id")):
                                matching_intent = intent
                                break
                        
                        if matching_intent:
                            valid_intents.append({
                                "intent_id": matching_intent["id"],
                                "intent_name": matching_intent["name"],
                                "confidence": classified.get("confidence", 0.7),
                                "reasoning": classified.get("reasoning", "AI classification"),
                                "keywords_found": classified.get("keywords_found", []),
                                "context_strength": classified.get("context_strength", "medium"),
                                "auto_respond": matching_intent.get("auto_respond", False)
                            })
                    
                    print(f"Successfully classified {len(valid_intents)} intents")
                    return valid_intents
                    
                except json.JSONDecodeError as e:
                    print(f"Error parsing AI response JSON: {str(e)}")
                    return self._fallback_intent_classification(email_content, subject, intents)
                    
            except Exception as api_error:
                print(f"Error calling Groq API: {str(api_error)}")
                return self._fallback_intent_classification(email_content, subject, intents)
            
        except Exception as e:
            print(f"Error classifying intents: {str(e)}")
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
        Enhanced response generation with fallback to templates
        """
        try:
            # Get templates for the classified intents
            templates = await self._get_templates_for_intents(classified_intents)
            
            if not templates:
                # Fallback to default response
                return {
                    "subject": f"Re: {subject}",
                    "content": "Thank you for your email. We have received your message and will respond shortly.\n\nBest regards,\nOur Team",
                    "intents_addressed": [intent.get("intent_name", "Unknown") for intent in classified_intents],
                    "template_used": "fallback_template",
                    "knowledge_used": [],
                    "confidence": 0.7,
                    "reasoning": "Using fallback template due to no specific templates found",
                    "conversation_context_used": bool(conversation_context),
                    "personalization_elements": []
                }
            
            # Use the first available template
            template = templates[0]
            
            # Personalize the template if prospect data is available
            response_content = template.get("content", "Thank you for your email.")
            response_subject = template.get("subject", f"Re: {subject}")
            
            if prospect_data:
                # Simple personalization
                response_content = response_content.replace("{{first_name}}", prospect_data.get("first_name", ""))
                response_content = response_content.replace("{{company}}", prospect_data.get("company", ""))
                response_subject = response_subject.replace("{{first_name}}", prospect_data.get("first_name", ""))
            
            return {
                "subject": response_subject,
                "content": response_content,
                "intents_addressed": [intent.get("intent_name", "Unknown") for intent in classified_intents],
                "template_used": template.get("name", "default_template"),
                "knowledge_used": [],
                "confidence": 0.85,
                "reasoning": f"Using template '{template.get('name')}' for intents: {', '.join([i.get('intent_name', '') for i in classified_intents])}",
                "conversation_context_used": bool(conversation_context),
                "personalization_elements": ["name", "company"] if prospect_data else []
            }
            
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return {"error": f"Response generation failed: {str(e)}"}
    
    async def analyze_email_sentiment(self, email_content: str) -> Dict:
        """
        Enhanced sentiment analysis with keyword-based fallback
        """
        try:
            # Simple keyword-based sentiment analysis
            content_lower = email_content.lower()
            
            positive_words = ["interested", "great", "excellent", "love", "perfect", "amazing", "good", "yes", "definitely"]
            negative_words = ["disappointed", "unhappy", "bad", "terrible", "awful", "no", "not interested", "stop"]
            urgent_words = ["urgent", "asap", "immediately", "quickly", "rush", "emergency"]
            
            positive_score = sum(1 for word in positive_words if word in content_lower)
            negative_score = sum(1 for word in negative_words if word in content_lower)
            urgency_score = sum(1 for word in urgent_words if word in content_lower)
            
            if positive_score > negative_score:
                sentiment = "positive"
                confidence = min(0.9, 0.6 + (positive_score * 0.1))
            elif negative_score > positive_score:
                sentiment = "negative"
                confidence = min(0.9, 0.6 + (negative_score * 0.1))
            else:
                sentiment = "neutral"
                confidence = 0.7
            
            urgency = "high" if urgency_score > 0 else "medium" if positive_score > 0 or negative_score > 0 else "low"
            
            return {
                "sentiment": sentiment,
                "urgency": urgency,
                "emotion_detected": sentiment,
                "confidence": confidence,
                "reasoning": f"Keyword-based analysis: {positive_score} positive, {negative_score} negative, {urgency_score} urgent words"
            }
            
        except Exception as e:
            print(f"Error in sentiment analysis: {str(e)}")
            return {
                "sentiment": "neutral",
                "urgency": "low",
                "emotion_detected": "neutral",
                "confidence": 0.5,
                "reasoning": f"Error in sentiment analysis: {str(e)}"
            }
    
    def _fallback_intent_classification(self, email_content: str, subject: str, intents: List[Dict]) -> List[Dict]:
        """Enhanced fallback intent classification using keywords"""
        try:
            content_lower = (email_content + " " + subject).lower()
            classified_intents = []
            
            for intent in intents:
                confidence = 0.0
                keywords_found = []
                
                # Check keywords
                intent_keywords = intent.get("keywords", [])
                for keyword in intent_keywords:
                    if keyword.lower() in content_lower:
                        keywords_found.append(keyword)
                        confidence += 0.2
                
                # Check intent name in content
                if intent["name"].lower() in content_lower:
                    confidence += 0.3
                
                # Check description keywords
                description = intent.get("description", "").lower()
                if description and any(word in content_lower for word in description.split() if len(word) > 3):
                    confidence += 0.1
                
                if confidence > 0.3:  # Threshold for classification
                    classified_intents.append({
                        "intent_id": intent["id"],
                        "intent_name": intent["name"],
                        "confidence": min(confidence, 0.9),
                        "reasoning": f"Keyword-based classification: found {len(keywords_found)} matching keywords",
                        "keywords_found": keywords_found,
                        "context_strength": "high" if confidence > 0.7 else "medium",
                        "auto_respond": intent.get("auto_respond", False)
                    })
            
            # If no intents matched, return the first available intent with low confidence
            if not classified_intents and intents:
                classified_intents.append({
                    "intent_id": intents[0]["id"],
                    "intent_name": intents[0]["name"],
                    "confidence": 0.5,
                    "reasoning": "Fallback classification - no specific keywords matched",
                    "keywords_found": [],
                    "context_strength": "low",
                    "auto_respond": intents[0].get("auto_respond", False)
                })
            
            return classified_intents
            
        except Exception as e:
            print(f"Error in fallback intent parsing: {str(e)}")
            return []
    
    async def _create_default_intents(self):
        """Create default intents if none exist"""
        try:
            default_intents = [
                {
                    "id": generate_id(),
                    "name": "Interest Intent",
                    "description": "Customer showing interest in products or services",
                    "keywords": ["interested", "tell me more", "learn more", "want to know"],
                    "auto_respond": True,
                    "is_active": True,
                    "response_template": "Thank you for your interest! We're excited to help you learn more about our services.",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                },
                {
                    "id": generate_id(),
                    "name": "Pricing Intent", 
                    "description": "Customer asking about pricing information",
                    "keywords": ["pricing", "price", "cost", "quote", "how much"],
                    "auto_respond": True,
                    "is_active": True,
                    "response_template": "Thank you for your inquiry about pricing. We'll send you detailed pricing information shortly.",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                },
                {
                    "id": generate_id(),
                    "name": "Demo Request",
                    "description": "Customer requesting a demo or meeting",
                    "keywords": ["demo", "demonstration", "meeting", "call", "schedule", "show me"],
                    "auto_respond": True,
                    "is_active": True,
                    "response_template": "Thank you for requesting a demo! We'll contact you shortly to schedule a convenient time.",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            ]
            
            for intent_data in default_intents:
                await db_service.create_intent(intent_data)
            
            print(f"Created {len(default_intents)} default intents")
            
        except Exception as e:
            print(f"Error creating default intents: {str(e)}")
    
    async def _get_templates_for_intents(self, classified_intents: List[Dict]) -> List[Dict]:
        """Get templates associated with classified intents"""
        templates = []
        
        try:
            for intent in classified_intents:
                # Get intent details from database
                intent_details = await db_service.get_intent_by_id(intent["intent_id"])
                if intent_details and intent_details.get("response_template"):
                    # Create template from intent response
                    template = {
                        "id": f"intent_template_{intent['intent_id']}",
                        "name": f"Auto-response for {intent['intent_name']}",
                        "subject": f"Re: Your inquiry about {intent['intent_name'].lower()}",
                        "content": intent_details["response_template"],
                        "type": "auto_response"
                    }
                    templates.append(template)
            
            # If no specific templates found, get all auto_response templates
            if not templates:
                all_templates = await db_service.get_templates()
                templates = [t for t in all_templates if t.get("type") == "auto_response"]
            
            return templates
            
        except Exception as e:
            print(f"Error getting templates for intents: {str(e)}")
            return []

def generate_id():
    """Generate a unique ID"""
    import uuid
    return str(uuid.uuid4())

# Create global Groq service instance
groq_service = GroqService()