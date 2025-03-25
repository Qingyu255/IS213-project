from pydantic import BaseModel, UUID4
from datetime import datetime
from typing import Optional, List
from decimal import Decimal

class Organizer(BaseModel):
    id: str
    username: str

class Coordinates(BaseModel):
    lat: float
    lng: float

class Venue(BaseModel):
    address: str
    name: str
    city: str
    state: str
    additionalDetails: Optional[str] = None
    coordinates: Coordinates

class EventCreate(BaseModel):
    id: str
    title: str
    description: Optional[str]
    startDateTime: datetime
    endDateTime: Optional[datetime]
    imageUrl: Optional[str]
    venue: Optional[Venue]
    price: Decimal
    capacity: int
    # List of category names that the user inputs
    categories: List[str]
    # List of organizer names associated with the event
    organizer: Organizer

class EventCreateResponse(BaseModel):
    message: str
    id: UUID4
    title: str
    description: Optional[str]
    startDateTime: datetime
    endDateTime: Optional[datetime]
    imageUrl: Optional[str]
    venue: Optional[str]
    price: Decimal
    capacity: int
    # List of category names that the user inputs
    categories: List[str]
    # List of organizer names associated with the event
    organizer: Organizer
    

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    startDateTime: Optional[datetime] = None
    endDateTime: Optional[datetime] = None
    imageUrl: Optional[str] = None
    venue: Optional[Venue] = None
    price: Optional[Decimal] = None
    capacity: Optional[int] = None
    # Optionally update categories and organizer using names
    categories: Optional[List[str]] = None
    organizer: Optional[Organizer] = None

class EventRead(BaseModel):
    id: UUID4
    title: str
    description: Optional[str]
    startDateTime: datetime
    endDateTime: Optional[datetime]
    imageUrl: Optional[str]
    venue: Optional[Venue]
    price: Decimal
    capacity: int
    createdAt: datetime
    updatedAt: datetime
    categories: List[str]
    organizer: Organizer

    class Config:
        orm_mode = True
