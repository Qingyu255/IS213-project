import requests
import time
from typing import Optional, Dict, Any, List
from uuid import UUID
from src.config.settings import EVENT_SERVICE_URL
import logging

logger = logging.getLogger()


class EventServiceException(Exception):
    """Custom exception for event service errors"""
    pass

class EventService:
    def __init__(self):
        self.base_url = EVENT_SERVICE_URL
        self.timeout = 10.0
        self.max_retries = 3
        self.initial_backoff = 1.0  # 1 second

    def _make_request_with_retry(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request with retry mechanism"""
        retries = 0
        backoff = self.initial_backoff

        while retries < self.max_retries:
            try:
                response = requests.get(
                    f"{self.base_url}/{endpoint}",
                    params=params,
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.ConnectionError as e:
                retries += 1
                if retries == self.max_retries:
                    logger.error(f"Network error after {retries} retries: {str(e)}")
                    raise EventServiceException(f"Network error: {str(e)}")
                logger.warning(f"Network error (attempt {retries}/{self.max_retries}): {str(e)}")
                time.sleep(backoff)
                backoff *= 2  # Exponential backoff
            except requests.exceptions.HTTPError as e:
                logger.error(f"HTTP error: {str(e)}")
                raise EventServiceException(f"HTTP error: {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
                raise EventServiceException(f"Unexpected error: {str(e)}")

    def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get event details from the events service"""
        try:
            # Convert string ID to UUID to match service expectation
            event_uuid = UUID(event_id)
            return self._make_request_with_retry(f"api/v1/events/{event_uuid}")
        except ValueError as e:
            logger.error(f"Invalid event ID format: {str(e)}")
            return None
        except EventServiceException as e:
            logger.error(f"Error fetching event details: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching event details: {str(e)}")
            return None

   