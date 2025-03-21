# Billing Service Postman Tests

## Environment Variables

Create a new environment in Postman with these variables:

- `base_url`: Your billing service URL (e.g., http://localhost:5000)
- `stripe_test_key`: Your Stripe test secret key
- `test_payment_method`: A valid Stripe test payment method ID (e.g., pm_card_visa)

## Payment Endpoints

### 1. Process Payment

**POST** `/payment/process`

```json
{
  "amount": 1000,
  "currency": "sgd",
  "payment_method": "{{test_payment_method}}",
  "description": "Test payment",
  "metadata": {
    "order_id": "test_123",
    "customer_name": "Test User"
  },
  "customer_email": "test@example.com"
}
```

Headers:

```
Content-Type: application/json
Idempotency-Key: {{$guid}}
```

Expected Response (200):

```json
{
  "payment": {
    "payment_intent_id": "pi_...",
    "status": "succeeded",
    "amount": 1000,
    "currency": "sgd",
    "receipt_email": "test@example.com",
    "receipt_url": "https://...",
    "success": true
  }
}
```

### 2. Get Payment Details

**GET** `/payment/{payment_intent_id}`

Replace `{payment_intent_id}` with the ID from the process payment response.

Expected Response (200):

```json
{
  "payment_intent_id": "pi_...",
  "amount": 1000,
  "currency": "sgd",
  "status": "succeeded",
  "created": 1234567890,
  "metadata": {
    "order_id": "test_123",
    "customer_name": "Test User"
  },
  "payment_method": "pm_...",
  "charge_id": "ch_...",
  "receipt_url": "https://...",
  "payment_method_details": {
    "type": "card",
    "card": {
      "brand": "visa",
      "last4": "4242"
    }
  }
}
```

### 3. Verify Payment

**POST** `/payment/verify`

```json
{
  "payment_intent_id": "pi_..."
}
```

Expected Response (200):

```json
{
  "payment_intent_id": "pi_...",
  "verified": true,
  "status": "succeeded",
  "is_paid": true,
  "amount": 1000,
  "currency": "sgd",
  "created": 1234567890,
  "livemode": false,
  "charge_id": "ch_...",
  "payment_method": "card",
  "risk_level": "normal",
  "risk_score": 0
}
```

## Refund Endpoints

### 1. Process Refund

**POST** `/refund/process`

```json
{
  "payment_intent_id": "pi_...",
  "amount": 1000,
  "reason": "requested_by_customer",
  "metadata": {
    "refund_reason": "Customer request",
    "requested_by": "Support agent"
  }
}
```

Expected Response (200):

```json
{
  "success": true,
  "refund_id": "re_...",
  "payment_intent_id": "pi_...",
  "charge_id": "ch_...",
  "amount": 1000,
  "currency": "sgd",
  "status": "succeeded",
  "reason": "requested_by_customer",
  "created": 1234567890,
  "metadata": {
    "refund_reason": "Customer request",
    "requested_by": "Support agent"
  }
}
```

### 2. Get Refund Details

**GET** `/refund/{refund_id}`

Replace `{refund_id}` with the ID from the process refund response.

Expected Response (200):

```json
{
  "refund_id": "re_...",
  "charge_id": "ch_...",
  "payment_intent_id": "pi_...",
  "amount": 1000,
  "currency": "sgd",
  "status": "succeeded",
  "reason": "requested_by_customer",
  "created": 1234567890,
  "metadata": {
    "refund_reason": "Customer request",
    "requested_by": "Support agent"
  },
  "receipt_url": "https://..."
}
```

### 3. Verify Refund

**POST** `/refund/verify`

```json
{
  "refund_id": "re_..."
}
```

Expected Response (200):

```json
{
  "refund_id": "re_...",
  "verified": true,
  "status": "succeeded",
  "is_succeeded": true,
  "amount": 1000,
  "currency": "sgd",
  "charge_id": "ch_...",
  "payment_intent_id": "pi_...",
  "reason": "requested_by_customer",
  "created": 1234567890
}
```

## Error Cases to Test

### Payment Endpoints

1. Invalid currency (not SGD)
2. Amount below minimum (50 cents)
3. Invalid payment method
4. Missing required fields
5. Invalid payment intent ID format
6. Non-existent payment intent ID

### Refund Endpoints

1. Invalid refund ID format
2. Non-existent refund ID
3. Missing payment intent ID
4. Invalid amount (greater than original payment)
5. Missing required fields

## Test Cards

Use these Stripe test card numbers:

- Success: 4242 4242 4242 4242
- Requires Authentication: 4000 0025 0000 3155
- Decline: 4000 0000 0000 9995
- Insufficient Funds: 4000 0000 0000 9995

Expiry: Any future date
CVC: Any 3 digits
Postal Code: Any 5 digits
