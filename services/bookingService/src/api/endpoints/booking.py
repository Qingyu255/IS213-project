from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from ...schemas.booking import BookingCreate, BookingResponse
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
        error = None
        try:
            # 1. Log incoming request -> should send to logging service
            logger.info(f"Received booking request: {booking_details}")
            await self.logging_service.send_log(
                level="info",
                message=f"Received booking request for event: {booking_details.event_id}"
            )

            # 2. Fetch and validate event details
            event = await self.event_service.get_event(booking_details.event_id)
            if not event:
                raise HTTPException(status_code=404, detail="Event not found")

            # 3. Check ticket availability
            available = await self.ticket_service.check_availability(
                event_id=booking_details.event_id,
                quantity=booking_details.ticket_quantity
            )
            if not available:
                raise HTTPException(status_code=400, detail="Not enough tickets available")

            # 4. Create pending booking record
            booking = await self.ticket_service.create_booking(
                event_id=booking_details.event_id,
                user_id=booking_details.user_id,
                quantity=booking_details.ticket_quantity,
                status="PENDING"
            )

            # 5. Create Stripe payment session
            payment_session = await self.billing_service.create_payment_session(
                booking_id=booking.id,
                amount=event.price * booking_details.ticket_quantity,
                currency="sgd",
                customer_email=booking_details.email
            )

            # 6. Log successful booking creation and send to logging service
            await self.logging_service.send_log(
                level="info",
                message=f"Created pending booking {booking.id} for event {event.id}",
                booking_id=booking.id
            )

            return BookingResponse(
                status="PENDING",
                booking_id=booking.id,
                payment_url=payment_session.url,
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
                logger.error(error)
                await self.logging_service.send_log(
                    level="error",
                    message=error
                )

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

@router.post("/bookings", response_model=BookingResponse)
async def create_booking(
    booking_details: BookingCreate,
    controller: BookingController = Depends(get_booking_controller)
):
    return await controller.create_booking(booking_details)

# Stripe webhook handler
@router.post("/webhook/stripe")
async def stripe_webhook(
    payload: dict,
    controller: BookingController = Depends(get_booking_controller)
):
    try:
        # 1. Verify Stripe signature (implementation in billing service)
        event = await controller.billing_service.verify_webhook(payload)
        
        if event.type == "payment_intent.succeeded":
            booking_id = event.data.object.metadata.booking_id
            
            # 2. Update booking status
            await controller.ticket_service.update_booking_status(
                booking_id=booking_id,
                status="confirmed"
            )

            # 3. Log successful payment
            await controller.logging_service.send_log(
                level="info",
                message=f"Payment succeeded for booking {booking_id}",
                booking_id=booking_id
            )

            # 4. Send confirmation email
            await controller.notification_service.send_booking_confirmation(booking_id)

            return {"status": "success"}

        return {"status": "ignored"}
    except Exception as e:
        logger.error(f"Error processing Stripe webhook: {str(e)}")
        return {"status": "error", "message": "An error occurred while processing the webhook"} 