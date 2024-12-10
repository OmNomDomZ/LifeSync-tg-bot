\connect lifebot_db;

CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    title TEXT NOT NULL,
    event_date DATE NOT NULL,
    event_time TIME NOT NULL,
    description TEXT
);

GRANT ALL PRIVILEGES ON TABLE events TO lifebot_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO lifebot_user;
