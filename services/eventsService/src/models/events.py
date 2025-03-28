import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, ForeignKey, Numeric, Integer, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base

# Events Table
class Event(Base):
    __tablename__ = "events"

    id = Column(UUID, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    start_date_time = Column(TIMESTAMP(timezone=True), nullable=False)
    end_date_time = Column(TIMESTAMP(timezone=True), nullable=True)
    image_url = Column(String)
    venue = Column(String)
    price = Column(Numeric(10, 2))
    capacity = Column(Integer)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    categories = relationship("Category", secondary="event_categories", back_populates="events")
    organizers = relationship("EventOrganizer", back_populates="event", cascade="all, delete-orphan", passive_deletes=True)