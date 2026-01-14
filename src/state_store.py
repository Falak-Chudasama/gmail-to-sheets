import sqlite3
import os
import datetime

class StateStore:
    def __init__(self, db_path):
        self.db_path = db_path
        self._ensure_db()

    def _ensure_db(self):
        dirname = os.path.dirname(self.db_path)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS processed (
                message_id TEXT PRIMARY KEY,
                processed_at TEXT
            )
        """)
        conn.commit()
        conn.close()

    def is_processed(self, message_id):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM processed WHERE message_id = ?", (message_id,))
        res = cur.fetchone()
        conn.close()
        return res is not None

    def mark_processed(self, message_id):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("INSERT OR REPLACE INTO processed (message_id, processed_at) VALUES (?, ?)",
                    (message_id, datetime.datetime.utcnow().isoformat()))
        conn.commit()
        conn.close()