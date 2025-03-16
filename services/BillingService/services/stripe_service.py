import stripe
from services.billingService.config import Config

stripe.api_key = Config.STRIPE_SECRET_KEY

def create_stripe_payment(data):
    """
    Creates a payment (charge) using Stripe.
    Expected data keys: amount, currency, source, description
    """
    charge = stripe.Charge.create(
        amount=data["amount"],
        currency=data["currency"],
        source=data["source"],
        description=data.get("description", "Payment from billing service")
    )
    return charge



def create_stripe_invoice(data):
    """
    Creates an invoice using Stripe.
    Expected data keys: customer_email, amount, currency
    """
    # Create or retrieve a customer based on email
    customer = stripe.Customer.create(
        email=data["customer_email"]
    )
    # Create an invoice item
    stripe.InvoiceItem.create(
        customer=customer.id,
        amount=data["amount"],
        currency=data["currency"],
        description="Invoice from billing service"
    )
    # Create the invoice
    invoice = stripe.Invoice.create(
        customer=customer.id,
        auto_advance=True  # Automatically finalizes the invoice
    )
    return invoice

def refund_stripe_payment(data):
    """
    Refunds a payment using Stripe.
    Expected data key: charge_id
    """
    refund = stripe.Refund.create(
        charge=data["charge_id"]
    )
    return refund