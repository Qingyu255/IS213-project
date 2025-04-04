from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from .api.endpoints.booking import router as booking_router
import asyncio
import logging
from prometheus_client import make_asgi_app, Counter, Histogram
import time
from starlette.middleware.base import BaseHTTPMiddleware

# Configure logging
logging.basicConfig(level=logging.DEBUG)
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

# Create FastAPI app
app = FastAPI(
    title="Booking Service",
    description="Composite Service for managing event bookings and tickets",
    version="1.0.0"
)

# Add Prometheus middleware
app.add_middleware(PrometheusMiddleware)

# Create metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600  # Cache preflight requests for 1 hour
)

# Include router
app.include_router(booking_router, prefix="/api/v1")  # Bookings endpoints

@app.get("/")
async def root():
    return RedirectResponse(url="/docs")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    logger.info("Starting up the application")
    # Set the event loop policy for Windows if needed
    if asyncio.get_event_loop_policy()._loop_factory is not asyncio.SelectorEventLoop:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down the application")
