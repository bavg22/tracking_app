from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class PendingItem:
    id: Optional[int]
    title: str
    description: str
    due_date: Optional[str]
    priority: str
    status: str
    category: str
    created_at: str
    updated_at: str


@dataclass
class TodoItem:
    id: Optional[int]
    task_text: str
    is_done: bool
    due_date: Optional[str]
    category: str
    position: int
    created_at: str
    updated_at: str


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")
