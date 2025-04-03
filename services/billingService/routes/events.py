"""
API routes for event-related payment operations
"""
from http import HTTPStatus
from flask import Blueprint, request, jsonify, abort
import logging
from services.payment_verification_service import PaymentVerificationService


logger = logging.getLogger(__name__)

payment_verification_service = PaymentVerificationService()

events_bp = Blueprint('events', __name__)

@events_bp.route("/verify-payment", methods=['GET'])
def verify_event_payment():
    """
    Verify payment status for an event by verifying completion of event_type: checkout.session.completed
    
    Query Parameters:
      - event_id: ID of the event to verify payment for
      - organizer_id: (Optional) ID of the organizer for additional verification
    
    Returns:
      JSON object with payment verification details
    """
    event_id = request.args.get('event_id')
    organizer_id = request.args.get('organizer_id')
    
    if not event_id or not organizer_id:
        return jsonify({
            "success": False,
            "error": "Missing event_id and/or organizer_id parameter"
        }), HTTPStatus.BAD_REQUEST
    
    try:
        # Get all verifications for this event
        verifications = payment_verification_service.get_verifications_by_event_id_and_organizer_id(event_id, organizer_id)
        
        # Find successful payments
        successful_payments = [
            v for v in verifications 
            if v.get("event_type") == "checkout.session.completed" and
               v.get("status") == "paid"
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
            "total_paid": total_paid, # in cents btw
            "currency": successful_payments[0].get("currency", "sgd"),
            "verification_count": len(verifications),
            "successful_payment_count": len(successful_payments),
            "latest_payment": successful_payments[0] if successful_payments else None
        })
    except Exception as e:
        logger.error(f"Error verifying payment for event {event_id}: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Error verifying payment: {str(e)}"
        }), HTTPStatus.INTERNAL_SERVER_ERROR


@events_bp.route("/payment-ids-and-amount", methods=['GET'])
def get_payment_ids():
    """
    Retrieve payment IDs and amounts for an event and organizer.
    
    Query Parameters:
      - event_id: ID of the event
      - organizer_id: ID of the organizer
    
    Returns:
      JSON object containing a list of payment IDs and their corresponding amounts
    """
    event_id = request.args.get('event_id')
    organizer_id = request.args.get('organizer_id')
    
    if not event_id or not organizer_id:
        return jsonify({
            "success": False,
            "error": "Missing event_id and/or organizer_id parameter"
        }), HTTPStatus.BAD_REQUEST
    
    try:
        # Call the service method to get verifications
        logger.debug(f"fetching verifications for event_id={event_id}, organizer_id={organizer_id}")
        verifications = payment_verification_service.get_verifications_by_event_id_and_organizer_id(event_id, organizer_id)
        
        if not verifications:
            return jsonify({
                "success": False,
                "error": "No payment verifications found for the given event and organizer"
            }), HTTPStatus.NOT_FOUND
        
        # Extract payment IDs and amounts from the verifications
        payment_details = [
            {
                "payment_id": v['payment_id'],
                "amount": v['amount'],  # Amount in cents
                "currency": v['currency']  # Optional: Include currency for clarity
            }
            for v in verifications
        ]
        
        return jsonify({
            "success": True,
            "event_id": event_id,
            "organizer_id": organizer_id,
            "payment_details": payment_details
        }), HTTPStatus.OK
    
    except Exception as e:
        logger.error(f"Error retrieving payment IDs for event {event_id}: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"An unexpected error occurred: {str(e)}"
        }), HTTPStatus.INTERNAL_SERVER_ERROR