## business logic for CRUD operations on events

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete  
from fastapi import HTTPException
from ..models.events import Event
from ..models.eventCategory import EventCategory
from ..models.eventOrganizers import EventOrganizer
from ..models.category import Category
from ..schemas.event import EventCreate, EventUpdate, Organizer, Venue
from pydantic import UUID4
import json

async def create_event(event_data: EventCreate, db: AsyncSession):
    async with db.begin():
        # Create the event record
        new_event = Event(
            id=event_data.id,
            title=event_data.title,
            description=event_data.description,
            start_date_time=event_data.startDateTime,
            end_date_time=event_data.endDateTime,
            image_url=event_data.imageUrl,
            venue=json.dumps(event_data.venue.dict() if event_data.venue else None),
            price=event_data.price,
            capacity=event_data.capacity,
        )
        db.add(new_event)
        await db.flush()  # flush to get new_event.id without committing

        # Process each category name provided.
        for category_name in event_data.categories:
            # Check if the category exists in the table.
            result = await db.execute(select(Category).filter(Category.name == category_name))
            category = result.scalars().first()
            if not category:
                raise HTTPException(status_code=400, detail=f"Category '{category_name}' does not exist")
            # Link the event with the existing category.
            event_category = EventCategory(event_id=new_event.id, category_id=category.id)
            db.add(event_category)

        # Process organizer id and username
        organizer = EventOrganizer(
            event_id=new_event.id,
            organizer_id=event_data.organizer.id,
            organizer_username=event_data.organizer.username
        )
        db.add(organizer)

    # Commit happens here automatically at the end of the context block if no exception is raised
    await db.refresh(new_event)

    return {
        "message": f"Event '{new_event.title}' has been created successfully",
        "id": new_event.id,
        "title": new_event.title,
        "description": new_event.description,
        "startDateTime": new_event.start_date_time,
        "endDateTime": new_event.end_date_time,
        "imageUrl": new_event.image_url,
        "venue": new_event.venue,
        "price": new_event.price,
        "capacity": new_event.capacity,
        "createdAt": new_event.created_at,
        "updatedAt": new_event.updated_at,
        "categories": event_data.categories,
        "organizer": event_data.organizer
    }

############################################################################################################

# Get an event by ID along with its categories and organizers
async def get_event_by_id(event_id: UUID4, db: AsyncSession):
    # Fetch the event
    result = await db.execute(select(Event).filter(Event.id == event_id))
    event = result.scalars().first()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Fetch event categories
    category_result = await db.execute(
        select(Category.name)
        .join(EventCategory, Category.id == EventCategory.category_id)
        .filter(EventCategory.event_id == event_id)
    )
    categories = category_result.scalars().all()  # Extract category names

    # Fetch event organizers
    organizer_result = await db.execute(
        select(EventOrganizer)
        .filter(EventOrganizer.event_id == event_id)
    )
    organizer_obj = organizer_result.scalars().first()
    organizer = Organizer(
        id=str(organizer_obj.organizer_id),
        username=organizer_obj.organizer_username
    )

    if event.venue:
        try:
            venue_data = json.loads(event.venue) # as venue is stored as a json string in db
            # Create a Venue instance using the parsed data
            venue_obj = Venue(**venue_data)
        except Exception:
            venue_obj = None
    else:
        venue_obj = None

    return {
        "id": event.id,
        "title": event.title,
        "description": event.description,
        "startDateTime": event.start_date_time,
        "endDateTime": event.end_date_time,
        "imageUrl": event.image_url,
        "venue": venue_obj,
        "price": event.price,
        "capacity": event.capacity,
        "createdAt": event.created_at,
        "updatedAt": event.updated_at,
        "categories": categories,  # List of category names
        "organizer": organizer
    }

############################################################################################################
# Get all events along with their categories and organizers
async def get_all_events(db: AsyncSession, skip: int = 0, limit: int = 100):
    # Fetch all events with pagination
    result = await db.execute(select(Event).order_by(Event.created_at.desc()).offset(skip).limit(limit))
    events = result.scalars().all()

    # Prepare list of events with categories and organizers
    event_list = []
    
    for event in events:
        # Fetch event categories
        category_result = await db.execute(
            select(Category.name)
            .join(EventCategory, Category.id == EventCategory.category_id)
            .filter(EventCategory.event_id == event.id)
        )
        categories = category_result.scalars().all()

        # Fetch event organizer
        organizer_result = await db.execute(
            select(EventOrganizer)
            .filter(EventOrganizer.event_id == event.id)
        )
        organizer_obj = organizer_result.scalars().first()
        organizer = Organizer(
            id=str(organizer_obj.organizer_id),
            username=organizer_obj.organizer_username
        )

        if event.venue:
            try:
                venue_data = json.loads(event.venue) # as venue is stored as a json string in db
                # Create a Venue instance using the parsed data
                venue_obj = Venue(**venue_data)
            except Exception:
                venue_obj = None
        else:
            venue_obj = None

        # Append event details with categories and organizers
        event_list.append({
            "id": event.id,
            "title": event.title,
            "description": event.description,
            "startDateTime": event.start_date_time,
            "endDateTime": event.end_date_time,
            "imageUrl": event.image_url,
            "venue": venue_obj,
            "price": event.price,
            "capacity": event.capacity,
            "createdAt": event.created_at,
            "updatedAt": event.updated_at,
            "categories": categories,  # List of category names
            "organizer": organizer
        })

    return event_list

############################################################################################################

# Update an event
async def update_event(event_id: UUID4, event_data: EventUpdate, db: AsyncSession):
    result = await db.execute(select(Event).filter(Event.id == event_id))
    event = result.scalars().first()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Update basic event fields (excluding associations)
    update_data = event_data.dict(exclude_unset=True, exclude={"categories", "organizer"})
    for key, value in update_data.items():
        setattr(event, key, value)

    # Update category associations if provided
    if event_data.categories is not None:
        # Remove existing event_category associations for this event.
        await db.execute(delete(EventCategory).where(EventCategory.event_id == event_id))
        # Validate each new category and add the association.
        for category_name in event_data.categories:
            result = await db.execute(select(Category).filter(Category.name == category_name))
            category = result.scalars().first()
            if not category:
                raise HTTPException(status_code=400, detail=f"Category '{category_name}' does not exist")
            new_association = EventCategory(event_id=event.id, category_id=category.id)
            db.add(new_association)

    # Update organizer associations if provided
    if event_data.organizer is not None:
        # Remove existing event_organizer associations for this event.
        await db.execute(delete(EventOrganizer).where(EventOrganizer.event_id == event_id))
        # Add new organizer record.
        organizer = EventOrganizer(
            event_id=event.id,
            organizer_id=event_data.organizer.id,
            organizer_username=event_data.organizer.username
        )
        db.add(organizer)

    if event_data.venue is not None:
        setattr(event, 'venue', json.dumps(event_data.venue.dict()))

    await db.commit()
    await db.refresh(event)

    return await get_event_by_id(event.id, db)


# Delete an event
async def delete_event(event_id: UUID4, db: AsyncSession):
    result = await db.execute(select(Event).filter(Event.id == event_id))
    event = result.scalars().first()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    event_name = event.title

    await db.delete(event)
    await db.commit()

    return {"message": f"Event '{event_name}' with id '{event_id}' has been deleted."}


