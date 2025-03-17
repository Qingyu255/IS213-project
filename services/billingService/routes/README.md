# Billing Service Routes

This directory contains the API routes for the billing service, separated into production and test routes.

## Route Structure

### Production Routes

These routes are intended for real payment processing in production environments:

- **payment.py**: Handles real payment processing using Stripe Payment Intents

  - `/api/payment/process`: Process real payments with payment methods
  - `/api/payment/confirm`: Confirm payments that require additional authentication
  - `/api/payment/invoice`: Create invoices for customers

- **refund.py**: Handles real refund processing

  - `/api/refund/create`: Process refunds for charges
  - `/api/refund/payment_intent`: Process refunds for payment intents
  - `/api/refund/{refund_id}`: Get refund details

- **webhook.py**: Handles Stripe webhook events with signature verification
  - `/api/webhook`: Process webhook events from Stripe

### Test Routes

These routes are intended for testing and development purposes only:

- **test_payment.py**: Simplified payment processing for testing

  - `/api/test/payment/create`: Create test payments using Stripe test tokens
  - `/api/test/payment/{payment_id}`: Get test payment details
  - `/api/test/payment/verify`: Verify test payment status

- **test_refund.py**: Simplified refund processing for testing

  - `/api/test/refund/create`: Process test refunds
  - `/api/test/refund/{refund_id}`: Get test refund details

- **test_webhook.py**: Simplified webhook handling for testing
  - `/api/test/webhook`: Process test webhook events without signature verification
  - `/api/test/webhook/simulate`: Simulate webhook events for testing

## Usage Guidelines

1. **Development/Testing**: Use the test routes (`/api/test/*`) during development and testing.

   - These routes use Stripe test tokens and don't require real payment methods.
   - They have simplified error handling and validation.
   - The test webhook routes don't require signature verification.

2. **Production**: Use the production routes (`/api/*`) for real payment processing.
   - These routes use Stripe Payment Intents for real payments.
   - They include comprehensive error handling and validation.
   - The webhook routes require proper signature verification.

## Security Considerations

- **Test Routes**: Do not expose test routes in production environments.
- **Production Routes**: Always use HTTPS in production and ensure proper authentication.
- **Webhooks**: Always verify webhook signatures in production.

## Testing with Postman

See the main README.md file for detailed instructions on testing these routes with Postman.
