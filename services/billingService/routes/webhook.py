from flask import Blueprint, request, jsonify, render_template_string, abort
import stripe
import logging
import json
import requests
from config import Config
import os
import datetime
from services.payment_verification_service import PaymentVerificationService
from models.booking_payment import BookingPayment
from models import get_session  

logger = logging.getLogger(__name__)

stripe.api_key = Config.STRIPE_SECRET_KEY

payment_verification_service = PaymentVerificationService()

webhook_bp = Blueprint('webhook', __name__)

@webhook_bp.route("/", methods=['POST'])
def handle_webhook():
    """
    Handle Stripe webhook events with signature verification
    ---
    tags:
      - Webhooks
    description: |
      This endpoint processes webhook events from Stripe with proper signature verification.
      It handles various event types including payment intents, charges, refunds, and more.
    parameters:
      - name: Stripe-Signature
        in: header
        type: string
        required: true
        description: Signature provided by Stripe to verify the webhook
      - name: X-Development-Testing
        in: header
        type: string
        required: false
        description: Set to "true" to bypass signature verification (development only)
    responses:
      200:
        description: Webhook processed successfully
      400:
        description: Invalid signature or payload
      500:
        description: Server error
    """
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = Config.STRIPE_WEBHOOK_SECRET
    
    # Check if development testing mode is enabled
    is_development_testing = request.headers.get('X-Development-Testing') == 'true'
    
    # In development, bypass signature verification for testing
    if is_development_testing:
        logger.warning("DEVELOPMENT MODE: Bypassing Stripe signature verification")
        try:
            event = json.loads(payload)
            logger.info(f"Development webhook received: {event['type']}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON payload: {str(e)}")
            return jsonify({"error": "Invalid payload format"}), 400
    else:
        # Production path with proper signature verification
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
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid signature: {str(e)}")
            return jsonify({"error": "Invalid signature"}), 400
        except json.JSONDecodeError as e:
            logger.error(f"Invalid payload: {str(e)}")
            return jsonify({"error": "Invalid payload"}), 400
        except Exception as e:
            logger.error(f"Webhook error: {str(e)}")
            return jsonify({"error": "An unexpected error occurred"}), 500
    
    # Process specific events - this code runs for both production and development testing
    try:
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
    except Exception as e:
        logger.error(f"Error processing webhook event: {str(e)}", exc_info=True)
        return jsonify({"error": "Error processing webhook event"}), 500



# Event handlers for different webhook events

def handle_payment_succeeded(event):
    """Handle successful payment"""
    payment_intent = event['data']['object']
    logger.info(f"Payment succeeded: {payment_intent['id']}")
    
    # Extract payment info...
    metadata = payment_intent.get('metadata', {})
    
    # Also check the payment intent's invoice/charge for metadata
    if not metadata:
        if payment_intent.get('invoice'):
            metadata = payment_intent['invoice'].get('metadata', {})
        elif payment_intent.get('charges', {}).get('data'):
            metadata = payment_intent['charges']['data'][0].get('metadata', {})
    
    booking_id = metadata.get('booking_id')
    event_id = metadata.get('event_id')
    
    try:
        if booking_id:
            return handle_booking_payment_success(payment_intent, metadata)
        elif event_id:
            return handle_event_payment_success(payment_intent, metadata)
        else:
            # Don't error if we can't find IDs - this might be a different type of payment
            logger.info("No booking_id or event_id found in payment metadata")
            return jsonify({"status": "success"}), 200
            
    except Exception as e:
        logger.error(f"Error processing payment success: {str(e)}")
        return jsonify({"error": str(e)}), 500

