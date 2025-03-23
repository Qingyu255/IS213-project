import httpx
from typing import Dict, Any, Optional
from uuid import UUID
from ..core.config import get_settings
from ..core.logging import logger

settings = get_settings()

class BillingService:
    def __init__(self):
        self.base_url = f"{settings.BILLING_SERVICE_URL}/api"
        self.timeout = httpx.Timeout(10.0)

    async def create_payment_session(
        self,
        booking_id: str,
        amount: float,
        currency: str,
        customer_email: str
    ) -> Dict[str, Any]:
        """Create a payment session for the booking"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/payments/create-session",
                    json={
                        "booking_id": booking_id,
                        "amount": amount,
                        "currency": currency.lower(),
                        "customer_email": customer_email,
                        "success_url": f"{settings.FRONTEND_URL}/bookings/{booking_id}/success",
                        "cancel_url": f"{settings.FRONTEND_URL}/bookings/{booking_id}/cancel"
                    }
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error creating payment session: {str(e)}")
            raise Exception(f"Failed to create payment session: {str(e)}")

    async def verify_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Verify and process payment webhook"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/payments/webhook",
                    json=payload
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error processing webhook: {str(e)}")
            raise Exception(f"Failed to process webhook: {str(e)}")

    async def get_payment_status(self, booking_id: str) -> Optional[str]:
        """Get payment status for a booking"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/payments/{booking_id}/status"
                )
                response.raise_for_status()
                data = response.json()
                return data.get("status")
        except Exception as e:
            logger.error(f"Error getting payment status: {str(e)}")
            return None

    async def refund_payment(self, booking_id: str) -> Dict[str, Any]:
        """Refund a payment for a booking"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/payments/{booking_id}/refund"
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error refunding payment: {str(e)}")
            raise Exception(f"Failed to refund payment: {str(e)}") 