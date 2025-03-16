# routes/webhook.py
from flask import Blueprint, request, jsonify, current_app
import stripe
from config import Config

stripe.api_key = Config.STRIPE_SECRET_KEY

webhook_bp = Blueprint('webhook', __name__)

@webhook_bp.route("/", methods=['POST'])
def handle_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = Config.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.webhooks.construct_event(payload, sig_header, webhook_secret)
    except Exception as e:
        current_app.logger.error(f"Webhook error: {e}")
        return jsonify({'error': str(e)}), 400

    # Process specific events
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        current_app.logger.info(f"Checkout session completed: {session['id']}, status: {session.get('payment_status')}")
        # TODO: Add business logic (e.g., update order status in DB)
    
    return jsonify({'message': 'Received'}), 200