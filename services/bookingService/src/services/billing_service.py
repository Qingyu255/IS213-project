import requests
import time
from typing import Dict, Any, Optional, Tuple
from uuid import UUID
from ..core.config import get_settings
from ..core.logging import logger
from .rabbitmq_service import RabbitMQService
from .logging_service import LoggingService

settings = get_settings()

class BillingServiceException(Exception):
    """Custom exception for billing service errors"""
    pass

class BillingService:
    def __init__(self):
        self.base_url = f"{settings.BILLING_SERVICE_URL}/api"
        self.timeout = 10.0
        self.max_retries = 3
        self.initial_backoff = 1.0  # 1 second
        
        # Initialize services
        self.rabbitmq = RabbitMQService("billing_service")
        self.logger = LoggingService("billing_service")

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
                url = f"{self.base_url}/{endpoint}"
                logger.debug(f"Making {method.upper()} request to {url}")
                response = getattr(requests, method)(url, **kwargs)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.ConnectionError as e:
                retries += 1
                if retries == self.max_retries:
                    self.logger.log_error(
                        message=f"Network error after {retries} retries: {str(e)}",
                        context={"url": url, "method": method}
                    )
                    raise BillingServiceException(f"Network error: {str(e)}")
                logger.warning(f"Network error (attempt {retries}/{self.max_retries}): {str(e)}")
                time.sleep(backoff)
                backoff *= 2
            except requests.exceptions.HTTPError as e:
                self.logger.log_error(
                    message=f"HTTP error: {str(e)}",
                    context={"url": url, "method": method, "response": getattr(e.response, 'text', None)}
                )
                raise BillingServiceException(f"HTTP error: {str(e)}")
            except Exception as e:
                self.logger.log_error(
                    message=f"Unexpected error: {str(e)}",
                    context={"url": url, "method": method}
                )
                raise BillingServiceException(f"Unexpected error: {str(e)}")

    def create_payment_session(
        self,
        booking_id: str,
        amount: float,
        currency: str,
        customer_email: str
    ) -> Dict[str, Any]:
        """Create a payment session for the booking"""
        try:
            frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
            
            payload = {
                "booking_id": booking_id,
                "amount": amount,
                "currency": currency.lower(),
                "customer_email": customer_email,
                "success_url": f"{frontend_url}/bookings/{booking_id}/success",
                "cancel_url": f"{frontend_url}/bookings/{booking_id}/cancel"
            }
            
            # Log payment session creation
            self.logger.log_info(
                message=f"Creating payment session for booking {booking_id}",
                context={"amount": amount, "currency": currency}
            )
            
            result = self._make_request_with_retry(
                "post",
                "payments/create-session",
                json=payload
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error creating payment session: {str(e)}")
            raise BillingServiceException(f"Failed to create payment session: {str(e)}")

    def verify_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Verify and process payment webhook"""
        try:
            event_type = payload.get("type")
            booking_id = payload.get("data", {}).get("object", {}).get("metadata", {}).get("booking_id")
            
            # Log webhook processing
            self.logger.log_info(
                message=f"Processing payment webhook for booking {booking_id}",
                context={"event_type": event_type, "booking_id": booking_id}
            )
            
            result = self._make_request_with_retry(
                "post",
                "payments/webhook",
                json=payload
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing webhook: {str(e)}")
            raise BillingServiceException(f"Failed to process webhook: {str(e)}")

    def get_payment_status(self, booking_id: str) -> Optional[str]:
        """Get payment status for a booking"""
        try:
            response = self._make_request_with_retry(
                "get",
                f"payments/{booking_id}/status"
            )
            return response.get("status")
        except BillingServiceException as e:
            logger.error(f"Error getting payment status: {str(e)}")
            return None

    def refund_payment(self, booking_id: str, amount: Optional[float] = None) -> Dict[str, Any]:
        """Refund a payment for a booking"""
        try:
            payload = {"booking_id": booking_id}
            if amount is not None:
                payload["amount"] = amount
            
            # Log refund initiation
            self.logger.log_info(
                message=f"Initiating refund for booking {booking_id}",
                context={"amount": amount}
            )
            
            result = self._make_request_with_retry(
                "post",
                f"payments/{booking_id}/refund",
                json=payload
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error refunding payment: {str(e)}")
            raise BillingServiceException(f"Failed to refund payment: {str(e)}")

    def verify_payment_completed(self, booking_id: str) -> Tuple[bool, Optional[str]]:
        """Verify if payment for a booking has been completed"""
        try:
            response = self._make_request_with_retry(
                "get",
                f"payments/{booking_id}/verify"
            )
            
            is_paid = response.get("is_paid", False)
            error = None if is_paid else response.get("error", "Payment not verified")
            
            # Log payment verification result
            if is_paid:
                self.logger.log_info(
                    message=f"Payment completed for booking {booking_id}"
                )
            else:
                logger.debug(f"Payment not completed for booking {booking_id}: {error}")
            
            return is_paid, error
            
        except Exception as e:
            logger.error(f"Error verifying payment completion: {str(e)}")
            return False, str(e) 