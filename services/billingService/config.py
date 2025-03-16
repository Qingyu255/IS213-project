import os
from dotenv import load_dotenv
load_dotenv('/Users/leozhengkai/Documents/GitHub/IS213-project/.env')

class Config:
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev")  # For Flask sessions, etc.
    DEBUG = os.getenv("DEBUG", True)