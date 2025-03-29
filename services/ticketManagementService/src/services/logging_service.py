from typing import Dict, Any, Optional
from datetime import datetime
from ..core.config import get_settings
from ..core.rabbitmq import RabbitMQClient

settings = get_settings()

class LoggingService:
    def __init__(self):
        self.service_name = "ticket_management_service"
        self.rabbitmq = RabbitMQClient()
        self.queue_name = settings.RABBITMQ_QUEUE

    async def send_log(
        self,
        level: str,
        message: str,
        transaction_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None  # Kept for backward compatibility but won't be sent
    ) -> None:
        """Send a log entry to the logging service queue"""
        try:
            # Only include fields that the logging service expects
            payload = {
                "service_name": self.service_name,
                "level": level.upper(),
                "message": message
            }
            
            # Only add transaction_id if provided
            if transaction_id:
                payload["transaction_id"] = transaction_id

            # Publish to queue
            await self.rabbitmq.publish_to_queue(
                self.queue_name,
                payload
            )
        except Exception as e:
            # If RabbitMQ fails, print to console as fallback
            print(f"Error sending log to RabbitMQ: {str(e)}")
            print(f"Log payload: {payload}") 