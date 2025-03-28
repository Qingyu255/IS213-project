from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from pydantic import UUID4
from ..models.ticket import Ticket
from .base_service import BaseService
from ..schemas.booking import BookingStatus
import json
import pika
import time
import logging
from datetime import datetime
from typing import Dict, Any
from uuid import UUID

logger = logging.getLogger(__name__)

class TicketServiceException(Exception):
    """Custom exception for ticket service errors"""
    pass

class TicketService(BaseService):
    def __init__(self):
        super().__init__(Ticket)

    async def get_available_tickets(self, event_id: UUID4, db: AsyncSession) -> int:
        """Get count of available tickets for an event"""
        result = await db.execute("""
            SELECT COUNT(*) 
            FROM tickets t
            JOIN bookings b ON t.booking_id = b.booking_id
            WHERE b.event_id = :event_id 
            AND b.status IN ('pending', 'confirmed')
        """, {"event_id": event_id})

        return result.scalar()

# Get tickets by user_id
async def get_tickets_by_user_id(user_id: str, db: AsyncSession):
    results = await db.execute("""
        SELECT t.ticket_id, t.booking_id
        FROM tickets t
        JOIN bookings b ON t.booking_id = b.booking_id
        WHERE b.user_id = :user_id
    """, {"user_id": user_id})

    tickets = results.mappings().all()
    if not tickets:
        raise HTTPException(status_code=404, detail="No tickets found for this user")
    
    return tickets

# Get tickets by event_id
async def get_tickets_by_event(event_id: UUID4, db: AsyncSession):
    result = await db.execute("""
        SELECT t.ticket_id, t.booking_id
        FROM tickets t
        JOIN bookings b ON t.booking_id = b.booking_id
        WHERE b.event_id = :event_id
    """, {"event_id": event_id})

    tickets = result.mappings().all()
    if not tickets:
        raise HTTPException(status_code=404, detail="No tickets found for this event")
    
    return tickets

def _publish_message(self, routing_key: str, message: Dict[str, Any]) -> None:
    """Generic method to publish messages to RabbitMQ"""
    try:
        connection, channel = self._get_rabbitmq_channel()
        
        channel.basic_publish(
            exchange=self.exchange_name,
            routing_key=routing_key,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
                content_type='application/json',
                timestamp=int(time.time())
            )
        )
        connection.close()
        logger.info(f"Published message with routing key {routing_key}: {message}")
    except Exception as e:
        logger.error(f"Failed to publish message: {str(e)}")
        raise TicketServiceException(f"Failed to publish message: {str(e)}")

def update_booking_status(self, booking_id: str, status: str) -> None:
    """Update booking status via RabbitMQ"""
    try:
        booking_uuid = UUID(booking_id)
        
        # Get current booking to validate status transition
        current_booking = self.get_booking(booking_id)
        current_status = current_booking["status"]
        new_status = status.upper()
        
        # Validate status transition
        if not BookingStatus.can_transition_to(current_status, new_status):
            raise TicketServiceException(f"Cannot transition from {current_status} to {new_status}")
        
        # Send status update via RabbitMQ
        routing_key = self.routing_keys.get(new_status)
        if not routing_key:
            raise TicketServiceException(f"Invalid status: {status}")
        
        # Publish status update message
        message = {
            "booking_id": str(booking_uuid),
            "status": new_status,
            "timestamp": datetime.utcnow().isoformat(),
            "previous_status": current_status
        }
        
        self._publish_message(routing_key, message)
        
    except Exception as e:
        logger.error(f"Error updating booking status: {str(e)}")
        raise TicketServiceException(f"Failed to update booking status: {str(e)}")
        raise TicketServiceException(f"Failed to update booking status: {str(e)}")