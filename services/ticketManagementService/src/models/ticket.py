from sqlalchemy import Column, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base
import uuid

class Ticket(Base):
    __tablename__ = "tickets"

    ticket_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.booking_id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship with booking
    booking = relationship("Booking", back_populates="tickets")

    def to_dict(self):
        return {
            "ticket_id": self.ticket_id,
            "booking_id": self.booking_id,
            "created_at": self.created_at
        }
