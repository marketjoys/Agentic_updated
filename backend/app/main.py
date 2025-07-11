from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import logging
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

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

# Try to import and register routes
try:
    # Import route modules
    from app.routes.campaigns import router as campaigns_router
    from app.routes.email_providers import router as email_providers_router
    from app.routes.lists import router as lists_router
    from app.routes.prospects import router as prospects_router
    from app.routes.templates import router as templates_router
    from app.routes.intents import router as intents_router
    from app.routes.analytics import router as analytics_router
    
    # Register route modules
    app.include_router(campaigns_router, prefix="/api", tags=["campaigns"])
    app.include_router(email_providers_router, prefix="/api", tags=["email_providers"])
    app.include_router(lists_router, prefix="/api", tags=["lists"])
    app.include_router(prospects_router, prefix="/api", tags=["prospects"])
    app.include_router(templates_router, prefix="/api", tags=["templates"])
    app.include_router(intents_router, prefix="/api", tags=["intents"])
    app.include_router(analytics_router, prefix="/api", tags=["analytics"])
    
    print("✅ All routes registered successfully")
except Exception as e:
    print(f"⚠️  Warning: Could not register all routes: {e}")
    # Continue with basic functionality

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)