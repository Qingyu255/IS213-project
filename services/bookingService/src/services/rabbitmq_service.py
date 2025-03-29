import pika
import json
from typing import Dict, Any, Optional, Tuple
from ..core.config import get_settings
from ..core.logging import logger

settings = get_settings()

class RabbitMQService:
    def __init__(self, service_name: str, exchange_name: Optional[str] = None):
        self.service_name = service_name
        self.exchange_name = exchange_name
        self.connection_params = pika.URLParameters(settings.RABBITMQ_URL)
        self.max_retries = 3
        self.connection = None
        self.channel = None

    def _connect(self):
        """Establish connection to RabbitMQ"""
        try:
            self.connection = pika.BlockingConnection(self.connection_params)
            self.channel = self.connection.channel()
            
            if self.exchange_name:
                self.channel.exchange_declare(
                    exchange=self.exchange_name,
                    exchange_type='topic',
                    durable=True
                )
            
            logger.info(f"{self.service_name} connected to RabbitMQ")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {str(e)}")
            raise

    def _ensure_connection(self):
        """Ensure RabbitMQ connection is active"""
        if not self.connection or self.connection.is_closed:
            self._connect()

    def publish_message(
        self,
        routing_key: str,
        message: Dict[str, Any],
        exchange: Optional[str] = None
    ) -> None:
        """Publish message to RabbitMQ"""
        try:
            self._ensure_connection()
            
            exchange = exchange or self.exchange_name or ''
            
            self.channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type='application/json'
                )
            )
            
            logger.info(f"Published message with routing key {routing_key}")
        except Exception as e:
            logger.error(f"Failed to publish message: {str(e)}")
            raise

    def close(self):
        """Close RabbitMQ connection"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            self.connection = None
            self.channel = None 