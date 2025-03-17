# routes/webhook.py
from flask import Blueprint, request, jsonify
import stripe
import logging
import json
import requests
from config import Config

# Configure logging
logger = logging.getLogger(__name__)

# Configure Stripe
stripe.api_key = Config.STRIPE_SECRET_KEY

webhook_bp = Blueprint('webhook', __name__)

# PRODUCTION ENDPOINTS

@webhook_bp.route("/", methods=['POST'])
def handle_webhook():
    """
    [PRODUCTION] Handle Stripe webhook events with signature verification
    ---
    This endpoint processes webhook events from Stripe with proper signature verification.
    It handles various event types including payment intents, charges, refunds, and more.
    
    Headers:
      - Stripe-Signature: Signature provided by Stripe to verify the webhook
    
    Body:
      - Raw payload from Stripe
    """
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = Config.STRIPE_WEBHOOK_SECRET

    if not webhook_secret:
        logger.error("Webhook secret is not configured")
        return jsonify({"error": "Webhook secret is not configured"}), 500

    if not sig_header:
        logger.error("No Stripe-Signature header found")
        return jsonify({"error": "No Stripe-Signature header found"}), 400

    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
        logger.info(f"Webhook received: {event['type']}")
        
        # Process specific events
        event_handlers = {
            # Payment Intent events
            'payment_intent.succeeded': handle_payment_succeeded,
            'payment_intent.payment_failed': handle_payment_failed,
            'payment_intent.created': handle_payment_intent_created,
            'payment_intent.canceled': handle_payment_intent_canceled,
            
            # Charge events
            'charge.succeeded': handle_charge_succeeded,
            'charge.failed': handle_charge_failed,
            'charge.refunded': handle_refund_succeeded,
            'charge.dispute.created': handle_dispute_created,
            
            # Checkout events
            'checkout.session.completed': handle_checkout_completed,
            'checkout.session.expired': handle_checkout_expired
        }
        
        # Call the appropriate handler if it exists
        if event['type'] in event_handlers:
            return event_handlers[event['type']](event)
        else:
            logger.info(f"Unhandled event type: {event['type']}")
            return jsonify({"message": f"Unhandled event type: {event['type']}"}), 200
            
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {str(e)}")
        return jsonify({"error": "Invalid signature"}), 400
    except json.JSONDecodeError as e:
        logger.error(f"Invalid payload: {str(e)}")
        return jsonify({"error": "Invalid payload"}), 400
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500

# Event handlers for different webhook events

def handle_payment_succeeded(event):
    """Handle successful payment"""
    payment_intent = event['data']['object']
    logger.info(f"Payment succeeded: {payment_intent['id']}")
    
    # Extract metadata for business logic
    metadata = payment_intent.get('metadata', {})
    event_id = metadata.get('event_id')
    user_id = metadata.get('user_id')
    
    # Notify event service about successful payment
    try:
        requests.post(
            f"{Config.EVENT_SERVICE_URL}/api/events/payment-confirmation",
            json={
                "payment_id": payment_intent['id'],
                "amount": payment_intent['amount'],
                "status": "succeeded",
                "metadata": metadata,
                "event_id": event_id,
                "user_id": user_id
            }
        )
    except Exception as e:
        logger.error(f"Failed to notify event service: {str(e)}")
    
    return jsonify({"success": True}), 200

def handle_payment_failed(event):
    """Handle failed payment"""
    payment_intent = event['data']['object']
    logger.info(f"Payment failed: {payment_intent['id']}")
    
    # Extract error information
    error_message = "Unknown error"
    if 'last_payment_error' in payment_intent and payment_intent['last_payment_error']:
        error_message = payment_intent['last_payment_error'].get('message', 'Unknown error')
    
    # Extract metadata for business logic
    metadata = payment_intent.get('metadata', {})
    event_id = metadata.get('event_id')
    user_id = metadata.get('user_id')
    
    # Notify event service about failed payment
    try:
        requests.post(
            f"{Config.EVENT_SERVICE_URL}/api/events/payment-failed",
            json={
                "payment_id": payment_intent['id'],
                "error": error_message,
                "metadata": metadata,
                "event_id": event_id,
                "user_id": user_id
            }
        )
    except Exception as e:
        logger.error(f"Failed to notify event service: {str(e)}")
    
    return jsonify({"success": True}), 200

