## integrate api endpoints with the service

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from pydantic import UUID4
from src.schemas.event import EventCreate, EventUpdate, EventRead, EventCreateResponse
from src.services.event_service import (
    create_event,
    get_event_by_id,
    get_all_events,
    update_event,
    delete_event,
)
from src.db.connection import get_db 
from src.core.auth import get_current_user_id, validate_token

router = APIRouter(prefix="/events", tags=["Events"])

@router.post("/create", response_model=EventCreateResponse)
async def create_event_endpoint(event: EventCreate, db: AsyncSession = Depends(get_db) ):
    """
    Create a new event.
    """
    return await create_event(event, db)

@router.get("/{event_id}", response_model=EventRead)
async def get_event_by_id_endpoint(event_id: UUID4, db: AsyncSession = Depends(get_db)):
    """
    Retrieve a single event by its ID along with associated categories and organizers.
    """
    return await get_event_by_id(event_id, db)

@router.get("/", response_model=List[EventRead])
async def get_all_events_endpoint(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    """
    Retrieve all events with pagination.
    """
    return await get_all_events(db, skip, limit)

@router.put("/update/{event_id}", response_model=EventRead)
async def update_event_endpoint(event_id: UUID4, event: EventUpdate, db: AsyncSession = Depends(get_db), user_id: str = Depends(get_current_user_id) ):
    """
    Update an existing event.
    """
    return await update_event(event_id, event, db, user_id)

@router.delete("/delete/{event_id}")
async def delete_event_endpoint(event_id: UUID4, db: AsyncSession = Depends(get_db), user_id: str = Depends(get_current_user_id) ):
    """
    Delete an event by its ID.
    """
    return await delete_event(event_id, db, user_id)
