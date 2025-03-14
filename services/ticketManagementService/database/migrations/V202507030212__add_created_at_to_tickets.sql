-- Add created_at column to tickets table
ALTER TABLE tickets
ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP; 