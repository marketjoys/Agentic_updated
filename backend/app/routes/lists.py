from fastapi import APIRouter, HTTPException
from app.models import ProspectList
from app.services.database import db_service
from app.utils.helpers import generate_id
from typing import List
from datetime import datetime

router = APIRouter()

@router.post("/lists")
async def create_list(prospect_list: ProspectList):
    """Create a new prospect list"""
    prospect_list.id = generate_id()
    list_dict = prospect_list.dict()
    result = await db_service.create_list(list_dict)
    list_dict.pop('_id', None)
    return list_dict

@router.get("/lists")
async def get_lists():
    """Get all prospect lists with prospect counts"""
    lists = await db_service.get_lists()
    return lists

@router.get("/lists/{list_id}")
async def get_list(list_id: str):
    """Get a specific list by ID"""
    list_item = await db_service.get_list_by_id(list_id)
    if not list_item:
        raise HTTPException(status_code=404, detail="List not found")
    return list_item

@router.put("/lists/{list_id}")
async def update_list(list_id: str, prospect_list: ProspectList):
    """Update a prospect list"""
    list_dict = prospect_list.dict()
    list_dict.pop('id', None)
    list_dict["updated_at"] = datetime.utcnow()
    result = await db_service.update_list(list_id, list_dict)
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="List not found")
    return {"message": "List updated successfully"}

@router.delete("/lists/{list_id}")
async def delete_list(list_id: str):
    """Delete a prospect list"""
    result = await db_service.delete_list(list_id)
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="List not found")
    return {"message": "List deleted successfully"}

@router.post("/lists/{list_id}/prospects")
async def add_prospect_to_list(list_id: str, prospect_ids: List[str]):
    """Add prospects to a list"""
    # Verify list exists
    list_item = await db_service.get_list_by_id(list_id)
    if not list_item:
        raise HTTPException(status_code=404, detail="List not found")
    
    # Add list_id to prospects
    result = await db_service.add_prospects_to_list(list_id, prospect_ids)
    
    return {"message": f"Added {result.modified_count} prospects to list"}

@router.delete("/lists/{list_id}/prospects")
async def remove_prospect_from_list(list_id: str, prospect_ids: List[str]):
    """Remove prospects from a list"""
    result = await db_service.remove_prospects_from_list(list_id, prospect_ids)
    
    return {"message": f"Removed {result.modified_count} prospects from list"}