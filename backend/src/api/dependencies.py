from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import os
from typing import Generator

# Mock database dependency - would use actual SQLAlchemy session in production
def get_database() -> Generator:
    """Get database session"""
    # This would return actual database session
    # For now, return a mock object
    class MockDB:
        def query(self, *args, **kwargs):
            return self
        
        def filter(self, *args, **kwargs):
            return self
        
        def all(self):
            return []
        
        def first(self):
            return None
    
    db = MockDB()
    try:
        yield db
    finally:
        # Close database connection
        pass

# Security dependencies
security = HTTPBearer(auto_error=False)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    if not credentials:
        return None  # Allow anonymous access for now
    
    # In production, validate JWT token here
    token = credentials.credentials
    
    # Mock user validation
    if token == "valid-token":
        return {"id": "user-123", "username": "admin", "role": "admin"}
    
    return None

async def require_auth(current_user = Depends(get_current_user)):
    """Require authentication"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user

async def require_admin(current_user = Depends(require_auth)):
    """Require admin role"""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

def get_settings():
    """Get application settings"""
    return {
        "database_url": os.getenv("DATABASE_URL", "postgresql://iot_user:iot_password@localhost:5432/iot_security"),
        "redis_url": os.getenv("REDIS_URL", "redis://localhost:6379"),
        "secret_key": os.getenv("SECRET_KEY", "your-secret-key-here"),
        "algorithm": "HS256",
        "access_token_expire_minutes": 30,
    }