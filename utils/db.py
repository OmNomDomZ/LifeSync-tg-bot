import psycopg2
from psycopg2.extras import DictCursor

from config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER


def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )

def add_event(user_id, title, event_date, event_time, description):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO events (user_id, title, event_date, event_time, description)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id;
            """, (user_id, title, event_date, event_time, description))
            return cur.fetchone()[0]

def list_events(user_id):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT id, title, event_date, event_time, description FROM events WHERE user_id=%s ORDER BY event_date, event_time;", (user_id,))
            return [dict(row) for row in cur.fetchall()]

def delete_event(user_id, event_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM events WHERE user_id=%s AND id=%s;", (user_id, event_id))
            return cur.rowcount
