# Billing Service

This microservice handles payment processing for the event management system using Stripe as the payment gateway.

## Features

- Process payments for event tickets
- Handle refunds for canceled events or ticket returns
- Process Stripe webhooks for payment status updates

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
