"""
Chat history storage — persists conversations in SQLite.
"""
import sqlite3
from contextlib import contextmanager
from typing import List, Dict, Tuple


class ChatStorage:
    def __init__(self, db_path: str = "chat_history.db"):
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_db(self):
        with self._conn() as c:
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id  TEXT NOT NULL,
                    role        TEXT NOT NULL,
                    content     TEXT NOT NULL,
                    timestamp   TEXT NOT NULL
                )
                """
            )
            c.execute(
                "CREATE INDEX IF NOT EXISTS idx_session ON messages(session_id)"
            )

    def save_message(
        self, session_id: str, role: str, content: str, timestamp: str
    ) -> None:
        with self._conn() as c:
            c.execute(
                "INSERT INTO messages (session_id, role, content, timestamp) "
                "VALUES (?, ?, ?, ?)",
                (session_id, role, content, timestamp),
            )

    def get_messages(self, session_id: str) -> List[Dict[str, str]]:
        with self._conn() as c:
            rows = c.execute(
                "SELECT role, content FROM messages "
                "WHERE session_id = ? ORDER BY id ASC",
                (session_id,),
            ).fetchall()
        return [{"role": r["role"], "content": r["content"]} for r in rows]

    def list_sessions(self, limit: int = 20) -> List[Tuple[str, str, str]]:
        """Return [(session_id, first_user_message, timestamp), ...] newest first."""
        with self._conn() as c:
            rows = c.execute(
                """
                SELECT session_id,
                       (SELECT content FROM messages
                        WHERE session_id = m.session_id AND role = 'user'
                        ORDER BY id ASC LIMIT 1) AS first_msg,
                       MAX(timestamp) AS last_ts
                FROM messages m
                GROUP BY session_id
                ORDER BY last_ts DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [(r["session_id"], r["first_msg"] or "(empty)", r["last_ts"]) for r in rows]
    def clear_all(self) -> int:
        """Delete all messages from the database. Returns count of messages deleted."""
        with self._conn() as c:
            count = c.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
            c.execute("DELETE FROM messages")
        return count