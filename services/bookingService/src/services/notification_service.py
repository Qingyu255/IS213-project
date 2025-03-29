from typing import Dict, Any, Optional
import requests
from ..core.config import get_settings
from ..core.logging import logger

settings = get_settings()

class NotificationServiceException(Exception):
    """Custom exception for notification service errors"""
    pass

class NotificationService:
    def __init__(self):
        # Base URL for the notification service
        self.base_url = settings.NOTIFICATIONS_MICROSERVICE_URL
        self.booking_endpoint = f"{self.base_url}/rest/confirmation/booking"  # For booking confirmations

    def send_booking_confirmation(
        self,
        booking_id: str,
        customer_email: str,
        event_name: str,
        ticket_quantity: int,
        total_amount: float,
        user_id: str,
        event_datetime: str,
        additional_info: Optional[Dict[str, Any]] = None
    ) -> None:
        """Send booking confirmation email"""
        try:
            # Prepare request payload in OutSystems format
            payload = {
                "user_id": user_id,
                "email": customer_email,
                "event_name": event_name,
                "event_datetime": event_datetime,
                "booking_id": booking_id,
                "ticket_quantity": str(ticket_quantity),
                "total_amount": float(total_amount)
            }

            logger.info(f"Attempting to send booking confirmation to: {customer_email}")
            logger.debug(f"Notification payload: {payload}")

            # Make request to OutSystems notification service
            response = requests.post(
                self.booking_endpoint,
                json=payload
            )
            response.raise_for_status()
            
            response_data = response.json()
            if not response_data.get("Success", False): 
                error_msg = response_data.get("ErrorMsg") or "Unknown error from notification service"
                raise NotificationServiceException(f"Notification service error: {error_msg}")
                
            logger.info(f"Successfully sent booking confirmation for booking {booking_id} to {customer_email}")
            return response_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send booking confirmation: {str(e)}")
            raise NotificationServiceException(f"Failed to send booking confirmation: {str(e)}")
        except Exception as e:
            logger.error(f"Error sending booking confirmation: {str(e)}")
            raise NotificationServiceException(f"Error sending booking confirmation: {str(e)}")