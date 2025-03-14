from sqlalchemy import Column, String, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base
from ..core.enums import BookingStatus
import uuid

class Booking(Base):
    __tablename__ = "bookings"

    booking_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    event_id = Column(UUID(as_uuid=True), nullable=False)
    status = Column(Enum(BookingStatus), nullable=False, default=BookingStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship with tickets
    tickets = relationship("Ticket", back_populates="booking", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "booking_id": self.booking_id,
            "user_id": self.user_id,
            "event_id": self.event_id,
            "status": self.status.value if self.status else None,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "tickets": [ticket.ticket_id for ticket in self.tickets]
        } 