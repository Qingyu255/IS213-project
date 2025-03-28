from fastapi import APIRouter, HTTPException, Depends, Path, Query
from typing import Optional, List
from uuid import UUID
from ...schemas.booking import BookingCreate, BookingResponse, BookingStatus
from ...services.event_service import EventService
from ...services.ticket_service import TicketService
from ...services.billing_service import BillingService
from ...services.notification_service import NotificationService
from ...services.logging_service import LoggingService
from ...core.logging import logger

router = APIRouter()

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

    async def create_booking(self, booking_details: BookingCreate) -> BookingResponse:
        """Create a new booking with proper orchestration of all services"""
        error = None
        try:
            # 1. Log incoming request
            transaction_id = str(UUID.uuid4())
            await self.logging_service.send_log(
                level="info",
                message=f"Received booking request for event: {booking_details.event_id}",
                transaction_id=transaction_id
            )

            # 2. Fetch and validate event details
            event = await self.event_service.get_event(booking_details.event_id)
            if not event:
                raise HTTPException(status_code=404, detail="Event not found")

            # 3. Check ticket availability
            availability = await self.ticket_service.check_availability(
                event_id=booking_details.event_id,
                ticket_quantity=booking_details.ticket_quantity
            )
            if not availability.get("available_tickets", 0) < booking_details.ticket_quantity:
                raise HTTPException(status_code=400, detail="Not enough tickets available")

            # 4. Calculate total amount
            total_amount = float(event["price"]) * booking_details.ticket_quantity

            # 5. Create booking record
            booking = await self.ticket_service.create_booking(
                event_id=booking_details.event_id,
                user_id=booking_details.user_id,
                ticket_quantity=booking_details.ticket_quantity,
                total_amount=total_amount
            )

            # 6. Log booking creation
            await self.logging_service.send_log(
                level="info",
                message=f"Created pending booking {booking['id']} for event {event['id']}",
                transaction_id=transaction_id
            )

            # 7. Create payment session
            payment_session = await self.billing_service.create_payment_session(
                booking_id=booking["id"],
                amount=total_amount,
                currency="sgd",
                customer_email=booking_details.email
            )

            return BookingResponse(
                status="PENDING",
                booking_id=booking["id"],
                payment_url=payment_session["url"],
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
                await self.logging_service.send_log(
                    level="error",
                    message=error,
                    transaction_id=transaction_id
                )

    async def get_booking(self, booking_id: str) -> dict:
        """Get booking details"""
        try:
            booking = await self.ticket_service.get_booking(booking_id)
            if not booking:
                raise HTTPException(status_code=404, detail="Booking not found")
            return booking
        except Exception as e:
            logger.error(f"Error getting booking {booking_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def get_user_bookings(self, user_id: str) -> List[dict]:
        """Get all bookings for a user"""
        try:
            return await self.ticket_service.get_user_bookings(user_id)
        except Exception as e:
            logger.error(f"Error getting bookings for user {user_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))


# Dependency Injection
async def get_booking_controller():
    event_service = EventService()
    ticket_service = TicketService()
    billing_service = BillingService()
    notification_service = NotificationService()
    logging_service = LoggingService()
    return BookingController(
        event_service,
        ticket_service,
        billing_service,
        notification_service,
        logging_service
    )

# API Routes
@router.post("/bookings", response_model=BookingResponse)
async def create_booking(
    booking_details: BookingCreate,
    controller: BookingController = Depends(get_booking_controller)
):
    """Create a new booking"""
    return await controller.create_booking(booking_details)

@router.get("/bookings/{booking_id}")
async def get_booking(
    booking_id: str = Path(..., description="The ID of the booking to retrieve"),
    controller: BookingController = Depends(get_booking_controller)
):
    """Get booking details"""
    return await controller.get_booking(booking_id)

@router.get("/bookings/user/{user_id}")
async def get_user_bookings(
    user_id: str = Path(..., description="The ID of the user"),
    controller: BookingController = Depends(get_booking_controller)
):
    """Get all bookings for a user"""
    return await controller.get_user_bookings(user_id)

@router.post("/webhook/stripe")
async def stripe_webhook(
    payload: dict,
    controller: BookingController = Depends(get_booking_controller)
):
    """Handle Stripe webhook events"""
    try:
        # 1. Verify Stripe signature
        event = await controller.billing_service.verify_webhook(payload)
        
        if event.type == "payment_intent.succeeded":
            booking_id = event.data.object.metadata.booking_id
            
            # 2. Verify payment with billing service
            payment_verified = await controller.billing_service.verify_payment(booking_id)
            if not payment_verified:
                logger.warning(f"Payment verification failed for booking {booking_id}")
                return {"status": "payment_verification_failed"}

            # 3. Update booking status
            await controller.ticket_service.update_booking_status(
                booking_id=booking_id,
                status=BookingStatus.CONFIRMED.value
            )

            # 4. Get booking and event details
            booking = await controller.ticket_service.get_booking(booking_id)
            event = await controller.event_service.get_event(booking["event_id"])

            # 5. Send confirmation notification (only after payment verification)
            await controller.notification_service.send_booking_confirmation(
                booking_id=booking_id,
                user_email=booking["user_email"],
                event_name=event["name"]
            )

            # 6. Log successful payment
            await controller.logging_service.send_log(
                level="info",
                message=f"Payment verified and confirmed for booking {booking_id}",
                transaction_id=booking_id
            )

            return {"status": "success"}
        
        elif event.type == "payment_intent.payment_failed":
            booking_id = event.data.object.metadata.booking_id
            
            # Handle payment failure
            await controller.ticket_service.update_booking_status(
                booking_id=booking_id,
                status=BookingStatus.CANCELED.value
            )

            # Log payment failure
            await controller.logging_service.send_log(
                level="error",
                message=f"Payment failed for booking {booking_id}",
                transaction_id=booking_id
            )

            return {"status": "payment_failed"}

        return {"status": "ignored"}
    except Exception as e:
        logger.error(f"Error processing Stripe webhook: {str(e)}")
        return {"status": "error", "message": str(e)} 