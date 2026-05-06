from datetime import date
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout, QFrame


class DashboardView(QWidget):
    def __init__(self, db):
        super().__init__(); self.db = db
        self.layout = QVBoxLayout(self)
        self.title = QLabel("Daily / Weekly Dashboard")
        self.layout.addWidget(self.title)
        self.grid = QGridLayout(); self.layout.addLayout(self.grid)
        self.cards = {}
        for i, k in enumerate(["Today's tasks", "Overdue pendings", "Upcoming deadlines", "Completed today", "By status", "Priority summary"]):
            card = QFrame(); card.setObjectName("card")
            cl = QVBoxLayout(card); lbl = QLabel(k); val = QLabel("-"); val.setWordWrap(True)
            cl.addWidget(lbl); cl.addWidget(val)
            self.cards[k] = val
            self.grid.addWidget(card, i // 2, i % 2)
        self.refresh()

    def refresh(self):
        today = date.today().isoformat()
        pendings = self.db.get_pendings()
        todos = self.db.get_todos()
        todays = sum(1 for t in todos if t["due_date"] == today or not t["due_date"])
        overdue = [p for p in pendings if p["due_date"] and p["due_date"] < today and p["status"] != "Done"]
        upcoming = [p for p in pendings if p["due_date"] and p["due_date"] >= today and p["status"] != "Done"][:5]
        completed_today = sum(1 for p in pendings if p["status"] == "Done" and p["updated_at"].startswith(today)) + sum(1 for t in todos if t["is_done"] and t["updated_at"].startswith(today))
        by_status = {s: sum(1 for p in pendings if p["status"] == s) for s in ["Pending", "In Progress", "Done"]}
        by_pri = {s: sum(1 for p in pendings if p["priority"] == s) for s in ["Low", "Medium", "High"]}
        self.cards["Today's tasks"].setText(str(todays))
        self.cards["Overdue pendings"].setText(str(len(overdue)))
        self.cards["Upcoming deadlines"].setText("\n".join([f"{p['title']} ({p['due_date']})" for p in upcoming]) or "None")
        self.cards["Completed today"].setText(str(completed_today))
        self.cards["By status"].setText(", ".join([f"{k}: {v}" for k, v in by_status.items()]))
        self.cards["Priority summary"].setText(", ".join([f"{k}: {v}" for k, v in by_pri.items()]))
