# Ticket Management Service

A FastAPI-based microservice for managing event tickets and bookings.

## Features

- Create and manage event bookings
- Track booking status (pending, confirmed, canceled, refunded)
- Manage tickets associated with bookings
- View available tickets for events
- Track user's ticket history

## Tech Stack

- FastAPI
- SQLAlchemy (Async)
- PostgreSQL
- Docker
- Pydantic

## Project Structure

```
ticketManagementService/
├── src/
│   ├── api/            # API routes and dependencies
│   │   ├── routes/     # Route handlers
│   │   │   ├── bookings.py
│   │   │   └── tickets.py
│   ├── core/           # Core configurations
│   │   ├── config.py   # Environment and app configs
│   │   └── database.py # Database connection setup
│   ├── models/         # SQLAlchemy models
│   │   ├── booking.py  # Booking data model
│   │   └── ticket.py   # Ticket data model
│   ├── schemas/        # Pydantic models
│   │   ├── booking.py  # Booking request/response models
│   │   └── ticket.py   # Ticket response models
│   └── main.py         # FastAPI application entry point
├── Dockerfile          # Container configuration
└── requirements.txt    # Python dependencies
```

## Database Schema

### Bookings Table

- `booking_id`: UUID (Primary Key)
- `user_id`: UUID
- `event_id`: UUID
- `status`: String (pending, confirmed, canceled, refunded)
- `created_at`: DateTime
- `updated_at`: DateTime

### Tickets Table

- `ticket_id`: UUID (Primary Key)
- `booking_id`: UUID (Foreign Key to Bookings)

## Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL
- Docker (optional)

### Local Development Setup

1. Create and activate virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables:

```bash
# Create .env file
cp .env.example .env

# Edit .env with your database credentials
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/ticket_db
```

4. Run database migrations:

```bash
# Using Docker
docker-compose up -d postgres
docker-compose up db-migrations

# Or manually using psql
psql -U postgres -d ticket_db -f database/migrations/V202507030211__create_bookings_tickets_table.sql
```

5. Start the development server:

```bash
uvicorn src.main:app --reload
```

### Docker Setup

1. Build and run with Docker Compose:

```bash
docker-compose up -d
```

2. Check service logs:

```bash
docker-compose logs -f ticket-management-service
```

## API Documentation

Once the service is running, access the API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Bookings API

- `POST /api/v1/bookings`: Create a new booking with tickets
- `GET /api/v1/bookings/{booking_id}`: Retrieve booking details
- `PUT /api/v1/bookings/{booking_id}/confirm`: Confirm a booking
- `PUT /api/v1/bookings/{booking_id}/cancel`: Cancel a booking
- `PUT /api/v1/bookings/{booking_id}/refund`: Refund a booking

### Tickets API

- `GET /api/v1/tickets/user/{user_id}`: Get all tickets for a user
- `GET /api/v1/tickets/event/{event_id}`: Get all tickets for an event
- `GET /api/v1/tickets/event/{event_id}/available`: Get available ticket count

## Environment Variables

Required environment variables:

- `DATABASE_URL`: PostgreSQL connection string
- `POSTGRES_USER`: Database user
- `POSTGRES_PASSWORD`: Database password
- `POSTGRES_DB`: Database name

## Development

### Code Style

```bash
# Format code
black .

# Check types
mypy .
```
