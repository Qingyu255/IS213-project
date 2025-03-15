import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, ForeignKey, Numeric, Integer, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base

# Categories Table
class Category(Base):
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)

    events = relationship("Event", secondary="event_categories", back_populates="categories")