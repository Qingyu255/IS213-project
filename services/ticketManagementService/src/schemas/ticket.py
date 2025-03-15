from pydantic import BaseModel
from pydantic.types import UUID4
from uuid import UUID

class TicketResponse(BaseModel):
    ticket_id: str
    booking_id: str

    class Config:
        from_attributes = True