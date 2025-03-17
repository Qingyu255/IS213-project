# routes/refund.py
from flask import Blueprint, request, jsonify
import logging
from services.refund_service import RefundService

# Configure logging
logger = logging.getLogger(__name__)

refund_bp = Blueprint('refund', __name__)

@refund_bp.route("/process", methods=['POST'])
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
            "metadata": {}
        }
        400: {"error": "Error message"}
        500: {"error": "Error message"}
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing request data"}), 400
            
        if 'payment_intent_id' not in data:
            return jsonify({"error": "Missing payment_intent_id parameter"}), 400
            
        result, error = RefundService.process_refund(data)
        if error:
            return jsonify({"error": error}), 400
            
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Refund endpoint error: {str(e)}")
        return jsonify({"error": str(e)}), 500

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
        404: {"error": "Refund not found"}
        500: {"error": "Error message"}
    """
    try:
        result, error = RefundService.get_refund(refund_id)
        if error:
            return jsonify({"error": error}), 404 if error == "Refund not found" else 500
            
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error retrieving refund: {str(e)}")
        return jsonify({"error": str(e)}), 500

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
            "created": 1234567890
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
        data = request.get_json()
        
        if not data or 'refund_id' not in data:
            return jsonify({
                "verified": False,
                "error": "Missing refund_id parameter"
            }), 400
            
        result, error = RefundService.verify_refund(data['refund_id'])
        if error:
            return jsonify({
                "verified": False,
                "error": error
            }), 404 if error == "Refund not found" else 500
            
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error verifying refund: {str(e)}")
        return jsonify({
            "verified": False,
            "error": str(e)
        }), 500