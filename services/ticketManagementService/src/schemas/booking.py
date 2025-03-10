from pydantic import BaseModel, UUID4
from datetime import datetime
from typing import List
from enum import Enum
from .ticket import TicketResponse

class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELED = "canceled"
    REFUNDED = "refunded"


# Booking Request Model
class BookingRequest(BaseModel):
    user_id: UUID4
    event_id: UUID4
    ticket_count: int

# Booking Response Model
class BookingResponse(BaseModel):
    booking_id: UUID4
    user_id: UUID4
    event_id: UUID4
    status: BookingStatus
    created_at: datetime
    updated_at: datetime
    tickets: List[TicketResponse]

    class Config:
        from_attributes = True


