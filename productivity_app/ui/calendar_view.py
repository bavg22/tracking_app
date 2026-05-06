from PySide6.QtCore import QDate
from PySide6.QtGui import QTextCharFormat, QColor
from PySide6.QtWidgets import QWidget, QVBoxLayout, QCalendarWidget, QLabel, QListWidget, QPushButton, QHBoxLayout


class CalendarView(QWidget):
    def __init__(self, db, add_from_calendar_cb):
        super().__init__(); self.db = db; self.add_from_calendar_cb = add_from_calendar_cb
        l = QVBoxLayout(self)
        self.cal = QCalendarWidget(); self.info = QLabel("Items due on selected date"); self.list = QListWidget()
        l.addWidget(self.cal)
        row = QHBoxLayout()
        self.add_btn = QPushButton("Add pending on selected date")
        self.add_todo_btn = QPushButton("Add to-do on selected date")
        row.addWidget(self.add_btn); row.addWidget(self.add_todo_btn)
        l.addLayout(row)
        l.addWidget(self.info); l.addWidget(self.list)
        self.cal.selectionChanged.connect(self.refresh_for_date)
        self.add_btn.clicked.connect(lambda: self.add_from_calendar_cb("pending", self.selected_date()))
        self.add_todo_btn.clicked.connect(lambda: self.add_from_calendar_cb("todo", self.selected_date()))
        self.highlight_dates(); self.refresh_for_date()

    def selected_date(self):
        return self.cal.selectedDate().toString("yyyy-MM-dd")

    def highlight_dates(self):
        self.cal.setDateTextFormat(QDate(), QTextCharFormat())
        fmt = QTextCharFormat(); fmt.setBackground(QColor("#dbeafe"))
        for p in self.db.get_pendings():
            if p["due_date"]:
                self.cal.setDateTextFormat(QDate.fromString(p["due_date"], "yyyy-MM-dd"), fmt)
        for t in self.db.get_todos():
            if t["due_date"]:
                self.cal.setDateTextFormat(QDate.fromString(t["due_date"], "yyyy-MM-dd"), fmt)

    def refresh_for_date(self):
        d = self.selected_date()
        self.list.clear()
        for p in self.db.get_pendings():
            if p["due_date"] == d:
                self.list.addItem(f"[Pending] {p['title']} - {p['status']}")
        for t in self.db.get_todos():
            if t["due_date"] == d:
                self.list.addItem(f"[Todo] {t['task_text']}")
