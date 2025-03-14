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
            # Create booking object
            booking = Booking(
                user_id=uuid.UUID(booking_data["user_id"]),  # Convert string to UUID
                event_id=booking_data["event_id"],
                status='PENDING'
            )
            
            # Add booking to session
            db.add(booking)
            
            # Flush to get the booking ID
            await db.flush()
            
            # Create tickets
            created_tickets = []
            for _ in range(booking_data["ticket_count"]):
                ticket = Ticket(booking_id=booking.booking_id)
                db.add(ticket)
                created_tickets.append(ticket)
            
            # Commit the transaction
            await db.commit()
            
            # Create the response with booking and ticket information
            booking_dict = booking.to_dict()
            booking_dict['tickets'] = [ticket.to_dict() for ticket in created_tickets]
            
            return booking_dict
        except Exception as e:
            # Rollback in case of error
            await db.rollback()
            raise e

    async def get_booking_by_id(self, booking_id: UUID4, db: AsyncSession) -> Dict[str, Any]:
        booking = await self.get_by_id(db, booking_id, "booking_id")
        if not booking:
            self.raise_not_found("Booking not found")
        
        # Fetch tickets for this booking separately
        tickets_result = await db.execute(
            select(Ticket).where(Ticket.booking_id == booking_id)
        )
        tickets = tickets_result.scalars().all()
        
        # Create the booking dictionary
        booking_dict = booking.to_dict()
        
        # Add tickets to the booking dictionary
        booking_dict['tickets'] = [ticket.to_dict() for ticket in tickets]
        
        return booking_dict

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

    async def get_tickets(self, filter_value, filter_type: TicketFilterType, db: AsyncSession) -> List[Dict[str, Any]]:
        """
        Generic method to get tickets filtered by either user_id or event_id.
        This replaces get_tickets_by_user_id and get_tickets_by_event.
        
        filter_value can be either a string (for user_id) or UUID (for event_id)
        """
        # First, get all bookings for the filter
        query = select(Booking)
        
        # Handle different filter types
        if filter_type == TicketFilterType.USER:
            # For user_id, convert string to UUID for comparison
            try:
                user_uuid = uuid.UUID(str(filter_value))
                query = query.filter(Booking.user_id == user_uuid)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=f"Invalid user ID format: {str(e)}")
        else:
            # For event_id, use UUID comparison
            query = query.filter(Booking.event_id == filter_value)
        
        # Add ordering
        query = query.order_by(Booking.created_at.desc())
        
        # Execute query
        result = await db.execute(query)
        bookings = result.scalars().all()
        
        if not bookings:
            return []  # Return empty list instead of raising an error
        
        # Get all booking IDs
        booking_ids = [booking.booking_id for booking in bookings]
        
        # Fetch all tickets for these bookings in a single query
        tickets_result = await db.execute(
            select(Ticket).where(Ticket.booking_id.in_(booking_ids))
        )
        all_tickets = tickets_result.scalars().all()
        
        # Create a mapping of booking_id to tickets
        tickets_by_booking = {}
        for ticket in all_tickets:
            if ticket.booking_id not in tickets_by_booking:
                tickets_by_booking[ticket.booking_id] = []
            tickets_by_booking[ticket.booking_id].append(ticket)
        
        # Collect all tickets
        tickets = []
        for booking in bookings:
            booking_tickets = tickets_by_booking.get(booking.booking_id, [])
            tickets.extend([ticket.to_dict() for ticket in booking_tickets])
            
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