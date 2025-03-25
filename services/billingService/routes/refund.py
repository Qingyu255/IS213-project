# routes/refund.py
# TODO: This file needs work for refund composite service
from flask import Blueprint, request, jsonify
import logging
from services.refund_service import RefundService
from services.validation import RefundRequest, validate_stripe_id

logger = logging.getLogger(__name__)

refund_bp = Blueprint('refund', __name__)

@refund_bp.route("/process", methods=['POST']) # TODO: Check if still needed
def process_refund():
    """
    Process a refund using Stripe's Payment Intents API.
    
    Request body:
    {
        "payment_intent_id": "pi_...",  # Required: Stripe Payment Intent ID
        "amount": 1000,  # Optional: Amount in cents for partial refund
        "reason": "requested_by_customer",  # Optional: Reason for refund
        "metadata": {  # Optional: Additional metadata
            "refund_reason": "Customer request",
            "requested_by": "Support agent"
        }
    }
    
    Returns:
        200: {
            "success": true,
            "refund_id": "re_...",
            "payment_intent_id": "pi_...",
            "charge_id": "ch_...",
            "amount": 1000,
            "currency": "usd",
            "status": "succeeded",
            "reason": "requested_by_customer",
            "created": 1234567890,
            "metadata": {},
            "receipt_url": "https://..."  # Optional
        }
        400: {"error": "Error message"}
        500: {"error": "Error message"}
    """
    try:
        # Validate request data
        data = request.get_json()
        if not data:
            logger.warning("Missing request data")
            return jsonify({"error": "Missing request data"}), 400
            
        # Validate using Pydantic model
        try:
            refund_request = RefundRequest(**data)
            validated_data = refund_request.dict()
        except Exception as e:
            logger.warning(f"Validation error: {str(e)}")
            return jsonify({"error": str(e)}), 400
            
        # Process the refund
        result, error = RefundService.process_refund(validated_data)
        if error:
            logger.warning(f"Refund processing failed: {error}")
            return jsonify({"error": error}), 400
            
        logger.info(f"Successfully processed refund: {result['refund_id']}")
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Refund endpoint error: {str(e)}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred while processing the refund"}), 500

@refund_bp.route("/<refund_id>", methods=['GET'])
def get_refund(refund_id):
    """
    Get refund details by ID.
    
    Parameters:
        refund_id: Stripe Refund ID (re_...)
    
    Returns:
        200: {
            "refund_id": "re_...",
            "charge_id": "ch_...",
            "payment_intent_id": "pi_...",
            "amount": 1000,
            "currency": "usd",
            "status": "succeeded",
            "reason": "requested_by_customer",
            "created": 1234567890,
            "metadata": {},
            "receipt_url": "https://..."  # Optional
        }
        400: {"error": "Invalid refund ID format"}
        404: {"error": "Refund not found"}
        500: {"error": "Error message"}
    """
    try:
        # Validate refund_id format
        if not validate_stripe_id(refund_id, 're_'):
            logger.warning(f"Invalid refund ID format: {refund_id}")
            return jsonify({"error": "Invalid refund ID format"}), 400
            
        result, error = RefundService.get_refund(refund_id)
        if error:
            logger.warning(f"Error retrieving refund: {error}")
            return jsonify({"error": error}), 404 if error == "Refund not found" else 500
            
        logger.info(f"Successfully retrieved refund: {refund_id}")
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error retrieving refund: {str(e)}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred while retrieving the refund"}), 500

@refund_bp.route("/verify", methods=['POST'])
def verify_refund():
    """
    Verify the status of a refund.
    
    Request body:
    {
        "refund_id": "re_..."  # Required: Stripe Refund ID
    }
    
    Returns:
        200: {
            "refund_id": "re_...",
            "verified": true,
            "status": "succeeded",
            "is_succeeded": true,
            "amount": 1000,
            "currency": "usd",
            "charge_id": "ch_...",
            "payment_intent_id": "pi_...",
            "reason": "requested_by_customer",
            "created": 1234567890,
            "receipt_url": "https://...",  # Optional
            "charge_status": "succeeded",
            "charge_amount": 1000,
            "charge_refunded": true,
            "charge_dispute": false
        }
        400: {
            "verified": false,
            "error": "Missing refund_id parameter"
        }
        404: {
            "verified": false,
            "error": "Refund not found"
        }
        500: {
            "verified": false,
            "error": "Error message"
        }
    """
    try:
        # Validate request data
        data = request.get_json()
        if not data:
            logger.warning("Missing request data")
            return jsonify({
                "verified": False,
                "error": "Missing request data"
            }), 400
            
        if 'refund_id' not in data:
            logger.warning("Missing refund_id in request")
            return jsonify({
                "verified": False,
                "error": "Missing refund_id parameter"
            }), 400
            
        # Validate refund_id format
        if not validate_stripe_id(data['refund_id'], 're_'):
            logger.warning(f"Invalid refund ID format: {data['refund_id']}")
            return jsonify({
                "verified": False,
                "error": "Invalid refund ID format"
            }), 400
            
        result, error = RefundService.verify_refund(data['refund_id'])
        if error:
            logger.warning(f"Refund verification failed: {error}")
            return jsonify({
                "verified": False,
                "error": error
            }), 404 if error == "Refund not found" else 500
            
        logger.info(f"Successfully verified refund: {data['refund_id']}")
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error verifying refund: {str(e)}", exc_info=True)
        return jsonify({
            "verified": False,
            "error": "An unexpected error occurred while verifying the refund"
        }), 500