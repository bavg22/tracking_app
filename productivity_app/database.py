import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

from models import now_iso


class Database:
    def __init__(self, db_path: str = "productivity.db"):
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.init_db()

    def init_db(self) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS pendings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                due_date TEXT,
                priority TEXT NOT NULL DEFAULT 'Medium',
                status TEXT NOT NULL DEFAULT 'Pending',
                category TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_text TEXT NOT NULL,
                is_done INTEGER NOT NULL DEFAULT 0,
                due_date TEXT,
                category TEXT DEFAULT '',
                position INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        self.conn.commit()
        self.seed_if_empty()

    def seed_if_empty(self) -> None:
        if not self.get_pendings() and not self.get_todos():
            self.add_pending(
                {
                    "title": "Finish weekly report",
                    "description": "Prepare summary metrics and blockers.",
                    "due_date": now_iso().split("T")[0],
                    "priority": "High",
                    "status": "In Progress",
                    "category": "Work",
                }
            )
            self.add_todo({"task_text": "Plan tomorrow priorities", "due_date": None, "category": "Daily"})

    def query(self, sql: str, params: tuple = ()):
        cur = self.conn.cursor()
        cur.execute(sql, params)
        self.conn.commit()
        return cur

    def get_pendings(self, status: Optional[str] = None, priority: Optional[str] = None, q: str = "") -> List[sqlite3.Row]:
        sql = "SELECT * FROM pendings WHERE 1=1"
        params: List[Any] = []
        if status and status != "All":
            sql += " AND status = ?"
            params.append(status)
        if priority and priority != "All":
            sql += " AND priority = ?"
            params.append(priority)
        if q:
            sql += " AND (title LIKE ? OR description LIKE ?)"
            like_q = f"%{q}%"
            params.extend([like_q, like_q])
        sql += " ORDER BY due_date IS NULL, due_date ASC, updated_at DESC"
        return self.query(sql, tuple(params)).fetchall()

    def add_pending(self, data: Dict[str, Any]) -> None:
        now = now_iso()
        self.query(
            """
            INSERT INTO pendings (title, description, due_date, priority, status, category, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["title"],
                data.get("description", ""),
                data.get("due_date"),
                data.get("priority", "Medium"),
                data.get("status", "Pending"),
                data.get("category", ""),
                now,
                now,
            ),
        )

    def update_pending(self, item_id: int, data: Dict[str, Any]) -> None:
        now = now_iso()
        self.query(
            """
            UPDATE pendings SET title=?, description=?, due_date=?, priority=?, status=?, category=?, updated_at=?
            WHERE id=?
            """,
            (data["title"], data.get("description", ""), data.get("due_date"), data["priority"], data["status"], data.get("category", ""), now, item_id),
        )

    def delete_pending(self, item_id: int) -> None:
        self.query("DELETE FROM pendings WHERE id=?", (item_id,))

    def get_todos(self) -> List[sqlite3.Row]:
        return self.query("SELECT * FROM todos ORDER BY position ASC, id ASC").fetchall()

    def add_todo(self, data: Dict[str, Any]) -> None:
        now = now_iso()
        pos = self.query("SELECT COALESCE(MAX(position),0)+1 FROM todos").fetchone()[0]
        self.query(
            "INSERT INTO todos (task_text, is_done, due_date, category, position, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (data["task_text"], int(data.get("is_done", False)), data.get("due_date"), data.get("category", ""), pos, now, now),
        )

    def update_todo_status(self, item_id: int, is_done: bool) -> None:
        self.query("UPDATE todos SET is_done=?, updated_at=? WHERE id=?", (int(is_done), now_iso(), item_id))

    def delete_todo(self, item_id: int) -> None:
        self.query("DELETE FROM todos WHERE id=?", (item_id,))

    def clear_completed_todos(self) -> None:
        self.query("DELETE FROM todos WHERE is_done=1")

    def update_todo_order(self, ids: List[int]) -> None:
        for pos, item_id in enumerate(ids, start=1):
            self.query("UPDATE todos SET position=?, updated_at=? WHERE id=?", (pos, now_iso(), item_id))
