-- Feature 1: Logs Table

CREATE TABLE IF NOT EXISTS logs (
    id SERIAL PRIMARY KEY,
    service_name VARCHAR(100),
    level VARCHAR(10),
    message TEXT,
    transaction_id VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- (Optional) Add indexes to optimize queries
CREATE INDEX IF NOT EXISTS idx_logs_service_name ON logs(service_name);
CREATE INDEX IF NOT EXISTS idx_logs_transaction_id ON logs(transaction_id);
