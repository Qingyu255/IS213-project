from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from .api.routes import bookings, tickets
import asyncio
import logging
from .core.rabbitmq import RabbitMQConsumer
from .services.booking_service import BookingService
from .core.database import get_db, engine
from sqlalchemy.ext.asyncio import AsyncSession
from .core.config import get_settings
from prometheus_client import make_asgi_app, Counter, Histogram
import time
from starlette.middleware.base import BaseHTTPMiddleware

# Configure logging to show debug messages
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

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
    title="Ticket Management Service",
    description="Service for managing event bookings and tickets",
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
    allow_origins=["http://localhost:3000"],  # Explicitly allow frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include router
app.include_router(bookings.router, prefix="/api/v1/mgmt")  # Bookings endpoints
app.include_router(tickets.router, prefix="/api/v1")  # Tickets endpoints

# Initialize services
booking_service = BookingService()
rabbitmq_consumer = RabbitMQConsumer()

@app.get("/")
async def root():
    return RedirectResponse(url="/docs")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize RabbitMQ consumer and register message handlers"""
    try:
        # Register message handlers
        async def handle_status_update(message: dict):
            async with AsyncSession(engine) as db:
                await booking_service.handle_booking_status_update(message, db)

        # Add handlers to consumer
        rabbitmq_consumer.add_handler("booking.status_updated", handle_status_update)
        rabbitmq_consumer.add_handler("booking.confirmed", handle_status_update)
        rabbitmq_consumer.add_handler("booking.cancelled", handle_status_update)
        rabbitmq_consumer.add_handler("booking.refunded", handle_status_update)

        # Start consuming in the background
        asyncio.create_task(rabbitmq_consumer.start_consuming())
        logger.info("RabbitMQ consumer started successfully")
    except Exception as e:
        logger.error(f"Error starting RabbitMQ consumer: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources"""
    await rabbitmq_consumer.close()
    logger.info("RabbitMQ connection closed")
