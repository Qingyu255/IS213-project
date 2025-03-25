from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base

# Event-Organizers Many-to-Many Table
class EventOrganizer(Base):
    __tablename__ = "event_organizers"

    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id", ondelete="CASCADE"), primary_key=True)
    organizer_id = Column(UUID(as_uuid=True), primary_key=True)  # No FK constraint, assuming external reference
    organizer_username = Column(String, nullable=False)

    event = relationship("Event", back_populates="organizers")
