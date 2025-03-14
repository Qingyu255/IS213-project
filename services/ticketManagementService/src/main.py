from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from .api.routes import bookings, tickets
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Ticket Management Service",
    description="Service for managing event bookings and tickets",
    version="1.0.0"
)

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
app.include_router(bookings.router, prefix="/api/v1")  # Bookings endpoints
app.include_router(tickets.router, prefix="/api/v1")  # Tickets endpoints

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
