from fastapi import APIRouter, HTTPException
from app.models import KnowledgeBase
from app.services.knowledge_base_service import knowledge_base_service
from typing import List, Dict, Optional

router = APIRouter()

@router.post("/knowledge-base")
async def create_knowledge_article(article: KnowledgeBase):
    """Create a new knowledge base article"""
    article_dict = article.dict()
    article_id, error = await knowledge_base_service.create_knowledge_article(article_dict)
    
    if error:
        raise HTTPException(status_code=400, detail=error)
    
    return {"id": article_id, "message": "Knowledge article created successfully"}

@router.get("/knowledge-base")
async def get_knowledge_articles(category: Optional[str] = None, active_only: bool = True):
    """Get knowledge base articles"""
    articles = await knowledge_base_service.get_knowledge_articles(category, active_only)
    return articles

@router.get("/knowledge-base/{article_id}")
async def get_knowledge_article(article_id: str):
    """Get a specific knowledge article by ID"""
    article = await knowledge_base_service.get_knowledge_article_by_id(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Knowledge article not found")
    return article

@router.put("/knowledge-base/{article_id}")
async def update_knowledge_article(article_id: str, article_data: Dict):
    """Update a knowledge article"""
    success, error = await knowledge_base_service.update_knowledge_article(article_id, article_data)
    
    if error:
        raise HTTPException(status_code=400, detail=error)
    
    if not success:
        raise HTTPException(status_code=404, detail="Knowledge article not found")
    
    return {"message": "Knowledge article updated successfully"}

@router.delete("/knowledge-base/{article_id}")
async def delete_knowledge_article(article_id: str):
    """Delete a knowledge article"""
    success, error = await knowledge_base_service.delete_knowledge_article(article_id)
    
    if error:
        raise HTTPException(status_code=400, detail=error)
    
    if not success:
        raise HTTPException(status_code=404, detail="Knowledge article not found")
    
    return {"message": "Knowledge article deleted successfully"}

@router.get("/knowledge-base/search/{query}")
async def search_knowledge_articles(query: str, category: Optional[str] = None, limit: int = 10):
    """Search knowledge base articles"""
    articles = await knowledge_base_service.search_knowledge_articles(query, category, limit)
    return articles

@router.get("/knowledge-base/intent/{intent_name}/relevant")
async def get_relevant_knowledge_for_intent(intent_name: str, context: str = ""):
    """Get relevant knowledge articles for a specific intent"""
    articles = await knowledge_base_service.get_relevant_knowledge_for_intent(intent_name, context)
    return articles

@router.post("/knowledge-base/personalization/prospect")
async def get_knowledge_for_personalization(prospect_data: Dict):
    """Get knowledge articles for personalizing responses"""
    articles = await knowledge_base_service.get_knowledge_for_personalization(prospect_data)
    return articles

@router.get("/knowledge-base/categories/available")
async def get_knowledge_categories():
    """Get all available knowledge categories"""
    categories = await knowledge_base_service.get_knowledge_categories()
    return {"categories": categories}

@router.get("/knowledge-base/statistics/overview")
async def get_knowledge_statistics():
    """Get knowledge base statistics"""
    stats = await knowledge_base_service.get_knowledge_statistics()
    return stats

@router.post("/knowledge-base/bulk-import")
async def bulk_import_articles(articles_data: List[Dict]):
    """Bulk import knowledge articles"""
    results = {"successful": [], "failed": []}
    
    for article_data in articles_data:
        try:
            article_id, error = await knowledge_base_service.create_knowledge_article(article_data)
            if error:
                results["failed"].append({"data": article_data, "error": error})
            else:
                results["successful"].append(article_id)
        except Exception as e:
            results["failed"].append({"data": article_data, "error": str(e)})
    
    return {
        "message": f"Imported {len(results['successful'])} articles successfully, {len(results['failed'])} failed",
        "results": results
    }

@router.get("/knowledge-base/export/all")
async def export_all_articles():
    """Export all knowledge articles"""
    articles = await knowledge_base_service.get_knowledge_articles(active_only=False)
    return {"articles": articles, "count": len(articles)}

@router.post("/knowledge-base/{article_id}/test-relevance")
async def test_article_relevance(article_id: str, test_data: Dict):
    """Test relevance of an article for a given query"""
    article = await knowledge_base_service.get_knowledge_article_by_id(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Knowledge article not found")
    
    query = test_data.get("query", "")
    if not query:
        raise HTTPException(status_code=400, detail="Query is required")
    
    relevance_score = await knowledge_base_service._calculate_relevance_score(article, query)
    
    return {
        "article_id": article_id,
        "query": query,
        "relevance_score": relevance_score,
        "is_relevant": relevance_score > 0.3
    }