import requests
import time
from typing import Dict, Any, List, Optional
from uuid import UUID
from enum import Enum
from datetime import datetime
from ..core.config import get_settings
from fastapi import HTTPException
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
            cls.CONFIRMED: [cls.REFUNDED, cls.CANCELED],
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
        self.logger = LoggingService("ticket_service")

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
                    error_msg = f"Network error after {retries} retries: {str(e)}"
                    logger.error(error_msg)
                    self.logger.log_error(
                        "Network error in ticket service",
                        error_type="ConnectionError",
                        error_details=str(e),
                        retries=retries
                    )
                    raise TicketServiceException(error_msg)
                logger.warning(f"Network error (attempt {retries}/{self.max_retries}): {str(e)}")
                time.sleep(backoff)
                backoff *= 2
            except requests.exceptions.HTTPError as e:
                error_msg = f"HTTP error: {str(e)}"
                logger.error(error_msg)
                self.logger.log_error(
                    "HTTP error in ticket service",
                    error_type="HTTPError",
                    error_details=str(e),
                    status_code=e.response.status_code
                )
                raise TicketServiceException(error_msg)
            except Exception as e:
                error_msg = f"Unexpected error: {str(e)}"
                logger.error(error_msg)
                self.logger.log_error(
                    "Unexpected error in ticket service",
                    error_type="UnexpectedError",
                    error_details=str(e)
                )
                raise TicketServiceException(error_msg)

    def get_booking(self, booking_id: str, auth_token: str = None) -> Dict[str, Any]:
        """Get booking details"""
        try:
            return self._make_request_with_retry(
                "get",
                f"api/v1/mgmt/bookings/{booking_id}",
                auth_token=auth_token
            )
        except Exception as e:
            error_msg = f"Error getting booking details: {str(e)}"
            logger.error(error_msg)
            self.logger.log_error(
                "Error getting booking details",
                transaction_id=booking_id,
                error_type="GetBookingError",
                error_details=str(e)
            )
            raise HTTPException(status_code=500, detail=error_msg)

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
                "CONFIRMED": "confirm",
                "CANCELED": "cancel",
                "REFUNDED": "refund"
            }
            
            endpoint = status_endpoints.get(status)
            if not endpoint:
                error_msg = f"Invalid status transition to {status}"
                logger.error(error_msg)
                self.logger.log_error(
                    "Invalid status transition",
                    transaction_id=booking_id,
                    error_type="InvalidStatus",
                    current_status=status
                )
                raise ValueError(error_msg)
            
            logger.info(f"Updating booking {booking_id} to status {status}")
            result = self._make_request_with_retry(
                "post",
                f"api/v1/mgmt/bookings/{booking_id}/{endpoint}",
                auth_token=auth_token
            )

            logger.info(f"Successfully updated booking {booking_id} to {status}")
            
            # Log based on the status type
            if status == BookingStatus.CONFIRMED.value:
                self.logger.log_booking_confirmation(
                    booking_id=booking_id,
                    transaction_id=booking_id
                )
            elif status == BookingStatus.CANCELED.value:
                self.logger.log_booking_cancellation(
                    booking_id=booking_id,
                    transaction_id=booking_id
                )

            return result

        except ValueError as e:
            error_msg = str(e)
            logger.error(error_msg)
            self.logger.log_error(
                "Invalid status update",
                transaction_id=booking_id,
                error_type="InvalidStatus",
                error_details=error_msg
            )
            raise HTTPException(status_code=400, detail=error_msg)
        except Exception as e:
            error_msg = f"Error updating booking status: {str(e)}"
            logger.error(error_msg)
            self.logger.log_error(
                "Error updating booking status",
                transaction_id=booking_id,
                error_type="UpdateStatusError",
                error_details=str(e)
            )
            raise HTTPException(status_code=500, detail=error_msg)

    def get_user_bookings(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all bookings for a user"""
        try:
            user_uuid = UUID(user_id)
            return self._make_request_with_retry(
                "get",
                f"api/v1/mgmt/bookings/user/{user_uuid}"
            )
        except Exception as e:
            error_msg = f"Failed to get user bookings: {str(e)}"
            logger.error(error_msg)
            self.logger.log_error(
                "Error getting user bookings",
                transaction_id=user_id,
                error_type="GetUserBookingsError",
                error_details=str(e)
            )
            raise TicketServiceException(error_msg)

    def get_event_tickets(self, event_id: str) -> List[Dict[str, Any]]:
        """Get all tickets for an event"""
        try:
            event_uuid = UUID(event_id)
            return self._make_request_with_retry(
                "get",
                f"api/v1/tickets/event/{event_uuid}"
            )
        except Exception as e:
            self.logger.log_error(
                "Error getting event tickets",
                transaction_id=event_id,
                error_type="GetEventTicketsError",
                error_details=str(e),
                event_id=event_id
            )
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
            self.logger.log_error(
                "Error getting user event tickets",
                transaction_id=f"{user_id}_{event_id}",
                error_type="GetUserEventTicketsError",
                error_details=str(e),
                user_id=user_id,
                event_id=event_id
            )
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
            logger.info(f"Creating booking for event {event_id}")
            # Prepare request data according to BookingRequest schema
            booking_data = {
                "event_id": event_id,
                "ticket_quantity": ticket_quantity,
                "total_amount": total_amount
            }

            result = self._make_request_with_retry(
                "post",
                "api/v1/mgmt/bookings/book",
                auth_token=auth_token,
                json=booking_data
            )

            logger.info(f"Successfully created booking {result['booking_id']}")
            self.logger.log_booking_creation(
                booking_id=result["booking_id"],
                transaction_id=result["booking_id"]
            )

            return result

        except Exception as e:
            error_msg = f"Error creating booking: {str(e)}"
            logger.error(error_msg)
            self.logger.log_error(
                "Error creating booking",
                transaction_id=event_id,
                error_type="CreateBookingError",
                error_details=str(e),
                event_id=event_id,
                user_id=user_id
            )
            raise HTTPException(status_code=500, detail=error_msg)

    def get_available_tickets(self, event_id: str, auth_token: str) -> dict:
        """Check ticket availability for an event"""
        try:
            logger.debug(f"Checking ticket availability for event {event_id}")
            response = self._make_request_with_retry(
                "get",
                f"api/v1/tickets/event/{event_id}/available",
                auth_token=auth_token
            )
            logger.debug(f"Ticket availability response: {response}")
            return {
                "available_tickets": response["available_tickets"],
                "total_capacity": response["total_capacity"],
                "booked_tickets": response["booked_tickets"]
            }
        except Exception as e:
            error_msg = f"Failed to check ticket availability: {str(e)}"
            logger.error(error_msg)
            self.logger.log_error(
                "Error checking ticket availability",
                transaction_id=event_id,
                error_type="AvailabilityCheckError",
                error_details=str(e),
                event_id=event_id
            )
            raise HTTPException(
                status_code=500,
                detail=error_msg
            )