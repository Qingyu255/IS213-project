# Refund Composite Service

A Python-based microservice that orchestrates the refund process by interacting with multiple external services (Billing MS, Logging MS) and publishing events to RabbitMQ. Built with [FastAPI](https://fastapi.tiangolo.com/), [pydantic](https://pydantic-docs.helpmanual.io/), and [pika](https://pika.readthedocs.io/en/stable/).

---

## Table of Contents
1. [Overview](#overview)
2. [Project Structure](#project-structure)
3. [Key Components](#key-components)
4. [Tech Stack](#tech-stack)
5. [Getting Started](#getting-started)
6. [Configuration](#configuration)
7. [Running the Service](#running-the-service)
8. [Testing](#testing)
9. [Contributing](#contributing)
10. [License](#license)

---

## Overview

This **Refund Composite Service** is responsible for:
- **Receiving** refund requests via a RESTful API.
- **Validating** and **processing** those requests by calling:
  - A **Billing** microservice (to actually perform the refund).
  - A **Logging** microservice (to log refund-related actions).
- **Publishing** events to RabbitMQ for:
  - **Ticket Management** updates.
  - **Notifications** (e.g., user notifications about the refund).

The service centralizes these calls into a single, cohesive flow, reducing complexity for any upstream clients or front-end systems.

---

## Project Structure



**Folders:**

- **app/controllers**  
  Contains FastAPI routers/controllers. For example, `refund_controller.py` defines endpoints like `POST /refunds`.
  
- **app/services**  
  Houses business logic/orchestration. `refund_service.py` calls the Billing/Logging microservices and publishes to RabbitMQ.
  
- **app/clients**  
  Contains code to call external microservices. `billing_client.py` and `logging_client.py` each handle their respective endpoints.
  
- **app/messaging**  
  Contains RabbitMQ-related logic.  
  - `rabbitmq_config.py` sets up connections.  
  - `ticket_management_publisher.py` and `notification_publisher.py` define methods to publish messages to specific queues.
  
- **app/models**  
  Defines pydantic models for request/response data and enumerations for refund status.
  
- **app/config**  
  Holds configuration logic (e.g., environment variables, connection settings).
  
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
   - Returns a `RefundResponse` model to the controller.

3. **BillingClient** and **LoggingClient** (`app/clients/`)  
   - Send HTTP requests to the respective microservices.  
   - Handle any request exceptions, parse responses, and return simplified results to the service layer.

4. **RabbitMQ Publishers** (`app/messaging/`)  
   - Manage publishing messages to RabbitMQ.  
   - Example: `TicketManagementPublisher` publishes a “REFUND_INITIATED” event to the `ticketmanagement` queue.

5. **Models** (`app/models/`)  
   - `RefundRequest` (incoming request format).  
   - `RefundResponse` (outgoing response format).  
   - `RefundStatus` (enum for statuses like `APPROVED`, `FAILED`, etc.).

6. **Configuration** (`app/config/settings.py`)  
   - Uses environment variables or a `.env` file to configure service URLs, RabbitMQ host/port, credentials, etc.  
   - Typically uses [pydantic BaseSettings](https://pydantic-docs.helpmanual.io/usage/settings/) for clean loading of config.

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

## Getting Started

1. **Clone the Repository**  
   ```bash
   git clone https://github.com/your-org/refund-composite-service.git
   cd refund-composite-service
