import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging
import json
from app.models import KnowledgeBase
from app.services.database import db_service
from app.utils.helpers import generate_id

logger = logging.getLogger(__name__)

class KnowledgeBaseService:
    def __init__(self):
        self.categories = [
            "general",
            "product_info",
            "pricing",
            "company_info",
            "technical_support",
            "sales_process",
            "objection_handling",
            "competitor_info",
            "case_studies",
            "testimonials"
        ]
    
    async def create_knowledge_article(self, article_data: Dict) -> Tuple[Optional[str], Optional[str]]:
        """Create a new knowledge base article"""
        try:
            # Generate ID
            article_id = generate_id()
            article_data["id"] = article_id
            
            # Validate article data
            validation_error = await self._validate_article_data(article_data)
            if validation_error:
                return None, validation_error
            
            # Extract keywords from content
            if not article_data.get("keywords"):
                article_data["keywords"] = await self._extract_keywords(article_data["content"])
            
            # Generate embedding vector (placeholder for now - would use actual embedding service)
            article_data["embedding_vector"] = await self._generate_embedding(article_data["content"])
            
            # Save to database
            result = await db_service.create_knowledge_article(article_data)
            if result:
                return article_id, None
            else:
                return None, "Failed to save knowledge article"
                
        except Exception as e:
            logger.error(f"Error creating knowledge article: {str(e)}")
            return None, str(e)
    
    async def get_knowledge_articles(self, category: str = None, active_only: bool = True) -> List[Dict]:
        """Get knowledge base articles"""
        try:
            articles = await db_service.get_knowledge_articles(category, active_only)
            return articles
        except Exception as e:
            logger.error(f"Error getting knowledge articles: {str(e)}")
            return []
    
    async def get_knowledge_article_by_id(self, article_id: str) -> Optional[Dict]:
        """Get knowledge article by ID"""
        try:
            article = await db_service.get_knowledge_article_by_id(article_id)
            if article:
                # Update usage count
                await self._update_usage_count(article_id)
            return article
        except Exception as e:
            logger.error(f"Error getting knowledge article {article_id}: {str(e)}")
            return None
    
    async def update_knowledge_article(self, article_id: str, article_data: Dict) -> Tuple[bool, Optional[str]]:
        """Update a knowledge article"""
        try:
            # Validate article data
            validation_error = await self._validate_article_data(article_data)
            if validation_error:
                return False, validation_error
            
            # Update keywords if content changed
            if "content" in article_data and not article_data.get("keywords"):
                article_data["keywords"] = await self._extract_keywords(article_data["content"])
            
            # Regenerate embedding if content changed
            if "content" in article_data:
                article_data["embedding_vector"] = await self._generate_embedding(article_data["content"])
            
            # Update in database
            article_data["updated_at"] = datetime.utcnow()
            result = await db_service.update_knowledge_article(article_id, article_data)
            return bool(result), None
            
        except Exception as e:
            logger.error(f"Error updating knowledge article {article_id}: {str(e)}")
            return False, str(e)
    
    async def delete_knowledge_article(self, article_id: str) -> Tuple[bool, Optional[str]]:
        """Delete a knowledge article"""
        try:
            result = await db_service.delete_knowledge_article(article_id)
            return bool(result), None
        except Exception as e:
            logger.error(f"Error deleting knowledge article {article_id}: {str(e)}")
            return False, str(e)
    
    async def search_knowledge_articles(self, query: str, category: str = None, 
                                      limit: int = 10) -> List[Dict]:
        """Search knowledge articles by query"""
        try:
            # Simple text search for now - would use vector search in production
            articles = await db_service.search_knowledge_articles(query, category, limit)
            
            # Sort by relevance (placeholder scoring)
            for article in articles:
                article["relevance_score"] = await self._calculate_relevance_score(article, query)
            
            articles.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
            return articles
            
        except Exception as e:
            logger.error(f"Error searching knowledge articles: {str(e)}")
            return []
    
    async def get_relevant_knowledge_for_intent(self, intent_name: str, 
                                              context: str = "") -> List[Dict]:
        """Get relevant knowledge articles for a specific intent"""
        try:
            # Search by intent name and context
            search_query = f"{intent_name} {context}".strip()
            articles = await self.search_knowledge_articles(search_query, limit=5)
            
            # Filter and rank by relevance to intent
            relevant_articles = []
            for article in articles:
                if article.get("relevance_score", 0) > 0.3:  # Threshold for relevance
                    relevant_articles.append(article)
            
            return relevant_articles
            
        except Exception as e:
            logger.error(f"Error getting relevant knowledge for intent {intent_name}: {str(e)}")
            return []
    
    async def get_knowledge_for_personalization(self, prospect_data: Dict) -> List[Dict]:
        """Get knowledge articles for personalizing responses"""
        try:
            relevant_articles = []
            
            # Search by company industry
            if prospect_data.get("industry"):
                industry_articles = await self.search_knowledge_articles(
                    prospect_data["industry"], limit=3
                )
                relevant_articles.extend(industry_articles)
            
            # Search by company size
            if prospect_data.get("company_size"):
                size_articles = await self.search_knowledge_articles(
                    prospect_data["company_size"], limit=2
                )
                relevant_articles.extend(size_articles)
            
            # Search by job title
            if prospect_data.get("job_title"):
                role_articles = await self.search_knowledge_articles(
                    prospect_data["job_title"], limit=2
                )
                relevant_articles.extend(role_articles)
            
            # Remove duplicates and sort by relevance
            unique_articles = {}
            for article in relevant_articles:
                if article["id"] not in unique_articles:
                    unique_articles[article["id"]] = article
            
            return list(unique_articles.values())[:5]  # Return top 5
            
        except Exception as e:
            logger.error(f"Error getting knowledge for personalization: {str(e)}")
            return []
    
    async def get_knowledge_categories(self) -> List[str]:
        """Get all available knowledge categories"""
        return self.categories
    
    async def get_knowledge_statistics(self) -> Dict:
        """Get knowledge base statistics"""
        try:
            stats = await db_service.get_knowledge_statistics()
            return stats
        except Exception as e:
            logger.error(f"Error getting knowledge statistics: {str(e)}")
            return {}
    
    async def _validate_article_data(self, article_data: Dict) -> Optional[str]:
        """Validate knowledge article data"""
        required_fields = ["title", "content"]
        
        for field in required_fields:
            if field not in article_data or not article_data[field]:
                return f"Missing required field: {field}"
        
        # Validate category
        if article_data.get("category") and article_data["category"] not in self.categories:
            return f"Invalid category. Must be one of: {', '.join(self.categories)}"
        
        # Validate content length
        if len(article_data["content"]) < 10:
            return "Content is too short (minimum 10 characters)"
        
        return None
    
    async def _extract_keywords(self, content: str) -> List[str]:
        """Extract keywords from content"""
        try:
            # Simple keyword extraction - would use NLP in production
            words = content.lower().split()
            
            # Remove common stop words
            stop_words = {
                "the", "is", "at", "which", "on", "and", "a", "to", "are", "as", "was", "with",
                "for", "his", "her", "that", "of", "in", "it", "you", "i", "will", "be", "can",
                "have", "has", "had", "do", "does", "did", "would", "could", "should", "may",
                "might", "must", "shall", "will", "am", "is", "are", "was", "were", "being",
                "been", "have", "has", "had", "do", "does", "did", "get", "got", "make", "made"
            }
            
            # Filter and count words
            word_count = {}
            for word in words:
                word = word.strip(".,!?;:()[]{}\"'")
                if len(word) > 3 and word not in stop_words:
                    word_count[word] = word_count.get(word, 0) + 1
            
            # Get top keywords
            keywords = sorted(word_count.items(), key=lambda x: x[1], reverse=True)[:10]
            return [keyword[0] for keyword in keywords]
            
        except Exception as e:
            logger.error(f"Error extracting keywords: {str(e)}")
            return []
    
    async def _generate_embedding(self, content: str) -> List[float]:
        """Generate embedding vector for content"""
        try:
            # Placeholder for actual embedding generation
            # In production, this would use services like OpenAI embeddings, SentenceTransformers, etc.
            # For now, return a simple hash-based vector
            import hashlib
            
            hash_obj = hashlib.md5(content.encode())
            hash_hex = hash_obj.hexdigest()
            
            # Convert hash to float vector (simplified)
            vector = []
            for i in range(0, len(hash_hex), 2):
                vector.append(float(int(hash_hex[i:i+2], 16)) / 255.0)
            
            # Pad or truncate to 128 dimensions
            while len(vector) < 128:
                vector.append(0.0)
            
            return vector[:128]
            
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            return [0.0] * 128
    
    async def _calculate_relevance_score(self, article: Dict, query: str) -> float:
        """Calculate relevance score for an article"""
        try:
            score = 0.0
            query_lower = query.lower()
            
            # Title match
            if query_lower in article["title"].lower():
                score += 0.5
            
            # Content match
            content_lower = article["content"].lower()
            query_words = query_lower.split()
            word_matches = sum(1 for word in query_words if word in content_lower)
            score += (word_matches / len(query_words)) * 0.3
            
            # Keywords match
            keywords = article.get("keywords", [])
            keyword_matches = sum(1 for word in query_words if word in [kw.lower() for kw in keywords])
            if keywords:
                score += (keyword_matches / len(keywords)) * 0.2
            
            # Category bonus
            if article.get("category") and article["category"].lower() in query_lower:
                score += 0.1
            
            return min(score, 1.0)  # Cap at 1.0
            
        except Exception as e:
            logger.error(f"Error calculating relevance score: {str(e)}")
            return 0.0
    
    async def _update_usage_count(self, article_id: str):
        """Update usage count for an article"""
        try:
            await db_service.increment_knowledge_article_usage(article_id)
        except Exception as e:
            logger.error(f"Error updating usage count: {str(e)}")

# Create global knowledge base service instance
knowledge_base_service = KnowledgeBaseService()