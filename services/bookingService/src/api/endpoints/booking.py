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
            self.logging_service.send_log(
                level="info",
                message=f"Received booking request for event: {booking_details.event_id}",
                transaction_id=transaction_id
            )

            # 2a. Fetch and validate event details
            event = self.event_service.get_event(booking_details.event_id)
            if not event:
                raise HTTPException(status_code=404, detail="Event not found")

            # 2b. Check ticket availability
            availability = self.ticket_service.get_available_tickets(
                event_id=booking_details.event_id,
                auth_token=auth_token
            )
            
            if availability["available_tickets"] < booking_details.ticket_quantity:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Only {availability['available_tickets']} tickets available "
                        f"(requested: {booking_details.ticket_quantity}, "
                        f"total capacity: {availability['total_capacity']}, "
                        f"already booked: {availability['booked_tickets']})"
                    )
                )

            # 3. Calculate total amount
            total_amount = float(event["price"]) * booking_details.ticket_quantity

            # 4. Create booking record
            booking = self.ticket_service.create_booking(
                event_id=booking_details.event_id,
                user_id=booking_details.user_id,
                ticket_quantity=booking_details.ticket_quantity,
                total_amount=total_amount,
                auth_token=auth_token,
                email=booking_details.email
            )

            # 5. Log booking creation
            self.logging_service.send_log(
                level="info",
                message=f"Created pending booking {booking['booking_id']} for event {event['id']}",
                transaction_id=transaction_id
            )

            return BookingResponse(
                status="PENDING",
                booking_id=booking["booking_id"],
                event_id=booking_details.event_id,
                user_id=booking_details.user_id,
                ticket_quantity=booking_details.ticket_quantity,
                created_at=booking.get("created_at", datetime.now()),
                message="Booking created successfully. Please complete payment."
            )

        except HTTPException as he:
            error = f"HTTP Exception: {he.detail}"
            raise he
        except Exception as e:
            error = f"An unexpected error occurred: {str(e)}"
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
                raise HTTPException(status_code=404, detail="Event not found")

            # 4. Send confirmation notification
            try:
                self.notification_service.send_booking_confirmation(
                    booking_id=booking_id,
                    customer_email=booking.get("email", ""),
                    event_name=event["name"],
                    ticket_quantity=booking["ticket_quantity"],
                    total_amount=float(payment_confirmation.amount) / 100,
                    user_id=booking["user_id"],
                    event_datetime=event["datetime"],
                    additional_info={
                        "payment_id": payment_confirmation.payment_intent_id,
                        "currency": payment_confirmation.currency
                    }
                )
                
            except Exception as e:
                logger.error(f"Error sending confirmation notifications: {str(e)}")

            # 5. Log successful confirmation
            self.logging_service.send_log(
                level="info",
                message=f"Booking {booking_id} confirmed after payment",
                transaction_id=booking_id
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
            logger.error(f"Billing service error: {str(be)}")
            raise HTTPException(status_code=400, detail=str(be))
        except Exception as e:
            logger.error(f"Error confirming booking: {str(e)}")
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
            raise HTTPException(status_code=404, detail="Booking not found")

        # Log booking details for debugging
        logger.debug(f"Booking details: {booking}")
        logger.debug(f"User ID from token (custom:id): {claims.get('custom:id')}")
        logger.debug(f"User ID from booking: {booking['user_id']}")

        # Verify the user owns the booking using custom:id
        if booking["user_id"] != claims.get('custom:id'):
            raise HTTPException(status_code=403, detail="Not authorized to confirm this booking")

        # Get event details to verify the amount
        event = booking_controller.event_service.get_event(booking["event_id"])
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        # Log event details for debugging
        logger.debug(f"Event details: {event}")

        # Calculate total amount
        total_amount = int(float(event["price"]) * booking["ticket_quantity"] * 100)  # Convert to cents
        logger.debug(f"Calculated total amount: {total_amount}")

        # Create payment confirmation
        payment_confirmation = PaymentConfirmation(
            payment_intent_id=session_id,
            amount=total_amount,
            currency="sgd"
        )

        # Verify payment completion before confirming
        is_paid, error = booking_controller.verify_payment(booking_id)
        if not is_paid:
            raise HTTPException(status_code=400, detail=f"Payment verification failed: {error}")

        # Store payment intent information
        # booking_controller.billing_service.store_payment_intent(
        #     booking_id=booking_id,
        #     payment_intent_id=session_id,  # This might need to be retrieved from Stripe
        #     session_id=session_id,
        #     amount=total_amount,
        #     currency="sgd",
        #     customer_email=booking.get("email"),
        #     customer_name=claims.get("name")  # Assuming name is in the claims
        # )

        # Call the controller's confirm_booking method
        result = booking_controller.confirm_booking(
            booking_id=booking_id,
            payment_confirmation=payment_confirmation,
            authorization=authorization
        )

        logger.debug(f"Booking confirmation result: {result}")
        return result
    except HTTPException as he:
        logger.error(f"HTTP error in confirm_booking: {str(he)}")
        raise
    except BillingServiceException as be:
        logger.error(f"Billing service error: {str(be)}")
        raise HTTPException(status_code=400, detail=str(be))
    except Exception as e:
        logger.error(f"Error confirming booking: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 