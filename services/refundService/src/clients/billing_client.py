# src/clients/billing_client.py

import requests
import logging
from src.config.settings import BILLING_MS_URL, TICKET_SERVICE_URL, BOOKING_SERVICE_URL

logger = logging.getLogger(__name__)
class BillingClient:
    def process_refund(self, payment_intent_id: str, amount: int, reason: str = None, metadata: dict = None) -> dict:
        
        url = f"{BILLING_MS_URL}/api/refund/process"
        
        # Build the refund payload
        payload = {
            "payment_intent_id": payment_intent_id,
            "amount": amount,
            "reason": reason,
            "metadata": metadata
        }
        
        # Remove keys with None values to keep the payload clean
        payload = {key: value for key, value in payload.items() if value is not None}
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()  # Raise an error for non-2xx responses
            return response.json()
        
        except requests.RequestException as e:
            # Handle network-related errors (e.g., connection issues)
            logger.error(f"Error communicating with Billing MS: {str(e)}")
            return {
                "success": False,
                "message": f"Error communicating with Billing MS: {str(e)}"
            }


    def get_payment_details(self, event_id: str, organizer_id: str) -> dict:
        """
        Fetch payment details (payment_intent_id and amount) for a given event and organizer.
        
        Args:
            event_id (str): Event ID
            organizer_id (str): Organizer ID
        
        Returns:
            dict: Payment details (e.g., payment_intent_id, amount) or an error message
        """
        url = f"{BILLING_MS_URL}/api/events/payment-ids-and-amount"
        
        # Build the query parameters
        params = {
            "event_id": event_id,
            "organizer_id": organizer_id
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()  # Raise an error for non-2xx responses
            
            data = response.json()
            
            if not data.get("success", False):
                return {
                    "success": False,
                    "message": data.get("error", "Failed to fetch payment details")
                }
            
            # Extract the first payment detail (assuming there's at least one)
            payment_details = data.get("payment_details", [])
            if not payment_details:
                return {
                    "success": False,
                    "message": "No payment details found for the given event_id and organizer_id"
                }
            
            first_payment = payment_details[0]
            return {
                "success": True,
                "payment_intent_id": first_payment.get("payment_id"),
                "amount": first_payment.get("amount"),
                "currency": first_payment.get("currency")
            }
        
        except requests.RequestException as e:
            # Log the exception here if needed
            return {
                "success": False,
                "message": f"Error communicating with Billing MS: {str(e)}"
            }
    
    # add function to call billing microservice using booking id
    def get_payment_details_from_booking(self, booking_id: str) -> dict:
        """
        Fetch payment details (payment_intent_id and amount) for a given booking.
        
        Args:
            booking_id (str): Unique identifier for the booking
        
        Returns:
            dict: Payment details (e.g., payment_intent_id, amount) or an error message
        """
        url = f"{BILLING_MS_URL}/payments/intent/{booking_id}" #Test
        
        try:
            logger.debug(f"Fetching payment details for booking_id: {booking_id}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Raise an error for non-2xx responses
            
            data = response.json()
            
            if not data.get("success", False):
                logger.error(f"Failed to fetch payment details for booking_id={booking_id}: {data.get('message')}")
                return {
                    "success": False,
                    "message": data.get("message", "Failed to fetch payment details")
                }
            
            # Extract payment_intent_id and amount from the response
            payment_intent_id = data.get("payment_intent_id")
            amount = data.get("amount")
            
            if not payment_intent_id or not amount:
                logger.error(f"Incomplete payment details for booking_id={booking_id}: {data}")
                return {
                    "success": False,
                    "message": "Incomplete payment details received from Billing MS"
                }
            
            return {
                "success": True,
                "payment_intent_id": payment_intent_id,
                "amount": amount
            }
        
        except requests.RequestException as e:
            logger.error(f"Error communicating with Billing MS for booking_id={booking_id}: {str(e)}")
            return {
                "success": False,
                "message": f"Error communicating with Billing MS: {str(e)}"
            }
        

    #add function to update booking status by calling ticketManagementService
    def update_booking_status(self, booking_id: str, authorization: str = None) -> dict:
        """
        Updates the status of a booking in the Ticket Service to "refunded".
        
        Args:
            booking_id (str): Unique identifier for the booking
        
        Returns:
            dict: Response indicating success or failure, including the updated status
        """
        url = f"{TICKET_SERVICE_URL}/api/v1/mgmt/bookings/{booking_id}/refund"
        headers = {}
        if authorization:
            headers["Authorization"] = authorization

        try:
            logger.debug(f"Updating booking status for booking_id={booking_id} to 'refunded'")
            response = requests.post(url, headers=headers, timeout=10)
            response.raise_for_status()  # Raise an error for non-2xx responses
            
            data = response.json()
            logger.info(f"Received response from Ticket Service: {data}")
        
            # Infer success based on the presence of a valid "message" field
            if "message" in data and "REFUNDED" in data["message"]:
                logger.info(f"Booking {booking_id} successfully updated to 'refunded'")
                return {
                    "success": True,
                    "message": data["message"],
                    "status": "REFUNDED"  # Assume status is REFUNDED based on the message
                }
            else:
                logger.error(f"Unexpected response format from Ticket Service for booking_id={booking_id}: {data}")
                return {
                    "success": False,
                    "message": "Unexpected response format from Ticket Service",
                    "status": None
                }
        
        except requests.HTTPError as e:
            # Log HTTP errors (e.g., 4xx or 5xx responses)
            logger.error(f"HTTP error updating booking status for booking_id={booking_id}: {str(e)}")
            return {
                "success": False,
                "message": f"HTTP error: {str(e)}",
                "status": None
            }
        
        except requests.RequestException as e:
            # Log connection or timeout errors
            logger.error(f"Error communicating with Ticket Service for booking_id={booking_id}: {str(e)}")
            return {
                "success": False,
                "message": f"Error communicating with Ticket Service: {str(e)}",
                "status": None
            }
        
    ## get booking
       
    # Existing methods...

    def get_booking(self, booking_id: str, authorization: str = None):
        """
        Fetch booking details for a given booking ID by calling the Booking Service.
        
        Args:
            booking_id (str): Unique identifier for the booking
            authorization (str): Bearer token for authentication
        
        Returns:
            dict: Booking details
        
        Raises:
            Exception: If the request fails or the response indicates an error
        """
        url = f"{BOOKING_SERVICE_URL}/api/v1/bookings/{booking_id}"
        headers = {}
        if authorization:
            headers["Authorization"] = authorization

        try:
            logger.debug(f"Fetching booking details for booking_id={booking_id}")
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()  # Raise an error for non-2xx responses
            
            data = response.json()
            
            # Log the fetched booking details
            logger.info(f"Fetched booking details for booking_id={booking_id}: {data}")
            
            return data
        
        except requests.HTTPError as e:
            # Log HTTP errors (e.g., 4xx or 5xx responses)
            logger.error(f"HTTP error fetching booking details for booking_id={booking_id}: {str(e)}")
            raise Exception(f"Failed to fetch booking details: {response.status_code} {response.reason}")
        
        except requests.RequestException as e:
            # Log connection or timeout errors
            logger.error(f"Error communicating with Booking Service for booking_id={booking_id}: {str(e)}")
            raise Exception(f"Error communicating with Booking Service: {str(e)}")