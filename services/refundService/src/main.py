from fastapi import FastAPI
from src.api.routes.refund_service import router as refund_router

app = FastAPI(
    title="Refund Composite Service API",
    description="A composite service that processes refund requests, logs events, and interacts with Billing and Logging services.",
    version="1.0.0"
)

# Include the refund service router under the '/api' prefix
app.include_router(refund_router, prefix="/api")

# Define a simple root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the Refund Composite Service API"}


