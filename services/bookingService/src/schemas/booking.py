from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional
from ..core.enums import BookingStatus
from .ticket import TicketResponse

class BookingCreate(BaseModel):
    """Request model for creating a booking"""
    event_id: str
    user_id: str
    ticket_quantity: int
    email: EmailStr

class BookingResponse(BaseModel):
    """Response model for booking operations"""
    booking_id: str
    event_id: str
    user_id: str
    status: BookingStatus
    ticket_quantity: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    tickets: List[TicketResponse] = []
    payment_url: Optional[str] = None
    message: str

class BookingDetails(BaseModel):
    id: str
    event_id: str
    user_id: str
    ticket_quantity: int
    status: str
    created_at: datetime
    updated_at: datetime

class PaymentSession(BaseModel):
    """Response model for payment session creation"""
    url: str
    session_id: str
    booking_id: str


