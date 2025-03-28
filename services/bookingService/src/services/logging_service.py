from typing import Dict, Any, Optional
import pika
from ..core.config import get_settings
from ..core.logging import logger

settings = get_settings()

class LoggingService:
    def __init__(self):
        self.service_name = "booking_service"
        self.queue_name = settings.RABBITMQ_QUEUE
        # Initialize connection parameters
        self.connection_params = pika.URLParameters(settings.RABBITMQ_URL)
        self.max_retries = 3

    def _get_channel(self):
        """Create a new connection and channel"""
        connection = pika.BlockingConnection(self.connection_params)
        channel = connection.channel()
        # Ensure queue exists
        channel.queue_declare(queue=self.queue_name, durable=True)
        return connection, channel

    def send_log(
        self,
        level: str,
        message: str,
        transaction_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Send a log entry to the logging service queue"""
        payload = {
            "service_name": self.service_name,
            "level": level.upper(),
            "message": message
        }
        
        if transaction_id:
            payload["transaction_id"] = transaction_id

        retries = 0
        last_error = None

        while retries < self.max_retries:
            try:
                # Create new connection for each attempt
                connection, channel = self._get_channel()
                
                # Convert dict to string if needed
                if isinstance(payload, dict):
                    import json
                    payload = json.dumps(payload)

                # Publish message
                channel.basic_publish(
                    exchange='',
                    routing_key=self.queue_name,
                    body=payload,
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # make message persistent
                    )
                )
                
                # Close connection
                connection.close()
                logger.info(f"Successfully sent log message: {message}")
                return
                
            except Exception as e:
                retries += 1
                last_error = e
                logger.warning(f"Attempt {retries}/{self.max_retries} failed: {str(e)}")
                
                if retries == self.max_retries:
                    logger.error(f"Failed to send log after {retries} attempts. Last error: {str(last_error)}")
                    logger.error(f"Log payload: {payload}")
                    break

    def log_info(self, message: str, **kwargs):
        """Convenience method for info logs"""
        self.send_log("INFO", message, **kwargs)

    def log_error(self, message: str, **kwargs):
        """Convenience method for error logs"""
        self.send_log("ERROR", message, **kwargs)

    def log_warning(self, message: str, **kwargs):
        """Convenience method for warning logs"""
        self.send_log("WARNING", message, **kwargs) 