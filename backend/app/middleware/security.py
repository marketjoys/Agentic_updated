from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from typing import Optional
import time
import logging
from collections import defaultdict
import json
import os
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import redis
from dotenv import load_dotenv

load_dotenv()

# Security configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Bearer token authentication
security = HTTPBearer()

# Redis connection for caching and rate limiting
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    redis_client.ping()
except Exception as e:
    logging.warning(f"Redis connection failed: {e}")
    redis_client = None

# Rate limiting configuration
RATE_LIMITS = {
    "default": {"requests": 100, "window": 60},  # 100 requests per minute
    "auth": {"requests": 10, "window": 60},      # 10 auth attempts per minute
    "api": {"requests": 1000, "window": 60},     # 1000 API calls per minute
}

# In-memory rate limiting fallback
rate_limit_storage = defaultdict(lambda: defaultdict(list))

class SecurityMiddleware(BaseHTTPMiddleware):
    """Security middleware for headers and basic protection"""
    
    async def dispatch(self, request: Request, call_next):
        # Record start time
        start_time = time.time()
        
        # Call the next middleware/endpoint
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Add processing time header
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware"""
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host
        
        # Determine rate limit type based on path
        path = request.url.path
        if path.startswith("/auth"):
            limit_type = "auth"
        elif path.startswith("/api"):
            limit_type = "api"
        else:
            limit_type = "default"
        
        # Check rate limit
        if not await self._check_rate_limit(client_ip, limit_type):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )
        
        response = await call_next(request)
        return response
    
    async def _check_rate_limit(self, client_ip: str, limit_type: str) -> bool:
        """Check if request is within rate limit"""
        limit_config = RATE_LIMITS[limit_type]
        window = limit_config["window"]
        max_requests = limit_config["requests"]
        
        current_time = time.time()
        window_start = current_time - window
        
        if redis_client:
            # Use Redis for rate limiting
            key = f"rate_limit:{client_ip}:{limit_type}"
            
            # Add current request
            redis_client.zadd(key, {str(current_time): current_time})
            
            # Remove old entries
            redis_client.zremrangebyscore(key, 0, window_start)
            
            # Set expiration
            redis_client.expire(key, window)
            
            # Count requests in window
            request_count = redis_client.zcard(key)
            
            return request_count <= max_requests
        else:
            # Fallback to in-memory storage
            requests = rate_limit_storage[client_ip][limit_type]
            
            # Remove old requests
            requests[:] = [req_time for req_time in requests if req_time > window_start]
            
            # Add current request
            requests.append(current_time)
            
            return len(requests) <= max_requests

# Authentication utilities
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    return {"username": username}

# Caching utilities
class CacheService:
    """Cache service for performance optimization"""
    
    def __init__(self):
        self.redis_client = redis_client
        self.default_ttl = 300  # 5 minutes
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from cache"""
        if not self.redis_client:
            return None
        
        try:
            return self.redis_client.get(key)
        except Exception as e:
            logging.error(f"Cache get error: {e}")
            return None
    
    async def set(self, key: str, value: str, ttl: int = None) -> bool:
        """Set value in cache"""
        if not self.redis_client:
            return False
        
        try:
            return self.redis_client.setex(key, ttl or self.default_ttl, value)
        except Exception as e:
            logging.error(f"Cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        if not self.redis_client:
            return False
        
        try:
            return self.redis_client.delete(key) > 0
        except Exception as e:
            logging.error(f"Cache delete error: {e}")
            return False
    
    async def get_json(self, key: str) -> Optional[dict]:
        """Get JSON value from cache"""
        value = await self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return None
        return None
    
    async def set_json(self, key: str, value: dict, ttl: int = None) -> bool:
        """Set JSON value in cache"""
        try:
            return await self.set(key, json.dumps(value), ttl)
        except Exception as e:
            logging.error(f"Cache set JSON error: {e}")
            return False

# Global cache instance
cache_service = CacheService()

# Dependency for optional authentication
async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Get current user from JWT token (optional)"""
    if not credentials:
        return None
    
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return {"username": username}
    except JWTError:
        return None

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Performance monitoring
class PerformanceMonitor:
    """Monitor API performance"""
    
    def __init__(self):
        self.metrics = defaultdict(list)
    
    def record_request(self, endpoint: str, duration: float, status_code: int):
        """Record request metrics"""
        self.metrics[endpoint].append({
            "duration": duration,
            "status_code": status_code,
            "timestamp": time.time()
        })
        
        # Keep only last 1000 requests per endpoint
        if len(self.metrics[endpoint]) > 1000:
            self.metrics[endpoint] = self.metrics[endpoint][-1000:]
    
    def get_metrics(self, endpoint: str = None) -> dict:
        """Get performance metrics"""
        if endpoint:
            return self.metrics.get(endpoint, [])
        return dict(self.metrics)

# Global performance monitor
performance_monitor = PerformanceMonitor()