import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class Config:
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key")  # For Flask sessions, etc.
    DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    # Add service URLs for communication with other microservices
    EVENT_SERVICE_URL = os.getenv("EVENT_SERVICE_URL", "http://event-service:5000")
    USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user-service:5000")