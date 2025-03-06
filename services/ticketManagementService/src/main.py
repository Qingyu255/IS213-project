from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from .api.routes import router

app = FastAPI(
    title="Ticket Management Service",
    description="Service for managing event bookings and tickets",
    version="1.0.0"
)

app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    return RedirectResponse(url="/docs")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
