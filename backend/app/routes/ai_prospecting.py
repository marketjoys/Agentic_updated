# AI Prospecting API Routes
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging
from datetime import datetime
from app.services.database import db_service
from app.services.ai_prospecting_service import ai_prospecting_service
from app.utils.helpers import generate_id

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Request models
class AIProspectingRequest(BaseModel):
    query: str
    target_list: Optional[str] = None
    max_results: Optional[int] = 25

class ClarificationRequest(BaseModel):
    query: str
    target_list: Optional[str] = None
    clarifications: Dict[str, str]

class IndustryTag(BaseModel):
    industry: str
    tag_id: str
    description: Optional[str] = ""

class BulkIndustryTags(BaseModel):
    tags: List[IndustryTag]

# AI Prospecting endpoints
@router.post("/ai-prospecting/search")
async def ai_prospecting_search(request: AIProspectingRequest):
    """
    Main AI prospecting endpoint - processes natural language queries and finds prospects
    """
    try:
        logger.info(f"AI Prospecting request: {request.query}")
        
        # Process the AI prospecting request
        result = await ai_prospecting_service.complete_ai_prospecting(
            query=request.query,
            target_list=request.target_list,
            db_service=db_service
        )
        
        # Save search history
        if result.get('success'):
            search_data = {
                "id": generate_id(),
                "query": request.query,
                "target_list": request.target_list,
                "result": result,
                "created_at": datetime.utcnow()
            }
            await db_service.save_ai_search(search_data)
        
        return result
        
    except Exception as e:
        logger.error(f"Error in AI prospecting search: {e}")
        raise HTTPException(status_code=500, detail=f"AI prospecting search failed: {str(e)}")

