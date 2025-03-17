from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, TypeDecorator
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base
from ..core.enums import BookingStatus
import uuid

class BookingStatusType(TypeDecorator):
    """Custom type to handle case conversion for BookingStatus"""
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, BookingStatus):
            return value.value
        return str(value).upper()

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        try:
            return BookingStatus(str(value).upper())
        except ValueError:
            return None

class Booking(Base):
    __tablename__ = "bookings"

    booking_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    event_id = Column(UUID(as_uuid=True), nullable=False)
    status = Column(BookingStatusType, nullable=False, default=BookingStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship with tickets
    tickets = relationship("Ticket", back_populates="booking", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "booking_id": str(self.booking_id),
            "user_id": str(self.user_id),
            "event_id": str(self.event_id),
            "status": self.status.value if self.status else None,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "tickets": [str(ticket.ticket_id) for ticket in self.tickets]
        } 