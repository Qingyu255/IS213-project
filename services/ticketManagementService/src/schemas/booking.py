from pydantic import BaseModel, Field, UUID4
from pydantic.types import UUID
from datetime import datetime
from typing import List, Optional
from enum import Enum
from ..core.enums import BookingStatus
from .ticket import TicketResponse

class BookingStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELED = "CANCELED"
    REFUNDED = "REFUNDED"

    @classmethod
    def can_transition_to(cls, current_status: str, new_status: str) -> bool:
        """Validate status transitions based on atomic service rules"""
        transitions = {
            cls.PENDING: [cls.CONFIRMED, cls.CANCELED],
            cls.CONFIRMED: [cls.REFUNDED, cls.CANCELED],
            cls.CANCELED: [],
            cls.REFUNDED: []
        }
        try:
            current = cls(current_status) if isinstance(current_status, str) else current_status
            new = cls(new_status) if isinstance(new_status, str) else new_status
            return new in transitions.get(current, [])
        except ValueError:
            return False


# Booking Request Model
class BookingRequest(BaseModel):
    event_id: UUID4
    ticket_quantity: int
    total_amount: float
    user_id: Optional[str] = None  # Make user_id optional, it will be taken from the token

# Booking Response Model
class BookingResponse(BaseModel):
    booking_id: str
    user_id: str  # Changed from UUID4 to str to match the database model
    event_id: str  # Keep as str in response for consistency with API
    ticket_quantity: int
    total_amount: float
    status: BookingStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    tickets: List[TicketResponse] = []

    class Config:
        from_attributes = True


