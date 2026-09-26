import sqlite3

DB_NAME = "hand_cricket.db"


def connect_db():
    return sqlite3.connect(DB_NAME)


def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS players (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            wins INTEGER DEFAULT 0,
            losses INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()


def add_player(user_id, username):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO players (user_id, username)
        VALUES (?, ?)
    """, (user_id, username))

    conn.commit()
    conn.close(), 
