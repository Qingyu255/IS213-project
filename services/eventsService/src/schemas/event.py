from pydantic import BaseModel, UUID4
from datetime import datetime
from typing import Optional, List
from decimal import Decimal

class EventCreate(BaseModel):
    title: str
    description: Optional[str]
    start_date_time: datetime
    end_date_time: Optional[datetime]
    image_url: Optional[str]
    venue: Optional[str]
    price: Decimal
    capacity: int
    # List of category names that the user inputs
    categories: List[str]
    # List of organizer names associated with the event
    organizers: List[str]

class EventCreateResponse(BaseModel):
    message: str
    id: UUID4
    title: str
    description: Optional[str]
    start_date_time: datetime
    end_date_time: Optional[datetime]
    image_url: Optional[str]
    venue: Optional[str]
    price: Decimal
    capacity: int
    # List of category names that the user inputs
    categories: List[str]
    # List of organizer names associated with the event
    organizers: List[str]
    

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_date_time: Optional[datetime] = None
    end_date_time: Optional[datetime] = None
    image_url: Optional[str] = None
    venue: Optional[str] = None
    price: Optional[Decimal] = None
    capacity: Optional[int] = None
    # Optionally update categories and organizers using names
    categories: Optional[List[str]] = None
    organizers: Optional[List[str]] = None

class EventRead(BaseModel):
    id: UUID4
    title: str
    description: Optional[str]
    start_date_time: datetime
    end_date_time: Optional[datetime]
    image_url: Optional[str]
    venue: Optional[str]
    price: Decimal
    capacity: int
    created_at: datetime
    updated_at: datetime
    categories: List[str]
    organizers: List[str]

    class Config:
        orm_mode = True
