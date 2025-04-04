import json
import aio_pika
from typing import Any, Dict, Callable, Awaitable
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
        """Publish a message to a specific queue"""
        await self.connect()
        
        # Declare queue
        queue = await self.channel.declare_queue(queue_name, durable=True)
        
        # Convert message to JSON string
        message_body = json.dumps(message)
        
        # Create message
        message = aio_pika.Message(
            body=message_body.encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            content_type='application/json'
        )
        
        # Publish message
        await self.channel.default_exchange.publish(
            message,
            routing_key=queue_name
        )

class RabbitMQConsumer:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.url = settings.RABBITMQ_URL
        self.exchange_name = "booking"
        self.queue_name = "ticket_management"
        self.handlers: Dict[str, Callable[[Dict[str, Any]], Awaitable[None]]] = {}

    async def connect(self):
        if not self.connection:
            self.connection = await aio_pika.connect_robust(self.url)
            self.channel = await self.connection.channel()
            await self.channel.set_qos(prefetch_count=10)

    async def close(self):
        if self.connection:
            await self.connection.close()
            self.connection = None
            self.channel = None

    def add_handler(self, routing_key: str, handler: Callable[[Dict[str, Any]], Awaitable[None]]):
        """Register a handler for a specific routing key"""
        self.handlers[routing_key] = handler

    async def process_message(self, message: aio_pika.IncomingMessage):
        """Process incoming messages and route to appropriate handlers"""
        async with message.process():
            routing_key = message.routing_key
            body = json.loads(message.body.decode())
            
            if handler := self.handlers.get(routing_key):
                try:
                    await handler(body)
                except Exception as e:
                    print(f"Error processing message {routing_key}: {str(e)}")
                    # Depending on error, might want to nack the message
                    # await message.nack(requeue=True)
            else:
                print(f"No handler for routing key: {routing_key}")

    async def start_consuming(self):
        """Start consuming messages from RabbitMQ"""
        await self.connect()
        
        # Declare exchange
        exchange = await self.channel.declare_exchange(
            self.exchange_name,
            aio_pika.ExchangeType.TOPIC,
            durable=True
        )

        # Create queue and bind to all relevant routing keys
        queue = await self.channel.declare_queue(self.queue_name, durable=True)
        
        # Bind to relevant routing patterns
        routing_patterns = [
            "booking.confirmed",
            "booking.cancelled",
            "booking.refunded"
        ]
        
        for pattern in routing_patterns:
            await queue.bind(exchange, pattern)

        # Start consuming
        await queue.consume(self.process_message)
        print(f" [*] Waiting for messages on queue {self.queue_name}. To exit press CTRL+C") 