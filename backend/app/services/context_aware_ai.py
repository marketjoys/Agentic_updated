import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
import json
from app.services.database import db_service
from app.services.groq_service import groq_service
from app.services.knowledge_base_service import knowledge_base_service
from app.utils.helpers import generate_id

logger = logging.getLogger(__name__)

class ContextAwareAI:
    def __init__(self):
        self.conversation_memory = {}
        self.context_window = 10  # Number of previous messages to consider
        self.personalization_cache = {}
    
    async def generate_context_aware_response(self, 
                                            prospect_id: str,
                                            email_content: str,
                                            subject: str,
                                            enhanced_context: bool = True) -> Dict:
        """Generate context-aware response using conversation history and knowledge base"""
        try:
            # Get prospect data
            prospect = await db_service.get_prospect_by_id(prospect_id)
            if not prospect:
                return {"error": "Prospect not found"}
            
            # Get thread context
            thread = await db_service.get_thread_by_prospect_id(prospect_id)
            conversation_history = []
            
            if thread:
                messages = thread.get("messages", [])
                # Get last N messages for context
                conversation_history = messages[-self.context_window:] if messages else []
            
            # Classify intents with enhanced prompts
            classified_intents = await groq_service.classify_intents(
                email_content, subject, use_custom_prompt=True
            )
            
            # Get enhanced context if requested
            context_data = {}
            if enhanced_context:
                context_data = await self._build_enhanced_context(
                    prospect, conversation_history, classified_intents
                )
            
            # Generate response with full context
            response_data = await groq_service.generate_response(
                email_content, subject, classified_intents,
                conversation_history, prospect,
                use_knowledge_base=True, use_custom_prompt=True
            )
            
            # Enhance response with context data
            if context_data and not response_data.get("error"):
                response_data["context_used"] = context_data
                response_data["enhanced_with_context"] = True
            
            return response_data
            
        except Exception as e:
            logger.error(f"Error generating context-aware response: {str(e)}")
            return {"error": str(e)}
    
    async def _build_enhanced_context(self, prospect: Dict, 
                                    conversation_history: List[Dict],
                                    classified_intents: List[Dict]) -> Dict:
        """Build enhanced context for better AI responses"""
        try:
            context_data = {
                "prospect_insights": await self._get_prospect_insights(prospect),
                "conversation_patterns": await self._analyze_conversation_patterns(conversation_history),
                "intent_evolution": await self._analyze_intent_evolution(prospect["id"], classified_intents),
                "knowledge_relevance": await self._get_relevant_knowledge_context(prospect, classified_intents),
                "personalization_data": await self._get_personalization_context(prospect)
            }
            
            return context_data
            
        except Exception as e:
            logger.error(f"Error building enhanced context: {str(e)}")
            return {}
    
    async def _get_prospect_insights(self, prospect: Dict) -> Dict:
        """Get insights about the prospect"""
        try:
            insights = {
                "engagement_level": "unknown",
                "response_frequency": 0,
                "last_interaction": prospect.get("last_contact"),
                "follow_up_count": prospect.get("follow_up_count", 0),
                "response_type": prospect.get("response_type", ""),
                "industry_context": prospect.get("industry", "")
            }
            
            # Calculate engagement level
            if prospect.get("responded_at"):
                days_since_response = (datetime.utcnow() - prospect["responded_at"]).days
                if days_since_response < 7:
                    insights["engagement_level"] = "high"
                elif days_since_response < 30:
                    insights["engagement_level"] = "medium"
                else:
                    insights["engagement_level"] = "low"
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting prospect insights: {str(e)}")
            return {}
    
    async def _analyze_conversation_patterns(self, conversation_history: List[Dict]) -> Dict:
        """Analyze conversation patterns for context"""
        try:
            if not conversation_history:
                return {"pattern": "new_conversation", "message_count": 0}
            
            patterns = {
                "message_count": len(conversation_history),
                "avg_response_time": 0,
                "communication_style": "formal",
                "topic_progression": [],
                "sentiment_trend": "neutral"
            }
            
            # Analyze message timing
            timestamps = [msg.get("timestamp") for msg in conversation_history if msg.get("timestamp")]
            if len(timestamps) > 1:
                time_diffs = []
                for i in range(1, len(timestamps)):
                    if isinstance(timestamps[i], datetime) and isinstance(timestamps[i-1], datetime):
                        diff = (timestamps[i] - timestamps[i-1]).total_seconds() / 3600  # hours
                        time_diffs.append(diff)
                
                if time_diffs:
                    patterns["avg_response_time"] = sum(time_diffs) / len(time_diffs)
            
            # Analyze communication style
            all_content = " ".join([msg.get("content", "") for msg in conversation_history])
            if any(word in all_content.lower() for word in ["thanks", "please", "appreciate"]):
                patterns["communication_style"] = "polite"
            elif any(word in all_content.lower() for word in ["urgent", "asap", "immediately"]):
                patterns["communication_style"] = "urgent"
            elif len(all_content) > 500:
                patterns["communication_style"] = "detailed"
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error analyzing conversation patterns: {str(e)}")
            return {"pattern": "error", "message_count": 0}
    
    async def _analyze_intent_evolution(self, prospect_id: str, 
                                      current_intents: List[Dict]) -> Dict:
        """Analyze how intents have evolved over time"""
        try:
            # Get historical intent data (this would require storing intent history)
            # For now, we'll analyze current intents
            
            intent_analysis = {
                "current_intents": [intent.get("intent_name") for intent in current_intents],
                "intent_confidence": [intent.get("confidence", 0) for intent in current_intents],
                "primary_intent": current_intents[0].get("intent_name") if current_intents else "unknown",
                "multi_intent": len(current_intents) > 1,
                "intent_strength": sum(intent.get("confidence", 0) for intent in current_intents) / len(current_intents) if current_intents else 0
            }
            
            return intent_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing intent evolution: {str(e)}")
            return {"current_intents": [], "primary_intent": "unknown"}
    
    async def _get_relevant_knowledge_context(self, prospect: Dict, 
                                            classified_intents: List[Dict]) -> Dict:
        """Get relevant knowledge base context"""
        try:
            knowledge_context = {
                "relevant_articles": [],
                "industry_insights": [],
                "personalization_knowledge": []
            }
            
            # Get knowledge for intents
            for intent in classified_intents:
                intent_name = intent.get("intent_name", "")
                relevant_articles = await knowledge_base_service.get_relevant_knowledge_for_intent(
                    intent_name, prospect.get("industry", "")
                )
                knowledge_context["relevant_articles"].extend(relevant_articles[:2])
            
            # Get industry-specific knowledge
            if prospect.get("industry"):
                industry_knowledge = await knowledge_base_service.search_knowledge_articles(
                    prospect["industry"], limit=3
                )
                knowledge_context["industry_insights"] = industry_knowledge
            
            # Get personalization knowledge
            personalization_knowledge = await knowledge_base_service.get_knowledge_for_personalization(prospect)
            knowledge_context["personalization_knowledge"] = personalization_knowledge[:2]
            
            return knowledge_context
            
        except Exception as e:
            logger.error(f"Error getting relevant knowledge context: {str(e)}")
            return {"relevant_articles": [], "industry_insights": []}
    
    async def _get_personalization_context(self, prospect: Dict) -> Dict:
        """Get personalization context for the prospect"""
        try:
            personalization_context = {
                "name_usage": f"{prospect.get('first_name', '')} {prospect.get('last_name', '')}".strip(),
                "company_context": prospect.get("company", ""),
                "industry_context": prospect.get("industry", ""),
                "job_title_context": prospect.get("job_title", ""),
                "location_context": prospect.get("location", ""),
                "company_size_context": prospect.get("company_size", ""),
                "personalization_opportunities": []
            }
            
            # Identify personalization opportunities
            if prospect.get("company"):
                personalization_context["personalization_opportunities"].append("company_mention")
            if prospect.get("industry"):
                personalization_context["personalization_opportunities"].append("industry_relevance")
            if prospect.get("job_title"):
                personalization_context["personalization_opportunities"].append("role_specific")
            if prospect.get("location"):
                personalization_context["personalization_opportunities"].append("location_reference")
            
            return personalization_context
            
        except Exception as e:
            logger.error(f"Error getting personalization context: {str(e)}")
            return {"personalization_opportunities": []}
    
    async def update_conversation_memory(self, prospect_id: str, 
                                       message_data: Dict):
        """Update conversation memory for a prospect"""
        try:
            if prospect_id not in self.conversation_memory:
                self.conversation_memory[prospect_id] = []
            
            self.conversation_memory[prospect_id].append({
                "timestamp": datetime.utcnow(),
                "message_data": message_data,
                "context_used": True
            })
            
            # Keep only recent messages in memory
            if len(self.conversation_memory[prospect_id]) > self.context_window:
                self.conversation_memory[prospect_id] = self.conversation_memory[prospect_id][-self.context_window:]
            
        except Exception as e:
            logger.error(f"Error updating conversation memory: {str(e)}")
    
    async def get_conversation_summary(self, prospect_id: str) -> Dict:
        """Get a summary of the conversation with a prospect"""
        try:
            thread = await db_service.get_thread_by_prospect_id(prospect_id)
            if not thread:
                return {"summary": "No conversation history found"}
            
            messages = thread.get("messages", [])
            if not messages:
                return {"summary": "No messages in conversation"}
            
            # Use AI to generate conversation summary
            conversation_text = "\n".join([
                f"{msg.get('type', 'unknown')}: {msg.get('content', '')[:200]}..."
                for msg in messages[-5:]  # Last 5 messages
            ])
            
            summary_prompt = f"""
            Summarize the following conversation between a salesperson and a prospect:
            
            {conversation_text}
            
            Provide a concise summary including:
            1. Key points discussed
            2. Current status of the conversation
            3. Next steps or follow-up needed
            4. Prospect's level of interest
            
            Keep it under 200 words.
            """
            
            response = await groq_service.client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": "You are an expert conversation summarizer."},
                    {"role": "user", "content": summary_prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            summary = response.choices[0].message.content.strip()
            
            return {
                "summary": summary,
                "message_count": len(messages),
                "last_activity": thread.get("last_activity"),
                "conversation_status": thread.get("status", "active")
            }
            
        except Exception as e:
            logger.error(f"Error getting conversation summary: {str(e)}")
            return {"summary": "Error generating summary", "error": str(e)}

# Create global context-aware AI instance
context_aware_ai = ContextAwareAI()