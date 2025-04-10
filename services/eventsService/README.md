# Events Microservice

This microservice is responsible for managing events, including creating, updating, reading, and deleting event data. It is built using Flask and follows a modular structure for scalability and maintainability.

## Project Structure

```
eventsMicroservice/
├── src/
│   ├── api/                 # API routes and dependencies
│   │   ├── routes/
│   │   │   ├── events.py    # Event CRUD handlers
│   ├── core/                # Core configurations
│   │   ├── config.py        # Environment and app configs
│   │   ├── database.py      # Database connection setup
│   ├── models/              # SQLAlchemy models
│   │   ├── event.py         # Event data model
│   ├── schemas/             # Pydantic models
│   │   ├── event.py         # Event request/response models
│   ├── services/            # Business logic
│   │   ├── event_service.py # Event CRUD operations
│   ├── main.py              # Flask application entry point
│   ├── migrations/          # Flyway migration scripts
│   │   ├── V1__create_events_table.sql
├── Dockerfile               # Container configuration
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables
├── README.md                # Project documentation
```

## Event Model and Schemas

The event model and schemas are designed to align with the frontend object types. Below is the structure:

### `models/event.py`

- **id**: UUID  
- **title**: String  
- **description**: String  
- **startDateTime**: DateTime  
- **endDateTime**: DateTime (optional)  
- **venue**: JSON (with address, name, city, state, additionalDetails, coordinates {lat, lng})  
- **imageUrl**: String  
- **category**: String (InterestCategory as enum)  
- **price**: JSON (with amount and currency)  
- **schedule**: JSON (list of objects with startTime, endTime, title, description)  
- **organizer**: JSON (with id, username)  
- **totalAttendees**: Integer  
- **capacity**: Integer (optional)  
- **eventType**: String (public/private)  
- **invitedEmails**: JSON (optional list of emails)  
- **createdAt**: DateTime  
- **updatedAt**: DateTime  

### `schemas/event.py`

The Pydantic schemas are used for request validation and response serialization:

- **EventCreate**: Schema for creating an event.  
- **EventCreateResponse**: Schema for the response after creating an event.  
- **EventUpdate**: Schema for updating an event.  
- **EventRead**: Schema for reading event details.  

## Features

- **CRUD Operations**: Create, read, update, and delete events.  
- **Validation**: Input validation using Pydantic schemas.  
- **Database Integration**: SQLAlchemy models for database interaction.  
- **Modular Design**: Separation of concerns for better maintainability.  

## Setup Instructions

1. Clone the repository.  
2. Navigate to the `eventsService` directory.  
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up the environment variables in the `.env` file.  
5. Run the application:
   ```bash
   python src/main.py
   ```

## Docker Support

Build and run the service using Docker:

1. Build the Docker image:  
   ```bash
   docker build -t events-service .
   ```
2. Run the container:  
   ```bash
   docker run -p 8001:8001 events-service
   ```

## License

This project is licensed under the MIT License.
