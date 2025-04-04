-- First, insert booking payments data
INSERT INTO booking_payments (booking_id, payment_intent_id, amount, currency, status, customer_email, customer_name, created_at, updated_at)
VALUES
    -- Tech Conference bookings
    ('aaaaaaaa-e89b-4111-a456-556642441111', 'pi_tech_conf_1_123456789', 29999, 'USD', 'paid', 'john.doe@example.com', 'John Doe', NOW() - INTERVAL '30 minutes', NOW() - INTERVAL '30 minutes'),
    ('bbbbbbbb-e89b-4222-a456-556642442222', 'pi_tech_conf_2_123456789', 29999, 'USD', 'paid', 'jane.smith@example.com', 'Jane Smith', NOW() - INTERVAL '25 minutes', NOW() - INTERVAL '25 minutes'),
    
    -- Summer Music Festival bookings
    ('cccccccc-e89b-4333-a456-556642443333', 'pi_music_fest_1_123456789', 45000, 'USD', 'paid', 'mike.wilson@example.com', 'Mike Wilson', NOW() - INTERVAL '20 minutes', NOW() - INTERVAL '20 minutes'),
    ('dddddddd-e89b-4444-a456-556642444444', 'pi_music_fest_2_123456789', 30000, 'USD', 'paid', 'sarah.brown@example.com', 'Sarah Brown', NOW() - INTERVAL '15 minutes', NOW() - INTERVAL '15 minutes'),
    
    -- Art Exhibition booking
    ('eeeeeeee-e89b-4555-a456-556642445555', 'pi_art_exhibit_1_123456789', 2500, 'USD', 'paid', 'john.doe@example.com', 'John Doe', NOW() - INTERVAL '10 minutes', NOW() - INTERVAL '10 minutes'),
    
    -- Business Leadership Summit booking
    ('ffffffff-e89b-4666-a456-556642446666', 'pi_business_summit_1_123456789', 49999, 'USD', 'paid', 'jane.smith@example.com', 'Jane Smith', NOW() - INTERVAL '5 minutes', NOW() - INTERVAL '5 minutes'),
    
    -- Food & Wine Festival booking
    ('99999999-e89b-4777-a456-556642447777', 'pi_food_fest_1_123456789', 15000, 'USD', 'paid', 'mike.wilson@example.com', 'Mike Wilson', NOW(), NOW());

