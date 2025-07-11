import os
from groq import Groq
from typing import List, Dict, Optional, Tuple
import json
import asyncio
from datetime import datetime
from app.services.database import db_service
from app.services.knowledge_base_service import knowledge_base_service
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GroqService:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set")
        self.client = Groq(api_key=api_key)
        self.model = "llama3-8b-8192"
        
    async def classify_intents(self, email_content: str, subject: str = "", 
                              use_custom_prompt: bool = True) -> List[Dict]:
        """
        Enhanced intent classification using custom system prompts
        """
        try:
            # Get available intents from database
            intents = await db_service.get_intents()
            
            if not intents:
                return []
            
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
                system_prompt = "You are an expert email intent classifier. Always respond with valid JSON."
            
            # Prepare intent descriptions for AI
            intent_descriptions = []
            for intent in intents:
                intent_descriptions.append({
                    "id": intent["id"],
                    "name": intent["name"],
                    "description": intent["description"],
                    "keywords": intent.get("keywords", [])
                })
            
            # Create enhanced classification prompt
            prompt = f"""
            Analyze the following email and classify it into up to 3 most relevant intents from the available options. 
            Pay special attention to detecting multiple intents in a single email.

            Email Subject: {subject}
            Email Content: {email_content}

            Available Intents:
            {json.dumps(intent_descriptions, indent=2)}

            Instructions:
            1. Carefully analyze the email content and subject for multiple intentions
            2. Look for combinations like: interest + questions, positive response + pricing inquiry, etc.
            3. Identify up to 3 most relevant intents with confidence scores
            4. Assign higher confidence for clearly expressed intents
            5. Only return intents with confidence >= 0.6
            6. If multiple intents are present, rank them by strength of evidence
            7. Return results in JSON format

            Response Format:
            {{
                "intents": [
                    {{
                        "intent_id": "intent_id_here",
                        "intent_name": "intent_name_here",
                        "confidence": 0.85,
                        "reasoning": "Detailed explanation including specific keywords/phrases that indicate this intent",
                        "keywords_found": ["keyword1", "keyword2"],
                        "context_strength": "high/medium/low"
                    }}
                ]
            }}
            """
            
            # Use custom system prompt or default
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            # Parse AI response
            try:
                response_content = response.choices[0].message.content.strip()
                
                # Try to extract JSON from the response
                if '{' in response_content and '}' in response_content:
                    start_idx = response_content.find('{')
                    end_idx = response_content.rfind('}') + 1
                    json_str = response_content[start_idx:end_idx]
                    result = json.loads(json_str)
                else:
                    result = json.loads(response_content)
                    
            except json.JSONDecodeError:
                # Fallback parsing
                result = self._fallback_intent_parsing(response_content, intents, email_content)
            
            # Filter and limit to top 3 intents
            classified_intents = []
            for intent in result.get("intents", []):
                if intent.get("confidence", 0) >= 0.6:
                    classified_intents.append(intent)
            
            # Sort by confidence and limit to 3
            classified_intents.sort(key=lambda x: x.get("confidence", 0), reverse=True)
            return classified_intents[:3]
            
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
        Enhanced response generation with knowledge base integration and custom prompts
        """
        try:
            # Convert datetime objects to strings in prospect_data
            if prospect_data:
                for key, value in prospect_data.items():
                    if hasattr(value, 'isoformat'):  # datetime object
                        prospect_data[key] = value.isoformat()
            
            # Get custom system prompt for response generation
            system_prompt = ""
            if use_custom_prompt:
                custom_prompt = await db_service.get_default_system_prompt("response_generation")
                if custom_prompt:
                    system_prompt = custom_prompt["prompt_text"]
                    # Update usage count
                    await db_service.update_system_prompt(custom_prompt["id"], {
                        "usage_count": custom_prompt.get("usage_count", 0) + 1,
                        "last_used": datetime.utcnow()
                    })
            
            # Fallback to default prompt
            if not system_prompt:
                system_prompt = "You are a professional email response generator. Always respond with valid JSON and create engaging, contextual email responses."
            
            # Get relevant knowledge base articles
            knowledge_context = ""
            knowledge_used = []
            if use_knowledge_base and classified_intents:
                for intent in classified_intents:
                    intent_name = intent.get("intent_name", "")
                    relevant_articles = await knowledge_base_service.get_relevant_knowledge_for_intent(
                        intent_name, email_content[:200]
                    )
                    
                    for article in relevant_articles[:3]:  # Top 3 articles per intent
                        knowledge_context += f"\n**{article['title']}**\n{article['content'][:300]}...\n"
                        knowledge_used.append(article['id'])
            
            # Add personalization knowledge
            if use_knowledge_base and prospect_data:
                personalization_articles = await knowledge_base_service.get_knowledge_for_personalization(prospect_data)
                for article in personalization_articles[:2]:  # Top 2 personalization articles
                    knowledge_context += f"\n**{article['title']}**\n{article['content'][:200]}...\n"
                    knowledge_used.append(article['id'])
            
            # Get templates for the classified intents
            templates = await self._get_templates_for_intents(classified_intents)
            
            if not templates:
                return {"error": "No templates found for classified intents"}
            
            # Build enhanced context from conversation history
            context_text = ""
            if conversation_context:
                context_text = "\n\nConversation History:\n"
                for msg in conversation_context[-5:]:  # Last 5 messages
                    timestamp = msg.get('timestamp', '')
                    if hasattr(timestamp, 'strftime'):
                        timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                    elif isinstance(timestamp, str):
                        timestamp = timestamp
                    else:
                        timestamp = str(timestamp)
                    content = msg.get('content', '')[:200]
                    msg_type = msg.get('type', 'unknown')
                    context_text += f"- {timestamp} ({msg_type}): {content}...\n"
            
            # Build prospect context
            prospect_context = ""
            if prospect_data:
                prospect_context = f"\n\nProspect Information:\n"
                prospect_context += f"- Name: {prospect_data.get('first_name', '')} {prospect_data.get('last_name', '')}\n"
                prospect_context += f"- Company: {prospect_data.get('company', '')}\n"
                prospect_context += f"- Job Title: {prospect_data.get('job_title', '')}\n"
                prospect_context += f"- Industry: {prospect_data.get('industry', '')}\n"
                prospect_context += f"- Location: {prospect_data.get('location', '')}\n"
            
            # Convert data to JSON-safe format
            safe_templates = self._make_json_safe(templates)
            safe_intents = self._make_json_safe(classified_intents)
            
            # Create enhanced response generation prompt
            prompt = f"""
            Generate a personalized, professional email response that addresses ALL identified intents using the provided knowledge base and context.

            Original Email Subject: {subject}
            Original Email Content: {email_content[:500]}

            Classified Intents (prioritized by confidence):
            {json.dumps(safe_intents, indent=2)}

            Available Templates:
            {json.dumps(safe_templates, indent=2)}

            {context_text}
            {prospect_context}

            Knowledge Base Context:
            {knowledge_context}

            Enhanced Instructions:
            1. Create a comprehensive response that addresses ALL identified intents
            2. Use the knowledge base information to provide accurate, helpful details
            3. Personalize extensively using prospect data (name, company, industry, job title)
            4. Maintain conversation context and avoid repetition from previous messages
            5. Use templates as guidance but enhance with knowledge base information
            6. Structure response for multiple intents: greeting → address each intent → call to action
            7. Include relevant knowledge base insights naturally in the response
            8. Match the tone and formality level of the original email
            9. End with appropriate call-to-action based on highest confidence intent

            Multi-Intent Handling Examples:
            - "Interest + Questions": Express appreciation, then provide detailed answers with knowledge base insights
            - "Pricing + Demo Request": Acknowledge interest, provide pricing context, focus on scheduling demo
            - "Objection + Request Info": Address concerns with knowledge base facts, then provide requested information

            Response Format:
            {{
                "subject": "Contextual response subject that reflects main intent and personalization",
                "content": "Full HTML email content addressing all intents with knowledge integration",
                "intents_addressed": ["intent1", "intent2"],
                "template_used": "primary_template_id",
                "knowledge_used": {knowledge_used},
                "confidence": 0.85,
                "reasoning": "Explanation of how multiple intents were handled and knowledge was integrated",
                "conversation_context_used": true/false,
                "personalization_elements": ["element1", "element2"]
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=1500
            )
            
            try:
                response_content = response.choices[0].message.content.strip()
                
                # Try to extract JSON from the response
                if '{' in response_content and '}' in response_content:
                    start_idx = response_content.find('{')
                    end_idx = response_content.rfind('}') + 1
                    json_str = response_content[start_idx:end_idx]
                    result = json.loads(json_str)
                else:
                    result = json.loads(response_content)
                
                # Add knowledge used to result
                result["knowledge_used"] = list(set(knowledge_used))
                return result
                    
            except json.JSONDecodeError:
                print(f"Failed to parse JSON from response: {response_content}")
                return {"error": "Failed to parse AI response", "raw_response": response_content}
            
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return {"error": f"Response generation failed: {str(e)}"}
    
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
                
                # Get combination templates if applicable
                for combo_template in intent_details.get("combination_templates", []):
                    template = await db_service.get_template_by_id(combo_template.get("template_id"))
                    if template:
                        templates.append(template)
        
        # If no specific templates found, get all auto_response templates
        if not templates:
            all_templates = await db_service.get_templates()
            templates = [t for t in all_templates if t.get("type") == "auto_response"]
        
        return templates
    
    async def analyze_email_sentiment(self, email_content: str) -> Dict:
        """Analyze email sentiment and urgency"""
        try:
            prompt = f"""
            Analyze the sentiment and urgency of this email:

            Email Content: {email_content}

            Provide analysis in JSON format:
            {{
                "sentiment": "positive/negative/neutral",
                "urgency": "high/medium/low",
                "emotion_detected": "excited/angry/confused/satisfied/etc",
                "confidence": 0.85,
                "key_phrases": ["phrase1", "phrase2"]
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert email sentiment analyzer. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=500
            )
            
            try:
                result = json.loads(response.choices[0].message.content)
            except json.JSONDecodeError:
                # If JSON parsing fails, create a fallback response
                content = response.choices[0].message.content
                print(f"Failed to parse JSON from Groq sentiment response: {content}")
                
                # Simple keyword-based sentiment analysis
                content_lower = email_content.lower()
                sentiment = "neutral"
                urgency = "medium"
                
                positive_words = ["interested", "yes", "great", "awesome", "love", "want", "need"]
                negative_words = ["no", "not interested", "stop", "remove", "unsubscribe"]
                urgent_words = ["urgent", "asap", "immediately", "now", "quick", "fast"]
                
                if any(word in content_lower for word in positive_words):
                    sentiment = "positive"
                elif any(word in content_lower for word in negative_words):
                    sentiment = "negative"
                
                if any(word in content_lower for word in urgent_words):
                    urgency = "high"
                
                result = {
                    "sentiment": sentiment,
                    "urgency": urgency,
                    "emotion_detected": "neutral",
                    "confidence": 0.5,
                    "key_phrases": []
                }
            
            return result
            
        except Exception as e:
            print(f"Error analyzing sentiment: {str(e)}")
            return {"sentiment": "neutral", "urgency": "medium", "confidence": 0.0}

# Create global Groq service instance
groq_service = GroqService()