import requests
import time
from typing import Dict, Any, Optional, Tuple
from uuid import UUID
from ..core.config import get_settings
from ..core.logging import logger

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
                    raise BillingServiceException(f"Network error: {str(e)}")
                logger.warning(f"Network error (attempt {retries}/{self.max_retries}): {str(e)}")
                time.sleep(backoff)
                backoff *= 2  # Exponential backoff
            except requests.exceptions.HTTPError as e:
                logger.error(f"HTTP error: {str(e)}")
                raise BillingServiceException(f"HTTP error: {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
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
            payload = {
                "booking_id": booking_id,
                "amount": amount,
                "currency": currency.lower(),
                "customer_email": customer_email,
                "success_url": f"{settings.FRONTEND_URL}/bookings/{booking_id}/success",
                "cancel_url": f"{settings.FRONTEND_URL}/bookings/{booking_id}/cancel"
            }
            return self._make_request_with_retry(
                "post",
                "payments/create-session",
                json=payload
            )
        except Exception as e:
            logger.error(f"Error creating payment session: {str(e)}")
            raise BillingServiceException(f"Failed to create payment session: {str(e)}")

    def verify_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Verify and process payment webhook"""
        try:
            return self._make_request_with_retry(
                "post",
                "payments/webhook",
                json=payload
            )
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
            
            return self._make_request_with_retry(
                "post",
                f"payments/{booking_id}/refund",
                json=payload
            )
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
            return is_paid, error
        except Exception as e:
            logger.error(f"Error verifying payment completion: {str(e)}")
            return False, str(e) 