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

@webhook_bp.route("/", methods=['POST'])
def handle_webhook():
    """
    Handle Stripe webhook events
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
            'payment_intent.succeeded': handle_payment_succeeded,
            'payment_intent.payment_failed': handle_payment_failed,
            'charge.refunded': handle_refund_succeeded,
            'checkout.session.completed': handle_checkout_completed,
            'invoice.paid': handle_invoice_paid,
            'invoice.payment_failed': handle_invoice_payment_failed
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

def handle_payment_succeeded(event):
    """Handle successful payment"""
    payment_intent = event['data']['object']
    logger.info(f"Payment succeeded: {payment_intent['id']}")
    
    # Notify event service about successful payment
    try:
        requests.post(
            f"{Config.EVENT_SERVICE_URL}/api/events/payment-confirmation",
            json={
                "payment_id": payment_intent['id'],
                "amount": payment_intent['amount'],
                "status": "succeeded",
                "metadata": payment_intent.get('metadata', {})
            }
        )
    except Exception as e:
        logger.error(f"Failed to notify event service: {str(e)}")
    
    return jsonify({"success": True}), 200

def handle_payment_failed(event):
    """Handle failed payment"""
    payment_intent = event['data']['object']
    logger.info(f"Payment failed: {payment_intent['id']}")
    
    # Notify event service about failed payment
    try:
        requests.post(
            f"{Config.EVENT_SERVICE_URL}/api/events/payment-failed",
            json={
                "payment_id": payment_intent['id'],
                "error": payment_intent.get('last_payment_error', {}).get('message', 'Unknown error'),
                "metadata": payment_intent.get('metadata', {})
            }
        )
    except Exception as e:
        logger.error(f"Failed to notify event service: {str(e)}")
    
    return jsonify({"success": True}), 200

def handle_refund_succeeded(event):
    """Handle successful refund"""
    charge = event['data']['object']
    logger.info(f"Refund succeeded for charge: {charge['id']}")
    
    return jsonify({"success": True}), 200

def handle_checkout_completed(event):
    """Handle completed checkout session"""
    session = event['data']['object']
    logger.info(f"Checkout completed: {session['id']}")
    
    return jsonify({"success": True}), 200

def handle_invoice_paid(event):
    """Handle paid invoice"""
    invoice = event['data']['object']
    logger.info(f"Invoice paid: {invoice['id']}")
    
    return jsonify({"success": True}), 200

def handle_invoice_payment_failed(event):
    """Handle failed invoice payment"""
    invoice = event['data']['object']
    logger.info(f"Invoice payment failed: {invoice['id']}")
    
    return jsonify({"success": True}), 200