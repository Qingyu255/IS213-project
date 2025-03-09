from pydantic import BaseModel, UUID4

class TicketResponse(BaseModel):
    ticket_id: UUID4
    booking_id: UUID4

    class Config:
        from_attributes = True