# Billing Service

This microservice handles payment processing for the event management system using Stripe as the payment gateway.

## Features

- Process payments for event tickets
- Handle refunds for canceled events or ticket returns
- Process Stripe webhooks for payment status updates
- Separate test and production routes for development and production use

## API Endpoints

### Production Endpoints

#### Payment Endpoints

- `POST /api/payment/process` - Process a real payment using Payment Intents
- `POST /api/payment/confirm` - Confirm a payment that requires additional authentication
- `POST /api/payment/invoice` - Create an invoice for a customer
- `GET /api/payment/:id` - Get payment details
- `POST /api/payment/verify` - Verify payment status

#### Refund Endpoints

- `POST /api/refund/create` - Process a refund for a charge
- `POST /api/refund/payment_intent` - Process a refund for a payment intent
- `GET /api/refund/:id` - Get refund details

#### Webhook Endpoints

- `POST /api/webhook` - Handle Stripe webhook events with signature verification

### Test Endpoints

These endpoints are for development and testing purposes only:

#### Test Payment Endpoints

- `POST /api/test/payment/create` - Create a test payment using Stripe test tokens
- `GET /api/test/payment/:id` - Get test payment details
- `POST /api/test/payment/verify` - Verify test payment status

#### Test Refund Endpoints

- `POST /api/test/refund/create` - Process a test refund
- `GET /api/test/refund/:id` - Get test refund details

#### Test Webhook Endpoints

- `POST /api/test/webhook` - Process test webhook events without signature verification
- `POST /api/test/webhook/simulate` - Simulate webhook events for testing

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

## Testing with Postman

### Testing Test Routes

1. **Create a Test Payment**:

   - **Method**: POST
   - **URL**: http://localhost:5001/api/test/payment/create
   - **Headers**: Content-Type: application/json
   - **Body**:
     ```json
     {
       "amount": 1000,
       "currency": "usd",
       "source": "tok_visa",
       "description": "Test payment"
     }
     ```

2. **Verify a Test Payment**:

   - **Method**: POST
   - **URL**: http://localhost:5001/api/test/payment/verify
   - **Headers**: Content-Type: application/json
   - **Body**:
     ```json
     {
       "payment_id": "ch_xxxxxxxxxxxxxxxx"
     }
     ```

3. **Process a Test Refund**:

   - **Method**: POST
   - **URL**: http://localhost:5001/api/test/refund/create
   - **Headers**: Content-Type: application/json
   - **Body**:
     ```json
     {
       "charge_id": "ch_xxxxxxxxxxxxxxxx",
       "reason": "requested_by_customer"
     }
     ```

4. **Simulate a Test Webhook Event**:
   - **Method**: POST
   - **URL**: http://localhost:5001/api/test/webhook/simulate
   - **Headers**: Content-Type: application/json
   - **Body**:
     ```json
     {
       "event_type": "payment_intent.succeeded",
       "object_id": "pi_test123",
       "amount": 1000,
       "currency": "usd"
     }
     ```

### Testing Production Routes

For testing production routes, you'll need to:

1. Set up a Stripe account and get API keys
2. Create payment methods using Stripe.js in your frontend
3. Use the payment method IDs in your API requests

See the [Stripe documentation](https://stripe.com/docs/payments/accept-a-payment) for more details.

## Unit Tests

Run tests with pytest:

```
pytest
```
