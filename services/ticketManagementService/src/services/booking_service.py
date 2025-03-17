from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from ..models.booking import Booking
from ..models.ticket import Ticket
from ..schemas.booking import BookingRequest, BookingStatus
from .base_service import BaseService
from pydantic import UUID4
from typing import List, Dict, Any
from enum import Enum
import uuid

class TicketFilterType(str, Enum):
    USER = "user_id"
    EVENT = "event_id"

class BookingService(BaseService):
    def __init__(self):
        super().__init__(Booking)

    async def create_booking(self, booking_data: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
        try:
            booking = Booking(
                user_id=uuid.UUID(booking_data["user_id"]),
                event_id=booking_data["event_id"],
                status='PENDING'
            )
            db.add(booking)
            await db.flush()
            
            tickets = [Ticket(booking_id=booking.booking_id) 
                      for _ in range(booking_data["ticket_count"])]
            db.add_all(tickets)
            await db.commit()
            
            return {
                **booking.to_dict(),
                'tickets': [ticket.to_dict() for ticket in tickets]
            }
        except Exception as e:
            await db.rollback()
            raise e

    async def get_booking_by_id(self, booking_id: UUID4, db: AsyncSession) -> Dict[str, Any]:
        booking = await self.get_by_id(db, booking_id, "booking_id")
        if not booking:
            self.raise_not_found("Booking not found")
        
        tickets = (await db.execute(
            select(Ticket).where(Ticket.booking_id == booking_id)
        )).scalars().all()
        
        return {
            **booking.to_dict(),
            'tickets': [ticket.to_dict() for ticket in tickets]
        }

    async def update_booking_status(self, booking_id: UUID4, new_status: BookingStatus, db: AsyncSession) -> Dict[str, str]:
        """Update booking status with validation."""
        booking = await self.get_by_id(db, booking_id, "booking_id")
        if not booking:
            self.raise_not_found("Booking not found")

        if not BookingStatus.can_transition_to(booking.status, new_status):
            self.raise_validation_error(f"Cannot transition from {booking.status} to {new_status}")

        await self.update(db, booking, {"status": new_status})
        return {"message": f"Booking {new_status} successfully"}

    async def get_tickets(self, filter_value, filter_type: TicketFilterType, db: AsyncSession) -> List[Dict[str, Any]]:
        """Get tickets filtered by user_id or event_id."""
        query = select(Booking)
        
        if filter_type == TicketFilterType.USER:
            try:
                user_uuid = uuid.UUID(str(filter_value))
                query = query.filter(Booking.user_id == user_uuid)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=f"Invalid user ID format: {str(e)}")
        else:
            query = query.filter(Booking.event_id == filter_value)
        
        bookings = (await db.execute(query.order_by(Booking.created_at.desc()))).scalars().all()
        if not bookings:
            return []
        
        booking_ids = [booking.booking_id for booking in bookings]
        tickets = (await db.execute(
            select(Ticket).where(Ticket.booking_id.in_(booking_ids))
        )).scalars().all()
        
        return [ticket.to_dict() for ticket in tickets]

    async def get_available_tickets(self, event_id: UUID4, db: AsyncSession) -> int:
        result = await db.execute(
            select(Ticket)
            .join(Booking)
            .filter(
                Booking.event_id == event_id,
                Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED])
            )
        )
        return len(result.scalars().all())