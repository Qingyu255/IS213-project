from typing import Dict, Any, Optional
import pika
import json
from datetime import datetime
from ..core.config import get_settings
from ..core.logging import logger

settings = get_settings()

class LoggingService:
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.queue_name = "logs_queue"  # Use the standard logs queue
        self.connection_params = pika.URLParameters(settings.RABBITMQ_URL)
        self.max_retries = 3

    def _get_channel(self):
        """Create a new connection and channel"""
        connection = pika.BlockingConnection(self.connection_params)
        channel = connection.channel()
        # Ensure queue exists
        channel.queue_declare(queue=self.queue_name, durable=True)
        return connection, channel

    def _format_payload(
        self,
        level: str,
        message: str,
        transaction_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Format the log payload"""
        payload = {
            "service": self.service_name,
            "level": level.upper(),
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if transaction_id:
            payload["transaction_id"] = transaction_id
        if context:
            payload["data"] = context
            
        return payload

    def send_log(
        self,
        level: str,
        message: str,
        transaction_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Send a log entry to the logging service queue"""
        payload = self._format_payload(level, message, transaction_id, context)
        
        retries = 0
        last_error = None

        while retries < self.max_retries:
            try:
                connection, channel = self._get_channel()
                
                channel.basic_publish(
                    exchange='',
                    routing_key=self.queue_name,
                    body=json.dumps(payload),
                    properties=pika.BasicProperties(
                        delivery_mode=2,
                        content_type='application/json'
                    )
                )

                connection.close()
                logger.info(f"Successfully sent log message: {message}")
                return

            except Exception as e:
                last_error = e
                retries += 1
                if retries < self.max_retries:
                    logger.warning(f"Failed to send log (attempt {retries}/{self.max_retries}): {str(e)}")
                continue

        logger.error(f"Failed to send log after {self.max_retries} attempts. Last error: {str(last_error)}")

    def log_info(self, message: str, **kwargs):
        """Send an info level log message"""
        self.send_log("info", message, **kwargs)

    def log_error(self, message: str, **kwargs):
        """Send an error level log message"""
        self.send_log("error", message, **kwargs)

    def log_warning(self, message: str, **kwargs):
        """Send a warning level log message"""
        self.send_log("warning", message, **kwargs) 