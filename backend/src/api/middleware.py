from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
import asyncio
from typing import Dict
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple rate limiting middleware"""
    
    def __init__(self, app, calls_per_minute: int = 60):
        super().__init__(app)
        self.calls_per_minute = calls_per_minute
        self.clients: Dict[str, list] = {}
    
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time.time()
        
        # Clean old entries
        if client_ip in self.clients:
            self.clients[client_ip] = [
                timestamp for timestamp in self.clients[client_ip]
                if current_time - timestamp < 60
            ]
        else:
            self.clients[client_ip] = []
        
        # Check rate limit
        if len(self.clients[client_ip]) >= self.calls_per_minute:
            return Response(
                content="Rate limit exceeded",
                status_code=429,
                headers={"Retry-After": "60"}
            )
        
        # Add current request
        self.clients[client_ip].append(current_time)
        
        response = await call_next(request)
        return response

class PrometheusMiddleware(BaseHTTPMiddleware):
    """Mock Prometheus metrics middleware"""
    
    def __init__(self, app):
        super().__init__(app)
        self.request_count = 0
        self.request_duration = []
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        duration = time.time() - start_time
        self.request_count += 1
        self.request_duration.append(duration)
        
        # Keep only last 1000 requests
        if len(self.request_duration) > 1000:
            self.request_duration = self.request_duration[-1000:]
        
        # Add metrics headers
        response.headers["X-Request-Count"] = str(self.request_count)
        response.headers["X-Request-Duration"] = f"{duration:.3f}"
        
        return response