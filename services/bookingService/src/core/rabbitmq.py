import json
import aio_pika
from typing import Any, Dict
from .config import get_settings

settings = get_settings()

class RabbitMQClient:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.url = settings.RABBITMQ_URL

    async def connect(self):
        if not self.connection:
            self.connection = await aio_pika.connect_robust(self.url)
            self.channel = await self.connection.channel()

    async def close(self):
        if self.connection:
            await self.connection.close()
            self.connection = None
            self.channel = None

    async def publish_to_queue(self, queue_name: str, message: Dict[str, Any]):
        """Publish message directly to a queue (for logging service)"""
        try:
            if not self.connection or self.connection.is_closed:
                await self.connect()

            # Declare queue
            queue = await self.channel.declare_queue(
                queue_name,
                durable=True
            )

            message_body = json.dumps(message).encode()
            await self.channel.default_exchange.publish(
                aio_pika.Message(
                    body=message_body,
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                ),
                routing_key=queue_name  # Queue name is the routing key for default exchange
            )
        except Exception as e:
            print(f"Error publishing message to queue: {str(e)}")
            raise

    async def publish_message(self, exchange_name: str, routing_key: str, message: Dict[str, Any]):
        """Publish message to RabbitMQ exchange (for event notifications)"""
        try:
            if not self.connection or self.connection.is_closed:
                await self.connect()

            exchange = await self.channel.declare_exchange(
                exchange_name,
                aio_pika.ExchangeType.TOPIC,
                durable=True
            )

            message_body = json.dumps(message).encode()
            await exchange.publish(
                aio_pika.Message(
                    body=message_body,
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                ),
                routing_key=routing_key
            )
        except Exception as e:
            print(f"Error publishing message to RabbitMQ: {str(e)}")
            # Re-raise to let service handle the error
            raise 