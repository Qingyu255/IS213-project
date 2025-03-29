from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from .config import get_settings

settings = get_settings()

# Create async engine with proper pooling parameters
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True
)

# Create async session factory
SessionLocal = sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession
)

async def get_db():
    """Dependency for getting async DB session"""
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
