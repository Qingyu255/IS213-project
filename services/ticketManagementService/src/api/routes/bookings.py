from fastapi import APIRouter, Depends, HTTPException, Security
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
import uuid
from ...services.booking_service import BookingService, TicketFilterType

# Create main router
router = APIRouter(tags=["bookings"])
booking_service = BookingService()

logger = logging.getLogger(__name__)

# Test endpoints (no auth required)
@router.get("/test/cors")
async def test_cors():
    """Test endpoint to verify CORS is working (no auth required)"""
    return {"message": "CORS is working"}

@router.get("/bookings/test-auth")
async def test_auth(claims: dict = Depends(validate_token)):
    """Test endpoint to verify authentication and return user claims"""
    user_id = (
        claims.get("custom:id") or 
        claims.get("sub") or 
        claims.get("userId") or
        claims.get("user_id")
    )
    return {
        "message": "Authentication successful",
        "user_id": user_id,
        "user_claims": claims
    }

# Protected endpoints
@router.post("/bookings/book", response_model=BookingResponse)
async def create_booking(
    booking: BookingRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    booking_data = booking.dict()
    booking_data["user_id"] = user_id
    return await booking_service.create_booking(booking_data, db)

@router.get("/bookings/user/{user_id}", response_model=List[BookingResponse], dependencies=[Depends(get_current_user_id)])
async def get_user_bookings(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    # Debug logging
    logger.debug(f"Requested user_id: {user_id}")
    logger.debug(f"Current user_id from token: {current_user_id}")
    
    # Verify user is accessing their own bookings
    if user_id != current_user_id:
        logger.warning(f"User {current_user_id} attempted to access bookings for user {user_id}")
        raise HTTPException(status_code=403, detail="Cannot access other users' bookings")
    
    # Get all bookings for the user
    result = await db.execute(
        Booking.__table__.select().where(Booking.user_id == user_id)
    )
    bookings = result.fetchall()
    
    # Get tickets for each booking
    booking_responses = []
    for booking in bookings:
        result = await db.execute(
            Ticket.__table__.select().where(Ticket.booking_id == booking.booking_id)
        )
        tickets = result.fetchall()
        
        booking_responses.append(
            BookingResponse(
                booking_id=booking.booking_id,
                user_id=booking.user_id,
                event_id=booking.event_id,
                status=booking.status,
                created_at=booking.created_at,
                updated_at=booking.updated_at,
                tickets=tickets
            )
        )
    
    return booking_responses

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

@router.get("/tickets/user/{user_id}")
async def get_user_tickets(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    if str(user_id) != current_user_id:
        raise HTTPException(status_code=403, detail="Cannot access other users' tickets")
    return await booking_service.get_tickets(user_id, TicketFilterType.USER, db)

@router.get("/tickets/event/{event_id}")
async def get_event_tickets(
    event_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user_id)
):
    return await booking_service.get_tickets(event_id, TicketFilterType.EVENT, db)

@router.get("/tickets/available/{event_id}")
async def get_available_tickets(
    event_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user_id)
):
    return {"available_tickets": await booking_service.get_available_tickets(event_id, db)}
