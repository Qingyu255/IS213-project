from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Service URLs
    EVENT_SERVICE_URL: str
    TICKET_SERVICE_URL: str
    BILLING_SERVICE_URL: str
    NOTIFICATION_SERVICE_URL: str
    LOGGING_SERVICE_URL: str

    # RabbitMQ Configuration
    RABBITMQ_HOST: str
    RABBITMQ_QUEUE: str
    RABBITMQ_USER: str
    RABBITMQ_PASS: str

    # Constructed RabbitMQ URL (will be built in __init__)
    RABBITMQ_URL: str = ""

    # AWS Configuration
    AWS_REGION: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_COGNITO_USER_POOL_ID: str
    AWS_COGNITO_APP_CLIENT_ID: str

    # Stripe Configuration
    STRIPE_SECRET_KEY: str
    STRIPE_WEBHOOK_SECRET: str
    NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY: str

    # Frontend Configuration
    FRONTEND_URL: str

    # JWT Configuration
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # Database Configuration
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_PORT: int

    class Config:
        env_file = ".env"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Construct RabbitMQ URL after loading environment variables
        self.RABBITMQ_URL = f"amqp://{self.RABBITMQ_USER}:{self.RABBITMQ_PASS}@{self.RABBITMQ_HOST}:5672/"

@lru_cache()
def get_settings():
    return Settings()
