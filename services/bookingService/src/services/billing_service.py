import requests
import time
from typing import Dict, Any, Optional, Tuple
from uuid import UUID
from ..core.config import get_settings
from ..core.logging import logger
from .logging_service import LoggingService
from fastapi import HTTPException

settings = get_settings()

class BillingServiceException(Exception):
    """Custom exception for billing service errors"""
    pass

class BillingService:
    def __init__(self):
        self.base_url = settings.BILLING_SERVICE_URL
        self.timeout = 10.0
        self.max_retries = 3
        self.initial_backoff = 1.0  # 1 second
        
        # Initialize logging service
        self.logger = LoggingService("billing_service")

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to billing service"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.log_error(
                f"Billing service request error",
                error_type="RequestException",
                error_details=str(e),
                endpoint=endpoint
            )
            raise HTTPException(status_code=500, detail=f"Billing service error: {str(e)}")

    def create_payment_session(self, booking_id: str, amount: float, event_title: str, quantity: int) -> Dict[str, Any]:
        """Create a Stripe checkout session"""
        endpoint = "api/payments/create-session"
        data = {
            "booking_id": booking_id,
            "amount": amount,
            "event_title": event_title,
            "quantity": quantity
        }
        return self._make_request("POST", endpoint, json=data)

    def store_payment_intent(
        self, 
        booking_id: str, 
        payment_intent_id: str, 
        session_id: str,
        amount: int,
        currency: str,
        customer_email: str = None,
        customer_name: str = None
    ) -> Dict[str, Any]:
        """Store payment intent information for a booking"""
        endpoint = "api/payments/store-intent-booking"
        data = {
            "booking_id": booking_id,
            "payment_intent_id": payment_intent_id,
            "session_id": session_id,
            "amount": amount,
            "currency": currency,
            "customer_email": customer_email,
            "customer_name": customer_name
        }
        return self._make_request("POST", endpoint, json=data)

    def get_payment_intent(self, booking_id: str) -> Dict[str, Any]:
        """Get payment intent information for a booking"""
        endpoint = f"api/payments/intent/{booking_id}"
        return self._make_request("GET", endpoint)

    def verify_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Verify and process payment webhook"""
        try:
            event_type = payload.get("type")
            booking_id = payload.get("data", {}).get("object", {}).get("metadata", {}).get("booking_id")
            
            # Log webhook processing
            self.logger.log_payment_verification(
                booking_id=booking_id,
                transaction_id=booking_id,
                status="WEBHOOK_RECEIVED"
            )
            
            result = self._make_request(
                "post",
                "payments/webhook",
                json=payload
            )
            
            return result
            
        except Exception as e:
            self.logger.log_error(
                "Error processing webhook",
                transaction_id=booking_id,
                error_type="WebhookError",
                error_details=str(e)
            )
            raise BillingServiceException(f"Failed to process webhook: {str(e)}")

    def get_payment_status(self, booking_id: str) -> Optional[str]:
        """Get payment status for a booking"""
        try:
            response = self._make_request(
                "get",
                f"payments/{booking_id}/status"
            )
            return response.get("status")
        except BillingServiceException as e:
            self.logger.log_error(
                "Error getting payment status",
                transaction_id=booking_id,
                error_type="PaymentStatusError",
                error_details=str(e)
            )
            return None

    def refund_payment(self, booking_id: str, amount: Optional[float] = None) -> Dict[str, Any]:
        """Refund a payment for a booking"""
        try:
            payload = {"booking_id": booking_id}
            if amount is not None:
                payload["amount"] = amount
            
            # Log refund initiation
            self.logger.log_payment_verification(
                booking_id=booking_id,
                transaction_id=booking_id,
                status="REFUND_INITIATED"
            )
            
            result = self._make_request(
                "post",
                f"payments/{booking_id}/refund",
                json=payload
            )
            
            return result
            
        except Exception as e:
            self.logger.log_error(
                "Error refunding payment",
                transaction_id=booking_id,
                error_type="RefundError",
                error_details=str(e),
                amount=amount
            )
            raise BillingServiceException(f"Failed to refund payment: {str(e)}")

    def verify_payment_completed(self, booking_id: str) -> Tuple[bool, Optional[str]]:
        """Verify if payment for a booking has been completed"""
        try:
            response = self._make_request(
                "get",
                f"payments/{booking_id}/verify"
            )
            
            is_paid = response.get("is_paid", False)
            error = None if is_paid else response.get("error", "Payment not verified")
            
            # Log payment verification result
            if is_paid:
                self.logger.log_payment_verification(
                    booking_id=booking_id,
                    transaction_id=booking_id,
                    status="PAYMENT_COMPLETED"
                )
            else:
                self.logger.log_error(
                    "Payment not completed",
                    transaction_id=booking_id,
                    error_type="PaymentIncomplete",
                    error_details=error
                )
            
            return is_paid, error
            
        except Exception as e:
            self.logger.log_error(
                "Error verifying payment completion",
                transaction_id=booking_id,
                error_type="PaymentVerificationError",
                error_details=str(e)
            )
            return False, str(e) 