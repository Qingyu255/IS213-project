-- First, backup existing events data before modifying the structure
CREATE TABLE events_backup AS SELECT * FROM events;

-- Drop dependent tables first to avoid foreign key constraints
DROP TABLE IF EXISTS event_categories CASCADE;
DROP TABLE IF EXISTS event_organizers CASCADE;

-- Drop the original events table
DROP TABLE IF EXISTS events CASCADE;

-- Recreate the events table with modified id column (no auto-generation)
CREATE TABLE events (
    id UUID PRIMARY KEY NOT NULL, -- Changed from auto-generated to explicitly provided UUID
    title VARCHAR NOT NULL,
    description TEXT,
    start_date_time TIMESTAMPTZ NOT NULL,
    end_date_time TIMESTAMPTZ,  -- Nullable, allows ongoing/one-day events
    image_url VARCHAR,
    venue VARCHAR,
    price NUMERIC(10,2),  -- NUMERIC for precise money values
    capacity INT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Recreate the event_categories table with the foreign key to the new events table
CREATE TABLE IF NOT EXISTS event_categories (
    event_id UUID NOT NULL,
    category_id UUID NOT NULL,
    PRIMARY KEY (event_id, category_id),
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
);

-- Recreate the event_organizers table with the foreign key to the new events table
CREATE TABLE IF NOT EXISTS event_organizers (
    event_id UUID NOT NULL,
    organizer_id UUID NOT NULL, -- External reference, no FK constraint
    organizer_username VARCHAR NOT NULL,
    PRIMARY KEY (event_id, organizer_id),
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
);

-- Restore data from backup to the new table structure
INSERT INTO events (
    id, title, description, start_date_time, end_date_time, 
    image_url, venue, price, capacity, created_at, updated_at
)
SELECT 
    id, title, description, start_date_time, end_date_time, 
    image_url, venue, price, capacity, created_at, updated_at
FROM events_backup;

-- Drop the backup table when finished
DROP TABLE events_backup; 