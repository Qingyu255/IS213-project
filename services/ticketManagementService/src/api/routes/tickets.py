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

@router.get(
    "/user/{user_id}",
    response_model=List[TicketResponse],
    summary="Get User Tickets",
    description="Retrieve all tickets associated with a specific user",
    responses={
        200: {"description": "List of tickets found for the user"},
        404: {"description": "No tickets found for the user"}
    }
)
async def get_user_tickets(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all tickets for a specific user.
    
    Parameters:
    - user_id: String ID of the user (from custom:id in Cognito)
    
    Returns:
    - List of tickets owned by the user
    """
    query = select(Ticket).join(Booking).where(Booking.user_id == user_id)
    result = await db.execute(query)
    return result.scalars().all()

@router.get(
    "/event/{event_id}",
    response_model=List[TicketResponse],
    summary="Get Event Tickets",
    description="Retrieve all tickets for a specific event",
    responses={
        200: {"description": "List of tickets found for the event"},
        404: {"description": "No tickets found for the event"}
    }
)
async def get_event_tickets(
    event_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all tickets for a specific event.
    
    Parameters:
    - event_id: UUID of the event
    
    Returns:
    - List of tickets for the event
    """
    query = select(Ticket).join(Booking).where(Booking.event_id == event_id)
    result = await db.execute(query)
    return result.scalars().all()

@router.get(
    "/event/{event_id}/available",
    summary="Get Available Tickets Count",
    description="Get the number of available tickets for a specific event",
    responses={
        200: {
            "description": "Available ticket count retrieved successfully",
            "content": {
                "application/json": {
                    "example": {"available_tickets": 50}
                }
            }
        }
    }
)
async def get_available_tickets(
    event_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get the number of available tickets for a specific event.
    
    Parameters:
    - event_id: UUID of the event
    
    Returns:
    - Dictionary containing the number of available tickets
    """
    query = select(func.count(Ticket.ticket_id)).join(Booking).where(
        Booking.event_id == event_id,
        Booking.status == BookingStatus.CONFIRMED
    )
    result = await db.execute(query)
    booked_tickets = result.scalar()
    
    total_capacity = 100  # Example value
    available = total_capacity - booked_tickets
    
    return {"available_tickets": available}

@router.get(
    "/user/{user_id}/event/{event_id}",
    response_model=List[TicketResponse],
    summary="Get User Tickets for Event",
    description="Retrieve all tickets for a specific user and event",
    responses={
        200: {"description": "List of tickets found for the user and event"},
        404: {"description": "No tickets found for the user and event"}
    }
)
async def get_user_event_tickets(
    user_id: str,
    event_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all tickets for a specific user and event.
    
    Parameters:
    - user_id: String ID of the user (from custom:id in Cognito)
    - event_id: UUID of the event
    
    Returns:
    - List of tickets owned by the user for the specified event
    """
    query = select(Ticket).join(Booking).where(
        Booking.user_id == user_id,
        Booking.event_id == event_id
    )
    result = await db.execute(query)
    tickets = result.scalars().all()
    
    return {
        "tickets": tickets,
        "count": len(tickets),
        "ticket_ids": [str(ticket.ticket_id) for ticket in tickets]
    }
