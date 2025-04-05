import requests
import time
from typing import Dict, Any, List, Optional
from uuid import UUID
from enum import Enum
from datetime import datetime
from ..core.config import get_settings
from ..core.logging import logger
from fastapi import HTTPException
from .rabbitmq_service import RabbitMQService
from .logging_service import LoggingService
import logging

settings = get_settings()
logger = logging.getLogger(__name__)

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
        self.base_url = settings.TICKET_SERVICE_URL
        self.timeout = 10.0
        self.max_retries = 3
        self.initial_backoff = 1.0
        
        # Initialize services
        self.rabbitmq = RabbitMQService("ticket_service", "booking")
        self.logger = LoggingService("ticket_service")
        
        # Define routing keys
        self.routing_keys = {
            "CONFIRMED": "booking.confirmed",
            "CANCELLED": "booking.cancelled",
            "REFUNDED": "booking.refunded"
        }

    def _make_request_with_retry(
        self,
        method: str,
        endpoint: str,
        auth_token: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Make HTTP request with retry mechanism"""
        retries = 0
        backoff = self.initial_backoff
        kwargs['timeout'] = self.timeout

        if auth_token:
            if 'headers' not in kwargs:
                kwargs['headers'] = {}
            if not auth_token.startswith('Bearer '):
                auth_token = f"Bearer {auth_token}"
            kwargs['headers']['Authorization'] = auth_token
            logger.debug(f"Added auth token to request headers: {auth_token[:20]}...")

        while retries < self.max_retries:
            try:
                url = f"{self.base_url}/{endpoint}"
                logger.debug(f"Making {method.upper()} request to {url}")
                response = getattr(requests, method)(url, **kwargs)
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

    def get_booking(self, booking_id: str, auth_token: str = None) -> Dict[str, Any]:
        """Get booking details"""
        try:
            return self._make_request_with_retry(
                "get",
                f"api/v1/bookings/{booking_id}",
                auth_token=auth_token
            )
        except Exception as e:
            logger.error(f"Error getting booking details: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def update_booking_status(
        self,
        booking_id: str,
        status: str,
        auth_token: str = None
    ) -> Dict[str, Any]:
        """Update booking status"""
        try:
            # Map the endpoint based on the status
            status_endpoints = {
                BookingStatus.CONFIRMED.value: "confirm",
                BookingStatus.CANCELED.value: "cancel",
                BookingStatus.REFUNDED.value: "refund"
            }
            
            endpoint = status_endpoints.get(status)
            if not endpoint:
                raise ValueError(f"Invalid status transition to {status}")

            logger.debug(f"Updating booking {booking_id} to status {status} using endpoint {endpoint}")
            
            return self._make_request_with_retry(
                "post",  # Changed from put to post as the endpoints use POST
                f"api/v1/bookings/{booking_id}/{endpoint}",
                auth_token=auth_token
            )
        except ValueError as e:
            logger.error(f"Invalid status update: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Error updating booking status: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def get_user_bookings(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all bookings for a user"""
        try:
            user_uuid = UUID(user_id)
            return self._make_request_with_retry(
                "get",
                f"api/v1/bookings/user/{user_uuid}"
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
                f"api/v1/tickets/event/{event_uuid}"
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
                f"api/v1/tickets/user/{user_uuid}/event/{event_uuid}"
            )
        except Exception as e:
            logger.error(f"Error getting user event tickets: {str(e)}")
            raise TicketServiceException(f"Failed to get user event tickets: {str(e)}")

    def create_booking(
        self,
        event_id: str,
        user_id: str,
        ticket_quantity: int,
        total_amount: float,
        auth_token: str = None,
        email: str = None
    ) -> Dict[str, Any]:
        """Create a new booking"""
        try:
            # Prepare request data according to BookingRequest schema
            booking_data = {
                "event_id": event_id,  # Send as string
                "ticket_quantity": ticket_quantity,
                "total_amount": total_amount
                # user_id is optional, it will be taken from the token
            }

            # Make the request
            return self._make_request_with_retry(
                "post",
                "api/v1/bookings/book",
                auth_token=auth_token,
                json=booking_data
            )
        except TicketServiceException as e:
            logger.error(f"Error creating booking: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            logger.error(f"Unexpected error creating booking: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def get_available_tickets(self, event_id: str, auth_token: str) -> dict:
        """Check ticket availability for an event"""
        try:
            response = self._make_request_with_retry(
                "get",
                f"api/v1/tickets/event/{event_id}/available",
                auth_token=auth_token
            )
            logger.debug(f"Raw ticket service response: {response}")
            logger.debug(f"Response type: {type(response)}")
            logger.debug(f"available_tickets value: {response['available_tickets']}")
            logger.debug(f"available_tickets type: {type(response['available_tickets'])}")
            # Response now includes total_capacity and booked_tickets
            return {
                "available_tickets": response["available_tickets"],
                "total_capacity": response["total_capacity"],
                "booked_tickets": response["booked_tickets"]
            }
        except Exception as e:
            logger.error(f"Error checking ticket availability: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to check ticket availability"
            )