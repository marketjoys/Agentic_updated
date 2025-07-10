from fastapi import APIRouter, HTTPException, File, UploadFile
from app.models import Prospect
from app.services.database import db_service
from app.utils.helpers import generate_id
import pandas as pd
import io

router = APIRouter()

@router.post("/prospects")
async def create_prospect(prospect: Prospect):
    """Create a new prospect with email duplication check"""
    prospect.id = generate_id()
    prospect_dict = prospect.dict()
    
    # Check for duplicate email
    result, error = await db_service.create_prospect(prospect_dict)
    if error:
        raise HTTPException(status_code=400, detail=error)
    
    prospect_dict.pop('_id', None)
    return prospect_dict

@router.get("/prospects")
async def get_prospects(skip: int = 0, limit: int = 100):
    """Get prospects with pagination"""
    prospects = await db_service.get_prospects(skip, limit)
    return prospects

@router.get("/prospects/{prospect_id}")
async def get_prospect(prospect_id: str):
    """Get a specific prospect by ID"""
    prospect = await db_service.get_prospect_by_id(prospect_id)
    if not prospect:
        raise HTTPException(status_code=404, detail="Prospect not found")
    return prospect

@router.post("/prospects/upload")
async def upload_prospects(file: UploadFile = File(...)):
    """Upload prospects from CSV file with email duplication handling"""
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be CSV format")
        
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))
        
        required_columns = ['email', 'first_name', 'last_name']
        if not all(col in df.columns for col in required_columns):
            raise HTTPException(status_code=400, detail=f"CSV must contain columns: {required_columns}")
        
        # Define optional columns
        optional_columns = [
            'company', 'phone', 'linkedin_url', 'company_domain', 'industry',
            'company_linkedin_url', 'job_title', 'location', 'company_size',
            'annual_revenue', 'lead_source'
        ]
        
        prospects = []
        for _, row in df.iterrows():
            # Build prospect data
            prospect_data = {
                "id": generate_id(),
                "email": row['email'],
                "first_name": row['first_name'],
                "last_name": row['last_name']
            }
            
            # Add optional fields
            for col in optional_columns:
                if col in df.columns:
                    prospect_data[col] = row.get(col, '')
            
            # Handle additional fields (any column not in standard fields)
            standard_fields = set(required_columns + optional_columns + ['id'])
            additional_fields = {}
            for col in df.columns:
                if col not in standard_fields:
                    additional_fields[col] = str(row.get(col, ''))
            
            if additional_fields:
                prospect_data['additional_fields'] = additional_fields
            
            prospect = Prospect(**prospect_data)
            prospects.append(prospect.dict())
        
        if prospects:
            successful_inserts, failed_inserts = await db_service.upload_prospects(prospects)
            
            # Prepare response message
            message = f"Successfully uploaded {len(successful_inserts)} prospects"
            if failed_inserts:
                message += f". {len(failed_inserts)} prospects failed (duplicates or errors)"
            
            return {
                "message": message,
                "successful_count": len(successful_inserts),
                "failed_count": len(failed_inserts),
                "failed_prospects": failed_inserts
            }
        else:
            return {"message": "No prospects to upload", "successful_count": 0, "failed_count": 0}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")