import os
from flask import Flask, request, jsonify
import stripe

from api.payments import payments_bp
from api.refunds import refunds_bp
from api.invoices import invoices_bp

app = Flask(__name__)
app.config.from_object(Config)
app.register_blueprint(payments_bp, url_prefix="/payments")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)


# Configure Stripe with the secret key from environment variables
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_your_default_key_here")

# Endpoint to create a payment (charge)
@app.route("/create-payment", methods=["POST"])
def create_payment():
    try:
        data = request.get_json()
        # Expected JSON payload: { "amount": 5000, "currency": "usd", "source": "tok_visa", "description": "Charge for order #1234" }
        charge = stripe.Charge.create(
            amount=data["amount"],      # amount in cents
            currency=data["currency"],
            source=data["source"],
            description=data.get("description", "Charge from billing service")
        )
        return jsonify(charge), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Endpoint to refund a payment
@app.route("/refund-payment", methods=["POST"])
def refund_payment():
    try:
        data = request.get_json()
        # Expected JSON payload: { "charge_id": "ch_1GqIC8..." }
        refund = stripe.Refund.create(
            charge=data["charge_id"]
        )
        return jsonify(refund), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Endpoint to create an invoice (simple example)
@app.route("/create-invoice", methods=["POST"])
def create_invoice():
    try:
        data = request.get_json()
        # Expected JSON payload: { "customer_email": "customer@example.com", "amount": 3000, "currency": "usd" }
        
        # Create a new customer or fetch an existing one
        customer = stripe.Customer.create(
            email=data["customer_email"]
        )
        
        # Create an invoice item
        invoice_item = stripe.InvoiceItem.create(
            customer=customer.id,
            amount=data["amount"],  # amount in cents
            currency=data["currency"],
            description="Invoice item for billing service"
        )
        
        # Create the invoice for the customer
        invoice = stripe.Invoice.create(
            customer=customer.id,
            auto_advance=True  # Auto-finalize this draft after ~1 hour (for demo, you might set to False)
        )
        return jsonify(invoice), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)