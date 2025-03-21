INSERT INTO categories (id, name) VALUES
  (gen_random_uuid(), 'technology'),
  (gen_random_uuid(), 'sports'),
  (gen_random_uuid(), 'music'),
  (gen_random_uuid(), 'art'),
  (gen_random_uuid(), 'travel'),
  (gen_random_uuid(), 'food'),
  (gen_random_uuid(), 'science'),
  (gen_random_uuid(), 'business')
ON CONFLICT (name) DO NOTHING;
