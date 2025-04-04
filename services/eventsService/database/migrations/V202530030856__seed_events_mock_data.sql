-- Insert sample events
INSERT INTO events (id, title, description, start_date_time, end_date_time, image_url, venue, price, capacity, created_at, updated_at) 
VALUES
    ('123e4567-e89b-4aaa-a456-556642440000', 'Tech Conference 2024', 'Annual technology conference featuring the latest innovations', NOW() + INTERVAL '30 minutes', NOW() + INTERVAL '3 hours', '/eventplaceholder.png', 'Convention Center', 299.99, 1000, NOW(), NOW()),
    ('223e4567-e89b-4bbb-a456-556642440001', 'Summer Music Festival', 'Three days of amazing live performances', NOW() + INTERVAL '1 hour', NOW() + INTERVAL '4 hours', '/eventplaceholder.png', 'Central Park', 150.00, 5000, NOW(), NOW()),
    ('323e4567-e89b-4ccc-a456-556642440002', 'Art Exhibition: Modern Masters', 'Contemporary art showcase', NOW() + INTERVAL '2 hours', NOW() + INTERVAL '5 hours', '/eventplaceholder.png', 'Metropolitan Museum', 25.00, 200, NOW(), NOW()),
    ('423e4567-e89b-4ddd-a456-556642440003', 'Business Leadership Summit', 'Network with industry leaders', NOW() + INTERVAL '3 hours', NOW() + INTERVAL '6 hours', '/eventplaceholder.png', 'Grand Hotel', 499.99, 300, NOW(), NOW()),
    ('523e4567-e89b-4eee-a456-556642440004', 'Food & Wine Festival', 'Taste cuisines from around the world', NOW() + INTERVAL '4 hours', NOW() + INTERVAL '7 hours', '/eventplaceholder.png', 'City Square', 75.00, 2000, NOW(), NOW());

-- Get category IDs for linking (using subqueries for readability)
WITH category_ids AS (
    SELECT id, name FROM categories
)
INSERT INTO event_categories (event_id, category_id)
VALUES
    -- Tech Conference categories
    ('123e4567-e89b-4aaa-a456-556642440000', (SELECT id FROM categories WHERE name = 'technology')),
    ('123e4567-e89b-4aaa-a456-556642440000', (SELECT id FROM categories WHERE name = 'business')),
    
    -- Summer Music Festival categories
    ('223e4567-e89b-4bbb-a456-556642440001', (SELECT id FROM categories WHERE name = 'music')),
    ('223e4567-e89b-4bbb-a456-556642440001', (SELECT id FROM categories WHERE name = 'art')),
    
    -- Art Exhibition categories
    ('323e4567-e89b-4ccc-a456-556642440002', (SELECT id FROM categories WHERE name = 'art')),
    
    -- Business Leadership Summit categories
    ('423e4567-e89b-4ddd-a456-556642440003', (SELECT id FROM categories WHERE name = 'business')),
    
    -- Food & Wine Festival categories
    ('523e4567-e89b-4eee-a456-556642440004', (SELECT id FROM categories WHERE name = 'food'));

-- Insert sample event organizers
INSERT INTO event_organizers (event_id, organizer_id, organizer_username)
VALUES
    ('123e4567-e89b-4aaa-a456-556642440000', 'a1b2c3d4-e89b-4111-a456-556642440001', 'tech_events_org'),
    ('123e4567-e89b-4aaa-a456-556642440000', 'b2c3d4e5-e89b-4222-a456-556642440002', 'innovation_hub'),
    ('223e4567-e89b-4bbb-a456-556642440001', 'c3d4e5f6-e89b-4333-a456-556642440003', 'music_promotions'),
    ('323e4567-e89b-4ccc-a456-556642440002', 'd4e5f6a7-e89b-4444-a456-556642440004', 'art_gallery_official'),
    ('423e4567-e89b-4ddd-a456-556642440003', 'e5f6a7b8-e89b-4555-a456-556642440005', 'business_network'),
    ('523e4567-e89b-4eee-a456-556642440004', 'f6a7b8c9-e89b-4666-a456-556642440006', 'foodie_events'); 