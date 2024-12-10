CREATE USER lifebot_user WITH ENCRYPTED PASSWORD 'lifebot_pass';
CREATE DATABASE lifebot_db OWNER lifebot_user;
GRANT ALL PRIVILEGES ON DATABASE lifebot_db TO lifebot_user;
