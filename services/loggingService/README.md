# Logging Service

A Python-based microservice that collects logs from various services via RabbitMQ, stores them in a PostgreSQL database, and provides REST endpoints for retrieving logs with multiple filtering options.

---

## Features

- **Centralized Logging**: Receives logs from multiple services through a single RabbitMQ queue.
- **Database Storage**: Persists logs in a PostgreSQL database for reliable long-term storage.
- **Query & Filtering**: Exposes multiple GET endpoints to filter logs by date, level, service name, transaction ID, or combinations of these criteria.
- **Scalable Architecture**: Designed to handle a high volume of logs by decoupling log producers (publishers) and the consumer (this logging service).

---

## Tech Stack

- **Language**: Python 3.x
- **Framework**: Flask
- **Message Broker**: RabbitMQ
- **Database**: PostgreSQL
- **Containerization (Optional)**: Docker

---

## RabbitMQ Connection Details

RABBITMQ_HOST=rabbitmq
RABBITMQ_QUEUE=logs_queue
RABBITMQ_USER=guest
RABBITMQ_PASS=guest


## Message Payload Format

The logging service expects **JSON** messages containing specific fields. Below is the required format for publishers sending logs to RabbitMQ:

- **Required Fields**:
  1. **service_name**: A string indicating the name of the service generating the log.
  2. **level**: A string representing the log level (e.g., `"INFO"`, `"WARN"`, `"ERROR"`).
  3. **message**: The actual log message as a string.

- **Optional Field**:
  - **transaction_id**: An identifier to correlate logs with a particular transaction (if applicable).

**Example Payload**:
```json
{
  "service_name": "your_service",
  "level": "INFO",
  "message": "This is a sample log message.",
  "transaction_id": "abc123"  // optional
}
```



**Logging API**

- `GET /logs/by_date_level/{date}/{level}`: Get Logs by Date and Level  
- `GET /logs/by_date_range_level/{start_date}/{end_date}/{level}`: Get Logs by Date Range and Level  
- `GET /logs/by_service_level/{service}/{level}`: Get Logs by Service and Level  
- `GET /logs/by_service_level_daterange/{service}/{level}/{start_date}/{end_date}`: Get Logs by Service, Level, and Date Range  
- `GET /logs/by_transid_level/{transaction_id}/{level}`: Get Logs by Transaction ID and Level  
- `GET /logs/getall`: Get All Logs



