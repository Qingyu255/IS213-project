import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from functools import lru_cache

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"postgresql+asyncpg://{os.getenv('TICKET_DB_USER')}:{os.getenv('TICKET_DB_PASSWORD')}@ticket-db:5432/{os.getenv('TICKET_DB')}")
    POSTGRES_DB: str = os.getenv("TICKET_DB", "ticketlocaldb")
    POSTGRES_USER: str = os.getenv("TICKET_DB_USER", "ticketlocaldbuser")
    POSTGRES_PASSWORD: str = os.getenv("TICKET_DB_PASSWORD", "ticketlocaldbpassword")
    RABBITMQ_URL: str = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
    RABBITMQ_QUEUE: str = os.getenv("RABBITMQ_QUEUE", "logs_queue")

@lru_cache()
def get_settings():
    return Settings()
