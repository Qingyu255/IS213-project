# Ticket Management Service

A FastAPI-based microservice for managing event tickets and bookings.

## Features

- Create and manage event bookings
- Track booking status (pending, confirmed, canceled, refunded)
- Manage tickets associated with bookings
- View available tickets for events
- Track user's ticket history
- Hierarchical organization of events, bookings, and tickets
- Group bookings by event for better organization

## Tech Stack

- FastAPI
- SQLAlchemy (Async)
- PostgreSQL
- Docker
- Pydantic

## Project Structure

```
ticketManagementService/
├── database/                  # Database migrations and scripts
├── src/                      # Main source code directory
│   ├── api/                  # API layer
│   │   ├── routes/          # Route handlers
│   │   │   ├── bookings.py  # Booking endpoints
│   │   │   └── tickets.py   # Ticket endpoints
│   │   └── __init__.py      # API initialization
│   ├── core/                 # Core configurations
│   │   ├── auth.py          # Authentication utilities
│   │   ├── config.py        # Environment and app configs
│   │   └── database.py      # Database connection setup
│   ├── models/              # Database models
│   │   ├── booking.py       # Booking ORM model
│   │   └── ticket.py        # Ticket ORM model
│   ├── schemas/             # Data validation schemas
│   │   ├── booking.py       # Booking request/response schemas
│   │   └── ticket.py        # Ticket response schemas
│   ├── services/            # Business logic layer
│   │   ├── base_service.py  # Base service class
│   │   ├── booking_service.py # Booking operations
│   │   └── ticket_service.py  # Ticket operations
│   └── main.py             # Application entry point
├── venv/                   # Virtual environment (not in repo)
├── .env                    # Environment variables
├── Dockerfile             # Container configuration
├── README.md              # Service documentation
└── requirements.txt       # Python dependencies
```

## Directory Structure Explained

### Root Directory

- `Dockerfile`: Contains Docker build instructions for containerizing the service
- `requirements.txt`: Lists all Python package dependencies with versions
- `.env`: Contains environment variables for local development
- `README.md`: Documentation for the service

### src/ Directory

Main source code directory containing all application code:

#### api/

- Handles HTTP interface and request routing
- Contains FastAPI route definitions and endpoint handlers
- Manages request validation and response formatting
- Coordinates between HTTP requests and service layer

#### core/

- Contains essential service configurations and utilities
- `config.py`: Manages environment variables and app settings
- `database.py`: Handles database connection and session management
- Houses other core functionality like authentication and logging

#### models/

- Defines SQLAlchemy ORM models for database tables
- Contains data structure definitions and relationships
- Handles database schema representation in code
- Example: `booking.py` defines the structure of the bookings table

#### schemas/

- Contains Pydantic models for request/response validation
- Defines data validation rules and type checking
- Handles data serialization/deserialization
- Separates API contracts from database models

#### services/

- Implements core business logic and data operations
- Handles complex operations and transactions
- Provides reusable business logic layer
- Independent of HTTP/API concerns

#### main.py

- Application entry point
- Sets up FastAPI application
- Configures middleware and routes
- Initializes core components

## Data Organization

The service organizes data in a hierarchical structure:

1. **Events**

   - Top-level organization unit
   - Contains multiple bookings
   - Includes event-specific information

2. **Bookings**

   - Grouped by event
   - Contains status information (pending, confirmed, canceled, refunded)
   - Links to multiple tickets
   - Includes timestamps and user information

3. **Tickets**
   - Associated with a specific booking
   - Contains ticket-specific information
   - Includes validation status

## Database Schema

### Bookings Table

- `booking_id`: UUID (Primary Key)
- `user_id`: VARCHAR (String representation of UUID from userManagementService)
- `event_id`: UUID
- `status`: String (pending, confirmed, canceled, refunded)
- `created_at`: DateTime
- `updated_at`: DateTime

### Tickets Table

- `ticket_id`: UUID (Primary Key)
- `booking_id`: UUID (Foreign Key to Bookings)
- `created_at`: DateTime

## User Interface Organization

The frontend organizes the data in a hierarchical view:

1. **Event Level**

   - Events are displayed as cards
   - Shows event title and date
   - Groups all bookings for the event
   - Provides a link to view detailed event information

2. **Booking Level**

   - Displayed within event cards in an accordion
   - Shows booking status and ID
   - Provides action buttons (cancel/refund) based on status
   - Groups tickets associated with the booking

3. **Ticket Level**
   - Listed within each booking
   - Shows ticket ID and status
   - Provides a link to view detailed ticket information

## User ID Handling

The ticketManagementService uses the following approach for user identification:

1. **Primary Identifier**: The service first looks for the `custom:id` claim in the Cognito JWT token, which is a string representation of the UUID generated by the userManagementService when a user is created.

2. **Fallback Identifier**: If `custom:id` is not present, the service falls back to using the `sub` claim from the JWT token as the user identifier.

The authentication flow works as follows:

1. When a user is created in userManagementService, a UUID is generated using `Guid.NewGuid().ToString()`
2. This UUID is stored in the userManagementService database and also sent to AWS Cognito as a custom attribute (`custom:id`)
3. When a user logs in, Cognito issues a JWT token that contains either:
   - A `custom:id` claim (for newer users created with the custom attribute)
   - A `sub` claim (for all users, as this is a standard JWT claim)
4. The ticketManagementService extracts either the `custom:id` or `sub` from the JWT token and uses it as the user identifier
5. This ensures compatibility with both new and existing users

## API Endpoints

### Bookings API

- `POST /api/v1/mgmt/bookings`: Create a new booking with tickets
- `GET /api/v1/mgmt/bookings/{booking_id}`: Retrieve booking details
- `GET /api/v1/mgmt/bookings/user/{user_id}`: Get all bookings for a user (grouped by event)
- `PUT /api/v1/mgmt/bookings/{booking_id}/confirm`: Confirm a booking
- `PUT /api/v1/mgmt/bookings/{booking_id}/cancel`: Cancel a booking
- `PUT /api/v1/mgmt/bookings/{booking_id}/refund`: Refund a booking

### Tickets API

- `GET /api/v1/tickets/user/{user_id}`: Get all tickets for a user
- `GET /api/v1/tickets/event/{event_id}`: Get all tickets for an event
- `GET /api/v1/tickets/event/{event_id}/available`: Get available ticket count
- `GET /api/v1/tickets/user/{user_id}/event/{event_id}`: Get user's tickets for a specific event

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
