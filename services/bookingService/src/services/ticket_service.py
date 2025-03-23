import httpx
from typing import Dict, Any, List
from uuid import UUID
from enum import Enum
from datetime import datetime
from ..core.config import get_settings
from ..core.rabbitmq import RabbitMQClient

settings = get_settings()

class BookingStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELED = "CANCELED"
    REFUNDED = "REFUNDED"

    @classmethod
    def can_transition_to(cls, current_status: str, new_status: str) -> bool:
        """Validate status transitions based on atomic service rules"""
        transitions = {
            cls.PENDING: [cls.CONFIRMED, cls.CANCELED],
            cls.CONFIRMED: [cls.REFUNDED],
            cls.CANCELED: [],
            cls.REFUNDED: []
        }
        return cls(new_status) in transitions.get(cls(current_status), [])

class TicketService:
    def __init__(self):
        self.base_url = f"{settings.TICKET_SERVICE_URL}/api/v1"
        self.timeout = httpx.Timeout(10.0)
        self.rabbitmq = RabbitMQClient()
        self.exchange_name = "tickets"  # Match atomic service exchange name
        # Map status to routing keys
        self.routing_keys = {
            BookingStatus.CONFIRMED.value: "booking.confirmed",
            BookingStatus.CANCELED.value: "booking.cancelled",
            BookingStatus.REFUNDED.value: "booking.refunded",
            BookingStatus.PENDING.value: "booking.status_updated"
        }

    async def check_availability(self, event_id: str, ticket_quantity: int) -> Dict[str, Any]:
        """Check ticket availability for an event"""
        try:
            event_uuid = UUID(event_id)
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/tickets/event/{event_uuid}/available"
                )
                response.raise_for_status()
                return response.json()  # Returns {"available_tickets": int}
        except Exception as e:
            print(f"Error checking ticket availability: {str(e)}")
            raise

    async def create_booking(
        self,
        event_id: str,
        user_id: str,
        ticket_quantity: int,
        total_amount: float
    ) -> Dict[str, Any]:
        """Create a new booking"""
        try:
            # Convert string IDs to UUIDs as expected by atomic service
            event_uuid = UUID(event_id)
            user_uuid = UUID(user_id)
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/bookings/book",
                    json={
                        "event_id": str(event_uuid),
                        "user_id": str(user_uuid),
                        "ticket_count": ticket_quantity,  # Match atomic service field name
                        "total_amount": total_amount
                    }
                )
                response.raise_for_status()
                return response.json()  # Returns BookingResponse model
        except Exception as e:
            print(f"Error creating booking: {str(e)}")
            raise

    async def update_booking_status(self, booking_id: str, status: str) -> None:
        """Update booking status via HTTP and notify ticket service via RabbitMQ"""
        try:
            booking_uuid = UUID(booking_id)
            
            # Get current booking to validate status transition
            current_booking = await self.get_booking(booking_id)
            current_status = current_booking["status"]
            new_status = status.upper()
            
            # Validate status transition
            if not BookingStatus.can_transition_to(current_status, new_status):
                raise ValueError(f"Cannot transition from {current_status} to {new_status}")
            
            # First update via HTTP
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                endpoint = {
                    BookingStatus.CONFIRMED.value: "confirm",
                    BookingStatus.CANCELED.value: "cancel",
                    BookingStatus.REFUNDED.value: "refund"
                }.get(new_status)
                
                if not endpoint:
                    raise ValueError(f"Status {status} cannot be updated via HTTP")
                
                response = await client.post(
                    f"{self.base_url}/bookings/{booking_uuid}/{endpoint}"
                )
                response.raise_for_status()

            # Get the appropriate routing key for the status
            routing_key = self.routing_keys.get(new_status, "booking.status_updated")

            # Publish status update event
            await self.rabbitmq.publish_message(
                self.exchange_name,
                routing_key,
                {
                    "booking_id": str(booking_uuid),
                    "status": new_status,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        except Exception as e:
            print(f"Error updating booking status: {str(e)}")
            raise

    async def get_booking(self, booking_id: str) -> Dict[str, Any]:
        """Get booking details with tickets"""
        try:
            booking_uuid = UUID(booking_id)
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/bookings/{booking_uuid}"
                )
                response.raise_for_status()
                return response.json()  # Returns BookingResponse model with tickets
        except Exception as e:
            print(f"Error getting booking details: {str(e)}")
            raise

    async def get_user_bookings(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all bookings for a user"""
        try:
            user_uuid = UUID(user_id)
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/bookings/user/{user_uuid}"
                )
                response.raise_for_status()
                return response.json()  # Returns List[BookingResponse]
        except Exception as e:
            print(f"Error getting user bookings: {str(e)}")
            raise

    async def get_event_tickets(self, event_id: str) -> List[Dict[str, Any]]:
        """Get all tickets for an event"""
        try:
            event_uuid = UUID(event_id)
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/tickets/event/{event_uuid}"
                )
                response.raise_for_status()
                return response.json()  # Returns List[TicketResponse]
        except Exception as e:
            print(f"Error getting event tickets: {str(e)}")
            raise

    async def get_user_event_tickets(self, user_id: str, event_id: str) -> List[Dict[str, Any]]:
        """Get user's tickets for a specific event"""
        try:
            user_uuid = UUID(user_id)
            event_uuid = UUID(event_id)
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/tickets/user/{user_uuid}/event/{event_uuid}"
                )
                response.raise_for_status()
                return response.json()  # Returns List[TicketResponse]
        except Exception as e:
            print(f"Error getting user event tickets: {str(e)}")
            raise