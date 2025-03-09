from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from ..models.booking import Booking
from ..models.ticket import Ticket
from ..schemas.booking import BookingCreate
from pydantic import UUID4

# Create a new booking
async def create_booking(booking_data: BookingCreate, db: AsyncSession):
    new_booking = Booking(
        user_id=booking_data.user_id,
        event_id=booking_data.event_id,
        status="pending"
    )

    db.add(new_booking)
    await db.commit()
    await db.refresh(new_booking)

    # Create tickets for the booking
    tickets = []
    for i in range(booking_data.num_tickets):
        ticket = Ticket(
            booking_id=new_booking.booking_id
        )
        db.add(ticket)
        tickets.append(ticket)

    await db.commit()

    return {
        "booking_id": new_booking.booking_id,
        "user_id": new_booking.user_id,
        "event_id": new_booking.event_id,
        "status": new_booking.status,
        "created_at": new_booking.created_at,
        "updated_at": new_booking.updated_at,
        "tickets": [ticket.ticket_id for ticket in tickets]
    }

# Get a booking by ID
async def get_booking_by_id(booking_id: UUID4, db: AsyncSession):
    result = await db.execute(select(Booking).filter(Booking.booking_id == booking_id))
    booking = result.scalars().first()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    result = await db.execute(select(Ticket).filter(Ticket.booking_id == booking_id))
    tickets = result.scalars().all()

    return {
        "booking_id": booking.booking_id,
        "user_id": booking.user_id,
        "event_id": booking.event_id,
        "status": booking.status,
        "created_at": booking.created_at,
        "updated_at": booking.updated_at,
        "tickets": [ticket.ticket_id for ticket in tickets]
    }

# Confirm a booking (pending -> confirmed)
# probably should add billing_id or something as a requirement to confirm the booking
async def confirm_booking(booking_id: UUID4, db: AsyncSession):
    result = await db.execute(select(Booking).filter(Booking.booking_id == booking_id))
    booking = result.scalars().first()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if booking.status != "pending":
        raise HTTPException(status_code=400, detail="Only pending bookings can be confirmed")
    
    booking.status = "confirmed"
    await db.commit()
    await db.refresh(booking)

    return {"message": "Booking confirmed successfully"}

# Cancel a booking (pending -> canceled)
async def cancel_booking(booking_id: UUID4, db: AsyncSession):
    result = await db.execute(select(Booking).filter(Booking.booking_id == booking_id))
    booking = result.scalars().first()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if booking.status != "pending":
        raise HTTPException(status_code=400, detail="Only pending bookings can be canceled")
    
    booking.status = "canceled"
    await db.commit()
    await db.refresh(booking)

    return {"message": "Booking canceled successfully"}

# Refund a booking (confirmed -> refunded)
async def refund_booking(booking_id: UUID4, db: AsyncSession):
    result = await db.execute(select(Booking).filter(Booking.booking_id == booking_id))
    booking = result.scalars().first()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if booking.status != "confirmed":
        raise HTTPException(status_code=400, detail="Only confirmed bookings can be refunded")
    
    booking.status = "refunded"
    await db.commit()
    await db.refresh(booking)

    return {"message": "Booking refunded successfully"}