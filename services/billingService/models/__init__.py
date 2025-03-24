# Initialize the models package

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

Base = declarative_base(metadata=MetaData())

def get_db_url():
    """Get the database URL from environment or use a default"""
    return os.environ.get('DATABASE_URL', 'postgresql://billinglocaldbuser:billinglocaldbpassword@localhost:5437/billinglocaldb')

def create_db_engine():
    """Create and return a SQLAlchemy engine"""
    return create_engine(get_db_url())

def get_session():
    """Create and return a new session"""
    engine = create_db_engine()
    Session = sessionmaker(bind=engine)
    return Session()

# Create tables
def init_db():
    """Initialize the database by creating tables"""
    engine = create_db_engine()
    Base.metadata.create_all(engine) 