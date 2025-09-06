import sqlite3
from typing import List, Dict
from contextlib import contextmanager
from server.config import Config

@contextmanager
def get_db():
    conn = sqlite3.connect(Config.Path.DATABASE_PATH)
    try:
        yield conn
    finally:
        conn.close()

def list_sessions() -> List[int]:
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT session_id FROM messages ORDER BY session_id DESC")
        return [row[0] for row in cur.fetchall()]

def create_session() -> int:
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT MAX(session_id) FROM messages")
        max_id = cur.fetchone()[0]
        return (max_id + 1) if max_id else 1

def save_message(session_id: str, role: str, content: str):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
            (int(session_id), role, content)
        )
        conn.commit()

def load_session_messages(session_id: str) -> List[Dict[str, str]]:
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT role, content FROM messages WHERE session_id = ? ORDER BY id",
            (int(session_id),)
        )
        return [{"role": role, "content": content} for role, content in cur.fetchall()]