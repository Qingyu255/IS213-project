# src/clients/billing_client.py

import requests
from src.config.settings import BILLING_MS_URL


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
            # You can log the exception here if needed.
            return {
                "success": False,
                "message": f"Error communicating with Billing MS: {str(e)}"
            }
