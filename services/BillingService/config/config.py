import os

class Config:
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "sk_test_51R1MjVPuntYIWYQeOqiwForTAw17wLBDGuqkIKqpm7rwYNRJnDEDMdHPy3j8OH6jkXbWoVBdmXVFzK9EPpFWpTyv00fT96EAYk")
    DEBUG = os.getenv("DEBUG", True)