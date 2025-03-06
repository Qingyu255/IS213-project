from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
import logging

from ...core.database import get_db
from ...models.booking import Booking
from ...models.ticket import Ticket
from ...schemas.booking import BookingRequest, BookingResponse, BookingStatus

router = APIRouter(prefix="/bookings", tags=["bookings"])
logger = logging.getLogger(__name__)

@router.post("", response_model=BookingResponse)
async def create_booking(booking: BookingRequest, db: AsyncSession = Depends(get_db)):
    try:
        # Create booking
        db_booking = Booking(
            user_id=booking.user_id,
            event_id=booking.event_id,
            status=BookingStatus.PENDING
        )
        db.add(db_booking)
        await db.flush()  # Get the booking_id without committing

        # Create tickets
        for _ in range(booking.ticket_count):
            db_ticket = Ticket(booking_id=db_booking.booking_id)
            db.add(db_ticket)

        await db.commit()
        
        # Refresh the booking and load relationships
        result = await db.execute(select(Booking).where(Booking.booking_id == db_booking.booking_id))
        db_booking = result.scalar_one()
        
        return db_booking
    except Exception as e:
        logger.error(f"Error creating booking: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(booking_id: UUID, db: AsyncSession = Depends(get_db)):
    query = select(Booking).where(Booking.booking_id == booking_id)
    result = await db.execute(query)
    booking = result.scalar_one_or_none()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking

@router.put("/{booking_id}/confirm", response_model=BookingResponse)
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

@router.put("/{booking_id}/cancel", response_model=BookingResponse)
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

@router.put("/{booking_id}/refund", response_model=BookingResponse)
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