@router.post("/ai-prospecting/clarify")
async def ai_prospecting_with_clarification(request: ClarificationRequest):
    """
    AI prospecting with user clarifications for missing parameters
    """
    try:
        logger.info(f"AI Prospecting clarification request: {request.clarifications}")
        
        # Combine original query with clarifications
        enhanced_query = f"{request.query}. Additional details: {'; '.join([f'{k}: {v}' for k, v in request.clarifications.items()])}"
        
        # Process the enhanced query
        result = await ai_prospecting_service.complete_ai_prospecting(
            query=enhanced_query,
            target_list=request.target_list,
            db_service=db_service
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error in AI prospecting clarification: {e}")
        raise HTTPException(status_code=500, detail=f"AI prospecting clarification failed: {str(e)}")

@router.get("/ai-prospecting/search-history")
async def get_ai_prospecting_history(limit: int = 20):
    """
    Get AI prospecting search history
    """
    try:
        searches = await db_service.get_ai_search_history(limit=limit)
        return {
            "success": True,
            "searches": searches,
            "count": len(searches)
        }
        
    except Exception as e:
        logger.error(f"Error getting AI prospecting history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get search history: {str(e)}")

@router.get("/ai-prospecting/search-history/{search_id}")
async def get_ai_prospecting_search_details(search_id: str):
    """
    Get specific AI prospecting search details
    """
    try:
        search = await db_service.get_ai_search_by_id(search_id)
        if not search:
            raise HTTPException(status_code=404, detail="Search not found")
        
        return {
            "success": True,
            "search": search
        }
        
    except Exception as e:
        logger.error(f"Error getting AI prospecting search details: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get search details: {str(e)}")

# Industry Tags management endpoints
@router.get("/ai-prospecting/industry-tags")
async def get_industry_tags():
    """
    Get all industry tags for AI prospecting
    """
    try:
        tags = await db_service.get_industry_tags()
        return {
            "success": True,
            "tags": tags,
            "count": len(tags)
        }
        
    except Exception as e:
        logger.error(f"Error getting industry tags: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get industry tags: {str(e)}")

@router.post("/ai-prospecting/industry-tags")
async def create_industry_tag(tag: IndustryTag):
    """
    Create a new industry tag
    """
    try:
        # Check if tag already exists
        existing_tag = await db_service.get_industry_tag_by_name(tag.industry)
        if existing_tag:
            raise HTTPException(status_code=400, detail=f"Industry tag '{tag.industry}' already exists")
        
        tag_data = {
            "id": generate_id(),
            "industry": tag.industry,
            "tag_id": tag.tag_id,
            "description": tag.description,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await db_service.create_industry_tag(tag_data)
        
        return {
            "success": True,
            "message": "Industry tag created successfully",
            "tag": tag_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating industry tag: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create industry tag: {str(e)}")

@router.post("/ai-prospecting/industry-tags/bulk")
async def create_bulk_industry_tags(request: BulkIndustryTags):
    """
    Create multiple industry tags in bulk
    """
    try:
        tags_data = []
        for tag in request.tags:
            tag_data = {
                "id": generate_id(),
                "industry": tag.industry,
                "tag_id": tag.tag_id,
                "description": tag.description,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            tags_data.append(tag_data)
        
        result = await db_service.bulk_insert_industry_tags(tags_data)
        
        return {
            "success": True,
            "message": f"Successfully created {len(tags_data)} industry tags",
            "inserted_count": len(tags_data),
            "tags": tags_data
        }
        
    except Exception as e:
        logger.error(f"Error creating bulk industry tags: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create bulk industry tags: {str(e)}")

@router.put("/ai-prospecting/industry-tags/{tag_id}")
async def update_industry_tag(tag_id: str, tag: IndustryTag):
    """
    Update an industry tag
    """
    try:
        tag_data = {
            "industry": tag.industry,
            "tag_id": tag.tag_id,
            "description": tag.description,
            "updated_at": datetime.utcnow()
        }
        
        result = await db_service.update_industry_tag(tag_id, tag_data)
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Industry tag not found")
        
        return {
            "success": True,
            "message": "Industry tag updated successfully",
            "tag_id": tag_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating industry tag: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update industry tag: {str(e)}")

@router.delete("/ai-prospecting/industry-tags/{tag_id}")
async def delete_industry_tag(tag_id: str):
    """
    Delete an industry tag
    """
    try:
        result = await db_service.delete_industry_tag(tag_id)
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Industry tag not found")
        
        return {
            "success": True,
            "message": "Industry tag deleted successfully",
            "tag_id": tag_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting industry tag: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete industry tag: {str(e)}")

# Analytics endpoints
@router.get("/ai-prospecting/analytics")
async def get_ai_prospecting_analytics():
    """
    Get AI prospecting analytics and statistics
    """
    try:
        # Get search history for analytics
        searches = await db_service.get_ai_search_history(limit=100)
        
        # Calculate analytics
        total_searches = len(searches)
        successful_searches = len([s for s in searches if s.get('result', {}).get('success', False)])
        total_prospects_found = sum([s.get('result', {}).get('prospects_count', 0) for s in searches])
        
        # Get most used queries/industries
        queries = [s.get('query', '') for s in searches]
        target_lists = [s.get('target_list', '') for s in searches if s.get('target_list')]
        
        analytics = {
            "total_searches": total_searches,
            "successful_searches": successful_searches,
            "success_rate": (successful_searches / total_searches * 100) if total_searches > 0 else 0,
            "total_prospects_found": total_prospects_found,
            "average_prospects_per_search": (total_prospects_found / successful_searches) if successful_searches > 0 else 0,
            "most_used_target_lists": list(set(target_lists))[:10],
            "recent_searches": searches[:10]
        }
        
        return {
            "success": True,
            "analytics": analytics
        }
        
    except Exception as e:
        logger.error(f"Error getting AI prospecting analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

# Test endpoints
@router.post("/ai-prospecting/test-groq")
async def test_groq_connection():
    """
    Test Groq API connection and functionality
    """
    try:
        test_query = "Find me CEOs and founders in technology companies in California"
        
        result = await ai_prospecting_service.process_natural_language_query(test_query)
        
        return {
            "success": True,
            "message": "Groq API connection successful",
            "test_result": result
        }
        
    except Exception as e:
        logger.error(f"Error testing Groq connection: {e}")
        raise HTTPException(status_code=500, detail=f"Groq API test failed: {str(e)}")

@router.post("/ai-prospecting/test-apollo")
async def test_apollo_connection():
    """
    Test Apollo.io API connection
    """
    try:
        # Test with a simple search URL
        test_url = "https://app.apollo.io/#/people?sortAscending=false&sortByField=recommendations_score&personTitles[]=CEO&contactEmailStatusV2[]=verified&page=1"
        
        result = await ai_prospecting_service.search_apollo_prospects(test_url, page=1)
        
        return {
            "success": result['success'],
            "message": "Apollo.io API test completed",
            "test_result": {
                "status": result['success'],
                "data_available": bool(result.get('data')),
                "error": result.get('error')
            }
        }
        
    except Exception as e:
        logger.error(f"Error testing Apollo connection: {e}")
        raise HTTPException(status_code=500, detail=f"Apollo.io API test failed: {str(e)}")

# Initialize default industry tags
@router.post("/ai-prospecting/initialize-default-tags")
async def initialize_default_industry_tags():
    """
    Initialize default industry tags from common Apollo.io industries
    """
    try:
        default_tags = [
            {"industry": "Accounting", "tag_id": "5567ce1f7369643b78570000", "description": "Accounting and financial services"},
            {"industry": "Agriculture", "tag_id": "55718f947369642142b84a12", "description": "Agriculture and farming"},
            {"industry": "Airlines/Aviation", "tag_id": "5567e0bf7369641d115f0200", "description": "Airlines and aviation industry"},
            {"industry": "Technology", "tag_id": "5567ce1f7369643b78570001", "description": "Technology and software companies"},
            {"industry": "Healthcare", "tag_id": "55718f947369642142b84a13", "description": "Healthcare and medical services"},
            {"industry": "Finance", "tag_id": "5567e0bf7369641d115f0201", "description": "Financial services and banking"},
            {"industry": "Manufacturing", "tag_id": "5567ce1f7369643b78570002", "description": "Manufacturing and industrial"},
            {"industry": "Education", "tag_id": "55718f947369642142b84a14", "description": "Education and training"},
            {"industry": "Retail", "tag_id": "5567e0bf7369641d115f0202", "description": "Retail and e-commerce"},
            {"industry": "Construction", "tag_id": "5567ce1f7369643b78570003", "description": "Construction and engineering"},
            {"industry": "Real Estate", "tag_id": "55718f947369642142b84a15", "description": "Real estate and property"},
            {"industry": "Marketing", "tag_id": "5567e0bf7369641d115f0203", "description": "Marketing and advertising"},
            {"industry": "Consulting", "tag_id": "5567ce1f7369643b78570004", "description": "Consulting services"},
            {"industry": "Software", "tag_id": "55718f947369642142b84a16", "description": "Software development and tech"},
            {"industry": "Insurance", "tag_id": "5567e0bf7369641d115f0204", "description": "Insurance services"}
        ]
        
        # Check existing tags first
        existing_tags = await db_service.get_industry_tags()
        existing_industries = {tag['industry'].lower() for tag in existing_tags}
        
        # Filter out existing tags
        new_tags = []
        for tag in default_tags:
            if tag['industry'].lower() not in existing_industries:
                tag_data = {
                    "id": generate_id(),
                    "industry": tag['industry'],
                    "tag_id": tag['tag_id'],
                    "description": tag['description'],
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                new_tags.append(tag_data)
        
        if new_tags:
            await db_service.bulk_insert_industry_tags(new_tags)
        
        return {
            "success": True,
            "message": f"Initialized {len(new_tags)} default industry tags",
            "new_tags_count": len(new_tags),
            "existing_tags_count": len(existing_tags),
            "new_tags": new_tags
        }
        
    except Exception as e:
        logger.error(f"Error initializing default industry tags: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to initialize default tags: {str(e)}")