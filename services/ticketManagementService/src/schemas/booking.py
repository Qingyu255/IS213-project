from pydantic import BaseModel, Field
from pydantic.types import UUID4
from uuid import UUID
from datetime import datetime
from typing import List, Optional
from enum import Enum
from .ticket import TicketResponse

class BookingStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELED = "CANCELED"
    REFUNDED = "REFUNDED"


# Booking Request Model
class BookingRequest(BaseModel):
    event_id: str
    ticket_count: int
    user_id: Optional[str] = None  # Make user_id optional, it will be taken from the token

# Booking Response Model
class BookingResponse(BaseModel):
    booking_id: str
    user_id: str  # Changed from UUID4 to str to match the database model
    event_id: str
    status: BookingStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    tickets: List[TicketResponse] = []

    class Config:
        from_attributes = True


