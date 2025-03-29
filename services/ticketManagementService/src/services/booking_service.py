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
from uuid import UUID
from .logging_service import LoggingService
from sqlalchemy.orm import selectinload

class TicketFilterType(str, Enum):
    USER = "user_id"
    EVENT = "event_id"

class BookingService(BaseService):
    def __init__(self):
        super().__init__(Booking)
        self.logger = LoggingService()

    async def create_booking(self, booking_data: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
        """
        Create a new booking with initial ticket allocation.
        This is a synchronous operation (in terms of business logic) where everything happens in a single transaction:
        1. Create booking record
        2. Create ticket records
        3. Commit transaction
        4. Return complete booking details
        
        No async operations (like message queues) are used here to ensure data consistency.
        """
        try:
            # Start transaction
            async with db.begin():
                # 1. Create booking with PENDING status
                booking = Booking(
                    event_id=UUID(booking_data["event_id"]),
                    user_id=booking_data["user_id"],
                    status=BookingStatus.PENDING
                )
                db.add(booking)
                await db.flush()  # Flush to get the booking_id
                
                # 2. Create ticket records in the same transaction
                tickets = [
                    Ticket(
                        booking_id=booking.booking_id
                    )
                    for _ in range(booking_data["ticket_quantity"])
                ]
                db.add_all(tickets)
                
                # 3. Transaction will be committed automatically when the context exits
            
            # 4. Return complete booking details
            await self.logger.send_log(
                "INFO",
                f"Successfully created booking {booking.booking_id} with {len(tickets)} tickets",
                transaction_id=str(booking.booking_id)
            )
            return {
                "booking_id": str(booking.booking_id),
                "event_id": str(booking.event_id),
                "user_id": str(booking.user_id),  # Convert UUID to string
                "ticket_quantity": len(tickets),
                "total_amount": booking_data.get("total_amount", 0),  # Keep for API compatibility
                "status": booking.status,
                "created_at": booking.created_at,
                "updated_at": booking.updated_at,
                "tickets": [
                    {
                        "ticket_id": str(ticket.ticket_id),
                        "booking_id": str(ticket.booking_id),
                        "created_at": ticket.created_at
                    } for ticket in tickets
                ],
                "payment_url": f"/payment/{booking.booking_id}",  # Add payment URL
                "message": "Booking created successfully"
            }

        except Exception as e:
            # Transaction will be rolled back automatically on exception
            await self.logger.send_log(
                "ERROR",
                f"Error creating booking: {str(e)}"
            )
            raise HTTPException(status_code=500, detail=f"Failed to create booking: {str(e)}")

    async def handle_booking_status_update(self, data: Dict[str, Any], db: AsyncSession):
        """
        Handle asynchronous booking status updates via RabbitMQ.
        This method is truly asynchronous as it:
        1. Receives messages from queue
        2. Updates booking status
        3. Can handle retries and failures
        """
        try:
            booking_id = UUID(data["booking_id"])
            new_status = data["status"]
            
            # Get booking
            query = select(Booking).where(Booking.booking_id == booking_id)
            result = await db.execute(query)
            booking = result.scalar_one_or_none()
            
            if not booking:
                await self.logger.send_log(
                    "ERROR",
                    f"Booking not found for status update: {booking_id}",
                    transaction_id=str(booking_id)
                )
                return
            
            # Validate status transition
            if not BookingStatus.can_transition_to(booking.status, new_status):
                await self.logger.send_log(
                    "ERROR",
                    f"Invalid status transition from {booking.status} to {new_status}",
                    transaction_id=str(booking_id)
                )
                return
            
            async with db.begin():
                # Update booking status
                booking.status = new_status
            
            await self.logger.send_log(
                "INFO",
                f"Successfully processed booking status update: {booking_id} -> {new_status}",
                transaction_id=str(booking_id)
            )
            
        except Exception as e:
            await self.logger.send_log(
                "ERROR",
                f"Error processing booking status update: {str(e)}",
                transaction_id=str(data.get("booking_id", "unknown"))
            )
            # Let the message queue handle retries
            raise

    async def get_booking(self, booking_id: UUID, db: AsyncSession) -> Dict[str, Any]:
        """Get booking details with tickets"""
        query = (
            select(Booking)
            .where(Booking.booking_id == booking_id)
        )
        result = await db.execute(query)
        booking = result.scalar_one_or_none()
        
        if not booking:
            return None
        
        # Get associated tickets
        ticket_query = select(Ticket).where(Ticket.booking_id == booking_id)
        tickets = (await db.execute(ticket_query)).scalars().all()
            
        return {
            "booking_id": str(booking.booking_id),
            "event_id": str(booking.event_id),
            "user_id": str(booking.user_id),  # Convert UUID to string
            "ticket_quantity": len(tickets),  # Calculate from actual tickets
            "total_amount": 0,  # This will be updated by the booking service
            "status": booking.status,
            "created_at": booking.created_at,
            "updated_at": booking.updated_at,
            "tickets": [
                {
                    "ticket_id": str(ticket.ticket_id),
                    "booking_id": str(ticket.booking_id),
                    "created_at": ticket.created_at
                } for ticket in tickets
            ]
        }

    async def get_booking_by_id(self, booking_id: UUID4, db: AsyncSession) -> Dict[str, Any]:
        # Get booking with tickets relationship loaded
        query = (
            select(Booking)
            .options(selectinload(Booking.tickets))
            .where(Booking.booking_id == booking_id)
        )
        result = await db.execute(query)
        booking = result.scalar_one_or_none()
        
        if not booking:
            self.raise_not_found("Booking not found")
        
        # Create the response dict with consistent UUID handling
        booking_dict = {
            "booking_id": str(booking.booking_id),
            "user_id": str(booking.user_id),  # Ensure user_id is a string
            "event_id": str(booking.event_id),
            "status": booking.status.value if booking.status else None,
            "created_at": booking.created_at,
            "updated_at": booking.updated_at,
            "tickets": [
                {
                    "ticket_id": str(ticket.ticket_id),
                    "booking_id": str(ticket.booking_id),
                    "created_at": ticket.created_at
                } for ticket in booking.tickets
            ]
        }
        
        # Add required fields
        booking_dict['ticket_quantity'] = len(booking.tickets)
        booking_dict['total_amount'] = 0  # This will be updated by the booking service
        
        return booking_dict

    async def update_booking_status(self, booking_id: UUID4, new_status: BookingStatus, db: AsyncSession) -> Dict[str, str]:
        """Update booking status with validation."""
        # Get booking with tickets relationship loaded in a single query
        query = (
            select(Booking)
            .options(selectinload(Booking.tickets))
            .where(Booking.booking_id == booking_id)
        )
        result = await db.execute(query)
        booking = result.scalar_one_or_none()
        
        if not booking:
            self.raise_not_found("Booking not found")

        if not BookingStatus.can_transition_to(booking.status, new_status):
            self.raise_validation_error(f"Cannot transition from {booking.status} to {new_status}")

        # Update the status in the same transaction
        booking.status = new_status
        await db.commit()
        
        return {"message": f"Booking {new_status} successfully"}

    async def get_tickets(self, filter_value, filter_type: TicketFilterType, db: AsyncSession) -> List[Dict[str, Any]]:
        """Get tickets filtered by user_id or event_id."""
        query = select(Booking)
        
        if filter_type == TicketFilterType.USER:
            try:
                user_uuid = UUID(str(filter_value))
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