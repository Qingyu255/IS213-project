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

# Create main router
router = APIRouter(tags=["bookings"])

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
@router.post("/bookings/book", response_model=BookingResponse, dependencies=[Depends(get_current_user_id)])
async def create_booking(
    booking: BookingRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    try:
        # Create booking
        db_booking = Booking(
            booking_id=str(uuid.uuid4()),
            user_id=user_id,
            event_id=booking.event_id,
            status=BookingStatus.PENDING
        )
        db.add(db_booking)
        await db.flush()

        # Create tickets
        tickets = []
        for _ in range(booking.ticket_count):
            ticket = Ticket(
                ticket_id=str(uuid.uuid4()),
                booking_id=db_booking.booking_id,
                status="VALID"
            )
            tickets.append(ticket)
            db.add(ticket)

        await db.commit()
        
        # Refresh the booking and load relationships
        result = await db.execute(select(Booking).where(Booking.booking_id == db_booking.booking_id))
        db_booking = result.scalar_one()
        
        return BookingResponse(
            booking_id=db_booking.booking_id,
            user_id=db_booking.user_id,
            event_id=db_booking.event_id,
            status=db_booking.status,
            created_at=db_booking.created_at,
            tickets=tickets
        )
    except Exception as e:
        logger.error(f"Error creating booking: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

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
@router.get("/bookings/{booking_id}", response_model=BookingResponse, dependencies=[Depends(get_current_user_id)])
async def get_booking(
    booking_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    # Get the booking
    result = await db.execute(
        Booking.__table__.select().where(Booking.booking_id == booking_id)
    )
    booking = result.first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
        
    # Verify user owns the booking
    if booking.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Cannot access other users' bookings")
    
    # Get tickets for the booking
    result = await db.execute(
        Ticket.__table__.select().where(Ticket.booking_id == booking_id)
    )
    tickets = result.fetchall()
    
    return BookingResponse(
        booking_id=booking.booking_id,
        user_id=booking.user_id,
        event_id=booking.event_id,
        status=booking.status,
        created_at=booking.created_at,
        tickets=tickets
    )

@router.put("/bookings/{booking_id}/confirm", response_model=BookingResponse, dependencies=[Depends(get_current_user_id)])
async def confirm_booking(booking_id: UUID, db: AsyncSession = Depends(get_db)):
    query = select(Booking).where(Booking.booking_id == booking_id)
    result = await db.execute(query)
    booking = result.scalar_one_or_none()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.status != BookingStatus.PENDING:
        raise HTTPException(status_code=400, detail="Only pending bookings can be confirmed")
    
    booking.status = BookingStatus.CONFIRMED
    await db.commit()
    await db.refresh(booking)
    return booking

@router.put("/bookings/{booking_id}/cancel", response_model=BookingResponse, dependencies=[Depends(get_current_user_id)])
async def cancel_booking(booking_id: UUID, db: AsyncSession = Depends(get_db)):
    query = select(Booking).where(Booking.booking_id == booking_id)
    result = await db.execute(query)
    booking = result.scalar_one_or_none()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.status != BookingStatus.PENDING:
        raise HTTPException(status_code=400, detail="Only pending bookings can be canceled")
    
    booking.status = BookingStatus.CANCELED
    await db.commit()
    await db.refresh(booking)
    return booking

@router.put("/bookings/{booking_id}/refund", response_model=BookingResponse, dependencies=[Depends(get_current_user_id)])
async def refund_booking(booking_id: UUID, db: AsyncSession = Depends(get_db)):
    query = select(Booking).where(Booking.booking_id == booking_id)
    result = await db.execute(query)
    booking = result.scalar_one_or_none()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.status != BookingStatus.CONFIRMED:
        raise HTTPException(status_code=400, detail="Only confirmed bookings can be refunded")
    
    booking.status = BookingStatus.REFUNDED
    await db.commit()
    await db.refresh(booking)
    return booking
