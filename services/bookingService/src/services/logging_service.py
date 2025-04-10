from typing import Dict, Any, Optional
import json
import pika
from datetime import datetime
import os

# RabbitMQ Configuration
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST')
RABBITMQ_PORT = 5672
RABBITMQ_USER = os.getenv('RABBITMQ_USER')
RABBITMQ_PASS = os.getenv('RABBITMQ_PASS')
LOGGING_QUEUE = os.getenv('LOGGING_QUEUE', 'logs_queue') 

class LoggingService:
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
        self.parameters = pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            credentials=self.credentials
        )

    def _send_log(self, message: str, level: str = "INFO", transaction_id: Optional[str] = None, **kwargs):
        """Internal method to send logs to RabbitMQ"""
        try:
            payload = {
                "service_name": self.service_name,
                "timestamp": datetime.utcnow().isoformat(),
                "level": level.upper(),
                "message": message,
                "transaction_id": transaction_id,
                **kwargs
            }

            connection = pika.BlockingConnection(self.parameters)
            channel = connection.channel()
            channel.queue_declare(queue=LOGGING_QUEUE, durable=True)
            
            channel.basic_publish(
                exchange="",
                routing_key=LOGGING_QUEUE,
                body=json.dumps(payload)
            )
            connection.close()
        except Exception as e:
            print(f"Failed to send log: {str(e)}")  # Fallback logging

    def log_booking_request(self, booking_details: Dict[str, Any], transaction_id: str):
        """Log when a booking request is received"""
        self._send_log(
            message="Booking request received",
            level="INFO",
            transaction_id=transaction_id,
            booking_details=booking_details
        )

    def log_booking_creation(self, booking_id: str, transaction_id: str):
        """Log when a booking is created"""
        self._send_log(
            message=f"Booking created successfully",
            level="INFO",
            transaction_id=transaction_id,
            booking_id=booking_id
        )

    def log_payment_verification(self, booking_id: str, transaction_id: str, status: str):
        """Log payment verification status"""
        self._send_log(
            message=f"Payment verification {status}",
            level="INFO",
            transaction_id=transaction_id,
            booking_id=booking_id,
            payment_status=status
        )

    def log_booking_confirmation(self, booking_id: str, transaction_id: str):
        """Log when a booking is confirmed"""
        self._send_log(
            message=f"Booking confirmed",
            level="INFO",
            transaction_id=transaction_id,
            booking_id=booking_id
        )

    def log_booking_cancellation(self, booking_id: str, transaction_id: str):
        """Log when a booking is cancelled"""
        self._send_log(
            message=f"Booking cancelled",
            level="INFO",
            transaction_id=transaction_id,
            booking_id=booking_id
        )

    def log_email_sent(self, booking_id: str, transaction_id: str, email: str):
        """Log when confirmation email is sent"""
        self._send_log(
            message=f"Confirmation email sent",
            level="INFO",
            transaction_id=transaction_id,
            booking_id=booking_id,
            email=email
        )

    def log_error(self, error_message: str, transaction_id: Optional[str] = None, **context):
        """Log any errors that occur"""
        self._send_log(
            message=error_message,
            level="ERROR",
            transaction_id=transaction_id,
            error_context=context
        ) 