# src/services/refund_service.py
import logging
from fastapi import HTTPException
from src.clients.billing_client import BillingClient
from src.messaging.logging_publisher import (
    publish_refund_request_log,
    publish_refund_status_log
)
from src.models.refund_models import EventRefundRequest, EventRefundResponse, RefundStatus, BookingRefundRequest, BookingRefundResponse
from src.services.event_service import EventService
from src.services.notification_service import NotificationService
from src.core.auth import validate_token

logger=logging.getLogger()

class RefundService:
    def __init__(self):
        self.billing_client = BillingClient()
        self.event_service = EventService()
        self.notification_service = NotificationService()
        
    def process_event_refund(self, refund_request: EventRefundRequest) -> EventRefundResponse:
        service_name = "refund_composite_service"
        
        # Step 1: Fetch payment details using event_id and organizer_id
        payment_details = self.billing_client.get_payment_details(
            event_id=refund_request.event_id,
            organizer_id=refund_request.organizer_id
        )
        
        if not payment_details["success"]:
            # Log the failure to fetch payment details
            publish_refund_status_log(
                service_name=service_name,
                transaction_id=None,  # No transaction ID available yet
                message=f"Failed to fetch payment details: {payment_details['message']}",
                is_error=True
            )
            raise HTTPException(status_code=404, detail=payment_details["message"])
        
        # Extract payment_intent_id and amount from the fetched details
        payment_intent_id = payment_details["payment_intent_id"]
        amount = payment_details["amount"]
        
        # Step 2: Publish the refund request log
        publish_refund_request_log(
            service_name=service_name,
            transaction_id=payment_intent_id,
            message="Event refund request initiated",
            level="INFO"
        )
        
        # Step 3: Call the Billing service's refund process endpoint
        result = self.billing_client.process_refund(
            payment_intent_id=payment_intent_id,
            amount=amount,
            reason=refund_request.reason,
            metadata=refund_request.metadata
        )
        
        # Step 4: Log the refund status based on the response
        if result.get("success"):
            publish_refund_status_log(
                service_name=service_name,
                transaction_id=payment_intent_id,
                message="Event refund processed successfully",
                is_error=False
            )
            return EventRefundResponse(
                status=RefundStatus.APPROVED,
                message="Event refund processed successfully."
            )
        else:
            publish_refund_status_log(
                service_name=service_name,
                transaction_id=payment_intent_id,
                message="Event refund processing failed: " + result.get("message", "Unknown error"),
                is_error=True
            )
            # Raise an HTTPException with a 404 status code for any error
            raise HTTPException(status_code=result.get("error_code", 404), detail=result.get("message", " Event refund processing failed."))
    
    #process refund
    def process_booking_refund(self, booking_refund_request: BookingRefundRequest, authorization: str = None) -> BookingRefundResponse:
        service_name = "refund_composite_service"

        ## getting email
        if not authorization:
            raise HTTPException(status_code=401, detail="Authorization header is missing")
        
        try:
            # Extract claims from the token
            claims = validate_token(authorization)
            user_email = claims.get("email")
            
            if not user_email:
                raise ValueError("Email claim not found in the token")
            
            logger.info(f"User with email={user_email} is initiating a refund request for booking_id={booking_refund_request.booking_id}")
        except Exception as e:
            logger.error(f"Error validating authorization token: {str(e)}")
            raise HTTPException(status_code=401, detail="Invalid or expired authorization token")
    
        
        ## get booking from booking id
        booking_details_response = self.billing_client.get_booking(booking_refund_request.booking_id, authorization)
        
        # Extract event_id and ticket_quantity from the booking details
        event_id = booking_details_response.get("event_id")
        ticket_quantity = booking_details_response.get("ticket_quantity")     
        
        if not event_id or ticket_quantity is None:
            error_message = f"Failed to fetch valid booking details for booking_id={booking_refund_request.booking_id}"
            logger.error(error_message)
            publish_refund_status_log(
                service_name=service_name,
                transaction_id=booking_refund_request.booking_id,
                message=error_message,
                is_error=True
            )
            raise HTTPException(status_code=404, detail="Invalid or incomplete booking details")
        
        logger.info(f"Step 2: Successfully fetched booking details for booking_id={booking_refund_request.booking_id}. "
                    f"Event ID: {event_id}, Ticket Quantity: {ticket_quantity}")
        
        # get event
        event_details = self.event_service.get_event(event_id)
        
        if not event_details:
            raise ValueError("Event details not found")
        
        # Extract event_name, event_start_datetime, and event_end_datetime
        event_name = event_details.get("title")
        event_start_datetime = event_details.get("startDateTime")
        event_end_datetime = event_details.get("endDateTime")
        
        if not event_name or not event_start_datetime or not event_end_datetime:
            raise ValueError("Incomplete event details")
        
        logger.info(f"Successfully fetched event details for event_id={event_id}. "
                    f"Event Name: {event_name}, Start DateTime: {event_start_datetime}, End DateTime: {event_end_datetime}")
        

        # Step 1: Log the booking refund request
        logger.info(f"Step 1: Initiating booking refund request for booking_id={booking_refund_request.booking_id}")
        publish_refund_request_log(
            service_name=service_name,
            transaction_id=booking_refund_request.booking_id,
            message="Booking refund request initiated",
            level="INFO"
        )
        
        try:
            # Step 2: Fetch payment details (payment_intent_id and amount) using booking_id
            logger.debug(f"Step 2: Fetching payment details for booking_id={booking_refund_request.booking_id}")
            payment_details = self.billing_client.get_payment_details_from_booking(booking_refund_request.booking_id)
            
            if not payment_details["success"]:
                # Log the failure to fetch payment details
                error_message = f"Failed to fetch payment details for booking_id={booking_refund_request.booking_id}: {payment_details['message']}"
                logger.error(error_message)
                publish_refund_status_log(
                    service_name=service_name,
                    transaction_id=booking_refund_request.booking_id,
                    message=error_message,
                    is_error=True
                )
                raise HTTPException(status_code=404, detail=payment_details["message"])
            
            # Extract payment_intent_id and amount from the fetched details
            payment_intent_id = payment_details["payment_intent_id"]
            amount = payment_details["amount"]
            logger.info(f"Step 2: Successfully fetched payment details for booking_id={booking_refund_request.booking_id}. "
                        f"Payment Intent ID: {payment_intent_id}, Amount: {amount}")
            
            # Step 3: Call the Billing service's refund process endpoint
            logger.debug(f"Step 3: Initiating refund process for Payment Intent ID={payment_intent_id}, Amount={amount}")
            result = self.billing_client.process_refund(
                payment_intent_id=payment_intent_id,
                amount=amount,
                reason=booking_refund_request.reason,
                metadata=booking_refund_request.metadata
            )
            
            # Step 4: Log the refund status based on the response
            if result.get("success"):
                logger.info(f"Step 3: Refund processed successfully for Payment Intent ID={payment_intent_id}")
                publish_refund_status_log(
                    service_name=service_name,
                    transaction_id=booking_refund_request.booking_id,
                    message="Booking refund processed successfully",
                    is_error=False
                )
                
                # Step 5:FIXED  Update the booking status in the Ticket Service
                logger.debug(f"Step 5: Updating booking status to 'REFUNDED' for booking_id={booking_refund_request.booking_id}")
                update_booking_status_response = self.billing_client.update_booking_status(booking_refund_request.booking_id, authorization=authorization)
                
                if not update_booking_status_response["success"]:
                    error_message = (f"Step 5: Failed to update booking status for booking_id={booking_refund_request.booking_id}: "
                                    f"{update_booking_status_response['message']}")
                    logger.error(error_message)
                    publish_refund_status_log(
                        service_name=service_name,
                        transaction_id=booking_refund_request.booking_id,
                        message=error_message,
                        is_error=True
                    )
                    raise HTTPException(status_code=500, detail=update_booking_status_response["message"])
                
                logger.info(f"Step 5: Successfully updated booking status to 'REFUNDED' for booking_id={booking_refund_request.booking_id}")

                #### ---------- step 6:  call outsystems api for notification service
                try:
                    self.notification_service.send_refund_confirmation(
                        booking_id=booking_refund_request.booking_id,
                        customer_email=user_email,
                        event_name=event_name,
                        ticket_quantity= ticket_quantity,
                        total_amount=amount/100,
                        event_start_datetime= event_start_datetime,
                        event_end_datetime=event_end_datetime
                    )
                except Exception as e:
                    logger.error(f"Error sending refund confirmation: {str(e)}")
    

                return BookingRefundResponse(
                    success=True,
                    message="Booking refund processed successfully.",
                    # refund_id=result.get("refund_id")
                )
            else:
                error_message = (f"Step 3: Refund processing failed for Payment Intent ID={payment_intent_id}: "
                                f"{result.get('message', 'Unknown error')}")
                logger.error(error_message)
                publish_refund_status_log(
                    service_name=service_name,
                    transaction_id=booking_refund_request.booking_id,
                    message=error_message,
                    is_error=True
                )
                raise HTTPException(status_code=result.get("error_code", 400), detail=result.get("message", "Booking refund processing failed."))
        
        except HTTPException as exc:
            # Log HTTPExceptions raised during the process
            logger.error(f"HTTPException occurred while processing booking refund for booking_id={booking_refund_request.booking_id}: {exc.detail}")
            publish_refund_status_log(
                service_name=service_name,
                transaction_id=booking_refund_request.booking_id,
                message=f"HTTPException: {exc.detail}",
                is_error=True
            )
            raise exc
        
        except Exception as e:
            # Log unexpected exceptions
            error_message = f"Unexpected error occurred while processing booking refund for booking_id={booking_refund_request.booking_id}: {str(e)}"
            logger.exception(error_message)  # Logs the full traceback
            publish_refund_status_log(
                service_name=service_name,
                transaction_id=booking_refund_request.booking_id,
                message=error_message,
                is_error=True
            )
            raise HTTPException(status_code=500, detail=str(e))