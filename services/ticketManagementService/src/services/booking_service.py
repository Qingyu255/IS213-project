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

class TicketFilterType(str, Enum):
    USER = "user_id"
    EVENT = "event_id"

class BookingService(BaseService):
    def __init__(self):
        super().__init__(Booking)

    async def create_booking(self, booking_data: BookingRequest, db: AsyncSession) -> Dict[str, Any]:
        # Create booking
        booking_dict = {
            "user_id": booking_data.user_id,
            "event_id": booking_data.event_id,
            "status": BookingStatus.PENDING
        }
        booking = await self.create(db, booking_dict)

        # Create tickets
        for _ in range(booking_data.ticket_count):
            ticket = Ticket(booking_id=booking.booking_id)
            db.add(ticket)
        
        await db.commit()
        await db.refresh(booking)
        return booking.to_dict()

    async def get_booking_by_id(self, booking_id: UUID4, db: AsyncSession) -> Dict[str, Any]:
        booking = await self.get_by_id(db, booking_id, "booking_id")
        if not booking:
            self.raise_not_found("Booking not found")
        return booking.to_dict()

    async def update_booking_status(self, booking_id: UUID4, new_status: BookingStatus, db: AsyncSession) -> Dict[str, str]:
        """
        Update booking status with validation.
        This method replaces individual status update methods (confirm, cancel, refund).
        """
        booking = await self.get_by_id(db, booking_id, "booking_id")
        if not booking:
            self.raise_not_found("Booking not found")

        if not BookingStatus.can_transition_to(booking.status, new_status):
            self.raise_validation_error(f"Cannot transition from {booking.status} to {new_status}")

        await self.update(db, booking, {"status": new_status})
        return {"message": f"Booking {new_status} successfully"}

    async def get_tickets(self, filter_value: UUID4, filter_type: TicketFilterType, db: AsyncSession) -> List[Dict[str, Any]]:
        """
        Generic method to get tickets filtered by either user_id or event_id.
        This replaces get_tickets_by_user_id and get_tickets_by_event.
        """
        result = await db.execute(
            select(Booking)
            .filter(getattr(Booking, filter_type) == filter_value)
            .order_by(Booking.created_at.desc())
        )
        bookings = result.scalars().all()
        
        if not bookings:
            self.raise_not_found(f"No tickets found for this {filter_type.replace('_id', '')}")
        
        tickets = []
        for booking in bookings:
            tickets.extend([ticket.to_dict() for ticket in booking.tickets])
        return tickets

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