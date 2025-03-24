"""
Repository for PaymentVerification database operations
"""
import logging
from sqlalchemy.orm import Session
from sqlalchemy import desc
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, List, Dict, Any
from models.payment_verification import PaymentVerification
from models import get_session

class PaymentVerificationRepository:
    """Repository for payment verification records"""
    
    def __init__(self, session=None):
        """Initialize with optional session"""
        self._session = session or get_session()
    
    def save(self, payment_verification_data):
        """
        Save a new payment verification record
        
        Args:
            payment_verification_data (dict): Dictionary containing payment verification data
        
        Returns:
            PaymentVerification: The saved PaymentVerification instance
        """
        try:
            verification = PaymentVerification(**payment_verification_data)
            self._session.add(verification)
            self._session.commit()
            return verification
        except Exception as e:
            self._session.rollback()
            raise e
    
    def find_by_payment_id(self, payment_id):
        """
        Find payment verifications by payment ID
        
        Args:
            payment_id (str): Stripe payment intent ID or checkout session ID
        
        Returns:
            list: List of PaymentVerification instances
        """
        return self._session.query(PaymentVerification).filter(
            PaymentVerification.payment_id == payment_id
        ).order_by(desc(PaymentVerification.created_at)).all()
    
    def find_by_event_id(self, event_id):
        """
        Find payment verifications by event ID
        
        Args:
            event_id (str): Event ID in our system
        
        Returns:
            list: List of PaymentVerification instances
        """
        return self._session.query(PaymentVerification).filter(
            PaymentVerification.event_id == event_id
        ).order_by(desc(PaymentVerification.created_at)).all()
    
    def find_by_user_id(self, user_id):
        """
        Find payment verifications by user ID
        
        Args:
            user_id (str): User ID
        
        Returns:
            list: List of PaymentVerification instances
        """
        return self._session.query(PaymentVerification).filter(
            PaymentVerification.user_id == user_id
        ).order_by(desc(PaymentVerification.created_at)).all()
    
    def find_by_event_type(self, event_type, limit=50, offset=0):
        """
        Find payment verifications by event type
        
        Args:
            event_type (str): Stripe event type
            limit (int): Maximum number of records to return
            offset (int): Offset for pagination
        
        Returns:
            list: List of PaymentVerification instances
        """
        return self._session.query(PaymentVerification).filter(
            PaymentVerification.event_type == event_type
        ).order_by(desc(PaymentVerification.created_at)).limit(limit).offset(offset).all()
    
    def find_all(self, limit=50, offset=0):
        """
        Find all payment verifications with pagination
        
        Args:
            limit (int): Maximum number of records to return
            offset (int): Offset for pagination
        
        Returns:
            list: List of PaymentVerification instances
        """
        return self._session.query(PaymentVerification).order_by(
            desc(PaymentVerification.created_at)
        ).limit(limit).offset(offset).all()
    
    def count_all(self):
        """
        Count total number of payment verification records
        
        Returns:
            int: Total count of records
        """
        return self._session.query(PaymentVerification).count()
    
    def close(self):
        """Close the session"""
        if self._session:
            self._session.close() 