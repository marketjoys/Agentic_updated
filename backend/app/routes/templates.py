from fastapi import APIRouter, HTTPException
from app.models import Template
from app.services.database import db_service
from app.utils.helpers import generate_id

router = APIRouter()

@router.post("/templates")
async def create_template(template: Template):
    """Create a new template"""
    template.id = generate_id()
    template_dict = template.dict()
    result = await db_service.create_template(template_dict)
    template_dict.pop('_id', None)
    return template_dict

@router.get("/templates")
async def get_templates():
    """Get all templates"""
    templates = await db_service.get_templates()
    return templates

@router.get("/templates/{template_id}")
async def get_template(template_id: str):
    """Get a specific template by ID"""
    template = await db_service.get_template_by_id(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@router.put("/templates/{template_id}")
async def update_template(template_id: str, template: Template):
    """Update a template"""
    template_dict = template.dict()
    template_dict.pop('id', None)
    result = await db_service.update_template(template_id, template_dict)
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"message": "Template updated successfully"}