from typing import Dict, Any, List, Optional
import pika
import json
from ..core.config import get_settings
from ..core.logging import logger

settings = get_settings()

class NotificationServiceException(Exception):
    """Custom exception for notification service errors"""
    pass

class NotificationService:
    def __init__(self):
        self.exchange_name = "notifications"
        self.routing_key = "email.send"
        self.connection_params = pika.URLParameters(settings.RABBITMQ_URL)
        self.max_retries = 3
        self.initial_backoff = 1.0  # 1 second

    def _get_channel(self):
        """Create a new connection and channel"""
        connection = pika.BlockingConnection(self.connection_params)
        channel = connection.channel()
        # Declare exchange
        channel.exchange_declare(
            exchange=self.exchange_name,
            exchange_type='topic',
            durable=True
        )
        return connection, channel

    def _publish_with_retry(
        self,
        template: str,
        recipient: str,
        data: Dict[str, Any]
    ) -> None:
        """Publish message to RabbitMQ with retry mechanism"""
        retries = 0
        backoff = self.initial_backoff
        last_error = None

        message = {
            "template": template,
            "recipient": recipient,
            "data": data
        }

        while retries < self.max_retries:
            try:
                # Create new connection for each attempt
                connection, channel = self._get_channel()
                
                # Publish message
                channel.basic_publish(
                    exchange=self.exchange_name,
                    routing_key=self.routing_key,
                    body=json.dumps(message),
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # make message persistent
                        content_type='application/json'
                    )
                )
                
                # Close connection
                connection.close()
                logger.info(f"Successfully sent {template} notification to {recipient}")
                return
            except Exception as e:
                retries += 1
                last_error = e
                if retries == self.max_retries:
                    logger.error(f"Failed to send notification after {retries} attempts: {str(e)}")
                    raise NotificationServiceException(f"Failed to send notification: {str(e)}")
                logger.warning(f"Error sending notification (attempt {retries}/{self.max_retries}): {str(e)}")
                import time
                time.sleep(backoff)
                backoff *= 2  # Exponential backoff

    def send_booking_status_update(
        self,
        booking_id: str,
        customer_email: str,
        event_name: str,
        status: str,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Send booking status update email via RabbitMQ"""
        try:
            template = {
                "CONFIRMED": "booking_confirmation",
                "CANCELED": "booking_cancellation",
                "REFUNDED": "booking_refund",
                "PENDING": "booking_pending"
            }.get(status.upper(), "booking_status_update")

            data = {
                "booking_id": booking_id,
                "event_name": event_name,
                "status": status
            }

            if additional_data:
                data.update(additional_data)

            self._publish_with_retry(template, customer_email, data)
            logger.info(f"Sent booking status update ({status}) for booking {booking_id} to {customer_email}")
        except Exception as e:
            logger.error(f"Error sending booking status update notification: {str(e)}")
            raise NotificationServiceException(f"Failed to send booking status update: {str(e)}")

    def send_booking_confirmation(
        self,
        booking_id: str,
        customer_email: str,
        event_name: str,
        ticket_quantity: int,
        total_amount: float,
        additional_info: Optional[Dict[str, Any]] = None
    ) -> None:
        """Send booking confirmation email via RabbitMQ"""
        try:
            data = {
                "booking_id": booking_id,
                "event_name": event_name,
                "ticket_quantity": ticket_quantity,
                "total_amount": total_amount
            }

            if additional_info:
                data.update(additional_info)

            self._publish_with_retry("booking_confirmation", customer_email, data)
            logger.info(f"Sent booking confirmation for booking {booking_id} to {customer_email}")
        except Exception as e:
            logger.error(f"Error sending booking confirmation notification: {str(e)}")
            raise NotificationServiceException(f"Failed to send booking confirmation: {str(e)}")

    def send_payment_confirmation(
        self,
        booking_id: str,
        customer_email: str,
        event_name: str,
        payment_id: str,
        amount: float,
        payment_details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Send payment confirmation email via RabbitMQ"""
        try:
            data = {
                "booking_id": booking_id,
                "event_name": event_name,
                "payment_id": payment_id,
                "amount": amount
            }

            if payment_details:
                data.update(payment_details)

            self._publish_with_retry("payment_confirmation", customer_email, data)
            logger.info(f"Sent payment confirmation for booking {booking_id} to {customer_email}")
        except Exception as e:
            logger.error(f"Error sending payment confirmation notification: {str(e)}")
            raise NotificationServiceException(f"Failed to send payment confirmation: {str(e)}")

    def send_refund_notification(
        self,
        booking_id: str,
        customer_email: str,
        event_name: str,
        refund_id: str,
        amount: float,
        reason: Optional[str] = None
    ) -> None:
        """Send refund notification email via RabbitMQ"""
        try:
            data = {
                "booking_id": booking_id,
                "event_name": event_name,
                "refund_id": refund_id,
                "amount": amount,
                "reason": reason or "Refund processed"
            }

            self._publish_with_retry("booking_refund", customer_email, data)
            logger.info(f"Sent refund notification for booking {booking_id} to {customer_email}")
        except Exception as e:
            logger.error(f"Error sending refund notification: {str(e)}")
            raise NotificationServiceException(f"Failed to send refund notification: {str(e)}")

    def send_batch_notifications(
        self,
        template: str,
        notifications: List[Dict[str, Any]]
    ) -> None:
        """Send batch notifications via RabbitMQ"""
        try:
            for notification in notifications:
                self._publish_with_retry(
                    template,
                    notification["recipient"],
                    notification["data"]
                )
            logger.info(f"Successfully sent {len(notifications)} batch notifications")
        except Exception as e:
            logger.error(f"Error sending batch notifications: {str(e)}")
            raise NotificationServiceException(f"Failed to send batch notifications: {str(e)}")