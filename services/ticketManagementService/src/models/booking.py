from sqlalchemy import Column, String, UUID, DateTime, func
from sqlalchemy.orm import relationship

from .base import Base

class Booking(Base):
    __tablename__ = "bookings"

    booking_id = Column(UUID, primary_key=True, server_default=func.gen_random_uuid())
    user_id = Column(UUID, nullable=False)
    event_id = Column(UUID, nullable=False)
    status = Column(String, nullable=False, default="pending")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationship with tickets
    tickets = relationship("Ticket", back_populates="booking", cascade="all, delete-orphan", lazy="selectin") 