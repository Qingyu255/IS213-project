import httpx
from typing import Optional, Dict, Any, List
from uuid import UUID
from ..core.config import get_settings
from ..core.logging import logger

settings = get_settings()

class EventService:
    def __init__(self):
        self.base_url = settings.EVENT_SERVICE_URL
        self.timeout = httpx.Timeout(10.0)

    async def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get event details from the events service"""
        try:
            # Convert string ID to UUID to match service expectation
            event_uuid = UUID(event_id)
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/events/{event_uuid}")
                response.raise_for_status()
                return response.json()
        except ValueError as e:
            logger.error(f"Invalid event ID format: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error fetching event details: {str(e)}")
            return None

    async def get_all_events(self, skip: int = 0, limit: int = 10) -> List[Dict[str, Any]]:
        """Get list of events with pagination"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/events",
                    params={"skip": skip, "limit": limit}
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error fetching events list: {str(e)}")
            return []

   