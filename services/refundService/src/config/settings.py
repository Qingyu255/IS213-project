# src/config/settings.py

import os
from dotenv import load_dotenv

# Load environment variables from a .env file in the current directory
load_dotenv()

# Now you can read environment variables directly from os.environ
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")

LOGGING_QUEUE = os.getenv("RABBITMQ_QUEUE")
TICKET_QUEUE = os.getenv("TICKET_QUEUE", "ticketmanagement_queue")

BILLING_MS_URL = os.getenv("BILLING_MS_URL", "http://localhost:8100/api/v1/billing")
TICKET_SERVICE_URL = os.getenv("TICKET_SERVICE_URL", "http://localhost:8100/api/v1/tickets")
NOTIFICATIONS_MICROSERVICE_URL = os.getenv("NOTIFICATIONS_MICROSERVICE_URL", "https://personal-lqsiqj7y.outsystemscloud.com/notificationService")
EVENT_SERVICE_URL = os.getenv("EVENT_SERVICE_URL", "http://localhost:8100/api/v1/events")
BOOKING_SERVICE_URL = os.getenv("BOOKING_SERVICE_URL", "http://localhost:8100/api/v1/bookings")