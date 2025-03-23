from typing import Dict, Any
from ..core.config import get_settings
from ..core.rabbitmq import RabbitMQClient

settings = get_settings()

class NotificationService:
    def __init__(self):
        self.rabbitmq = RabbitMQClient()
        self.exchange_name = "notifications"
        self.routing_key = "email.send"

    async def send_booking_status_update(
        self,
        booking_id: str,
        customer_email: str,
        event_name: str,
        status: str
    ) -> None:
        """Send booking status update email via RabbitMQ"""
        try:
            template = {
                "CONFIRMED": "booking_confirmation",
                "CANCELED": "booking_cancellation",
                "REFUNDED": "booking_refund"
            }.get(status.upper(), "booking_status_update")

            await self.rabbitmq.publish_message(
                self.exchange_name,
                self.routing_key,
                {
                    "template": template,
                    "recipient": customer_email,
                    "data": {
                        "booking_id": booking_id,
                        "event_name": event_name,
                        "status": status
                    }
                }
            )
        except Exception as e:
            print(f"Error sending booking status update notification: {str(e)}")
            raise

    async def send_booking_confirmation(
        self,
        booking_id: str,
        customer_email: str,
        event_name: str,
        ticket_quantity: int,
        total_amount: float
    ) -> None:
        """Send booking confirmation email via RabbitMQ"""
        try:
            await self.rabbitmq.publish_message(
                self.exchange_name,
                self.routing_key,
                {
                    "template": "booking_confirmation",
                    "recipient": customer_email,
                    "data": {
                        "booking_id": booking_id,
                        "event_name": event_name,
                        "ticket_quantity": ticket_quantity,
                        "total_amount": total_amount
                    }
                }
            )
        except Exception as e:
            print(f"Error sending booking confirmation notification: {str(e)}")
            raise

    async def send_payment_confirmation(
        self,
        booking_id: str,
        customer_email: str,
        event_name: str,
        payment_id: str,
        amount: float
    ) -> None:
        """Send payment confirmation email via RabbitMQ"""
        try:
            await self.rabbitmq.publish_message(
                self.exchange_name,
                self.routing_key,
                {
                    "template": "payment_confirmation",
                    "recipient": customer_email,
                    "data": {
                        "booking_id": booking_id,
                        "event_name": event_name,
                        "payment_id": payment_id,
                        "amount": amount
                    }
                }
            )
        except Exception as e:
            print(f"Error sending payment confirmation notification: {str(e)}")
            raise