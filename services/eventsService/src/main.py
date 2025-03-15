from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes.events import router as api_router
from src.db.connection import engine
from src.models.base import Base
import asyncio

# Create FastAPI app
app = FastAPI(
    title="Event Management Service",
    description="A FastAPI backend for managing events, venues, schedules, organizers, and attendees.",
    version="1.0.0"
)

# 🌍 Configure CORS for Frontend Access
origins = [
    "http://localhost:3000",  # React frontend
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Restrict to known frontend origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE)
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"]   # Expose headers for frontend use
)

# 🔄 Initialize Database on Startup
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("startup")
async def startup():
    asyncio.create_task(init_db())

# 🚀 Include Event Routes
app.include_router(api_router, prefix="/api/v1")  # All API endpoints under /api/v1

# 🔀 Redirect Root to API Docs
@app.get("/")
async def root():
    return RedirectResponse(url="/docs")

# ✅ Health Check Endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
