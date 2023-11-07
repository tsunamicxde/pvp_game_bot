CREATE TABLE IF NOT EXISTS users (
    id serial PRIMARY KEY NOT NULL,
    user_id BIGINT UNIQUE NOT NULL,
    user_url TEXT UNIQUE,
    is_user_free BOOL DEFAULT FALSE,
    current_score INT DEFAULT 0,
    opponent_id BIGINT DEFAULT -1
);