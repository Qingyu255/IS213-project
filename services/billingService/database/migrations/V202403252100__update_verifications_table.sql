-- Create payment_verifications table to store all Stripe payment verification data
ALTER TABLE payment_verifications
ADD COLUMN organizer_id VARCHAR(255);

ALTER TABLE payment_verifications
DROP COLUMN verification_data;