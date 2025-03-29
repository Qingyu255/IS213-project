# publish refund request and status to logging service queue 
import json
import pika
from src.config.settings import RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_USER, RABBITMQ_PASS, LOGGING_QUEUE

def _publish_message(payload: dict):
    """Internal helper to publish a JSON payload to the logging queue."""
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    parameters = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        credentials=credentials
    )
    
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    # Declare the logging queue (ensures it exists)
    channel.queue_declare(queue=LOGGING_QUEUE, durable=True)
    # Publish the payload
    channel.basic_publish(
        exchange="",
        routing_key=LOGGING_QUEUE,
        body=json.dumps(payload)
    )
    connection.close()

def publish_refund_request_log(service_name: str, transaction_id: str, message: str, level: str = "INFO"):

    payload = {
        "service_name": service_name,
        "level": level,
        "message": message,
        "transaction_id": transaction_id,
        
    }
    _publish_message(payload)

def publish_refund_status_log(service_name: str, transaction_id: str, message: str, is_error: bool = False):
    
    level = "ERROR" if is_error else "INFO"
    payload = {
        "service_name": service_name,
        "level": level,
        "message": message,
        "transaction_id": transaction_id,
    }
    _publish_message(payload)
