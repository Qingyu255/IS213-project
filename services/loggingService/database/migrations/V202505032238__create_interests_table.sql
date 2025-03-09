CREATE TABLE IF NOT EXISTS user_interests (
    user_id VARCHAR(255) NOT NULL,
    interest VARCHAR NOT NULL,
    PRIMARY KEY (user_id, interest),
    FOREIGN KEY (user_id) REFERENCES users (id)
);