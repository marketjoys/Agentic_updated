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
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Simple test auth endpoint
@app.post("/api/auth/login")
async def login(request: LoginRequest):
    # Simple test auth - accept any credentials for demo
    if request.username and request.password:
        return {
            "access_token": "test_token_12345",
            "token_type": "bearer"
        }
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/api/auth/register")
async def register(request: LoginRequest):
    # Simple test registration - accept any credentials for demo
    if request.username and request.password:
        return {
            "access_token": "test_token_12345",
            "token_type": "bearer"
        }
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)