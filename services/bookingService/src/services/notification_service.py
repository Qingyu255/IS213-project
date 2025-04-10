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
        event_start_datetime: str,
        event_end_datetime: str
    ) -> None:
        """Send booking confirmation email"""
        try:
            # Prepare request payload in OutSystems format
            payload = {
                "email": customer_email,
                "event_name": event_name,
                "event_start_datetime": event_start_datetime,
                "event_end_datetime": event_end_datetime,
                "booking_id": booking_id,
                "ticket_quantity": ticket_quantity,
                "total_amount": total_amount
            }

            logger.info(f"Attempting to send booking confirmation to: {customer_email}")
            logger.info(f"Using endpoint URL: {self.booking_endpoint}")
            logger.info(f"Full notification payload: {payload}")

            # Make request to OutSystems notification service
            response = requests.post(
                self.booking_endpoint,
                json=payload,
                headers={'Content-Type': 'application/json'}  # Explicitly set content type
            )
            
            logger.info(f"Response status code: {response.status_code}")
            logger.info(f"Response headers: {dict(response.headers)}")
            logger.info(f"Response content: {response.text}")
            
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