from typing import Dict, Any, Optional
import requests
import logging
from src.config.settings import NOTIFICATIONS_MICROSERVICE_URL

logger= logging.getLogger()


class NotificationServiceException(Exception):
    """Custom exception for notification service errors"""
    pass

class NotificationService:
    def __init__(self):
        # Base URL for the notification service
        self.base_url = NOTIFICATIONS_MICROSERVICE_URL
        self.refund_endpoint = f"{self.base_url}/refund"  # For booking confirmations

    def send_refund_confirmation(
        self,
        booking_id: str,
        customer_email: str,
        event_name: str,
        ticket_quantity: int,
        total_amount: float,
        event_start_datetime: str,
        event_end_datetime: str
    ) -> None:
        """Send refund confirmation email"""
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

            logger.info(f"Attempting to send refund confirmation to: {customer_email}")
            logger.info(f"Using endpoint URL: {self.refund_endpoint}")
            logger.info(f"Full notification payload: {payload}")

            # Make request to OutSystems notification service
            response = requests.post(
                self.refund_endpoint,
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
                
            logger.info(f"Successfully sent refund confirmation for refund {booking_id} to {customer_email}")
            return response_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send refund confirmation: {str(e)}")
            raise NotificationServiceException(f"Failed to send refund confirmation: {str(e)}")
        except Exception as e:
            logger.error(f"Error sending refund confirmation: {str(e)}")
            raise NotificationServiceException(f"Error sending refund confirmation: {str(e)}")