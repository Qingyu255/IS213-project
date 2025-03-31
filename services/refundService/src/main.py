from fastapi import FastAPI
from src.api.routes.refund_service import router as refund_router
from prometheus_client import make_asgi_app, Counter, Histogram
import time
import os
import logging
from starlette.middleware.base import BaseHTTPMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total', 
    'Total HTTP Requests Count', 
    ['method', 'endpoint', 'status_code']
)
REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds', 
    'HTTP Request Latency', 
    ['method', 'endpoint']
)

# Create middleware for metrics collection
class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time.time()
        
        # Process the request
        response = await call_next(request)
        
        # Record metrics
        duration = time.time() - start_time
        REQUEST_LATENCY.labels(
            method=request.method, 
            endpoint=request.url.path
        ).observe(duration)
        
        REQUEST_COUNT.labels(
            method=request.method, 
            endpoint=request.url.path,
            status_code=response.status_code
        ).inc()
        
        return response

app = FastAPI(
    title="Refund Composite Service API",
    description="A composite service that processes refund requests, logs events, and interacts with Billing and Logging services.",
    version="1.0.0"
)

# Add Prometheus middleware
app.add_middleware(PrometheusMiddleware)

# Create metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Include the refund service router under the '/api' prefix
app.include_router(refund_router, prefix="/api")

# Define a simple root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the Refund Composite Service API"}

# Add health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}


