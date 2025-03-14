from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from pydantic import UUID4
from ..models.ticket import Ticket
from .base_service import BaseService

class TicketService(BaseService):
    def __init__(self):
        super().__init__(Ticket)

    async def get_available_tickets(self, event_id: UUID4, db: AsyncSession) -> int:
        """Get count of available tickets for an event"""
        result = await db.execute("""
            SELECT COUNT(*) 
            FROM tickets t
            JOIN bookings b ON t.booking_id = b.booking_id
            WHERE b.event_id = :event_id 
            AND b.status IN ('pending', 'confirmed')
        """, {"event_id": event_id})

        return result.scalar()

# Get tickets by user_id
async def get_tickets_by_user_id(user_id: str, db: AsyncSession):
    results = await db.execute("""
        SELECT t.ticket_id, t.booking_id
        FROM tickets t
        JOIN bookings b ON t.booking_id = b.booking_id
        WHERE b.user_id = :user_id
    """, {"user_id": user_id})

    tickets = results.mappings().all()
    if not tickets:
        raise HTTPException(status_code=404, detail="No tickets found for this user")
    
    return tickets

# Get tickets by event_id
async def get_tickets_by_event(event_id: UUID4, db: AsyncSession):
    result = await db.execute("""
        SELECT t.ticket_id, t.booking_id
        FROM tickets t
        JOIN bookings b ON t.booking_id = b.booking_id
        WHERE b.event_id = :event_id
    """, {"event_id": event_id})

    tickets = result.mappings().all()
    if not tickets:
        raise HTTPException(status_code=404, detail="No tickets found for this event")
    
    return tickets