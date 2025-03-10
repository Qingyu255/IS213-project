from sqlalchemy import Column, String, UUID, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base

class Ticket(Base):
    __tablename__ = "tickets"

    ticket_id = Column(UUID, primary_key=True, server_default=func.gen_random_uuid())
    booking_id = Column(UUID, ForeignKey("bookings.booking_id", ondelete="CASCADE"), nullable=False)
    
    # Relationship with booking
    booking = relationship("Booking", back_populates="tickets")