def handle_booking_payment_success(payment_intent: dict, metadata: dict):
    """Handle successful booking payment"""
    amount = payment_intent.get('amount')
    currency = payment_intent.get('currency')
    booking_id = metadata.get('booking_id')
    
    # Handle booking payment
    booking_service_url = os.getenv('BOOKING_SERVICE_URL', 'http://booking-service:8002')
    response = requests.post(
        f"{booking_service_url}/api/v1/bookings/{booking_id}/confirm",
        json={
            "payment_intent_id": payment_intent['id'],
            "amount": amount,
            "currency": currency
        }
    )
    
    if response.status_code != 200:
        logger.error(f"Failed to update booking status: {response.text}")
        return jsonify({"error": "Failed to update booking status"}), 500
        
    # Store payment verification...
    store_payment_verification(payment_intent, metadata)
    
    return jsonify({"status": "success"}), 200

def handle_event_payment_success(payment_intent: dict, metadata: dict):
    """Handle successful event payment"""
    amount = payment_intent.get('amount')
    currency = payment_intent.get('currency')
    event_id = metadata.get('event_id')
    
    # Handle event creation payment
    event_service_url = os.getenv('EVENT_SERVICE_URL', 'http://event-service:8001')
    response = requests.post(
        f"{event_service_url}/api/v1/events/{event_id}/confirm",
        json={
            "payment_intent_id": payment_intent['id'],
            "amount": amount,
            "currency": currency
        }
    )
    
    if response.status_code != 200:
        logger.error(f"Failed to update event status: {response.text}")
        return jsonify({"error": "Failed to update event status"}), 500
        
    # Store payment verification...
    store_payment_verification(payment_intent, metadata)
    
    return jsonify({"status": "success"}), 200

