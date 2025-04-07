-- Insert sample events
INSERT INTO events (id, title, description, start_date_time, end_date_time, image_url, venue, price, capacity, created_at, updated_at) 
VALUES
    ('123e4567-e89b-4aaa-a456-556642440000', 'Tech Conference 2024', 'Annual technology conference featuring the latest innovations', NOW() + INTERVAL '30 minutes', NOW() + INTERVAL '3 hours', '/eventplaceholder.png', 
    '{"address": "123 Convention Ave, Downtown, CA 94105, USA", "name": "Convention Center", "city": "San Francisco", "state": "California", "additionalDetails": "Main Exhibition Hall", "coordinates": {"lat": 37.7749, "lng": -122.4194}}',
    299.99, 1000, NOW(), NOW()),
    
    ('223e4567-e89b-4bbb-a456-556642440001', 'Summer Music Festival', 'Three days of amazing live performances', NOW() + INTERVAL '1 hour', NOW() + INTERVAL '4 hours', '/eventplaceholder.png',
    '{"address": "Central Park West, New York, NY 10024, USA", "name": "Central Park", "city": "New York", "state": "New York", "additionalDetails": "Great Lawn", "coordinates": {"lat": 40.7829, "lng": -73.9654}}',
    150.00, 5000, NOW(), NOW()),
    
    ('323e4567-e89b-4ccc-a456-556642440002', 'Art Exhibition: Modern Masters', 'Contemporary art showcase', NOW() + INTERVAL '2 hours', NOW() + INTERVAL '5 hours', '/eventplaceholder.png',
    '{"address": "1000 Fifth Avenue, New York, NY 10028, USA", "name": "Metropolitan Museum", "city": "New York", "state": "New York", "additionalDetails": "Modern Wing", "coordinates": {"lat": 40.7794, "lng": -73.9632}}',
    25.00, 200, NOW(), NOW()),
    
    ('423e4567-e89b-4ddd-a456-556642440003', 'Business Leadership Summit', 'Network with industry leaders', NOW() + INTERVAL '3 hours', NOW() + INTERVAL '6 hours', '/eventplaceholder.png',
    '{"address": "335 Powell St, San Francisco, CA 94102, USA", "name": "Grand Hotel", "city": "San Francisco", "state": "California", "additionalDetails": "Grand Ballroom", "coordinates": {"lat": 37.7879, "lng": -122.4075}}',
    499.99, 300, NOW(), NOW()),
    
    ('523e4567-e89b-4eee-a456-556642440004', 'Food & Wine Festival', 'Taste cuisines from around the world', NOW() + INTERVAL '4 hours', NOW() + INTERVAL '7 hours', '/eventplaceholder.png',
    '{"address": "585 Howard St, San Francisco, CA 94105, USA", "name": "City Square", "city": "San Francisco", "state": "California", "additionalDetails": "Open Plaza", "coordinates": {"lat": 37.7873, "lng": -122.3971}}',
    75.00, 2000, NOW(), NOW());

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