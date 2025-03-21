# Billing Service

This microservice handles payment processing for the event management system using Stripe as the payment gateway.

## Features

- Secure payment processing using Stripe Payment Intents API
- Support for 3D Secure authentication
- Comprehensive refund handling with partial refund support
- Production-grade webhook processing with signature verification
- Idempotent payment operations
- Detailed payment status tracking and verification
- Integration with event service for payment notifications

## Testing Guide

### 1. Test Cards & Payment Methods

For security, card information is never sent directly to this service. Instead:

1. **Create a Test Payment Method** using Stripe CLI:

```bash
# Create a Payment Method with test card
stripe payment_methods create \
  -d type=card \
  -d card[number]=4242424242424242 \
  -d card[exp_month]=12 \
  -d card[exp_year]=2024 \
  -d card[cvc]=123

# Save the Payment Method ID (pm_...) for API calls
```

**Available Test Cards:**

```
Successful Payment:
  Number: 4242 4242 4242 4242
  Expiry: Any future date
  CVC: Any 3 digits

3D Secure Required:
  Number: 4000 0000 0000 3220
  Expiry: Any future date
  CVC: Any 3 digits

Payment Fails:
  Number: 4000 0000 0000 9995
  Expiry: Any future date
  CVC: Any 3 digits
```

### 2. Test API Calls

1. **Process a Payment** (using Payment Method ID):

```bash
curl -X POST http://localhost:5001/api/payment/process \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 1000,
    "currency": "sgd",
    "payment_method": "pm_...",  # Use Payment Method ID from step 1
    "description": "Test payment",
    "metadata": {
      "event_id": "test_123"
    }
  }'
```

2. **Verify Payment Status**:

```bash
curl -X POST http://localhost:5001/api/payment/verify \
  -H "Content-Type: application/json" \
  -d '{
    "payment_intent_id": "pi_..."  # Use ID from previous response
  }'
```

3. **Process a Refund**:

```bash
curl -X POST http://localhost:5001/api/refund/process \
  -H "Content-Type: application/json" \
  -d '{
    "payment_intent_id": "pi_...",
    "amount": 1000,
    "reason": "requested_by_customer"
  }'
```

### 3. Testing Webhooks Locally

1. Install Stripe CLI:

```bash
# Windows (using Chocolatey)
choco install stripe-cli

# macOS (using Homebrew)
brew install stripe/stripe-cli/stripe
```

2. Login to Stripe CLI:

```bash
stripe login
```

3. Forward webhooks to your local server:

```bash
stripe listen --forward-to localhost:5001/api/webhook
```

4. In a new terminal, trigger test events:

```bash
# Test successful payment
stripe trigger payment_intent.succeeded

# Test failed payment
stripe trigger payment_intent.payment_failed

# Test refund
stripe trigger charge.refunded
```

## API Endpoints

### Payment Endpoints

- `POST /api/payment/create` - Create a new payment
- `GET /api/payment/:id` - Get payment details

### Refund Endpoints

- `POST /api/refund/create` - Process a refund
- `GET /api/refund/:id` - Get refund details

### Webhook Endpoints

- `POST /api/webhook` - Handle Stripe webhook events

## Setup

1. Clone the repository
2. Create a `.env` file with the following variables:
   ```
   STRIPE_SECRET_KEY=your_stripe_secret_key
   STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret
   SECRET_KEY=your_flask_secret_key
   FLASK_DEBUG=True
   EVENT_SERVICE_URL=http://event-service:5000
   USER_SERVICE_URL=http://user-service:5000
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run the service:
   ```
   python app.py
   ```

## Docker

Build the Docker image:

```
docker build -t billing-service .
```

Run the container:

```
docker run -p 5001:5001 -e STRIPE_SECRET_KEY=your_key billing-service
```

## Testing

Run tests with pytest:

```
pytest
```
