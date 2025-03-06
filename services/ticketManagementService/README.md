# Ticket Management Service

A FastAPI-based microservice for managing event tickets.

## Features

- Ticket creation and management
- Event ticket status tracking
- User ticket associations

## Tech Stack

- FastAPI
- SQLAlchemy (Async)
- PostgreSQL
- Docker

## Project Structure

```
ticketManagementService/
├── src/
│   ├── core/           # Core configurations
│   │   ├── config.py   # Environment and app configs
│   │   └── database.py # Database connection setup
│   ├── models/         # SQLAlchemy models
│   │   └── ticket.py   # Ticket data model
│   └── main.py         # FastAPI application entry point
├── Dockerfile          # Container configuration
└── requirements.txt    # Python dependencies
```

## Database Schema

The service uses the following main table:

### Tickets Table

- `ticket_id`: UUID (Primary Key)
- `event_id`: UUID
- `user_id`: UUID
- `status`: String
- `created_at`: DateTime
- `updated_at`: DateTime

## Getting Started

1. Build and run with Docker:

```bash
docker-compose up -d ticket-management-service
```

2. Access the API documentation:

```
http://localhost:8000/docs
```

## Environment Variables

Required environment variables:

- `DATABASE_URL`: PostgreSQL connection string
- AWS Cognito configuration (for authentication)

## API Endpoints

- `POST /tickets`: Create a new ticket
- `GET /tickets/{ticket_id}`: Get ticket details
- `GET /tickets/user/{user_id}`: Get user's tickets
- `PUT /tickets/{ticket_id}`: Update ticket status
