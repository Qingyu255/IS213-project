"""
Service for handling payment verification business logic
"""
import logging
import os
import json
from datetime import datetime
import uuid
from typing import Dict, Any, List, Optional
from repositories.payment_verification_repository import PaymentVerificationRepository

logger = logging.getLogger(__name__)

class PaymentVerificationService:
    """Service for handling payment verification operations"""
    
    def __init__(self, repository=None):
        """Initialize with optional repository"""
        self._repository = repository or PaymentVerificationRepository()
    
    def save_verification(self, verification_data):
        """
        Save payment verification data to the database
        
        Args:
            verification_data (dict): Payment verification data
            
        Returns:
            dict: Saved verification as dictionary
        """
        try:
            record_data = {
                'payment_id': verification_data.get('payment_intent_id') or verification_data.get('session_id', ''),
                'event_id': verification_data.get('event_id'),
                'organizer_id': verification_data.get('metadata').get('organizer_id'),
                'user_id': verification_data.get('user_id'),
                'event_type': verification_data.get('event_type'),
                'amount': self._extract_amount(verification_data),
                'currency': self._extract_currency(verification_data),
                'status': verification_data.get('payment_status'),
                'payment_method': verification_data.get('payment_details', {}).get('payment_method'),
                'receipt_email': verification_data.get('payment_details', {}).get('receipt_email'),
                'receipt_url': verification_data.get('charge_details', {}).get('receipt_url'),
                'created_at': datetime.fromtimestamp(verification_data.get('timestamp', 0)) if verification_data.get('timestamp') else None
            }
            
            # Save to database
            verification = self._repository.save(record_data)
            logger.info(f"Saved payment verification to database: {verification.id}")
            
            # Also maintain the file-based backup
            self._save_to_file(verification_data)
            
            return verification.to_dict()
        except Exception as e:
            logger.error(f"Error saving payment verification: {str(e)}")
            # Retry attempt to save to file even if database save fails
            self._save_to_file(verification_data)
            raise
    
    def _extract_amount(self, verification_data):
        """Extract amount from verification data"""
        if 'payment_details' in verification_data:
            return verification_data['payment_details'].get('amount') or verification_data['payment_details'].get('amount_total')
        return None
    
    def _extract_currency(self, verification_data):
        """Extract currency from verification data"""
        if 'payment_details' in verification_data:
            return verification_data['payment_details'].get('currency')
        return 'usd'  # Default
    
    def _save_to_file(self, verification_data):
        """Save verification data to a file as backup"""
        try:
            verification_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'payment_verifications')
            os.makedirs(verification_dir, exist_ok=True)
            
            payment_id = verification_data.get('payment_intent_id') or verification_data.get('session_id', 'unknown')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            verification_file = os.path.join(
                verification_dir, 
                f"payment_verification_{timestamp}_{payment_id}.json"
            )
            
            with open(verification_file, 'w') as f:
                json.dump(verification_data, f, indent=2)
                
            logger.info(f"Payment verification record saved to file: {verification_file}")
        except Exception as e:
            logger.error(f"Failed to save payment verification to file: {str(e)}")
    
    def get_verifications_by_payment_id(self, payment_id):
        """
        Get verifications by payment ID
        
        Args:
            payment_id (str): Payment intent ID or checkout session ID
            
        Returns:
            list: List of verification dictionaries
        """
        verifications = self._repository.find_by_payment_id(payment_id)
        return [v.to_dict() for v in verifications]
    
    def get_verifications_by_event_id(self, event_id):
        """
        Get verifications by event ID
        
        Args:
            event_id (str): Event ID
            
        Returns:
            list: List of verification dictionaries
        """
        verifications = self._repository.find_by_event_id(event_id)
        return [v.to_dict() for v in verifications]
    
    def get_verifications_by_event_id_and_organizer_id(self, event_id, organizer_id):
        """
        Get verifications by event ID
        
        Args:
            event_id (str): Event ID
            organizer_id (str): Organizer ID
            
        Returns:
            list: List of verification dictionaries
        """
        verifications = self._repository.find_by_event_id_and_organizer_id(event_id, organizer_id)
        return [v.to_dict() for v in verifications]
    
    def get_verifications_by_user_id(self, user_id):
        """
        Get verifications by user ID
        
        Args:
            user_id (str): User ID
            
        Returns:
            list: List of verification dictionaries
        """
        verifications = self._repository.find_by_user_id(user_id)
        return [v.to_dict() for v in verifications]
    
    def get_all_verifications(self, page=1, page_size=50):
        """
        Get all verifications with pagination
        
        Args:
            page (int): Page number (1-based)
            page_size (int): Page size
            
        Returns:
            dict: Dictionary with verifications and pagination info
        """
        offset = (page - 1) * page_size
        verifications = self._repository.find_all(limit=page_size, offset=offset)
        total = self._repository.count_all()
        
        return {
            'verifications': [v.to_dict() for v in verifications],
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total': total,
                'total_pages': (total + page_size - 1) // page_size
            }
        }
        
    def close(self):
        """Close the repository session"""
        if self._repository:
            self._repository.close() 