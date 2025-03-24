"""
API routes for event-related payment operations
"""
from flask import Blueprint, request, jsonify, abort
import logging
from services.payment_verification_service import PaymentVerificationService


logger = logging.getLogger(__name__)

payment_verification_service = PaymentVerificationService()

events_bp = Blueprint('events', __name__)

@events_bp.route("/verify-payment", methods=['GET'])
def verify_event_payment():
    """
    Verify payment status for an event
    
    Query Parameters:
      - event_id: ID of the event to verify payment for
      - organizer_id: (Optional) ID of the organizer for additional verification
    
    Returns:
      JSON object with payment verification details
    """
    event_id = request.args.get('event_id')
    organizer_id = request.args.get('organizer_id')
    
    if not event_id:
        return jsonify({
            "success": False,
            "error": "Missing event_id parameter"
        }), 400
    
    try:
        # Get all verifications for this event
        verifications = payment_verification_service.get_verifications_by_event_id(event_id)
        
        # Filter by organizer_id if provided
        if organizer_id:
            verifications = [
                v for v in verifications
                if (v.get("verification_data", {}).get("organizer_id") == organizer_id or
                   v.get("verification_data", {}).get("metadata", {}).get("organizer_id") == organizer_id)
            ]
        
        # Find successful payments
        successful_payments = [
            v for v in verifications 
            if v.get("status") == "succeeded" or
               v.get("payment_status") == "succeeded" or
               v.get("verification_data", {}).get("payment_status") == "succeeded"
        ]
        
        # Calculate total paid amount
        total_paid = sum(
            payment.get("amount", 0) 
            for payment in successful_payments
        )
        
        # Determine if the event is paid for
        is_paid = len(successful_payments) > 0
        
        return jsonify({
            "success": True,
            "event_id": event_id,
            "is_paid": is_paid,
            "total_paid": total_paid,
            "currency": successful_payments[0].get("currency", "usd") if successful_payments else "usd",
            "verification_count": len(verifications),
            "successful_payment_count": len(successful_payments),
            "latest_payment": successful_payments[0] if successful_payments else None
        })
    except Exception as e:
        logger.error(f"Error verifying payment for event {event_id}: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Error verifying payment: {str(e)}"
        }), 500

@events_bp.route("/payment-history", methods=['GET'])
def event_payment_history():
    """
    Get payment history for an event
    
    Query Parameters:
      - event_id: ID of the event to get payment history for
      - organizer_id: (Optional) ID of the organizer for additional filtering
    
    Returns:
      JSON object with payment history details
    """
    event_id = request.args.get('event_id')
    organizer_id = request.args.get('organizer_id')
    
    if not event_id:
        return jsonify({
            "success": False,
            "error": "Missing event_id parameter"
        }), 400
    
    try:
        # Get all verifications for this event
        verifications = payment_verification_service.get_verifications_by_event_id(event_id)
        
        # Filter by organizer_id if provided
        if organizer_id:
            verifications = [
                v for v in verifications
                if (v.get("verification_data", {}).get("organizer_id") == organizer_id or
                   v.get("verification_data", {}).get("metadata", {}).get("organizer_id") == organizer_id)
            ]
        
        # Return payment history
        return jsonify({
            "success": True,
            "event_id": event_id,
            "payment_history": verifications
        })
    except Exception as e:
        logger.error(f"Error retrieving payment history for event {event_id}: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Error retrieving payment history: {str(e)}"
        }), 500 