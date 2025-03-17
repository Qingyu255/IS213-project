import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, ForeignKey, Numeric, Integer, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base

# Event-Categories Many-to-Many Table
class EventCategory(Base):
    __tablename__ = "event_categories"

    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id", ondelete="CASCADE"), primary_key=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True)
