-- Create payment_verifications table to store all Stripe payment verification data
CREATE TABLE IF NOT EXISTS payment_verifications (
    id SERIAL PRIMARY KEY,
    payment_id VARCHAR(255) NOT NULL,
    event_id VARCHAR(255),
    user_id VARCHAR(255),
    event_type VARCHAR(100) NOT NULL,
    amount BIGINT,
    currency VARCHAR(10),
    status VARCHAR(50),
    payment_method VARCHAR(100),
    receipt_email VARCHAR(255),
    receipt_url VARCHAR(512),
    verification_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_payment_verifications_payment_id ON payment_verifications(payment_id);
CREATE INDEX IF NOT EXISTS idx_payment_verifications_event_id ON payment_verifications(event_id);
CREATE INDEX IF NOT EXISTS idx_payment_verifications_user_id ON payment_verifications(user_id);
CREATE INDEX IF NOT EXISTS idx_payment_verifications_event_type ON payment_verifications(event_type);
CREATE INDEX IF NOT EXISTS idx_payment_verifications_created_at ON payment_verifications(created_at);

-- Comments for documentation
COMMENT ON TABLE payment_verifications IS 'Stores verification data for all payment-related Stripe webhook events';
COMMENT ON COLUMN payment_verifications.payment_id IS 'Stripe payment intent ID or checkout session ID';
COMMENT ON COLUMN payment_verifications.event_id IS 'Associated event ID in our system';
COMMENT ON COLUMN payment_verifications.user_id IS 'User who made the payment';
COMMENT ON COLUMN payment_verifications.event_type IS 'Stripe event type like payment_intent.succeeded';
COMMENT ON COLUMN payment_verifications.amount IS 'Payment amount in cents';
COMMENT ON COLUMN payment_verifications.verification_data IS 'Complete JSON of the verification data';
COMMENT ON COLUMN payment_verifications.created_at IS 'When the payment was processed by Stripe';
COMMENT ON COLUMN payment_verifications.recorded_at IS 'When we received and recorded this payment'; 