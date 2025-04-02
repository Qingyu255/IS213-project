-- Create booking_payments table to store Stripe payment data specifically for bookings
CREATE TABLE IF NOT EXISTS booking_payments (
    id SERIAL PRIMARY KEY,
    booking_id UUID NOT NULL,
    payment_intent_id VARCHAR(255) NOT NULL,
    amount BIGINT NOT NULL,
    currency VARCHAR(10) NOT NULL,
    status VARCHAR(50) NOT NULL,
    customer_email VARCHAR(255),
    customer_name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_booking_payments_booking_id ON booking_payments(booking_id);
CREATE INDEX IF NOT EXISTS idx_booking_payments_payment_intent_id ON booking_payments(payment_intent_id);
CREATE INDEX IF NOT EXISTS idx_booking_payments_status ON booking_payments(status);

-- Add comments for documentation
COMMENT ON TABLE booking_payments IS 'Stores payment data specifically for ticket bookings';
COMMENT ON COLUMN booking_payments.booking_id IS 'ID of the booking in the ticket management service';
COMMENT ON COLUMN booking_payments.payment_intent_id IS 'Stripe payment intent ID for refunds';
COMMENT ON COLUMN booking_payments.status IS 'Payment status (paid, refunded, etc)'; 