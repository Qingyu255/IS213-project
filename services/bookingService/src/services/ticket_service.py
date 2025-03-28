import requests
import pika
import json
import time
from typing import Dict, Any, List, Optional
from uuid import UUID
from enum import Enum
from datetime import datetime
from ..core.config import get_settings
from ..core.logging import logger

settings = get_settings()

class TicketServiceException(Exception):
    """Custom exception for ticket service errors"""
    pass

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
        self.timeout = 10.0
        self.max_retries = 3
        self.initial_backoff = 1.0
        # RabbitMQ setup
        self.connection_params = pika.URLParameters(settings.RABBITMQ_URL)
        self.exchange_name = "tickets"
        self.routing_keys = {
            BookingStatus.CONFIRMED.value: "booking.confirmed",
            BookingStatus.CANCELED.value: "booking.cancelled",
            BookingStatus.REFUNDED.value: "booking.refunded",
            BookingStatus.PENDING.value: "booking.status_updated"
        }

    def _get_rabbitmq_channel(self):
        """Create a new RabbitMQ connection and channel"""
        connection = pika.BlockingConnection(self.connection_params)
        channel = connection.channel()
        channel.exchange_declare(
            exchange=self.exchange_name,
            exchange_type='topic',
            durable=True
        )
        return connection, channel

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

    def _make_request_with_retry(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Make HTTP request with retry mechanism"""
        retries = 0
        backoff = self.initial_backoff
        kwargs['timeout'] = self.timeout

        while retries < self.max_retries:
            try:
                response = getattr(requests, method)(
                    f"{self.base_url}/{endpoint}",
                    **kwargs
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.ConnectionError as e:
                retries += 1
                if retries == self.max_retries:
                    logger.error(f"Network error after {retries} retries: {str(e)}")
                    raise TicketServiceException(f"Network error: {str(e)}")
                logger.warning(f"Network error (attempt {retries}/{self.max_retries}): {str(e)}")
                time.sleep(backoff)
                backoff *= 2
            except requests.exceptions.HTTPError as e:
                logger.error(f"HTTP error: {str(e)}")
                raise TicketServiceException(f"HTTP error: {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
                raise TicketServiceException(f"Unexpected error: {str(e)}")

    def check_availability(self, event_id: str, ticket_quantity: int) -> Dict[str, Any]:
        """Check ticket availability for an event"""
        try:
            event_uuid = UUID(event_id)
            return self._make_request_with_retry(
                "get",
                f"tickets/event/{event_uuid}/available"
            )
        except Exception as e:
            logger.error(f"Error checking ticket availability: {str(e)}")
            raise TicketServiceException(f"Failed to check availability: {str(e)}")

    def create_booking(
        self,
        event_id: str,
        user_id: str,
        ticket_quantity: int,
        total_amount: float
    ) -> Dict[str, Any]:
        """Create a new booking"""
        try:
            event_uuid = UUID(event_id)
            user_uuid = UUID(user_id)
            
            # First create the booking via HTTP
            payload = {
                "event_id": str(event_uuid),
                "user_id": str(user_uuid),
                "ticket_count": ticket_quantity,
                "total_amount": total_amount
            }
            
            response = self._make_request_with_retry(
                "post",
                "bookings/book",
                json=payload
            )
            
            # Publish initial status
            self._publish_message(
                self.routing_keys[BookingStatus.PENDING.value],
                {
                    "booking_id": response["id"],
                    "status": BookingStatus.PENDING.value,
                    "timestamp": datetime.utcnow().isoformat(),
                    "metadata": {
                        "event_id": str(event_uuid),
                        "user_id": str(user_uuid),
                        "ticket_count": ticket_quantity
                    }
                }
            )
            
            return response
        except Exception as e:
            logger.error(f"Error creating booking: {str(e)}")
            raise TicketServiceException(f"Failed to create booking: {str(e)}")

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

    def get_booking(self, booking_id: str) -> Dict[str, Any]:
        """Get booking details with tickets"""
        try:
            booking_uuid = UUID(booking_id)
            return self._make_request_with_retry(
                "get",
                f"bookings/{booking_uuid}"
            )
        except Exception as e:
            logger.error(f"Error getting booking details: {str(e)}")
            raise TicketServiceException(f"Failed to get booking details: {str(e)}")

    def get_user_bookings(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all bookings for a user"""
        try:
            user_uuid = UUID(user_id)
            return self._make_request_with_retry(
                "get",
                f"bookings/user/{user_uuid}"
            )
        except Exception as e:
            logger.error(f"Error getting user bookings: {str(e)}")
            raise TicketServiceException(f"Failed to get user bookings: {str(e)}")

    def get_event_tickets(self, event_id: str) -> List[Dict[str, Any]]:
        """Get all tickets for an event"""
        try:
            event_uuid = UUID(event_id)
            return self._make_request_with_retry(
                "get",
                f"tickets/event/{event_uuid}"
            )
        except Exception as e:
            logger.error(f"Error getting event tickets: {str(e)}")
            raise TicketServiceException(f"Failed to get event tickets: {str(e)}")

    def get_user_event_tickets(self, user_id: str, event_id: str) -> List[Dict[str, Any]]:
        """Get user's tickets for a specific event"""
        try:
            user_uuid = UUID(user_id)
            event_uuid = UUID(event_id)
            return self._make_request_with_retry(
                "get",
                f"tickets/user/{user_uuid}/event/{event_uuid}"
            )
        except Exception as e:
            logger.error(f"Error getting user event tickets: {str(e)}")
            raise TicketServiceException(f"Failed to get user event tickets: {str(e)}")