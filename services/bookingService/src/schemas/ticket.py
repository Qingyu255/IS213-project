from pydantic import BaseModel
from pydantic.types import UUID4
from uuid import UUID
from datetime import datetime
from typing import Optional

class TicketResponse(BaseModel):
    """Response model for ticket information"""
    ticket_id: str
    booking_id: str
    created_at: datetime
    status: Optional[str] = None

class TicketCreate(BaseModel):
    """Request model for ticket creation"""
    booking_id: str
    quantity: int

    class Config:
        from_attributes = True