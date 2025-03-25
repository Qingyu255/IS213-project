# Billing Service

A Flask-based service that handles payment processing, verification, and refunds using Stripe.

## Features

- Payment processing and verification
- Webhook handling for Stripe events
- Refund processing and verification
- Payment verification records storage (both database and file-based)
- Event payment verification
- Comprehensive logging and error handling

## API Endpoints

### Event Payment Endpoints

#### GET /api/events/verify-payment
Verify payment status for an event.

**Query Parameters:**
- `event_id` (required): ID of the event to verify payment for
- `organizer_id` (required): ID of the organizer for additional verification

**Response:**
```json
{
    "success": true,
    "event_id": "event_id",
    "is_paid": true,
    "total_paid": 2000,  // in cents
    "currency": "sgd",
    "verification_count": 1,
    "successful_payment_count": 1,
    "latest_payment": {
        // payment details
    }
}
```

**Error Response:**
```json
{
    "success": false,
    "error": "Missing event_id and/or organizer_id parameter"
}
```

### Payment Verification

#### GET /api/events/verify-payment
Verify payment status for an event.

**Query Parameters:**
- `event_id` (required): ID of the event to verify payment for
- `organizer_id` (required): ID of the organizer for additional verification

**Response:**
```json
{
    "success": true,
    "event_id": "event_id",
    "is_paid": true,
    "total_paid": 2000,  // in cents
    "currency": "sgd",
    "verification_count": 1,
    "successful_payment_count": 1,
    "latest_payment": {
        // payment details
    }
}
```

### Webhook Endpoints

#### POST /api/webhook/
Handle Stripe webhook events.

**Headers:**
- `Stripe-Signature`: Signature provided by Stripe
- `X-Development-Testing`: Set to "true" to bypass signature verification (development only)

**Supported Events:**
- Payment Intent events:
  - `payment_intent.succeeded`
  - `payment_intent.payment_failed`
  - `payment_intent.created`
  - `payment_intent.canceled`
- Charge events:
  - `charge.succeeded`
  - `charge.failed`
  - `charge.refunded`
  - `charge.dispute.created`
- Checkout events:
  - `checkout.session.completed`
  - `checkout.session.expired`

#### GET /api/webhook/payment-verifications
View all payment verification records (UI endpoint).

**Query Parameters:**
- `payment_id`: Filter by payment ID
- `event_id`: Filter by event ID

#### GET /api/webhook/payment-verifications/api
API endpoint to get payment verifications.

**Query Parameters:**
- `payment_id`: Filter by payment ID
- `event_id`: Filter by event ID
- `user_id`: Filter by user ID
- `organizer_id`: Filter by organizer ID
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 50)

#### GET /api/webhook/view-verification
View a specific verification file.

**Query Parameters:**
- `file`: Verification file name

#### GET /api/webhook/debug
Get debug information about webhook configuration.

### Refund Endpoints

#### POST /api/refund/process
Process a refund.

**Request Body:**
```json
{
    "payment_intent_id": "pi_...",
    "amount": 1000,  // Optional: Amount in cents
    "reason": "requested_by_customer",  // Optional
    "metadata": {  // Optional
        "refund_reason": "Customer request",
        "requested_by": "Support agent"
    }
}
```

#### GET /api/refund/{refund_id}
Get refund details by ID.

#### POST /api/refund/verify
Verify the status of a refund.

**Request Body:**
```json
{
    "refund_id": "re_..."
}
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Run the service:
```bash
python app.py
```

## Testing

### Running Stripe CLI for Local Testing

Option 1: Using Docker (recommended)
```bash
docker-compose up stripe-cli
```

Option 2: Running directly on host
```bash
stripe listen --forward-to localhost:5001/api/webhook/
```

Note: Ensure the billing service is running on port 5001.

## Development

The service uses:
- Flask for the web framework
- SQLAlchemy for database operations
- Stripe for payment processing
- Pydantic for data validation

## Error Handling

The service implements comprehensive error handling:
- Input validation using Pydantic models
- Proper HTTP status codes
- Detailed error messages
- Logging of all operations
- Fallback mechanisms for database operations

## Security

- Stripe webhook signature verification
- Environment variable configuration for secrets
- Input validation and sanitization
- Secure error handling
