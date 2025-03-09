from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from uuid import UUID

from ...core.database import get_db
from ...models.booking import Booking
from ...models.ticket import Ticket
from ...schemas.ticket import TicketResponse
from ...schemas.booking import BookingStatus

# Create API Router
router = APIRouter(prefix="/tickets", tags=["tickets"])

# Get all tickets for a user
@router.get("/user/{user_id}", response_model=List[TicketResponse])
async def get_user_tickets(user_id: UUID, db: AsyncSession = Depends(get_db)):
    query = select(Ticket).join(Booking).where(Booking.user_id == user_id)
    result = await db.execute(query)
    return result.scalars().all()

# Get all tickets for an event
@router.get("/event/{event_id}", response_model=List[TicketResponse])
async def get_event_tickets(event_id: UUID, db: AsyncSession = Depends(get_db)):
    query = select(Ticket).join(Booking).where(Booking.event_id == event_id)
    result = await db.execute(query)
    return result.scalars().all()

# Get available ticket count for an event
@router.get("/event/{event_id}/available")
async def get_available_tickets(event_id: UUID, db: AsyncSession = Depends(get_db)):
    query = select(func.count(Ticket.ticket_id)).join(Booking).where(
        Booking.event_id == event_id,
        Booking.status == BookingStatus.CONFIRMED
    )
    result = await db.execute(query)
    booked_tickets = result.scalar()
    
    total_capacity = 100  # Example value
    available = total_capacity - booked_tickets
    
    return {"available_tickets": available}
