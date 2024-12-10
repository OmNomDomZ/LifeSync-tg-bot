from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "lifebot_db")
DB_USER = os.getenv("DB_USER", "lifebot_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "lifebot_pass")
DB_PORT = os.getenv("DB_PORT", "5432")
