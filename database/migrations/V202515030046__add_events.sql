-- Main events table
CREATE TABLE IF NOT EXISTS events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
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

-- Category table to maintain normalized event categories
CREATE TABLE IF NOT EXISTS categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR UNIQUE NOT NULL
);

-- Many-to-Many Relationship: Linking events with categories
CREATE TABLE IF NOT EXISTS event_categories (
    event_id UUID NOT NULL,
    category_id UUID NOT NULL,
    PRIMARY KEY (event_id, category_id),
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
);

-- Many-to-Many Relationship: Linking events with organizers
CREATE TABLE IF NOT EXISTS event_organizers (
    event_id UUID NOT NULL,
    organizer_id UUID NOT NULL, -- External reference, no FK constraint
    PRIMARY KEY (event_id, organizer_id),
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
);
