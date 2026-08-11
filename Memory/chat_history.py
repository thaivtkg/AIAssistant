import sqlite3
import os
from typing import List, Dict
from Core.interfaces import IChatHistory, ILogger


class SQLiteChatHistory(IChatHistory):
    def __init__(self, db_path: str = "Memory/chat_history.db", logger: ILogger | None = None):
        self.db_path = db_path
        self.logger = logger
        self._init_db()

    def _init_db(self) -> None:
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def add_message(self, role: str, content: str) -> None:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO history (role, content) VALUES (?, ?)",
                    (role, content)
                )
                conn.commit()
        except Exception as e:
            if self.logger:
                self.logger.error(f"Lỗi ghi lịch sử chat SQLite: {str(e)}")

    def get_recent_messages(self, limit: int = 10) -> List[Dict[str, str]]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT role, content FROM (SELECT id, role, content FROM history ORDER BY id DESC LIMIT ?) ORDER BY id ASC",
                    (limit,)
                )
                rows = cursor.fetchall()
                return [{"role": row[0], "content": row[1]} for row in rows]
        except Exception as e:
            if self.logger:
                self.logger.error(f"Lỗi đọc lịch sử chat SQLite: {str(e)}")
            return []

    def clear(self) -> None:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM history")
                conn.commit()
        except Exception as e:
            if self.logger:
                self.logger.error(f"Lỗi dọn dẹp lịch sử chat SQLite: {str(e)}")