# Refund Composite Service

A Python-based microservice that orchestrates the refund process by interacting with multiple external services (Billing MS, Logging MS, Ticket Management Service) and publishing events to RabbitMQ. Built with [FastAPI](https://fastapi.tiangolo.com/), [pydantic](https://pydantic-docs.helpmanual.io/), and [pika](https://pika.readthedocs.io/en/stable/).

---

## Table of Contents
1. [Overview](#overview)
2. [Project Structure](#project-structure)
3. [Key Components](#key-components)
4. [Tech Stack](#tech-stack)


---

## Overview

This **Refund Composite Service** is responsible for:
- **Receiving** refund requests via a RESTful API.
- **Validating** and **processing** those requests by:
  - Calling the **Billing** microservice to process refunds.
  - Calling the **Logging** microservice to log refund-related actions.
  - Updating the **Ticket Management Service** to reflect refund status.
- **Publishing** events to RabbitMQ for:
  - **Ticket Management** updates.
  - **Notifications** (e.g., user notifications about the refund).

The service centralizes these calls into a single, cohesive flow, reducing complexity for upstream clients or front-end systems.

---

## Project Structure

**Folders:**

- **app/controllers**  
  Contains FastAPI routers/controllers. For example, `refund_controller.py` defines endpoints like `POST /refunds`.

- **app/services**  
  Houses business logic/orchestration.  
  - `refund_service.py`: Orchestrates the refund process by interacting with external services and RabbitMQ.  
  - `event_service.py`: Handles communication with the Event Service.  
  - `notification_service.py`: Sends refund confirmation notifications.

- **app/clients**  
  Contains code to call external microservices.  
  - `billing_client.py`: Handles communication with the Billing microservice.  
  - `logging_client.py`: Handles communication with the Logging microservice.

- **app/messaging**  
  Contains RabbitMQ-related logic.  
  - `rabbitmq_config.py`: Sets up RabbitMQ connections.  
  - `ticket_management_publisher.py`: Publishes events to the `ticketmanagement` queue.  
  - `notification_publisher.py`: Publishes refund notifications to the notification queue.

- **app/models**  
  Defines pydantic models for request/response data and enumerations for refund status.  
  - `RefundRequest`: Represents incoming refund requests.  
  - `RefundResponse`: Represents outgoing responses.  
  - `RefundStatus`: Enum for statuses like `APPROVED` and `FAILED`.

- **app/config**  
  Holds configuration logic (e.g., environment variables, service URLs, RabbitMQ settings).  
  - Uses [pydantic BaseSettings](https://pydantic-docs.helpmanual.io/usage/settings/) for clean configuration management.

- **app/utils**  
  Utility classes and functions (e.g., error handlers, custom exceptions).

- **tests**  
  Unit and integration tests, using [pytest](https://docs.pytest.org/) or [unittest](https://docs.python.org/3/library/unittest.html).

---

## Key Components

1. **RefundController** (`app/controllers/refund_controller.py`)  
   - Exposes endpoints for initiating or querying refunds.  
   - Converts incoming requests (JSON) to pydantic models and delegates to `RefundService`.

2. **RefundService** (`app/services/refund_service.py`)  
   - Orchestrates the refund process:  
     - Validates the request.  
     - Calls `BillingClient` to process refunds.  
     - Calls `LoggingClient` to record logs.  
     - Publishes messages to RabbitMQ (ticket and notification queues).  
     - Updates booking status in the Ticket Management Service.  
   - Returns a `RefundResponse` model to the controller.

3. **BillingClient** and **LoggingClient** (`app/clients/`)  
   - Send HTTP requests to the respective microservices.  
   - Handle any request exceptions, parse responses, and return simplified results to the service layer.

4. **RabbitMQ Publishers** (`app/messaging/`)  
   - Manage publishing messages to RabbitMQ.  
   - Example: `TicketManagementPublisher` publishes a “REFUND_INITIATED” event to the `ticketmanagement` queue.

5. **NotificationService** (`app/services/notification_service.py`)  
   - Sends refund confirmation emails to customers using the Notification microservice.

6. **EventService** (`app/services/event_service.py`)  
   - Retrieves event details from the Event Service for refund processing.

---

## Tech Stack

- **Python 3.9+**  
- **FastAPI** for the REST API.  
- **pydantic** for data validation and serialization.  
- **requests** (or [httpx](https://www.python-httpx.org/)) for HTTP calls to external microservices.  
- **pika** (or [aio-pika](https://github.com/mosquito/aio-pika)) for RabbitMQ connections and publishing.  
- **pytest** for testing.  
- **Docker** (optional) for containerization.

---
