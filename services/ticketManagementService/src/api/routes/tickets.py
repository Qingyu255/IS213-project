import asyncio
from fastapi import APIRouter, Depends, HTTPException
import requests
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Dict
from uuid import UUID
import logging

from ...core.config import get_settings
from ...core.database import get_db
from ...models.booking import Booking
from ...models.ticket import Ticket
from ...schemas.ticket import TicketResponse, UserEventTicketsResponse
from ...schemas.booking import BookingStatus
from ...core.auth import get_current_user_id

router = APIRouter(tags=["tickets"])
settings = get_settings()
logger = logging.getLogger(__name__)

def format_ticket_response(ticket: Ticket) -> dict:
    return {
        "ticket_id": str(ticket.ticket_id),
        "booking_id": str(ticket.booking_id),
        "created_at": ticket.created_at
    }

@router.get(
    "/tickets/user/{user_id}",
    response_model=List[TicketResponse],
    summary="Get User Tickets"
)
async def get_user_tickets(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Cannot access other users' tickets")

    query = select(Ticket).join(Booking).where(Booking.user_id == user_id)
    result = await db.execute(query)
    tickets = result.scalars().all()
    
    return [format_ticket_response(ticket) for ticket in tickets]

@router.get(
    "/tickets/event/{event_id}",
    response_model=List[TicketResponse],
    summary="Get Event Tickets"
)
async def get_event_tickets(
    event_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user_id)
):
    query = select(Ticket).join(Booking).where(Booking.event_id == event_id)
    result = await db.execute(query)
    tickets = result.scalars().all()
    
    return [format_ticket_response(ticket) for ticket in tickets]

@router.get(
    "/tickets/event/{event_id}/available",
    summary="Get Available Tickets Count"
)
async def get_available_tickets(
    event_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user_id)
):
    # Get event capacity from events service first
    event_data = await asyncio.to_thread(fetch_event_data, event_id)
    total_capacity = event_data.get("capacity", 0)  # Will now be an int
    
    # Count tickets from confirmed bookings
    query = select(func.count(Ticket.ticket_id)).select_from(Ticket).join(Booking).where(
        Booking.event_id == event_id,
        Booking.status == BookingStatus.CONFIRMED
    )
    
    booked_tickets = (await db.execute(query)).scalar() or 0
    
    # If total capacity is 0, tickets are unlimited
    if total_capacity == 0:
        return {
            "available_tickets": 0,
            "total_capacity": 0,
            "booked_tickets": booked_tickets
        }
    
    # Calculate available tickets
    available = total_capacity - booked_tickets  # Now both are integers
    
    return {
        "available_tickets": max(0, available),
        "total_capacity": total_capacity,
        "booked_tickets": booked_tickets
    }

@router.get(
    "/tickets/user/{user_id}/event/{event_id}",
    response_model=List[TicketResponse],
    summary="Get User Tickets for Event"
)
async def get_user_event_tickets(
    user_id: str,
    event_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Cannot access other users' tickets")

    query = select(Ticket).join(Booking).where(
        Booking.user_id == user_id,
        Booking.event_id == event_id
    )
    result = await db.execute(query)
    tickets = result.scalars().all()
    
    return [format_ticket_response(ticket) for ticket in tickets]

def fetch_event_data(event_id: str):
    response = requests.get(f"{settings.EVENT_SERVICE_URL}/api/v1/events/{event_id}")
    if response.status_code != 200:
        raise HTTPException(status_code=404, detail="Event not found")
    event_json = response.json()
    
    # Convert capacity to int here
    if "capacity" in event_json:
        try:
            event_json["capacity"] = int(event_json["capacity"])
        except (ValueError, TypeError):
            event_json["capacity"] = 0
            
    logger.debug(f"Received event data: {event_json}")
    return event_json