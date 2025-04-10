from fastapi import APIRouter, HTTPException, Depends, Path, Query, Security, Header, Body
from typing import Optional, List
import uuid
from ...schemas.booking import BookingCreate, BookingResponse, BookingStatus
from ...services.event_service import EventService
from ...services.ticket_service import TicketService
from ...services.billing_service import BillingService, BillingServiceException
from ...services.notification_service import NotificationService
from ...services.logging_service import LoggingService
from ...core.logging import logger
from ...core.auth import validate_token
from datetime import datetime
from pydantic import BaseModel
from ...core.config import get_settings
import logging
from sqlalchemy.orm import Session

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()

settings = get_settings()

class PaymentConfirmation(BaseModel):
    payment_intent_id: str
    amount: int
    currency: str

class BookingController:
    def __init__(
        self,
        event_service: EventService,
        ticket_service: TicketService,
        billing_service: BillingService,
        notification_service: NotificationService,
        logging_service: LoggingService
    ):
        self.event_service = event_service
        self.ticket_service = ticket_service
        self.billing_service = billing_service
        self.notification_service = notification_service
        self.logging_service = logging_service

    def create_booking(
        self,
        booking_details: BookingCreate,
        auth_token: str
    ) -> BookingResponse:
        """Create a new booking with proper orchestration of all services"""
        error = None
        transaction_id = str(uuid.uuid4())
        
        try:
            # 1. Log incoming request
            self.logging_service.log_booking_request(
                booking_details=booking_details.dict(),
                transaction_id=transaction_id
            )
            
            # 2. Get event details and safely convert price once
            event = self.event_service.get_event(booking_details.event_id)
            if not event:
                self.logging_service.log_error(
                    "Event not found",
                    transaction_id=transaction_id,
                    event_id=booking_details.event_id
                )
                raise HTTPException(status_code=404, detail="Event not found")
            
            try:
                price = float(event.get("price", 0))
                capacity = int(event.get("capacity", 0))
            except ValueError:
                self.logging_service.log_error(
                    "Invalid price or capacity format in event data",
                    transaction_id=transaction_id,
                    event_data=event
                )
                raise HTTPException(status_code=400, detail="Invalid price or capacity format in event data")

            # 3. Check ticket availability
            availability = self.ticket_service.get_available_tickets(
                event_id=booking_details.event_id,
                auth_token=auth_token
            )

            available_tickets = int(availability["available_tickets"])
            total_capacity = int(availability["total_capacity"])

            if total_capacity == 0:
                logger.debug("Unlimited tickets detected, allowing booking")
                pass
            else:
                # Simple numeric comparison
                if int(available_tickets) < int(booking_details.ticket_quantity):
                    self.logging_service.log_error(
                        "Insufficient tickets available",
                        transaction_id=transaction_id,
                        available=available_tickets,
                        requested=booking_details.ticket_quantity
                    )
                    raise HTTPException(
                        status_code=400,
                        detail=f"Only {available_tickets} tickets available"
                    )

            # 4. Create booking record
            booking = self.ticket_service.create_booking(
                event_id=booking_details.event_id,
                user_id=booking_details.user_id,
                ticket_quantity=booking_details.ticket_quantity,
                total_amount=price * booking_details.ticket_quantity,
                auth_token=auth_token,
                email=booking_details.email
            )

            # 5. If event is free, auto-confirm the booking
            if price == 0:
                self.ticket_service.update_booking_status(
                    booking_id=booking["booking_id"],
                    status=BookingStatus.CONFIRMED.value,
                    auth_token=auth_token
                )

                # 4. Get user details from token claims
                claims = validate_token(auth_token)
                user_email = claims.get("email")  # Get email from token claims

                # Send confirmation for free event
                try:
                    self.notification_service.send_booking_confirmation(
                        booking_id=booking["booking_id"],
                        customer_email=user_email,
                        event_name=event["title"],
                        ticket_quantity=booking["ticket_quantity"],
                        total_amount=0,
                        event_start_datetime=event["startDateTime"],
                        event_end_datetime=event["endDateTime"]
                    )
                    self.logging_service.log_email_sent(
                        booking_id=booking["booking_id"],
                        transaction_id=transaction_id,
                        email=user_email
                    )
                except Exception as e:
                    self.logging_service.log_error(
                        f"Error sending free event confirmation: {str(e)}",
                        transaction_id=transaction_id,
                        booking_id=booking["booking_id"],
                        email=user_email
                    )

            return BookingResponse(
                status=BookingStatus.CONFIRMED.value if price == 0 else BookingStatus.PENDING.value,
                booking_id=booking["booking_id"],
                event_id=booking_details.event_id,
                user_id=booking_details.user_id,
                ticket_quantity=booking_details.ticket_quantity,
                created_at=booking.get("created_at", datetime.now()),
                message="Free event booking confirmed successfully" if price == 0 else "Pending payment"
            )

        except HTTPException as he:
            self.logging_service.log_error(
                f"HTTP Exception: {he.detail}",
                transaction_id=transaction_id,
                status_code=he.status_code,
                error_type="HTTPException"
            )
            raise he
        except Exception as e:
            error = f"An unexpected error occurred: {str(e)}"
            self.logging_service.log_error(
                error,
                transaction_id=transaction_id,
                error_type=type(e).__name__,
                error_details=str(e)
            )
            raise HTTPException(status_code=500, detail=error)
        finally:
            if error:
                self.logging_service.send_log(
                    level="error",
                    message=error,
                    transaction_id=transaction_id
                )

    def get_booking(self, booking_id: str, auth_token: str = None) -> dict:
        """Get booking details"""
        try:
            booking = self.ticket_service.get_booking(booking_id, auth_token)
            return booking
        except Exception as e:
            logger.error(f"Error getting booking: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def get_user_bookings(self, user_id: str) -> List[dict]:
        """Get all bookings for a user"""
        try:
            return self.ticket_service.get_user_bookings(user_id)
        except Exception as e:
            logger.error(f"Error getting bookings for user {user_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def confirm_booking(
        self,
        booking_id: str,
        payment_confirmation: PaymentConfirmation,
        authorization: str
    ) -> BookingResponse:
        """Confirm a booking after successful payment"""
        try:
            # 1. Get booking details
            booking = self.ticket_service.get_booking(booking_id, authorization)
            if not booking:
                self.logging_service.log_error(
                    "Booking not found",
                    transaction_id=booking_id,
                    booking_id=booking_id,
                    error_type="BookingNotFound"
                )
                raise HTTPException(status_code=404, detail="Booking not found")

            # 2. Update booking status
            self.ticket_service.update_booking_status(
                booking_id=booking_id,
                status=BookingStatus.CONFIRMED.value,
                auth_token=authorization
            )

            # 3. Get event details
            event = self.event_service.get_event(booking["event_id"])
            if not event:
                self.logging_service.log_error(
                    "Event not found",
                    transaction_id=booking_id,
                    event_id=booking["event_id"],
                    error_type="EventNotFound"
                )
                raise HTTPException(status_code=404, detail="Event not found")

            # 4. Get user details from token claims
            claims = validate_token(authorization)
            user_email = claims.get("email")  # Get email from token claims
            if not user_email:
                logger.error("No email found in token claims")
                raise HTTPException(status_code=400, detail="User email not found")

            # 5. Send confirmation notification
            try:
                self.notification_service.send_booking_confirmation(
                    booking_id=booking_id,
                    customer_email=user_email,  # Use email from token claims
                    event_name=event["title"],
                    ticket_quantity=booking["ticket_quantity"],
                    total_amount=float(payment_confirmation.amount) / 100,  # Amount from payment confirmation
                    event_start_datetime=event["startDateTime"],
                    event_end_datetime=event["endDateTime"],
                )
                
                self.logging_service.log_email_sent(
                    booking_id=booking_id,
                    transaction_id=booking_id,
                    email=user_email
                )
                
            except Exception as e:
                self.logging_service.log_error(
                    f"Error sending confirmation email",
                    transaction_id=booking_id,
                    booking_id=booking_id,
                    email=user_email,
                    error_type="EmailError",
                    error_details=str(e)
                )

            return BookingResponse(
                status=BookingStatus.CONFIRMED.value,
                booking_id=booking_id,
                event_id=booking["event_id"],
                user_id=booking["user_id"],
                ticket_quantity=booking["ticket_quantity"],
                created_at=booking.get("created_at", datetime.now()),
                message="Booking confirmed successfully"
            )

        except HTTPException:
            raise
        except BillingServiceException as be:
            self.logging_service.log_error(
                f"Billing service error: {str(be)}",
                transaction_id=booking_id,
                booking_id=booking_id,
                error_type="BillingServiceException",
                error_details=str(be)
            )
            raise HTTPException(status_code=400, detail=str(be))
        except Exception as e:
            self.logging_service.log_error(
                f"Error confirming booking",
                transaction_id=booking_id,
                booking_id=booking_id,
                error_type=type(e).__name__,
                error_details=str(e)
            )
            raise HTTPException(status_code=500, detail=str(e))

    def create_payment_session(self, booking_id: str, event: dict, quantity: int) -> dict:
        """Create a payment session for a booking"""
        amount = float(event["price"]) * quantity
        return self.billing_service.create_payment_session(
            booking_id=booking_id,
            amount=amount,
            event_title=event["name"],
            quantity=quantity
        )

    def verify_payment(self, booking_id: str) -> tuple[bool, Optional[str]]:
        """Verify payment status for a booking"""
        return self.billing_service.verify_payment_completed(booking_id)

# Dependency Injection
def get_booking_controller():
    event_service = EventService()
    ticket_service = TicketService()
    billing_service = BillingService()
    notification_service = NotificationService()
    logging_service = LoggingService("booking_service")
    return BookingController(
        event_service,
        ticket_service,
        billing_service,
        notification_service,
        logging_service
    )

# API Routes
@router.post("/bookings", response_model=BookingResponse)
def create_booking(
    booking_details: BookingCreate,
    authorization: str = Header(...),
    controller: BookingController = Depends(get_booking_controller)
):
    """Create a new booking"""
    try:
        # Validate the token and get claims
        claims = validate_token(authorization)
        
        # Log the token and claims for debugging
        logger.debug(f"Using auth token: {authorization[:20]}...")
        logger.debug(f"Token claims: {claims}")
        
        return controller.create_booking(
            booking_details=booking_details,
            auth_token=authorization  # Pass the full Bearer token
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating booking: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/bookings/{booking_id}")
def get_booking(
    booking_id: str = Path(..., description="The ID of the booking to retrieve"),
    authorization: str = Header(None),
    controller: BookingController = Depends(get_booking_controller)
):
    """Get booking details"""
    try:
        if authorization:
            claims = validate_token(authorization)
            logger.debug(f"Token claims for get_booking: {claims}")
        return controller.get_booking(booking_id, authorization)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting booking: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/bookings/user/{user_id}")
def get_user_bookings(
    user_id: str = Path(..., description="The ID of the user"),
    authorization: str = Header(...),
    controller: BookingController = Depends(get_booking_controller)
):
    """Get all bookings for a user"""
    try:
        claims = validate_token(authorization)
        logger.debug(f"Token claims: {claims}")
        logger.debug(f"Requested user_id: {user_id}")
        logger.debug(f"User ID from token (custom:id): {claims.get('custom:id')}")
        
        if claims.get('custom:id') != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to view these bookings")
        return controller.get_user_bookings(user_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user bookings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bookings/{booking_id}/confirm")
def confirm_booking(
    booking_id: str = Path(..., description="The ID of the booking to confirm"),
    session_id: str = Query(..., description="The Stripe session ID"),
    authorization: str = Header(...),
    booking_controller: BookingController = Depends(get_booking_controller)
):
    """Confirm a booking after successful payment"""
    try:
        # Validate the token and get claims
        claims = validate_token(authorization)
        logger.debug(f"Using auth token: {authorization}")
        logger.debug(f"Token claims: {claims}")

        # Get the booking to verify ownership
        booking = booking_controller.get_booking(booking_id, authorization)
        if not booking:
            booking_controller.logging_service.log_error(
                "Booking not found during confirmation",
                transaction_id=booking_id,
                error_type="BookingNotFound",
                session_id=session_id
            )
            raise HTTPException(status_code=404, detail="Booking not found")

        # Log booking details for debugging
        booking_controller.logging_service.log_booking_request(
            booking_details={
                "booking_id": booking_id,
                "status": booking["status"],
                "user_id": booking["user_id"],
                "event_id": booking["event_id"],
                "action": "process_confirmation"
            },
            transaction_id=booking_id
        )

        # Verify the user owns the booking using custom:id
        if booking["user_id"] != claims.get('custom:id'):
            booking_controller.logging_service.log_error(
                "Unauthorized confirmation attempt",
                transaction_id=booking_id,
                error_type="UnauthorizedConfirmation",
                requesting_user=claims.get('custom:id'),
                booking_owner=booking["user_id"]
            )
            raise HTTPException(status_code=403, detail="Not authorized to confirm this booking")

        # Get event details to verify the amount
        event = booking_controller.event_service.get_event(booking["event_id"])
        if not event:
            booking_controller.logging_service.log_error(
                "Event not found during confirmation",
                transaction_id=booking_id,
                error_type="EventNotFound",
                event_id=booking["event_id"]
            )
            raise HTTPException(status_code=404, detail="Event not found")

        # Calculate total amount
        total_amount = int(float(event["price"]) * booking["ticket_quantity"] * 100)  # Convert to cents

        # Create payment confirmation
        payment_confirmation = PaymentConfirmation(
            payment_intent_id=session_id,
            amount=total_amount,
            currency="sgd"
        )

        # Verify payment completion before confirming

        is_paid, error = booking_controller.verify_payment(booking_id)
        if not is_paid:
            booking_controller.logging_service.log_error(
                f"Payment verification failed",
                transaction_id=booking_id,
                error_type="PaymentVerificationFailed",
                error_details=error,
                session_id=session_id
            )
            raise HTTPException(status_code=400, detail=f"Payment verification failed: {error}")

        # Call the controller's confirm_booking method
        result = booking_controller.confirm_booking(
            booking_id=booking_id,
            payment_confirmation=payment_confirmation,
            authorization=authorization
        )

        return result

    except HTTPException as he:
        booking_controller.logging_service.log_error(
            f"HTTP error in confirm_booking: {he.detail}",
            transaction_id=booking_id,
            error_type="HTTPException",
            status_code=he.status_code,
            error_details=he.detail
        )
        raise
    except BillingServiceException as be:
        booking_controller.logging_service.log_error(
            f"Billing service error",
            transaction_id=booking_id,
            error_type="BillingServiceException",
            error_details=str(be),
            session_id=session_id
        )
        raise HTTPException(status_code=400, detail=str(be))
    except Exception as e:
        booking_controller.logging_service.log_error(
            f"Unexpected error in confirm_booking",
            transaction_id=booking_id,
            error_type=type(e).__name__,
            error_details=str(e),
            session_id=session_id
        )
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{booking_id}/cancel")
async def cancel_booking(
    booking_id: str = Path(..., description="The ID of the booking to cancel"),
    authorization: str = Header(None),
    controller: BookingController = Depends(get_booking_controller)
) -> dict:
    try:
        # Validate the token and get claims
        claims = validate_token(authorization)
        user_id = claims.get("custom:id")

        # Log cancellation attempt
        controller.logging_service.log_booking_request(
            booking_details={
                "booking_id": booking_id,
                "user_id": user_id,
                "action": "cancel"
            },
            transaction_id=booking_id
        )

        # Get booking
        booking = controller.get_booking(booking_id, authorization)
        if not booking:
            controller.logging_service.log_error(
                "Booking not found during cancellation",
                transaction_id=booking_id,
                booking_id=booking_id,
                user_id=user_id,
                error_type="BookingNotFound"
            )
            raise HTTPException(status_code=404, detail="Booking not found")
        
        # Check if user owns this booking
        if booking["user_id"] != user_id:
            controller.logging_service.log_error(
                "Unauthorized cancellation attempt",
                transaction_id=booking_id,
                booking_id=booking_id,
                requesting_user=user_id,
                booking_owner=booking["user_id"],
                error_type="UnauthorizedCancellation"
            )
            raise HTTPException(status_code=403, detail="Not authorized to cancel this booking")
        
        # Can cancel if status is CONFIRMED or PENDING
        if booking["status"] not in [BookingStatus.CONFIRMED.value, BookingStatus.PENDING.value]:
            controller.logging_service.log_error(
                f"Invalid booking status for cancellation: {booking['status']}",
                transaction_id=booking_id,
                booking_id=booking_id,
                current_status=booking["status"],
                error_type="InvalidCancellationStatus"
            )
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot cancel booking with status {booking['status']}"
            )
        
        # Update booking status through ticket service
        await controller.ticket_service.update_booking_status(
            booking_id=booking_id,
            status=BookingStatus.CANCELED.value,
            auth_token=authorization
        )
        
        return {"message": "Booking canceled successfully"}
    except Exception as e:
        controller.logging_service.log_error(
            f"Error canceling booking",
            transaction_id=booking_id,
            booking_id=booking_id,
            error_type=type(e).__name__,
            error_details=str(e)
        )
        logger.error(f"Error canceling booking: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 