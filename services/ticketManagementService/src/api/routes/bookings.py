from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
import logging

from ...core.database import get_db
from ...models.booking import Booking
from ...models.ticket import Ticket
from ...schemas.booking import BookingRequest, BookingResponse, BookingStatus
from ...core.auth import get_current_user_id, validate_token
from typing import List
from ...services.booking_service import BookingService, TicketFilterType

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
    current_user_id: str = Depends(get_current_user_id)
):
    try:
        # Use custom:id directly as string
        logger.debug(f"Creating booking for user (custom:id): {current_user_id}")
        
        booking_data = booking.dict()
        booking_data["user_id"] = current_user_id
        
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
    logger.debug(f"Current user_id from token: {current_user_id}")
    
    # Compare the requested user_id with the current user's ID
    if user_id != current_user_id:
        logger.warning(f"User {current_user_id} attempted to access bookings for user {user_id}")
        raise HTTPException(status_code=403, detail="Cannot access other users' bookings")
    
    try:
        # Get all bookings for the user
        logger.debug(f"Querying database for bookings with user_id: {user_id}")
        bookings_query = select(Booking).where(Booking.user_id == user_id)
        bookings_result = await db.execute(bookings_query)
        bookings = bookings_result.scalars().all()
        
        logger.debug(f"Found {len(bookings)} bookings in database")
        if not bookings:
            logger.debug(f"No bookings found for user {user_id}")
            return []
        
        # Get all tickets for these bookings in a single query
        booking_ids = [str(booking.booking_id) for booking in bookings]  # Convert UUIDs to strings
        logger.debug(f"Found bookings with IDs: {booking_ids}")
        tickets_query = select(Ticket).where(Ticket.booking_id.in_([UUID(bid) for bid in booking_ids]))  # Convert strings back to UUIDs
        tickets_result = await db.execute(tickets_query)
        tickets = tickets_result.scalars().all()
        
        # Create a mapping of booking_id to tickets
        tickets_by_booking = {}
        for ticket in tickets:
            booking_id_str = str(ticket.booking_id)  # Convert UUID to string for dictionary key
            if booking_id_str not in tickets_by_booking:
                tickets_by_booking[booking_id_str] = []
            tickets_by_booking[booking_id_str].append(ticket)
        
        # Create booking responses
        booking_responses = []
        for booking in bookings:
            booking_id_str = str(booking.booking_id)
            booking_tickets = tickets_by_booking.get(booking_id_str, [])
            
            booking_dict = {
                "booking_id": booking_id_str,
                "user_id": booking.user_id,  # Already a string
                "event_id": str(booking.event_id),  # Convert UUID to string
                "status": booking.status.value if booking.status else None,
                "created_at": booking.created_at,
                "updated_at": booking.updated_at,
                "ticket_quantity": len(booking_tickets),  # Add ticket quantity
                "total_amount": 0.0,  # Default to 0.0 as total amount is managed by billing service
                "tickets": [
                    {
                        "ticket_id": str(ticket.ticket_id),
                        "booking_id": str(ticket.booking_id),
                        "created_at": ticket.created_at
                    }
                    for ticket in booking_tickets
                ]
            }
            booking_responses.append(booking_dict)
        
        logger.debug(f"Returning {len(booking_responses)} bookings")
        logger.debug(f"First booking response: {booking_responses[0] if booking_responses else 'None'}")
        return booking_responses
    except Exception as e:
        logger.error(f"Error fetching bookings: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching bookings: {str(e)}")

@router.get("/bookings/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    # Get the booking first
    booking = await booking_service.get_booking_by_id(booking_id, db)
    
    # Add detailed logging
    logger.debug(f"=== GET /bookings/{booking_id} ===")
    logger.debug(f"Current user_id from token: {current_user_id}")
    logger.debug(f"Booking user_id: {booking['user_id']}")
    
    # Compare user IDs as strings
    if booking["user_id"] != current_user_id:
        logger.warning(f"User {current_user_id} attempted to access booking {booking_id} owned by user {booking['user_id']}")
        raise HTTPException(status_code=403, detail="Cannot access other users' bookings")
    
    return booking

@router.post("/bookings/{booking_id}/confirm")
async def confirm_booking(
    booking_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    # Get the booking first to check ownership
    booking = await booking_service.get_booking_by_id(booking_id, db)
    
    # Add detailed logging
    logger.debug(f"=== POST /bookings/{booking_id}/confirm ===")
    logger.debug(f"Current user_id from token: {current_user_id}")
    logger.debug(f"Booking user_id: {booking['user_id']}")
    logger.debug(f"Current booking status: {booking.get('status')}")
    
    # If booking is already confirmed, return success response
    if booking.get('status') == BookingStatus.CONFIRMED:
        logger.info(f"Booking {booking_id} is already confirmed")
        return {"message": "Booking already confirmed", "status": BookingStatus.CONFIRMED}
    
    # Compare user IDs as strings
    if booking["user_id"] != current_user_id:
        logger.warning(f"User {current_user_id} attempted to confirm booking {booking_id} owned by user {booking['user_id']}")
        raise HTTPException(status_code=403, detail="Cannot confirm other users' bookings")
    
    try:
        return await booking_service.update_booking_status(booking_id, BookingStatus.CONFIRMED, db)
    except Exception as e:
        logger.error(f"Error confirming booking: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bookings/{booking_id}/cancel")
async def cancel_booking(
    booking_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    # Get the booking first to check ownership
    booking = await booking_service.get_booking_by_id(booking_id, db)
    
    # Compare user IDs as strings
    if booking["user_id"] != current_user_id:
        logger.warning(f"User {current_user_id} attempted to cancel booking {booking_id} owned by user {booking['user_id']}")
        raise HTTPException(status_code=403, detail="Cannot cancel other users' bookings")
    
    return await booking_service.update_booking_status(booking_id, BookingStatus.CANCELED, db)

@router.post("/bookings/{booking_id}/refund")
async def refund_booking(
    booking_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    # Get the booking first to check ownership
    booking = await booking_service.get_booking_by_id(booking_id, db)
    
    # Compare user IDs as strings
    if booking["user_id"] != current_user_id:
        logger.warning(f"User {current_user_id} attempted to refund booking {booking_id} owned by user {booking['user_id']}")
        raise HTTPException(status_code=403, detail="Cannot refund other users' bookings")
    
    return await booking_service.update_booking_status(booking_id, BookingStatus.REFUNDED, db)
