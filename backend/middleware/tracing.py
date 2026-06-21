from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
import time

class TracingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response

def setup_tracing(app: FastAPI):
    # In a real app, this would setup OpenTelemetry
    app.add_middleware(TracingMiddleware)
