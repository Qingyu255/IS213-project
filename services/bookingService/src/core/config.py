from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Service URLs
    EVENT_SERVICE_URL: str
    TICKET_SERVICE_URL: str
    BILLING_SERVICE_URL: str
    LOGGING_SERVICE_URL: str
    FRONTEND_URL: str

    # RabbitMQ
    RABBITMQ_URL: str

    # AWS Cognito
    AWS_COGNITO_REGION: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_COGNITO_USER_POOL_ID: str
    AWS_COGNITO_APP_CLIENT_ID: str

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()