-- Insert payment verifications for both event creations and bookings
INSERT INTO payment_verifications (
    payment_id, event_id, user_id, organizer_id, event_type, 
    amount, currency, status, payment_method, receipt_email, receipt_url, 
    created_at, recorded_at
)
VALUES
    -- Event creation payments
    ('pi_event_create_tech_123456789', '123e4567-e89b-4aaa-a456-556642440000', NULL, 'a1b2c3d4-e89b-4111-a456-556642440001', 'event.creation.succeeded', 5000, 'USD', 'paid', 'card', 'tech.events@example.com', 'https://stripe.com/receipt/tech_conf', NOW() - INTERVAL '30 minutes', NOW() - INTERVAL '30 minutes'),
    ('pi_event_create_music_123456789', '223e4567-e89b-4bbb-a456-556642440001', NULL, 'c3d4e5f6-e89b-4333-a456-556642440003', 'event.creation.succeeded', 5000, 'USD', 'paid', 'card', 'music@example.com', 'https://stripe.com/receipt/music_fest', NOW() - INTERVAL '25 minutes', NOW() - INTERVAL '25 minutes'),
    ('pi_event_create_art_123456789', '323e4567-e89b-4ccc-a456-556642440002', NULL, 'd4e5f6a7-e89b-4444-a456-556642440004', 'event.creation.succeeded', 5000, 'USD', 'paid', 'card', 'art.gallery@example.com', 'https://stripe.com/receipt/art_exhibit', NOW() - INTERVAL '10 minutes', NOW() - INTERVAL '10 minutes'),
    ('pi_event_create_business_123456789', '423e4567-e89b-4ddd-a456-556642440003', NULL, 'e5f6a7b8-e89b-4555-a456-556642440005', 'event.creation.succeeded', 5000, 'USD', 'paid', 'card', 'business@example.com', 'https://stripe.com/receipt/business_summit', NOW() - INTERVAL '5 minutes', NOW() - INTERVAL '5 minutes'),
    ('pi_event_create_food_123456789', '523e4567-e89b-4eee-a456-556642440004', NULL, 'f6a7b8c9-e89b-4666-a456-556642440006', 'event.creation.succeeded', 5000, 'USD', 'paid', 'card', 'food.events@example.com', 'https://stripe.com/receipt/food_fest', NOW() - INTERVAL '30 minutes', NOW() - INTERVAL '30 minutes'),

    -- Booking payments verifications (matching booking_payments)
    ('pi_tech_conf_1_123456789', '123e4567-e89b-4aaa-a456-556642440000', 'aabbccdd-e89b-4777-a456-556642440007', NULL, 'payment_intent.succeeded', 29999, 'USD', 'paid', 'card', 'john.doe@example.com', 'https://stripe.com/receipt/tech_conf_1', NOW() - INTERVAL '30 minutes', NOW() - INTERVAL '30 minutes'),
    ('pi_tech_conf_2_123456789', '123e4567-e89b-4aaa-a456-556642440000', 'bbccddee-e89b-4888-a456-556642440008', NULL, 'payment_intent.succeeded', 29999, 'USD', 'paid', 'card', 'jane.smith@example.com', 'https://stripe.com/receipt/tech_conf_2', NOW() - INTERVAL '25 minutes', NOW() - INTERVAL '25 minutes'),
    ('pi_music_fest_1_123456789', '223e4567-e89b-4bbb-a456-556642440001', 'ccddeeff-e89b-4999-a456-556642440009', NULL, 'payment_intent.succeeded', 45000, 'USD', 'paid', 'card', 'mike.wilson@example.com', 'https://stripe.com/receipt/music_fest_1', NOW() - INTERVAL '20 minutes', NOW() - INTERVAL '20 minutes'),
    ('pi_music_fest_2_123456789', '223e4567-e89b-4bbb-a456-556642440001', 'ddeeffaa-e89b-4aaa-a456-556642440010', NULL, 'payment_intent.succeeded', 30000, 'USD', 'paid', 'card', 'sarah.brown@example.com', 'https://stripe.com/receipt/music_fest_2', NOW() - INTERVAL '15 minutes', NOW() - INTERVAL '15 minutes'),
    ('pi_art_exhibit_1_123456789', '323e4567-e89b-4ccc-a456-556642440002', 'aabbccdd-e89b-4777-a456-556642440007', NULL, 'payment_intent.succeeded', 2500, 'USD', 'paid', 'card', 'john.doe@example.com', 'https://stripe.com/receipt/art_exhibit_1', NOW() - INTERVAL '10 minutes', NOW() - INTERVAL '10 minutes'),
    ('pi_business_summit_1_123456789', '423e4567-e89b-4ddd-a456-556642440003', 'bbccddee-e89b-4888-a456-556642440008', NULL, 'payment_intent.succeeded', 49999, 'USD', 'paid', 'card', 'jane.smith@example.com', 'https://stripe.com/receipt/business_summit_1', NOW() - INTERVAL '5 minutes', NOW() - INTERVAL '5 minutes'),
    ('pi_food_fest_1_123456789', '523e4567-e89b-4eee-a456-556642440004', 'ccddeeff-e89b-4999-a456-556642440009', NULL, 'payment_intent.succeeded', 15000, 'USD', 'paid', 'card', 'mike.wilson@example.com', 'https://stripe.com/receipt/food_fest_1', NOW() - INTERVAL '30 minutes', NOW() - INTERVAL '30 minutes'); 