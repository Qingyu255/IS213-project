from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload
from uuid import UUID
import logging

from ...core.database import get_db
from ...models.booking import Booking
from ...models.ticket import Ticket
from ...schemas.booking import BookingRequest, BookingResponse, BookingStatus
from ...core.auth import get_current_user_id, validate_token
from typing import List
import uuid
from ...services.booking_service import BookingService, TicketFilterType

# Create main router
router = APIRouter(tags=["bookings"])
booking_service = BookingService()

logger = logging.getLogger(__name__)

# Test endpoints (no auth required)
@router.get("/test")
async def test_endpoints(claims: dict = Depends(validate_token)):
    """Combined test endpoint for CORS, auth, and token info"""
    user_id = claims.get("custom:id")
    return {
        "cors_status": "CORS is working",
        "auth_status": "Authentication successful",
        "user_id": user_id,
        "token_claims": claims
    }

# Protected endpoints
@router.post("/bookings/book", response_model=BookingResponse)
async def create_booking(
    booking: BookingRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    try:
        # Convert user_id string to UUID
        booking_data = booking.dict()
        booking_data["user_id"] = user_id
        
        # Log the booking data for debugging
        logger.debug(f"Creating booking with data: {booking_data}")
        
        return await booking_service.create_booking(booking_data, db)
    except Exception as e:
        logger.error(f"Error creating booking: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating booking: {str(e)}")

@router.get("/bookings/user/{user_id}", response_model=List[BookingResponse])
async def get_user_bookings(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    # Debug logging
    logger.debug("=== GET /bookings/user/{user_id} ===")
    logger.debug(f"Requested user_id: {user_id}")
    logger.debug(f"Current user_id from token (custom:id): {current_user_id}")
    
    # Compare IDs directly without normalization
    if user_id != current_user_id:
        logger.warning(f"User {current_user_id} attempted to access bookings for user {user_id}")
        raise HTTPException(status_code=403, detail="Cannot access other users' bookings")
    
    try:
        # First, get all bookings for the user
        logger.debug(f"Querying database for bookings with user_id: {current_user_id}")
        bookings_query = select(Booking).where(Booking.user_id == current_user_id)
        bookings_result = await db.execute(bookings_query)
        bookings = bookings_result.scalars().all()
        
        if not bookings:
            logger.debug(f"No bookings found for user {current_user_id}")
            return []
        
        # Get all tickets for these bookings in a single query
        booking_ids = [booking.booking_id for booking in bookings]
        logger.debug(f"Found bookings with IDs: {booking_ids}")
        tickets_query = select(Ticket).where(Ticket.booking_id.in_(booking_ids))
        tickets_result = await db.execute(tickets_query)
        tickets = tickets_result.scalars().all()
        
        # Create a mapping of booking_id to tickets
        tickets_by_booking = {}
        for ticket in tickets:
            if ticket.booking_id not in tickets_by_booking:
                tickets_by_booking[ticket.booking_id] = []
            tickets_by_booking[ticket.booking_id].append(ticket)
        
        # Create booking responses
        booking_responses = []
        for booking in bookings:
            booking_dict = {
                "booking_id": str(booking.booking_id),
                "user_id": str(booking.user_id),
                "event_id": str(booking.event_id),
                "status": booking.status.value if booking.status else None,
                "created_at": booking.created_at,
                "updated_at": booking.updated_at,
                "tickets": [
                    {
                        "ticket_id": str(ticket.ticket_id),
                        "booking_id": str(ticket.booking_id),
                        "created_at": ticket.created_at
                    }
                    for ticket in tickets_by_booking.get(booking.booking_id, [])
                ]
            }
            booking_responses.append(booking_dict)
        
        logger.debug(f"Returning {len(booking_responses)} bookings")
        return booking_responses
    except Exception as e:
        logger.error(f"Error fetching bookings: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching bookings: {str(e)}")

@router.get("/bookings/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user_id)
):
    return await booking_service.get_booking_by_id(booking_id, db)

@router.post("/bookings/{booking_id}/confirm")
async def confirm_booking(
    booking_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user_id)
):
    return await booking_service.update_booking_status(booking_id, BookingStatus.CONFIRMED, db)

@router.post("/bookings/{booking_id}/cancel")
async def cancel_booking(
    booking_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user_id)
):
    return await booking_service.update_booking_status(booking_id, BookingStatus.CANCELED, db)

@router.post("/bookings/{booking_id}/refund")
async def refund_booking(
    booking_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user_id)
):
    return await booking_service.update_booking_status(booking_id, BookingStatus.REFUNDED, db)
