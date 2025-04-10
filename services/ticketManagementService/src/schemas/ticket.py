from pydantic import BaseModel
from pydantic.types import UUID4
from uuid import UUID
from typing import List
from datetime import datetime

class TicketResponse(BaseModel):
    ticket_id: str
    booking_id: str
    created_at: datetime

    class Config:
        from_attributes = True

class UserEventTicketsResponse(BaseModel):
    tickets: List[TicketResponse]
    count: int
    ticket_ids: List[str]

    class Config:
        from_attributes = True