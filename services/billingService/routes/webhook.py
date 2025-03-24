# routes/webhook.py
from flask import Blueprint, request, jsonify, render_template_string, abort
import stripe
import logging
import json
import requests
from config import Config
import os
import datetime
from services.payment_verification_service import PaymentVerificationService

logger = logging.getLogger(__name__)

stripe.api_key = Config.STRIPE_SECRET_KEY

payment_verification_service = PaymentVerificationService()

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
      - X-Development-Testing: Set to "true" to bypass signature verification (development only)
    
    Body:
      - Raw payload from Stripe
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
    
    # Extract detailed payment information for verification
    amount = payment_intent.get('amount')
    currency = payment_intent.get('currency')
    receipt_email = payment_intent.get('receipt_email')
    description = payment_intent.get('description')
    payment_method = payment_intent.get('payment_method')
    metadata = payment_intent.get('metadata', {})
    event_id = metadata.get('event_id')
    user_id = metadata.get('user_id')
    organizer_id = metadata.get('organizer_id')  # Extract organizer_id from metadata
    
    # Extract charge information (contains receipt details)
    charge_data = {}
    charges = payment_intent.get('charges', {}).get('data', [])
    if charges:
        latest_charge = charges[0]
        charge_data = {
            "charge_id": latest_charge.get('id'),
            "receipt_url": latest_charge.get('receipt_url'),
            "receipt_number": latest_charge.get('receipt_number'),
            "payment_method_details": latest_charge.get('payment_method_details')
        }
    
    # Format payment details for storage
    payment_verification_data = {
        "event_type": "payment_intent.succeeded",
        "timestamp": event.get('created'),
        "payment_intent_id": payment_intent['id'],
        "payment_details": {
            "amount": amount,
            "currency": currency,
            "receipt_email": receipt_email,
            "description": description,
            "payment_method": payment_method
        },
        "charge_details": charge_data,
        "metadata": metadata,
        "event_id": event_id,
        "user_id": user_id,
        "organizer_id": organizer_id,  # Include organizer_id in verification data
        "payment_status": "succeeded"
    }
    
    # Log the verification data
    logger.info(f"Payment verification data: {json.dumps(payment_verification_data)}")
    
    # Save verification data using the service
    try:
        verification_result = payment_verification_service.save_verification(payment_verification_data)
        logger.info(f"Payment verification saved: {verification_result}")
    except Exception as e:
        logger.error(f"Failed to save payment verification: {str(e)}")
    
    
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
    organizer_id = metadata.get('organizer_id')  # Extract organizer_id from metadata
    
    # Format payment details for storage
    payment_verification_data = {
        "event_type": "payment_intent.payment_failed",
        "timestamp": event.get('created'),
        "payment_intent_id": payment_intent['id'],
        "payment_details": {
            "amount": payment_intent.get('amount'),
            "currency": payment_intent.get('currency'),
            "error": error_message
        },
        "metadata": metadata,
        "event_id": event_id,
        "user_id": user_id,
        "organizer_id": organizer_id,  # Include organizer_id in verification data
        "payment_status": "failed",
        "error_message": error_message
    }
    
    # Save verification data using the service
    try:
        verification_result = payment_verification_service.save_verification(payment_verification_data)
        logger.info(f"Payment failure verification saved: {verification_result}")
    except Exception as e:
        logger.error(f"Failed to save payment failure verification: {str(e)}")
    
    # Notify event service about failed payment
    try:
        requests.post(
            f"{Config.EVENT_SERVICE_URL}/api/events/payment-failed",
            json={
                "payment_id": payment_intent['id'],
                "error": error_message,
                "metadata": metadata,
                "event_id": event_id,
                "user_id": user_id,
                "organizer_id": organizer_id  # Include organizer_id in the notification
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
    
    # Extract detailed session information for verification
    payment_status = session.get('payment_status')
    payment_intent_id = session.get('payment_intent')
    customer_email = session.get('customer_details', {}).get('email')
    customer_name = session.get('customer_details', {}).get('name')
    amount_total = session.get('amount_total')
    currency = session.get('currency', 'usd')
    metadata = session.get('metadata', {})
    event_id = metadata.get('event_id')
    user_id = metadata.get('user_id')
    organizer_id = metadata.get('organizer_id')  # Extract organizer_id from metadata
    
    # Format payment details for storage
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
        "event_id": event_id,
        "user_id": user_id,
        "organizer_id": organizer_id  # Include organizer_id in verification data
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
                "event_id": event_id,
                "user_id": user_id,
                "organizer_id": organizer_id  # Include organizer_id in the notification
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

# VERIFICATION RECORDS VIEW

@webhook_bp.route("/payment-verifications", methods=['GET'])
def view_payment_verifications():
    """
    View all payment verification records
    This endpoint provides a UI to browse all payment verifications for audit purposes
    """
    try:
        verification_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'payment_verifications')
        os.makedirs(verification_dir, exist_ok=True)
        
        # Filter by payment ID if provided
        payment_id_filter = request.args.get('payment_id', '')
        event_id_filter = request.args.get('event_id', '')
        
        # Get all verification files
        verification_files = [f for f in os.listdir(verification_dir) 
                             if f.startswith('payment_verification_')
                             and (not payment_id_filter or payment_id_filter in f)
                             and '.json' in f]
        
        verification_files = sorted(verification_files, 
                                   key=lambda x: os.path.getctime(os.path.join(verification_dir, x)),
                                   reverse=True)
        
        verifications = []
        for file in verification_files:
            try:
                file_path = os.path.join(verification_dir, file)
                with open(file_path, 'r') as f:
                    verification_data = json.load(f)
                
                # Apply event_id filter if provided
                if event_id_filter and verification_data.get('event_id') != event_id_filter:
                    continue
                    
                # Extract key information for the list view
                verifications.append({
                    'filename': file,
                    'timestamp': datetime.datetime.fromtimestamp(verification_data.get('timestamp', 0)).strftime('%Y-%m-%d %H:%M:%S') if verification_data.get('timestamp') else 'Unknown',
                    'event_type': verification_data.get('event_type', 'Unknown'),
                    'payment_id': verification_data.get('payment_intent_id') or verification_data.get('session_id', 'Unknown'),
                    'amount': verification_data.get('payment_details', {}).get('amount') or verification_data.get('payment_details', {}).get('amount_total', 'Unknown'),
                    'currency': verification_data.get('payment_details', {}).get('currency', 'usd'),
                    'event_id': verification_data.get('event_id', 'N/A'),
                    'user_id': verification_data.get('user_id', 'N/A'),
                    'full_data': verification_data
                })
            except Exception as e:
                logger.error(f"Error reading verification file {file}: {str(e)}")
        
        # HTML Template for the verifications UI
        VERIFICATIONS_TEMPLATE = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Payment Verification Records</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }
                h1 {
                    border-bottom: 1px solid #eee;
                    padding-bottom: 10px;
                    margin-bottom: 20px;
                    color: #333;
                }
                .filters {
                    margin-bottom: 20px;
                    padding: 15px;
                    background-color: #f5f5f5;
                    border-radius: 4px;
                }
                .filters form {
                    display: flex;
                    gap: 10px;
                    align-items: flex-end;
                }
                .filters .form-group {
                    display: flex;
                    flex-direction: column;
                }
                .filters label {
                    font-size: 14px;
                    font-weight: 500;
                    margin-bottom: 5px;
                }
                .filters input {
                    padding: 8px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                }
                .verification-list {
                    list-style: none;
                    padding: 0;
                }
                .verification-item {
                    margin: 15px 0;
                    padding: 15px;
                    background-color: #f9f9f9;
                    border-radius: 4px;
                    border-left: 4px solid #6772e5;
                }
                .verification-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 10px;
                }
                .verification-item h3 {
                    margin: 0;
                    font-size: 16px;
                }
                .verification-meta {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 10px;
                    font-size: 14px;
                    color: #666;
                    margin-bottom: 10px;
                }
                .meta-item {
                    display: flex;
                    flex-direction: column;
                }
                .meta-label {
                    font-weight: 500;
                    color: #333;
                }
                .amount {
                    font-weight: 500;
                    color: #5469d4;
                }
                .actions {
                    margin-top: 15px;
                    display: flex;
                    gap: 8px;
                }
                .button, button {
                    display: inline-block;
                    padding: 8px 12px;
                    font-size: 14px;
                    font-weight: 500;
                    line-height: 1.5;
                    text-align: center;
                    white-space: nowrap;
                    vertical-align: middle;
                    cursor: pointer;
                    user-select: none;
                    background-color: #6772e5;
                    border: 1px solid transparent;
                    border-radius: 4px;
                    color: white;
                    text-decoration: none;
                }
                .button:hover, button:hover {
                    background-color: #5469d4;
                }
                .button-secondary {
                    background-color: #f7fafc;
                    border-color: #e2e8f0;
                    color: #4a5568;
                }
                .button-secondary:hover {
                    background-color: #edf2f7;
                }
                .json-view {
                    display: none;
                    background: #f0f0f0;
                    padding: 15px;
                    border-radius: 4px;
                    overflow: auto;
                    max-height: 400px;
                    margin-top: 15px;
                }
                pre {
                    margin: 0;
                    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', 'source-code-pro', monospace;
                    font-size: 13px;
                }
                .empty-state {
                    padding: 40px;
                    text-align: center;
                    background-color: #f9f9f9;
                    border-radius: 4px;
                    color: #666;
                }
            </style>
            <script>
                function toggleJson(id) {
                    const el = document.getElementById(id);
                    el.style.display = el.style.display === 'block' ? 'none' : 'block';
                }
                
                function formatCurrency(amount, currency) {
                    // Basic currency formatting
                    if (typeof amount !== 'number') return amount;
                    
                    // Convert cents to dollars for most currencies
                    const value = amount / 100;
                    
                    // Format based on currency
                    const formatter = new Intl.NumberFormat('en-US', {
                        style: 'currency',
                        currency: currency || 'USD'
                    });
                    
                    return formatter.format(value);
                }
                
                window.onload = function() {
                    // Format all currency amounts on page load
                    document.querySelectorAll('.amount-value').forEach(el => {
                        const amount = parseInt(el.dataset.amount);
                        const currency = el.dataset.currency;
                        if (!isNaN(amount)) {
                            el.textContent = formatCurrency(amount, currency);
                        }
                    });
                }
            </script>
        </head>
        <body>
            <h1>Payment Verification Records</h1>
            
            <div class="filters">
                <form action="" method="get">
                    <div class="form-group">
                        <label for="payment_id">Payment ID</label>
                        <input type="text" id="payment_id" name="payment_id" value="{{ payment_id_filter }}" placeholder="Filter by payment ID">
                    </div>
                    <div class="form-group">
                        <label for="event_id">Event ID</label>
                        <input type="text" id="event_id" name="event_id" value="{{ event_id_filter }}" placeholder="Filter by event ID">
                    </div>
                    <button type="submit" class="button">Filter</button>
                    <a href="{{ request.path }}" class="button button-secondary">Clear</a>
                </form>
            </div>
            
            {% if verifications %}
                <ul class="verification-list">
                    {% for v in verifications %}
                        <li class="verification-item">
                            <div class="verification-header">
                                <h3>{{ v.event_type }}</h3>
                                <span class="amount amount-value" data-amount="{{ v.amount }}" data-currency="{{ v.currency }}">{{ v.amount }}</span>
                            </div>
                            
                            <div class="verification-meta">
                                <div class="meta-item">
                                    <span class="meta-label">Timestamp</span>
                                    <span>{{ v.timestamp }}</span>
                                </div>
                                <div class="meta-item">
                                    <span class="meta-label">Payment ID</span>
                                    <span>{{ v.payment_id }}</span>
                                </div>
                                <div class="meta-item">
                                    <span class="meta-label">Event ID</span>
                                    <span>{{ v.event_id }}</span>
                                </div>
                                <div class="meta-item">
                                    <span class="meta-label">User ID</span>
                                    <span>{{ v.user_id }}</span>
                                </div>
                            </div>
                            
                            <div class="actions">
                                <button onclick="toggleJson('json-{{ loop.index }}')" class="button">View Details</button>
                                <a href="{{ view_url }}?file={{ v.filename }}" target="_blank" class="button button-secondary">View Raw JSON</a>
                            </div>
                            
                            <div id="json-{{ loop.index }}" class="json-view">
                                <pre>{{ v.full_data|tojson(indent=2) }}</pre>
                            </div>
                        </li>
                    {% endfor %}
                </ul>
            {% else %}
                <div class="empty-state">
                    <h3>No verification records found</h3>
                    <p>No payment verification records match your filter criteria.</p>
                </div>
            {% endif %}
        </body>
        </html>
        """
        
        return render_template_string(
            VERIFICATIONS_TEMPLATE, 
            verifications=verifications,
            payment_id_filter=payment_id_filter,
            event_id_filter=event_id_filter,
            request=request,
            view_url=request.url_root + "api/webhook/view-verification"
        )
    except Exception as e:
        logger.error(f"Error viewing payment verifications: {str(e)}")
        return jsonify({"error": "Error viewing payment verifications"}), 500

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

# VERIFICATION RECORDS API ENDPOINTS

@webhook_bp.route("/payment-verifications/api", methods=['GET'])
def api_payment_verifications():
    """API endpoint to get payment verifications"""
    try:
        # Get query parameters
        payment_id = request.args.get('payment_id')
        event_id = request.args.get('event_id')
        user_id = request.args.get('user_id')
        organizer_id = request.args.get('organizer_id')  # New parameter for organizer filtering
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 50))
        
        # Fetch verifications based on filters
        if payment_id:
            verifications = payment_verification_service.get_verifications_by_payment_id(payment_id)
            result = {"verifications": verifications}
        elif event_id:
            verifications = payment_verification_service.get_verifications_by_event_id(event_id)
            result = {"verifications": verifications}
        elif user_id:
            verifications = payment_verification_service.get_verifications_by_user_id(user_id)
            result = {"verifications": verifications}
        else:
            # Get all verifications with pagination
            result = payment_verification_service.get_all_verifications(page, page_size)
        
        # Additional filtering for organizer_id if specified
        if organizer_id and "verifications" in result:
            result["verifications"] = [
                v for v in result["verifications"] 
                if (v.get("verification_data", {}).get("organizer_id") == organizer_id or
                   v.get("verification_data", {}).get("metadata", {}).get("organizer_id") == organizer_id)
            ]
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error retrieving payment verifications: {str(e)}")
        return jsonify({"error": f"Error retrieving payment verifications: {str(e)}"}), 500

# Add a debug info endpoint for webhooks
@webhook_bp.route("/debug", methods=['GET'])
def webhook_debug_info():
    """
    Get debug information about the webhook configuration
    This is helpful for debugging webhook setup issues
    """
    try:
        # Only show the first few and last few characters of secrets
        webhook_secret = Config.STRIPE_WEBHOOK_SECRET
        masked_webhook_secret = None
        if webhook_secret:
            if len(webhook_secret) > 8:
                masked_webhook_secret = webhook_secret[:4] + "..." + webhook_secret[-4:]
            else:
                masked_webhook_secret = "***"
                
        # Get verification directories
        verification_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'payment_verifications')
        verification_files = []
        if os.path.exists(verification_dir):
            verification_files = [f for f in os.listdir(verification_dir) if f.startswith('payment_verification_')]
            verification_files = sorted(verification_files, 
                                      key=lambda x: os.path.getctime(os.path.join(verification_dir, x)),
                                      reverse=True)[:5]  # Get 5 most recent
            
        # Get service URLs we're connecting to
        event_service_url = Config.EVENT_SERVICE_URL
        
        # Get DB status
        db_status = "Unknown"
        try:
            # Try to get one verification to test database access
            verifications = payment_verification_service._repository.find_all(limit=1)
            db_status = "Connected" if verifications is not None else "No records found"
        except Exception as e:
            db_status = f"Error: {str(e)}"
            
        debug_info = {
            "webhook": {
                "url": request.url_root + "api/webhook",
                "secret_configured": webhook_secret is not None and len(webhook_secret) > 0,
                "secret_masked": masked_webhook_secret,
                "verifications_directory": verification_dir,
                "recent_verification_files": verification_files
            },
            "connections": {
                "event_service_url": event_service_url,
                "database_status": db_status
            },
            "environment": {
                "flask_env": os.getenv('FLASK_ENV', 'production'),
                "stripe_api_configured": stripe.api_key is not None and len(stripe.api_key) > 0
            },
            "handlers": {
                "supported_events": [
                    "payment_intent.succeeded",
                    "payment_intent.payment_failed",
                    "payment_intent.created",
                    "payment_intent.canceled",
                    "charge.succeeded",
                    "charge.failed",
                    "charge.refunded",
                    "charge.dispute.created",
                    "checkout.session.completed",
                    "checkout.session.expired"
                ]
            }
        }
        
        return jsonify(debug_info)
    except Exception as e:
        logger.error(f"Error getting webhook debug info: {str(e)}")
        return jsonify({"error": "Error getting webhook debug info"}), 500