def store_payment_verification(payment_intent: dict, metadata: dict):
    """Store payment verification data"""
    payment_verification_data = {
        "event_type": "payment_intent.succeeded",
        "timestamp": datetime.datetime.now().isoformat(),
        "payment_intent_id": payment_intent['id'],
        "booking_id": metadata.get('booking_id'),
        "event_id": metadata.get('event_id'),
        "user_id": metadata.get('user_id'),
        "organizer_id": metadata.get('organizer_id'),
        "payment_details": {
            "amount": payment_intent.get('amount'),
            "currency": payment_intent.get('currency'),
            "receipt_email": payment_intent.get('receipt_email'),
            "description": payment_intent.get('description'),
            "payment_method": payment_intent.get('payment_method')
        }
    }
    
    payment_verification_service.create_verification(payment_verification_data)

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
    booking_id = metadata.get('booking_id')
    event_id = metadata.get('event_id')
    user_id = metadata.get('user_id')
    organizer_id = metadata.get('organizer_id')
    
    try:
        if booking_id:
            # Handle booking payment failure
            booking_service_url = os.getenv('BOOKING_SERVICE_URL', 'http://localhost:8002')
            response = requests.post(
                f"{booking_service_url}/api/v1/bookings/{booking_id}/cancel",
                json={
                    "payment_intent_id": payment_intent['id'],
                    "error": error_message
                }
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to update booking status: {response.text}")
        elif event_id:
            # Handle event creation payment failure
            event_service_url = os.getenv('EVENT_SERVICE_URL', 'http://localhost:8001')
            response = requests.post(
                f"{event_service_url}/api/v1/events/{event_id}/cancel",
                json={
                    "payment_intent_id": payment_intent['id'],
                    "error": error_message
                }
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to update event status: {response.text}")
        
        # Format payment details for storage
        payment_verification_data = {
            "event_type": "payment_intent.payment_failed",
            "timestamp": event.get('created'),
            "payment_intent_id": payment_intent['id'],
            "booking_id": booking_id,
            "event_id": event_id,
            "user_id": user_id,
            "organizer_id": organizer_id,
            "payment_details": {
                "amount": payment_intent.get('amount'),
                "currency": payment_intent.get('currency'),
                "error": error_message
            },
            "payment_status": "failed",
            "error_message": error_message
        }
        
        # Save verification data using the service
        payment_verification_service.create_verification(payment_verification_data)
        
        return jsonify({"success": True}), 200
    except Exception as e:
        logger.error(f"Error processing payment failure: {str(e)}")
        return jsonify({"error": str(e)}), 500

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
    
    # Extract detailed session information
    payment_status = session.get('payment_status')
    payment_intent_id = session.get('payment_intent')
    customer_email = session.get('customer_details', {}).get('email')
    customer_name = session.get('customer_details', {}).get('name')
    amount_total = session.get('amount_total')
    currency = session.get('currency', 'usd')
    metadata = session.get('metadata', {})
    booking_id = metadata.get('booking_id')
    
    # Store in booking_payments if it's a booking payment
    if booking_id and payment_intent_id:
        try:
            with get_session() as db_session:
                booking_payment = BookingPayment(
                    booking_id=booking_id,
                    payment_intent_id=payment_intent_id,
                    amount=amount_total,
                    currency=currency,
                    status='paid',
                    customer_email=customer_email,
                    customer_name=customer_name
                )
                db_session.add(booking_payment)
                db_session.commit()
                logger.info(f"Saved to booking_payments: {booking_payment.to_dict()}")
                
                # # Update booking status
                # try:
                #     booking_service_url = os.getenv('BOOKING_SERVICE_URL', 'http://booking-service:8002')
                #     response = requests.post(
                #         f"{booking_service_url}/api/v1/bookings/{booking_id}/confirm",
                #         params={
                #             "session_id": session['id']  # Required by booking service
                #         },
                #         json={
                #             "payment_intent_id": payment_intent_id,
                #             "amount": amount_total,
                #             "currency": currency
                #         }
                #     )
                    
                #     if response.status_code != 200:
                #         logger.error(f"Failed to update booking status: {response.text}")
                #     else:
                #         logger.info(f"Successfully updated booking status for booking {booking_id}")
                # except Exception as e:
                #     logger.error(f"Error updating booking status: {str(e)}")
                #     # Don't return error - continue with verification storage
        except Exception as e:
            logger.error(f"Failed to save booking payment: {str(e)}")
    
    # Continue with existing payment verification storage...
    payment_verification_data = {
        "event_type": "checkout.session.completed",
        "timestamp": event.get('created'),
        "session_id": session['id'],
        "payment_intent_id": payment_intent_id,
        "payment_status": payment_status,
        "customer": {
            "email": customer_email,
            "name": customer_name
        },
        "payment_details": {
            "amount_total": amount_total,
            "currency": currency
        },
        "metadata": metadata,
        "booking_id": booking_id,
        "event_id": metadata.get('event_id'),
        "user_id": metadata.get('user_id'),
        "organizer_id": metadata.get('organizer_id')
    }
    
    # Log the verification data
    logger.info(f"Payment verification data: {json.dumps(payment_verification_data)}")
    
    # Save verification data using the service
    try:
        verification_result = payment_verification_service.save_verification(payment_verification_data)
        logger.info(f"Checkout verification saved: {verification_result}")
    except Exception as e:
        logger.error(f"Failed to save checkout verification: {str(e)}")
    
    # Notify event service
    try:
        requests.post(
            f"{Config.EVENT_SERVICE_URL}/api/events/checkout-completed",
            json={
                "session_id": session['id'],
                "payment_intent": payment_intent_id,
                "customer_email": customer_email,
                "amount_total": amount_total,
                "metadata": metadata,
                "booking_id": booking_id,
                "event_id": metadata.get('event_id'),
                "user_id": metadata.get('user_id'),
                "organizer_id": metadata.get('organizer_id')
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

@webhook_bp.route("/view-verification", methods=['GET'])
def view_verification_file():
    """View a specific verification file"""
    filename = request.args.get('file', '')
    if not filename or '..' in filename or not filename.startswith('payment_verification_'):
        abort(400)
    
    file_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), 
        'payment_verifications',
        filename
    )
    
    if not os.path.exists(file_path):
        abort(404)
    
    try:
        with open(file_path, 'r') as f:
            content = json.load(f)
            return jsonify(content)
    except Exception as e:
        logger.error(f"Error reading verification file {filename}: {str(e)}")
        return jsonify({"error": "Error reading verification file"}), 500
