import sqlite3
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SQLITE_PATH = BASE_DIR / "chat_history.db"


def init_db():
    conn = sqlite3.connect(SQLITE_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def save_message(username: str, role: str, content: str):
    conn = sqlite3.connect(SQLITE_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (username, role, content, created_at) VALUES (?, ?, ?, ?)",
        (username, role, content, datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()


def load_messages(username: str):
    conn = sqlite3.connect(SQLITE_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT role, content, created_at FROM messages WHERE username = ? ORDER BY id",
        (username,),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def clear_history(username: str):
    conn = sqlite3.connect(SQLITE_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM messages WHERE username = ?", (username,))
    conn.commit()
    conn.close()
