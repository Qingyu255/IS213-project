-- Insert users (including event organizers and regular users)
INSERT INTO users (id, email, username, created_at, updated_at) 
VALUES
    -- Event organizers
    ('a1b2c3d4-e89b-4111-a456-556642440001', 'tech.events@example.com', 'tech_events_org', NOW(), NOW()),
    ('b2c3d4e5-e89b-4222-a456-556642440002', 'innovation@example.com', 'innovation_hub', NOW(), NOW()),
    ('c3d4e5f6-e89b-4333-a456-556642440003', 'music@example.com', 'music_promotions', NOW(), NOW()),
    ('d4e5f6a7-e89b-4444-a456-556642440004', 'art.gallery@example.com', 'art_gallery_official', NOW(), NOW()),
    ('e5f6a7b8-e89b-4555-a456-556642440005', 'business@example.com', 'business_network', NOW(), NOW()),
    ('f6a7b8c9-e89b-4666-a456-556642440006', 'food.events@example.com', 'foodie_events', NOW(), NOW()),
    
    -- Regular users
    ('aabbccdd-e89b-4777-a456-556642440007', 'john.doe@example.com', 'john_doe', NOW(), NOW()),
    ('bbccddee-e89b-4888-a456-556642440008', 'jane.smith@example.com', 'jane_smith', NOW(), NOW()),
    ('ccddeeff-e89b-4999-a456-556642440009', 'mike.wilson@example.com', 'mike_wilson', NOW(), NOW()),
    ('ddeeffaa-e89b-4aaa-a456-556642440010', 'sarah.brown@example.com', 'sarah_brown', NOW(), NOW());

-- Insert user interests
INSERT INTO user_interests (user_id, interest)
VALUES
    -- Organizer interests
    ('a1b2c3d4-e89b-4111-a456-556642440001', 'technology'),
    ('a1b2c3d4-e89b-4111-a456-556642440001', 'business'),
    ('c3d4e5f6-e89b-4333-a456-556642440003', 'music'),
    ('d4e5f6a7-e89b-4444-a456-556642440004', 'art'),
    
    -- Regular user interests
    ('aabbccdd-e89b-4777-a456-556642440007', 'technology'),
    ('aabbccdd-e89b-4777-a456-556642440007', 'business'),
    ('bbccddee-e89b-4888-a456-556642440008', 'music'),
    ('bbccddee-e89b-4888-a456-556642440008', 'art'),
    ('ccddeeff-e89b-4999-a456-556642440009', 'food'),
    ('ddeeffaa-e89b-4aaa-a456-556642440010', 'technology'); 