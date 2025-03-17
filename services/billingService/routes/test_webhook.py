# routes/test_webhook.py
from flask import Blueprint, request, jsonify
import stripe
import logging
import json
from config import Config

# Configure logging
logger = logging.getLogger(__name__)

# Configure Stripe
stripe.api_key = Config.STRIPE_SECRET_KEY

test_webhook_bp = Blueprint('test_webhook', __name__)

@test_webhook_bp.route("/", methods=['POST'])
def handle_test_webhook():
    """
    Handle test Stripe webhook events without signature verification
    This endpoint is for testing purposes only and should not be used in production
    """
    try:
        # Get the webhook payload
        payload = request.get_data(as_text=True)
        data = json.loads(payload)
        
        # Log the event
        event_type = data.get('type', 'unknown')
        logger.info(f"Test webhook received: {event_type}")
        
        # Process based on event type
        if event_type == 'payment_intent.succeeded':
            return handle_test_payment_succeeded(data)
        elif event_type == 'payment_intent.payment_failed':
            return handle_test_payment_failed(data)
        elif event_type == 'charge.refunded':
            return handle_test_refund_succeeded(data)
        else:
            logger.info(f"Unhandled test event type: {event_type}")
            return jsonify({"message": f"Unhandled test event type: {event_type}"}), 200
            
    except json.JSONDecodeError as e:
        logger.error(f"Invalid payload: {str(e)}")
        return jsonify({"error": "Invalid payload"}), 400
    except Exception as e:
        logger.error(f"Test webhook error: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500

def handle_test_payment_succeeded(data):
    """Handle test successful payment"""
    payment_intent = data.get('data', {}).get('object', {})
    payment_id = payment_intent.get('id', 'unknown')
    logger.info(f"Test payment succeeded: {payment_id}")
    
    return jsonify({
        "success": True,
        "message": f"Test payment succeeded: {payment_id}",
        "event_type": "payment_intent.succeeded"
    }), 200

def handle_test_payment_failed(data):
    """Handle test failed payment"""
    payment_intent = data.get('data', {}).get('object', {})
    payment_id = payment_intent.get('id', 'unknown')
    logger.info(f"Test payment failed: {payment_id}")
    
    return jsonify({
        "success": True,
        "message": f"Test payment failed: {payment_id}",
        "event_type": "payment_intent.payment_failed"
    }), 200

def handle_test_refund_succeeded(data):
    """Handle test successful refund"""
    charge = data.get('data', {}).get('object', {})
    charge_id = charge.get('id', 'unknown')
    logger.info(f"Test refund succeeded for charge: {charge_id}")
    
    return jsonify({
        "success": True,
        "message": f"Test refund succeeded for charge: {charge_id}",
        "event_type": "charge.refunded"
    }), 200

@test_webhook_bp.route("/simulate", methods=['POST'])
def simulate_webhook():
    """
    Simulate a webhook event for testing
    ---
    Expected JSON body:
    {
        "event_type": "payment_intent.succeeded",
        "object_id": "pi_test123",
        "amount": 1000,
        "currency": "usd"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'event_type' not in data or 'object_id' not in data:
            return jsonify({"error": "Missing required parameters"}), 400
            
        event_type = data['event_type']
        object_id = data['object_id']
        amount = data.get('amount', 1000)
        currency = data.get('currency', 'usd')
        
        # Create a simulated event object
        if event_type == 'payment_intent.succeeded':
            event_object = {
                'id': object_id,
                'object': 'payment_intent',
                'amount': amount,
                'currency': currency,
                'status': 'succeeded',
                'metadata': data.get('metadata', {})
            }
        elif event_type == 'payment_intent.payment_failed':
            event_object = {
                'id': object_id,
                'object': 'payment_intent',
                'amount': amount,
                'currency': currency,
                'status': 'failed',
                'last_payment_error': {
                    'message': data.get('error_message', 'Test payment failed')
                },
                'metadata': data.get('metadata', {})
            }
        elif event_type == 'charge.refunded':
            event_object = {
                'id': object_id,
                'object': 'charge',
                'amount': amount,
                'currency': currency,
                'refunded': True,
                'refunds': {
                    'data': [
                        {
                            'id': 're_' + object_id[3:],
                            'amount': amount,
                            'currency': currency,
                            'status': 'succeeded'
                        }
                    ]
                },
                'metadata': data.get('metadata', {})
            }
        else:
            return jsonify({"error": f"Unsupported event type: {event_type}"}), 400
            
        # Create the simulated event
        simulated_event = {
            'id': 'evt_test_' + object_id[3:],
            'type': event_type,
            'data': {
                'object': event_object
            }
        }
        
        # Process the simulated event
        if event_type == 'payment_intent.succeeded':
            return handle_test_payment_succeeded(simulated_event)
        elif event_type == 'payment_intent.payment_failed':
            return handle_test_payment_failed(simulated_event)
        elif event_type == 'charge.refunded':
            return handle_test_refund_succeeded(simulated_event)
        else:
            return jsonify({"error": f"Unsupported event type: {event_type}"}), 400
            
    except Exception as e:
        logger.error(f"Error simulating webhook: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500 