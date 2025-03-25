import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class Config:
    """Configuration settings for the Billing Service"""
    # Stripe Configuration
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
    
    # Service URLs for microservice communication
    EVENT_SERVICE_URL = os.getenv("EVENT_SERVICE_URL", "http://event-service:5000")
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

    # Validate required configuration
    if not STRIPE_SECRET_KEY:
        raise ValueError("STRIPE_SECRET_KEY must be set")
    if not STRIPE_WEBHOOK_SECRET:
        raise ValueError("STRIPE_WEBHOOK_SECRET must be set")