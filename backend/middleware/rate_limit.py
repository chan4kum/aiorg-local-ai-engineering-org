import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.rate_limit_records = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # Simple token bucket or rate limit logic: max 100 req per minute
        if client_ip not in self.rate_limit_records:
            self.rate_limit_records[client_ip] = []
            
        # Clean old requests
        self.rate_limit_records[client_ip] = [t for t in self.rate_limit_records[client_ip] if current_time - t < 60]
        
        if len(self.rate_limit_records[client_ip]) >= 100:
            from fastapi.responses import JSONResponse
            return JSONResponse({"detail": "Too many requests"}, status_code=429)
            
        self.rate_limit_records[client_ip].append(current_time)
        return await call_next(request)
