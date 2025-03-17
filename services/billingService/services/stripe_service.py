import stripe
import logging
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Stripe API key
stripe.api_key = Config.STRIPE_SECRET_KEY

def create_stripe_payment(data):
    """
    Creates a payment (charge) using Stripe.
    Expected data keys: amount, currency, source, description
    """
    try:
        # Validate required fields
        required_fields = ['amount', 'currency', 'source']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
                
        charge = stripe.Charge.create(
            amount=data["amount"],
            currency=data["currency"],
            source=data["source"],
            description=data.get("description", "Payment from billing service")
        )
        logger.info(f"Created charge: {charge.id}")
        return charge
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error creating payment: {str(e)}")
        raise

def create_stripe_invoice(data):
    """
    Creates an invoice using Stripe.
    Expected data keys: customer_email, amount, currency
    """
    try:
        # Validate required fields
        required_fields = ['customer_email', 'amount', 'currency']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
                
        # Create or retrieve a customer based on email
        customer = stripe.Customer.create(
            email=data["customer_email"]
        )
        # Create an invoice item
        stripe.InvoiceItem.create(
            customer=customer.id,
            amount=data["amount"],
            currency=data["currency"],
            description=data.get("description", "Invoice from billing service")
        )
        # Create the invoice
        invoice = stripe.Invoice.create(
            customer=customer.id,
            auto_advance=True  # Automatically finalizes the invoice
        )
        logger.info(f"Created invoice: {invoice.id}")
        return invoice
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error creating invoice: {str(e)}")
        raise

def refund_stripe_payment(data):
    """
    Refunds a payment using Stripe.
    Expected data key: charge_id
    """
    try:
        # Validate required fields
        if 'charge_id' not in data:
            raise ValueError("Missing required field: charge_id")
            
        refund = stripe.Refund.create(
            charge=data["charge_id"]
        )
        logger.info(f"Created refund: {refund.id}")
        return refund
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error creating refund: {str(e)}")
        raise