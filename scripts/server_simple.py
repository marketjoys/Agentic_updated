from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="AI Email Responder", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoginRequest(BaseModel):
    username: str
    password: str

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.post("/api/auth/login")
async def login(request: LoginRequest):
    if request.username == "testuser" and request.password == "testpass123":
        return {"access_token": "test_token_12345", "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/api/auth/register")
async def register(request: LoginRequest):
    if request.username and request.password:
        return {"access_token": "test_token_12345", "token_type": "bearer"}
    raise HTTPException(status_code=400, detail="Registration failed")

@app.get("/api/auth/me")
async def get_me():
    return {
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "is_active": True,
        "created_at": datetime.utcnow()
    }

@app.get("/api/campaigns")
async def get_campaigns():
    return [{"id": "1", "name": "Test Campaign", "status": "draft", "prospect_count": 10, "max_emails": 1000, "created_at": datetime.utcnow()}]

@app.get("/api/email-providers")
async def get_email_providers():
    return [{"id": "1", "name": "Test Gmail Provider", "provider_type": "gmail", "email_address": "test@gmail.com", "is_active": True, "is_default": True, "daily_send_limit": 500, "hourly_send_limit": 50, "current_daily_count": 0, "current_hourly_count": 0}]

@app.get("/api/lists")
async def get_lists():
    return [{"id": "1", "name": "Tech Startups", "description": "Technology startup companies", "color": "#3B82F6", "prospect_count": 5, "tags": ["tech", "startup", "b2b"], "created_at": datetime.utcnow()}]

@app.get("/api/templates")
async def get_templates():
    return [{"id": "1", "name": "Welcome Email", "subject": "Welcome to Our Service, {{first_name}}!", "content": "Hello {{first_name}}, welcome to our service!", "type": "initial", "created_at": datetime.utcnow()}]

@app.get("/api/prospects")
async def get_prospects(skip: int = 0, limit: int = 100):
    return [{"id": "1", "email": "john.doe@techstartup.com", "first_name": "John", "last_name": "Doe", "company": "TechStartup Inc", "job_title": "CEO", "industry": "Technology", "status": "active", "created_at": datetime.utcnow()}]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)