def handle_payment_intent_created(event):
    """Handle payment intent creation"""
    payment_intent = event['data']['object']
    logger.info(f"Payment intent created: {payment_intent['id']}")
    return jsonify({"success": True}), 200

def handle_payment_intent_canceled(event):
    """Handle payment intent cancellation"""
    payment_intent = event['data']['object']
    logger.info(f"Payment intent canceled: {payment_intent['id']}")
    
    # Notify event service about canceled payment
    try:
        metadata = payment_intent.get('metadata', {})
        requests.post(
            f"{Config.EVENT_SERVICE_URL}/api/events/payment-canceled",
            json={
                "payment_id": payment_intent['id'],
                "metadata": metadata
            }
        )
    except Exception as e:
        logger.error(f"Failed to notify event service: {str(e)}")
    
    return jsonify({"success": True}), 200

def handle_charge_succeeded(event):
    """Handle successful charge"""
    charge = event['data']['object']
    logger.info(f"Charge succeeded: {charge['id']}")
    return jsonify({"success": True}), 200

def handle_charge_failed(event):
    """Handle failed charge"""
    charge = event['data']['object']
    logger.info(f"Charge failed: {charge['id']}")
    return jsonify({"success": True}), 200

def handle_refund_succeeded(event):
    """Handle successful refund"""
    charge = event['data']['object']
    logger.info(f"Refund succeeded for charge: {charge['id']}")
    
    # Notify event service about refund
    try:
        refund_id = None
        refund_amount = 0
        
        # Extract refund information
        if 'refunds' in charge and charge['refunds']['data']:
            latest_refund = charge['refunds']['data'][0]
            refund_id = latest_refund['id']
            refund_amount = latest_refund['amount']
        
        requests.post(
            f"{Config.EVENT_SERVICE_URL}/api/events/refund-processed",
            json={
                "charge_id": charge['id'],
                "refund_id": refund_id,
                "amount": refund_amount,
                "metadata": charge.get('metadata', {})
            }
        )
    except Exception as e:
        logger.error(f"Failed to notify event service: {str(e)}")
    
    return jsonify({"success": True}), 200

def handle_dispute_created(event):
    """Handle dispute creation"""
    dispute = event['data']['object']
    logger.info(f"Dispute created: {dispute['id']} for charge: {dispute['charge']}")
    
    # Notify relevant services about the dispute
    try:
        requests.post(
            f"{Config.EVENT_SERVICE_URL}/api/events/dispute-created",
            json={
                "dispute_id": dispute['id'],
                "charge_id": dispute['charge'],
                "reason": dispute['reason'],
                "status": dispute['status'],
                "amount": dispute['amount']
            }
        )
    except Exception as e:
        logger.error(f"Failed to notify event service: {str(e)}")
    
    return jsonify({"success": True}), 200

def handle_checkout_completed(event):
    """Handle completed checkout session"""
    session = event['data']['object']
    logger.info(f"Checkout completed: {session['id']}")
    
    # Extract payment intent if available
    payment_intent_id = session.get('payment_intent')
    
    # Notify event service
    try:
        requests.post(
            f"{Config.EVENT_SERVICE_URL}/api/events/checkout-completed",
            json={
                "session_id": session['id'],
                "payment_intent_id": payment_intent_id,
                "customer_email": session.get('customer_email'),
                "amount_total": session.get('amount_total'),
                "metadata": session.get('metadata', {})
            }
        )
    except Exception as e:
        logger.error(f"Failed to notify event service: {str(e)}")
    
    return jsonify({"success": True}), 200

def handle_checkout_expired(event):
    """Handle expired checkout session"""
    session = event['data']['object']
    logger.info(f"Checkout expired: {session['id']}")
    return jsonify({"success": True}), 200