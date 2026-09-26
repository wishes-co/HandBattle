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
            matches INTEGER DEFAULT 0,
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
        INSERT OR IGNORE INTO players
        (user_id, username, matches, wins, losses)
        VALUES (?, ?, 0, 0, 0)
    """, (user_id, username))

    conn.commit()
    conn.close()


def get_stats(user_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT username, matches, wins, losses
        FROM players
        WHERE user_id = ?
    """, (user_id,))

    result = cursor.fetchone()

    conn.close()

    return result


def record_result(winner_id, loser_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE players
        SET matches = matches + 1,
            wins = wins + 1
        WHERE user_id = ?
    """, (winner_id,))

    cursor.execute("""
        UPDATE players
        SET matches = matches + 1,
            losses = losses + 1
        WHERE user_id = ?
    """, (loser_id,))

    conn.commit()
    conn.close()
