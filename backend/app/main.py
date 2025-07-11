from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(title="AI Email Responder", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple models for testing
class LoginRequest(BaseModel):
    username: str
    password: str

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow(), "message": "AI Email Responder is running"}

# Simple test auth endpoint (fallback)
@app.post("/api/auth/login")
async def login_simple(request: LoginRequest):
    # Accept test credentials
    if request.username == "testuser" and request.password == "testpass123":
        return {
            "access_token": "test_token_12345",
            "token_type": "bearer"
        }
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/api/auth/register")
async def register_simple(request: LoginRequest):
    # Simple test registration - accept any credentials for demo
    if request.username and request.password:
        return {
            "access_token": "test_token_12345",
            "token_type": "bearer"
        }
    raise HTTPException(status_code=400, detail="Registration failed")

@app.get("/api/auth/me")
async def get_me_simple():
    return {
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "is_active": True,
        "created_at": datetime.utcnow()
    }

# Test endpoint for checking API functionality
@app.get("/api/test")
async def test_endpoint():
    return {"message": "API is working correctly", "timestamp": datetime.utcnow()}

# Mock data endpoints for testing
@app.get("/api/campaigns")
async def get_campaigns():
    return [
        {
            "id": "1",
            "name": "Test Campaign",
            "status": "draft",
            "prospect_count": 10,
            "max_emails": 1000,
            "created_at": datetime.utcnow(),
            "schedule": None
        }
    ]

@app.get("/api/email-providers")
async def get_email_providers():
    return [
        {
            "id": "1",
            "name": "Test Gmail Provider",
            "provider_type": "gmail",
            "email_address": "test@gmail.com",
            "is_active": True,
            "is_default": True,
            "daily_send_limit": 500,
            "hourly_send_limit": 50,
            "current_daily_count": 0,
            "current_hourly_count": 0,
            "last_sync": datetime.utcnow()
        }
    ]

@app.get("/api/lists")
async def get_lists():
    return [
        {
            "id": "1",
            "name": "Tech Startups",
            "description": "Technology startup companies",
            "color": "#3B82F6",
            "prospect_count": 5,
            "tags": ["tech", "startup", "b2b"],
            "created_at": datetime.utcnow()
        }
    ]

@app.get("/api/templates")
async def get_templates():
    return [
        {
            "id": "1",
            "name": "Welcome Email",
            "subject": "Welcome to Our Service, {{first_name}}!",
            "content": "Hello {{first_name}}, welcome to our service!",
            "type": "initial",
            "created_at": datetime.utcnow()
        }
    ]

@app.get("/api/prospects")
async def get_prospects(skip: int = 0, limit: int = 100):
    return [
        {
            "id": "1",
            "email": "john.doe@techstartup.com",
            "first_name": "John",
            "last_name": "Doe",
            "company": "TechStartup Inc",
            "job_title": "CEO",
            "industry": "Technology",
            "status": "active",
            "created_at": datetime.utcnow()
        }
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)