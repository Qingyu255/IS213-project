-- Insert sample bookings
INSERT INTO bookings (booking_id, user_id, event_id, status, created_at, updated_at)
VALUES
    -- Tech Conference bookings
    ('aaaaaaaa-e89b-4111-a456-556642441111', 'aabbccdd-e89b-4777-a456-556642440007', '123e4567-e89b-4aaa-a456-556642440000', 'CONFIRMED', NOW() - INTERVAL '30 minutes', NOW() - INTERVAL '30 minutes'),
    ('bbbbbbbb-e89b-4222-a456-556642442222', 'bbccddee-e89b-4888-a456-556642440008', '123e4567-e89b-4aaa-a456-556642440000', 'CONFIRMED', NOW() - INTERVAL '25 minutes', NOW() - INTERVAL '25 minutes'),
    
    -- Summer Music Festival bookings (multiple tickets per booking)
    ('cccccccc-e89b-4333-a456-556642443333', 'ccddeeff-e89b-4999-a456-556642440009', '223e4567-e89b-4bbb-a456-556642440001', 'CONFIRMED', NOW() - INTERVAL '20 minutes', NOW() - INTERVAL '20 minutes'),
    ('dddddddd-e89b-4444-a456-556642444444', 'ddeeffaa-e89b-4aaa-a456-556642440010', '223e4567-e89b-4bbb-a456-556642440001', 'CONFIRMED', NOW() - INTERVAL '15 minutes', NOW() - INTERVAL '15 minutes'),
    
    -- Art Exhibition booking
    ('eeeeeeee-e89b-4555-a456-556642445555', 'aabbccdd-e89b-4777-a456-556642440007', '323e4567-e89b-4ccc-a456-556642440002', 'CONFIRMED', NOW() - INTERVAL '10 minutes', NOW() - INTERVAL '10 minutes'),
    
    -- Business Leadership Summit bookings
    ('ffffffff-e89b-4666-a456-556642446666', 'bbccddee-e89b-4888-a456-556642440008', '423e4567-e89b-4ddd-a456-556642440003', 'CONFIRMED', NOW() - INTERVAL '5 minutes', NOW() - INTERVAL '5 minutes'),
    
    -- Food & Wine Festival bookings
    ('99999999-e89b-4777-a456-556642447777', 'ccddeeff-e89b-4999-a456-556642440009', '523e4567-e89b-4eee-a456-556642440004', 'CONFIRMED', NOW(), NOW());

-- Insert tickets for each booking
INSERT INTO tickets (ticket_id, booking_id)
VALUES
    -- Tech Conference tickets (1 ticket per booking)
    ('11111111-e89b-4111-a456-556642441001', 'aaaaaaaa-e89b-4111-a456-556642441111'),
    ('22222222-e89b-4222-a456-556642441002', 'bbbbbbbb-e89b-4222-a456-556642442222'),
    
    -- Summer Music Festival tickets (3 tickets per booking - family/group bookings)
    ('33333333-e89b-4333-a456-556642441003', 'cccccccc-e89b-4333-a456-556642443333'),
    ('44444444-e89b-4444-a456-556642441004', 'cccccccc-e89b-4333-a456-556642443333'),
    ('55555555-e89b-4555-a456-556642441005', 'cccccccc-e89b-4333-a456-556642443333'),
    ('66666666-e89b-4666-a456-556642441006', 'dddddddd-e89b-4444-a456-556642444444'),
    ('77777777-e89b-4777-a456-556642441007', 'dddddddd-e89b-4444-a456-556642444444'),
    
    -- Art Exhibition ticket (1 ticket)
    ('88888888-e89b-4888-a456-556642441008', 'eeeeeeee-e89b-4555-a456-556642445555'),
    
    -- Business Leadership Summit ticket (1 ticket)
    ('99999999-e89b-4999-a456-556642441009', 'ffffffff-e89b-4666-a456-556642446666'),
    
    -- Food & Wine Festival tickets (2 tickets - couple booking)
    ('aaaaaaaa-e89b-4aaa-a456-556642441010', '99999999-e89b-4777-a456-556642447777'),
    ('bbbbbbbb-e89b-4bbb-a456-556642441011', '99999999-e89b-4777-a456-556642447777'); 