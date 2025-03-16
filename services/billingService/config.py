import os
from dotenv import load_dotenv

class Config:
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "sk_test_51R1MjVPuntYIWYQeOqiwForTAw17wLBDGuqkIKqpm7rwYNRJnDEDMdHPy3j8OH6jkXbWoVBdmXVFzK9EPpFWpTyv00fT96EAYk")
    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev")  # For Flask sessions, etc.
    DEBUG = os.getenv("DEBUG", True)