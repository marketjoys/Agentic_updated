import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging
import json
from app.models import ResponseVerification
from app.services.database import db_service
from app.services.groq_service_mock import groq_service
from app.services.knowledge_base_service import knowledge_base_service
from app.utils.helpers import generate_id

logger = logging.getLogger(__name__)

class ResponseVerificationService:
    def __init__(self):
        self.verification_thresholds = {
            "context_alignment": 0.7,
            "intent_accuracy": 0.8,
            "content_quality": 0.75,
            "overall_score": 0.75
        }
    
    async def verify_response(self, message_id: str, response_content: str, 
                            original_email: str, classified_intents: List[Dict],
                            conversation_context: List[Dict], prospect_data: Dict) -> Dict:
        """Verify an AI-generated response before sending"""
        try:
            # Create verification record
            verification_id = generate_id()
            verification_data = {
                "id": verification_id,
                "message_id": message_id,
                "original_content": response_content,
                "verified_content": response_content,
                "status": "pending",
                "created_at": datetime.utcnow()
            }
            
            # Perform verification checks
            verification_result = await self._perform_verification_checks(
                response_content, original_email, classified_intents, 
                conversation_context, prospect_data
            )
            
            # Update verification data with results
            verification_data.update(verification_result)
            
            # Determine final status
            overall_score = verification_result.get("overall_score", 0.0)
            if overall_score >= self.verification_thresholds["overall_score"]:
                verification_data["status"] = "approved"
            elif overall_score >= 0.5:
                verification_data["status"] = "needs_review"
                verification_data["requires_manual_review"] = True
            else:
                verification_data["status"] = "rejected"
                verification_data["requires_manual_review"] = True
            
            # Save verification record
            await db_service.create_response_verification(verification_data)
            
            return verification_data
            
        except Exception as e:
            logger.error(f"Error verifying response: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def get_pending_verifications(self) -> List[Dict]:
        """Get all pending verifications"""
        try:
            verifications = await db_service.get_pending_verifications()
            return verifications
        except Exception as e:
            logger.error(f"Error getting pending verifications: {str(e)}")
            return []
    
    async def approve_verification(self, verification_id: str, reviewer: str, 
                                 notes: str = "") -> Tuple[bool, Optional[str]]:
        """Manually approve a verification"""
        try:
            verification_data = {
                "status": "approved",
                "manual_reviewer": reviewer,
                "manual_review_notes": notes,
                "verified_at": datetime.utcnow()
            }
            
            result = await db_service.update_response_verification(verification_id, verification_data)
            return bool(result), None
            
        except Exception as e:
            logger.error(f"Error approving verification {verification_id}: {str(e)}")
            return False, str(e)
    
    async def reject_verification(self, verification_id: str, reviewer: str, 
                                notes: str = "", suggested_changes: str = "") -> Tuple[bool, Optional[str]]:
        """Manually reject a verification"""
        try:
            verification_data = {
                "status": "rejected",
                "manual_reviewer": reviewer,
                "manual_review_notes": notes,
                "suggested_changes": suggested_changes,
                "verified_at": datetime.utcnow()
            }
            
            result = await db_service.update_response_verification(verification_id, verification_data)
            return bool(result), None
            
        except Exception as e:
            logger.error(f"Error rejecting verification {verification_id}: {str(e)}")
            return False, str(e)
    
    async def update_response_content(self, verification_id: str, new_content: str) -> Tuple[bool, Optional[str]]:
        """Update response content after verification"""
        try:
            verification_data = {
                "verified_content": new_content,
                "updated_at": datetime.utcnow()
            }
            
            result = await db_service.update_response_verification(verification_id, verification_data)
            return bool(result), None
            
        except Exception as e:
            logger.error(f"Error updating response content: {str(e)}")
            return False, str(e)
    
    async def get_verification_by_id(self, verification_id: str) -> Optional[Dict]:
        """Get verification by ID"""
        try:
            verification = await db_service.get_response_verification_by_id(verification_id)
            return verification
        except Exception as e:
            logger.error(f"Error getting verification {verification_id}: {str(e)}")
            return None
    
    async def get_verification_statistics(self) -> Dict:
        """Get verification statistics"""
        try:
            stats = await db_service.get_verification_statistics()
            return stats
        except Exception as e:
            logger.error(f"Error getting verification statistics: {str(e)}")
            return {}
    
    async def _perform_verification_checks(self, response_content: str, original_email: str,
                                         classified_intents: List[Dict], conversation_context: List[Dict],
                                         prospect_data: Dict) -> Dict:
        """Perform comprehensive verification checks"""
        try:
            verification_results = {}
            
            # 1. Context Alignment Check
            context_score = await self._check_context_alignment(
                response_content, original_email, conversation_context
            )
            verification_results["context_score"] = context_score
            
            # 2. Intent Accuracy Check
            intent_score = await self._check_intent_accuracy(
                response_content, classified_intents
            )
            verification_results["intent_alignment_score"] = intent_score
            
            # 3. Content Quality Check
            quality_score = await self._check_content_quality(
                response_content, prospect_data
            )
            verification_results["content_quality_score"] = quality_score
            
            # 4. Personalization Check
            personalization_score = await self._check_personalization(
                response_content, prospect_data
            )
            verification_results["personalization_score"] = personalization_score
            
            # 5. Professional Tone Check
            tone_score = await self._check_professional_tone(response_content)
            verification_results["tone_score"] = tone_score
            
            # 6. Calculate overall score
            overall_score = (
                context_score * 0.25 +
                intent_score * 0.25 +
                quality_score * 0.20 +
                personalization_score * 0.15 +
                tone_score * 0.15
            )
            verification_results["overall_score"] = overall_score
            
            # 7. Generate verification notes
            verification_results["verification_notes"] = await self._generate_verification_notes(
                verification_results
            )
            
            # 8. Generate suggested changes if needed
            if overall_score < self.verification_thresholds["overall_score"]:
                verification_results["suggested_changes"] = await self._generate_suggested_changes(
                    response_content, verification_results
                )
            
            return verification_results
            
        except Exception as e:
            logger.error(f"Error performing verification checks: {str(e)}")
            return {"overall_score": 0.0, "error": str(e)}
    
    async def _check_context_alignment(self, response_content: str, original_email: str,
                                     conversation_context: List[Dict]) -> float:
        """Check if response aligns with conversation context"""
        try:
            # Use AI to analyze context alignment
            context_text = ""
            if conversation_context:
                for msg in conversation_context[-3:]:  # Last 3 messages
                    content = msg.get('content', '')[:200]
                    msg_type = msg.get('type', 'unknown')
                    context_text += f"{msg_type}: {content}\n"
            
            prompt = f"""
            Analyze if the following response appropriately addresses the original email and maintains context with the conversation history.
            
            Original Email: {original_email[:500]}
            
            Conversation Context:
            {context_text}
            
            Generated Response: {response_content[:500]}
            
            Rate the context alignment on a scale of 0.0 to 1.0 where:
            - 1.0 = Perfect alignment, directly addresses the email and maintains context
            - 0.8 = Good alignment with minor context issues
            - 0.6 = Adequate alignment but some context missed
            - 0.4 = Poor alignment, doesn't address key points
            - 0.2 = Very poor alignment, off-topic
            - 0.0 = No alignment, completely irrelevant
            
            Respond with only a number between 0.0 and 1.0.
            """
            
            # Use Groq for analysis
            response = await groq_service.client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": "You are an expert email context analyzer. Respond only with a decimal number between 0.0 and 1.0."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=10
            )
            
            try:
                score = float(response.choices[0].message.content.strip())
                return max(0.0, min(1.0, score))
            except:
                return 0.5  # Default if parsing fails
                
        except Exception as e:
            logger.error(f"Error checking context alignment: {str(e)}")
            return 0.5
    
    async def _check_intent_accuracy(self, response_content: str, classified_intents: List[Dict]) -> float:
        """Check if response accurately addresses the classified intents"""
        try:
            if not classified_intents:
                return 0.5
            
            # Create intent summary
            intent_summary = ""
            for intent in classified_intents:
                intent_summary += f"- {intent.get('intent_name', 'Unknown')}: {intent.get('confidence', 0):.2f}\n"
            
            prompt = f"""
            Analyze if the following response appropriately addresses the classified intents.
            
            Classified Intents:
            {intent_summary}
            
            Generated Response: {response_content[:500]}
            
            Rate the intent accuracy on a scale of 0.0 to 1.0 where:
            - 1.0 = Perfectly addresses all intents
            - 0.8 = Addresses most intents well
            - 0.6 = Addresses some intents adequately
            - 0.4 = Addresses few intents properly
            - 0.2 = Barely addresses intents
            - 0.0 = Doesn't address intents at all
            
            Respond with only a number between 0.0 and 1.0.
            """
            
            response = await groq_service.client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": "You are an expert intent analyzer. Respond only with a decimal number between 0.0 and 1.0."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=10
            )
            
            try:
                score = float(response.choices[0].message.content.strip())
                return max(0.0, min(1.0, score))
            except:
                return 0.5
                
        except Exception as e:
            logger.error(f"Error checking intent accuracy: {str(e)}")
            return 0.5
    
    async def _check_content_quality(self, response_content: str, prospect_data: Dict) -> float:
        """Check overall content quality"""
        try:
            quality_score = 0.0
            
            # Check length (not too short, not too long)
            content_length = len(response_content)
            if 100 <= content_length <= 1000:
                quality_score += 0.3
            elif 50 <= content_length <= 1500:
                quality_score += 0.2
            else:
                quality_score += 0.1
            
            # Check for proper structure (greeting, body, closing)
            has_greeting = any(greeting in response_content.lower() for greeting in ["hello", "hi", "dear", "greetings"])
            has_closing = any(closing in response_content.lower() for closing in ["regards", "thanks", "sincerely", "best"])
            
            if has_greeting and has_closing:
                quality_score += 0.3
            elif has_greeting or has_closing:
                quality_score += 0.2
            
            # Check for personalization elements
            prospect_name = f"{prospect_data.get('first_name', '')} {prospect_data.get('last_name', '')}".strip()
            company_name = prospect_data.get('company', '')
            
            if prospect_name and prospect_name.lower() in response_content.lower():
                quality_score += 0.2
            if company_name and company_name.lower() in response_content.lower():
                quality_score += 0.2
            
            return min(1.0, quality_score)
            
        except Exception as e:
            logger.error(f"Error checking content quality: {str(e)}")
            return 0.5
    
    async def _check_personalization(self, response_content: str, prospect_data: Dict) -> float:
        """Check level of personalization"""
        try:
            personalization_score = 0.0
            response_lower = response_content.lower()
            
            # Check for name usage
            if prospect_data.get('first_name') and prospect_data['first_name'].lower() in response_lower:
                personalization_score += 0.3
            
            # Check for company mention
            if prospect_data.get('company') and prospect_data['company'].lower() in response_lower:
                personalization_score += 0.2
            
            # Check for industry relevance
            if prospect_data.get('industry') and prospect_data['industry'].lower() in response_lower:
                personalization_score += 0.2
            
            # Check for job title relevance
            if prospect_data.get('job_title') and prospect_data['job_title'].lower() in response_lower:
                personalization_score += 0.2
            
            # Check for location mention
            if prospect_data.get('location') and prospect_data['location'].lower() in response_lower:
                personalization_score += 0.1
            
            return min(1.0, personalization_score)
            
        except Exception as e:
            logger.error(f"Error checking personalization: {str(e)}")
            return 0.5
    
    async def _check_professional_tone(self, response_content: str) -> float:
        """Check for professional tone"""
        try:
            # Simple checks for professional tone
            content_lower = response_content.lower()
            
            # Negative indicators
            unprofessional_words = ["hate", "stupid", "dumb", "crazy", "insane", "ridiculous"]
            if any(word in content_lower for word in unprofessional_words):
                return 0.3
            
            # Positive indicators
            professional_phrases = [
                "thank you", "please", "would you", "could you", "i appreciate",
                "best regards", "sincerely", "looking forward", "happy to help"
            ]
            
            professional_count = sum(1 for phrase in professional_phrases if phrase in content_lower)
            tone_score = min(1.0, professional_count * 0.2 + 0.4)
            
            return tone_score
            
        except Exception as e:
            logger.error(f"Error checking professional tone: {str(e)}")
            return 0.5
    
    async def _generate_verification_notes(self, verification_results: Dict) -> str:
        """Generate verification notes based on results"""
        notes = []
        
        if verification_results.get("context_score", 0) < 0.7:
            notes.append("Context alignment could be improved")
        
        if verification_results.get("intent_alignment_score", 0) < 0.7:
            notes.append("Intent accuracy needs attention")
        
        if verification_results.get("content_quality_score", 0) < 0.7:
            notes.append("Content quality could be enhanced")
        
        if verification_results.get("personalization_score", 0) < 0.5:
            notes.append("More personalization recommended")
        
        if verification_results.get("tone_score", 0) < 0.7:
            notes.append("Professional tone could be improved")
        
        if not notes:
            notes.append("Response meets quality standards")
        
        return "; ".join(notes)
    
    async def _generate_suggested_changes(self, response_content: str, verification_results: Dict) -> str:
        """Generate suggested changes for improvement"""
        suggestions = []
        
        if verification_results.get("context_score", 0) < 0.7:
            suggestions.append("Better address the specific points mentioned in the original email")
        
        if verification_results.get("intent_alignment_score", 0) < 0.7:
            suggestions.append("More directly address the classified intents")
        
        if verification_results.get("personalization_score", 0) < 0.5:
            suggestions.append("Include more personalized elements (name, company, industry)")
        
        if verification_results.get("tone_score", 0) < 0.7:
            suggestions.append("Use more professional and courteous language")
        
        return "; ".join(suggestions) if suggestions else "No specific suggestions"

# Create global response verification service instance
response_verification_service = ResponseVerificationService()