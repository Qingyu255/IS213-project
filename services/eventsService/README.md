eventsMicroservice/
├── src/
│   ├── api/                     # API routes and dependencies
│   │   ├── routes/              # Route handlers
│   │   │   ├── events.py        # Event CRUD handlers
│   ├── core/                    # Core configurations
│   │   ├── config.py            # Environment and app configs
│   │   ├── database.py          # Database connection setup
│   ├── models/                  # SQLAlchemy models
│   │   ├── event.py             # Event data model
│   ├── schemas/                 # Pydantic models
│   │   ├── event.py             # Event request/response models
│   ├── services/                # Business logic
│   │   ├── event_service.py     # Event CRUD operations
│   ├── main.py                  # Flask application entry point
│   ├── migrations/              # Flyway migration scripts
│   │   ├── V1__create_events_table.sql
├── Dockerfile                   # Container configuration
├── requirements.txt              # Python dependencies
├── .env                          # Environment variables
├── README.md                     # Project documentation

# Updating event model and schemas based on frontend object type

models/event.py:
- id: UUID
- title: String
- description: String
- startDateTime: DateTime
- endDateTime: DateTime (optional)
- venue: JSON (with address, name, city, state, additionalDetails, coordinates {lat, lng})
- imageUrl: String
- category: String (InterestCategory as enum)
- price: JSON (with amount and currency)
- schedule: JSON (list of objects with startTime, endTime, title, description)
- organizer: JSON (with id, username)
- totalAttendees: Integer
- capacity: Integer (optional)
- eventType: String (public/private)
- invitedEmails: JSON (optional list of emails)
- createdAt: DateTime
- updatedAt: DateTime
