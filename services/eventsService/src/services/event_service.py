## business logic for CRUD operations on events

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete  
from fastapi import HTTPException
from ..models.events import Event
from ..models.eventCategory import EventCategory
from ..models.eventOrganizers import EventOrganizer
from ..models.category import Category
from ..schemas.event import EventCreate, EventUpdate
from pydantic import UUID4
import uuid

async def create_event(event_data: EventCreate, db: AsyncSession):
    async with db.begin():
        # Create the event record
        new_event = Event(
            title=event_data.title,
            description=event_data.description,
            start_date_time=event_data.start_date_time,
            end_date_time=event_data.end_date_time,
            image_url=event_data.image_url,
            venue=event_data.venue,
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

        # Process each organizer name provided.
        for organizer_name in event_data.organizers:
            organizer = EventOrganizer(
                event_id=new_event.id,
                organizer_id=uuid.uuid4(),  # Generating a new UUID for organizer_id
                name=organizer_name
            )
            db.add(organizer)

    # Commit happens here automatically at the end of the context block if no exception is raised
    await db.refresh(new_event)

    return {
        "message": f"Event '{new_event.title}' has been created successfully",
        "id": new_event.id,
        "title": new_event.title,
        "description": new_event.description,
        "start_date_time": new_event.start_date_time,
        "end_date_time": new_event.end_date_time,
        "image_url": new_event.image_url,
        "venue": new_event.venue,
        "price": new_event.price,
        "capacity": new_event.capacity,
        "created_at": new_event.created_at,
        "updated_at": new_event.updated_at,
        "categories": event_data.categories,
        "organizers": event_data.organizers
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

    # Fetch event organizers (now using the `name` column)
    organizer_result = await db.execute(
        select(EventOrganizer.name)  # Fetch organizer names directly
        .filter(EventOrganizer.event_id == event_id)
    )
    organizers = organizer_result.scalars().all()  # Extract organizer names

    return {
        "id": event.id,
        "title": event.title,
        "description": event.description,
        "start_date_time": event.start_date_time,
        "end_date_time": event.end_date_time,
        "image_url": event.image_url,
        "venue": event.venue,
        "price": event.price,
        "capacity": event.capacity,
        "created_at": event.created_at,
        "updated_at": event.updated_at,
        "categories": categories,  # List of category names
        "organizers": organizers  # List of organizer names
    }

############################################################################################################
# Get all events along with their categories and organizers
async def get_all_events(db: AsyncSession, skip: int = 0, limit: int = 100):
    # Fetch all events with pagination
    result = await db.execute(select(Event).offset(skip).limit(limit))
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

        # Fetch event organizers
        organizer_result = await db.execute(
            select(EventOrganizer.name)
            .filter(EventOrganizer.event_id == event.id)
        )
        organizers = organizer_result.scalars().all()

        # Append event details with categories and organizers
        event_list.append({
            "id": event.id,
            "title": event.title,
            "description": event.description,
            "start_date_time": event.start_date_time,
            "end_date_time": event.end_date_time,
            "image_url": event.image_url,
            "venue": event.venue,
            "price": event.price,
            "capacity": event.capacity,
            "created_at": event.created_at,
            "updated_at": event.updated_at,
            "categories": categories,  # List of category names
            "organizers": organizers  # List of organizer names
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
    update_data = event_data.dict(exclude_unset=True, exclude={"categories", "organizers"})
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
    if event_data.organizers is not None:
        # Remove existing event_organizer associations for this event.
        await db.execute(delete(EventOrganizer).where(EventOrganizer.event_id == event_id))
        # Add new organizer records.
        for organizer_name in event_data.organizers:
            organizer = EventOrganizer(
                event_id=event.id,
                organizer_id=uuid.uuid4(),
                name=organizer_name
            )
            db.add(organizer)

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


