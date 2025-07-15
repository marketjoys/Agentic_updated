"""
AI-Enhanced Email Service
Integrates Knowledge Base, System Prompts, and Response Verification
into the email sending workflow for improved email quality and consistency.
"""

from typing import Dict, List, Optional, Any
import logging
from datetime import datetime
from app.services.database import db_service, clean_document
from app.services.groq_service_mock import groq_service
from app.services.knowledge_base_service import knowledge_base_service
from app.services.response_verification_service import response_verification_service
from app.utils.helpers import generate_id, personalize_template

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIEnhancedEmailService:
    def __init__(self):
        self.verification_enabled = True
        self.knowledge_base_enabled = True
        self.ai_enhancement_enabled = True
        
    async def enhance_email_content(self, 
                                   template_content: str, 
                                   prospect_data: Dict,
                                   campaign_context: Dict = None,
                                   intent_context: str = None) -> Dict:
        """
        Enhanced email content generation using AI, Knowledge Base, and System Prompts
        """
        try:
            await db_service.connect()
            
            # Step 1: Get relevant knowledge base articles
            knowledge_articles = []
            if self.knowledge_base_enabled:
                knowledge_articles = await self._get_relevant_knowledge(
                    prospect_data, campaign_context, intent_context
                )
            
            # Step 2: Get appropriate system prompts
            system_prompts = await self._get_system_prompts()
            
            # Step 3: Generate enhanced content using AI
            enhanced_content = await self._generate_enhanced_content(
                template_content, 
                prospect_data, 
                knowledge_articles, 
                system_prompts,
                campaign_context
            )
            
            # Step 4: Personalize the enhanced content
            personalized_content = personalize_template(enhanced_content, prospect_data)
            
            # Step 5: Verify the response quality if enabled
            verification_result = None
            if self.verification_enabled:
                verification_result = await self._verify_response_quality(
                    personalized_content, 
                    prospect_data, 
                    template_content,
                    intent_context
                )
            
            return {
                "enhanced_content": personalized_content,
                "original_content": template_content,
                "knowledge_articles_used": knowledge_articles,
                "verification_result": verification_result,
                "ai_enhancement_applied": self.ai_enhancement_enabled,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in enhance_email_content: {str(e)}")
            # Fallback to original content if enhancement fails
            return {
                "enhanced_content": personalize_template(template_content, prospect_data),
                "original_content": template_content,
                "knowledge_articles_used": [],
                "verification_result": None,
                "ai_enhancement_applied": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _get_relevant_knowledge(self, 
                                    prospect_data: Dict, 
                                    campaign_context: Dict = None,
                                    intent_context: str = None) -> List[Dict]:
        """Get relevant knowledge base articles based on prospect and context"""
        try:
            # Build search query based on prospect data
            search_queries = []
            
            # Add industry-specific knowledge
            if prospect_data.get("industry"):
                search_queries.append(prospect_data["industry"])
            
            # Add company-specific knowledge
            if prospect_data.get("company"):
                search_queries.append(prospect_data["company"])
            
            # Add job title specific knowledge
            if prospect_data.get("job_title"):
                search_queries.append(prospect_data["job_title"])
            
            # Add intent-specific knowledge
            if intent_context:
                search_queries.append(intent_context)
                
            # Add campaign-specific knowledge
            if campaign_context and campaign_context.get("name"):
                search_queries.append(campaign_context["name"])
            
            # Search for relevant articles
            relevant_articles = []
            for query in search_queries:
                articles = await knowledge_base_service.search_knowledge_articles(
                    query, limit=3
                )
                relevant_articles.extend(articles)
            
            # Remove duplicates and limit results
            unique_articles = []
            seen_ids = set()
            for article in relevant_articles:
                if article.get("id") not in seen_ids:
                    unique_articles.append(article)
                    seen_ids.add(article.get("id"))
            
            # Clean the articles to remove ObjectId fields
            cleaned_articles = clean_document(unique_articles[:5])
            return cleaned_articles  # Limit to top 5 most relevant
            
        except Exception as e:
            logger.error(f"Error getting relevant knowledge: {str(e)}")
            return []
    
    async def _get_system_prompts(self) -> Dict:
        """Get system prompts for different AI operations"""
        try:
            prompts = {}
            
            # Get personalization prompt
            personalization_prompt = await db_service.get_default_system_prompt("personalization")
            if personalization_prompt:
                prompts["personalization"] = personalization_prompt
            
            # Get response generation prompt
            response_prompt = await db_service.get_default_system_prompt("response_generation")
            if response_prompt:
                prompts["response_generation"] = response_prompt
                
            # Get general behavior prompt
            general_prompt = await db_service.get_default_system_prompt("general")
            if general_prompt:
                prompts["general"] = general_prompt
                
            return prompts
            
        except Exception as e:
            logger.error(f"Error getting system prompts: {str(e)}")
            return {}
    
    async def _generate_enhanced_content(self, 
                                       template_content: str,
                                       prospect_data: Dict,
                                       knowledge_articles: List[Dict],
                                       system_prompts: Dict,
                                       campaign_context: Dict = None) -> str:
        """Generate enhanced email content using AI"""
        try:
            if not self.ai_enhancement_enabled:
                return template_content
                
            # Build context for AI enhancement
            context_parts = []
            
            # Add prospect context
            context_parts.append(f"Prospect Information:")
            context_parts.append(f"- Name: {prospect_data.get('first_name', '')} {prospect_data.get('last_name', '')}")
            context_parts.append(f"- Company: {prospect_data.get('company', '')}")
            context_parts.append(f"- Job Title: {prospect_data.get('job_title', '')}")
            context_parts.append(f"- Industry: {prospect_data.get('industry', '')}")
            
            # Add campaign context
            if campaign_context:
                context_parts.append(f"\nCampaign Context:")
                context_parts.append(f"- Campaign Name: {campaign_context.get('name', '')}")
                context_parts.append(f"- Campaign Type: {campaign_context.get('type', '')}")
            
            # Add knowledge base context
            if knowledge_articles:
                context_parts.append(f"\nRelevant Knowledge Base Articles:")
                for article in knowledge_articles:
                    context_parts.append(f"- {article.get('title', '')}: {article.get('content', '')[:200]}...")
            
            # Build AI prompt
            system_prompt = system_prompts.get("personalization", {}).get("prompt_text", 
                "You are a professional email assistant. Enhance the email content to be more personalized and effective.")
            
            enhancement_prompt = f"""
            {system_prompt}
            
            Context:
            {chr(10).join(context_parts)}
            
            Original Email Template:
            {template_content}
            
            Please enhance this email template to be more personalized and effective for this specific prospect.
            Make it more engaging while maintaining professionalism.
            Use the knowledge base information to add relevant insights.
            Return only the enhanced email content.
            """
            
            # Call AI service
            response = await groq_service.client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": enhancement_prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            enhanced_content = response.choices[0].message.content
            
            # Update usage count for knowledge articles
            for article in knowledge_articles:
                if article.get("id"):
                    await db_service.update_knowledge_article_usage(article["id"])
            
            return enhanced_content
            
        except Exception as e:
            logger.error(f"Error generating enhanced content: {str(e)}")
            return template_content
    
    async def _verify_response_quality(self, 
                                     email_content: str,
                                     prospect_data: Dict,
                                     original_template: str,
                                     intent_context: str = None) -> Dict:
        """Verify the quality of the enhanced email content"""
        try:
            # Create verification request
            verification_request = {
                "message_id": generate_id(),
                "response_content": email_content,
                "original_email": original_template,
                "classified_intents": [intent_context] if intent_context else [],
                "conversation_context": [],
                "prospect_data": prospect_data
            }
            
            # Run verification
            verification_result = await response_verification_service.verify_response(
                verification_request["message_id"],
                verification_request["response_content"],
                verification_request["original_email"],
                verification_request["classified_intents"],
                verification_request["conversation_context"],
                verification_request["prospect_data"]
            )
            
            # Clean the verification result to remove ObjectId fields
            cleaned_verification_result = clean_document(verification_result)
            return cleaned_verification_result
            
        except Exception as e:
            logger.error(f"Error verifying response quality: {str(e)}")
            return None
    
    async def process_campaign_email(self, 
                                   campaign_data: Dict,
                                   template_data: Dict,
                                   prospect_data: Dict) -> Dict:
        """Process a single campaign email with AI enhancement"""
        try:
            # Determine intent context from campaign
            intent_context = campaign_data.get("intent_context", "general_outreach")
            
            # Enhance email content
            enhancement_result = await self.enhance_email_content(
                template_data.get("content", ""),
                prospect_data,
                campaign_data,
                intent_context
            )
            
            # Also enhance subject line
            subject_enhancement = await self.enhance_email_content(
                template_data.get("subject", ""),
                prospect_data,
                campaign_data,
                intent_context
            )
            
            return {
                "content": enhancement_result["enhanced_content"],
                "subject": subject_enhancement["enhanced_content"],
                "original_content": enhancement_result["original_content"],
                "original_subject": template_data.get("subject", ""),
                "knowledge_articles_used": enhancement_result["knowledge_articles_used"],
                "verification_result": enhancement_result["verification_result"],
                "ai_enhancement_applied": enhancement_result["ai_enhancement_applied"],
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing campaign email: {str(e)}")
            return {
                "content": personalize_template(template_data.get("content", ""), prospect_data),
                "subject": personalize_template(template_data.get("subject", ""), prospect_data),
                "original_content": template_data.get("content", ""),
                "original_subject": template_data.get("subject", ""),
                "knowledge_articles_used": [],
                "verification_result": None,
                "ai_enhancement_applied": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_enhancement_statistics(self) -> Dict:
        """Get statistics about AI enhancement usage"""
        try:
            await db_service.connect()
            
            # Get knowledge base stats
            kb_stats = await knowledge_base_service.get_knowledge_statistics()
            
            # Get verification stats
            verification_stats = await response_verification_service.get_verification_statistics()
            
            # Get system prompt usage
            system_prompts = await db_service.get_system_prompts()
            total_prompt_usage = sum(prompt.get("usage_count", 0) for prompt in system_prompts)
            
            return {
                "knowledge_base": kb_stats,
                "response_verification": verification_stats,
                "system_prompts": {
                    "total_prompts": len(system_prompts),
                    "total_usage": total_prompt_usage,
                    "active_prompts": len([p for p in system_prompts if p.get("is_active", False)])
                },
                "enhancement_settings": {
                    "verification_enabled": self.verification_enabled,
                    "knowledge_base_enabled": self.knowledge_base_enabled,
                    "ai_enhancement_enabled": self.ai_enhancement_enabled
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting enhancement statistics: {str(e)}")
            return {}

# Create singleton instance
ai_enhanced_email_service = AIEnhancedEmailService()