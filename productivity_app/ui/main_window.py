from PySide6.QtCore import QDate
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget

from ui.dashboard import DashboardView
from ui.pendings_view import PendingsView, PendingDialog
from ui.todo_view import TodoView, TodoDialog
from ui.calendar_view import CalendarView
from ui.settings_view import SettingsView


class MainWindow(QMainWindow):
    def __init__(self, db):
        super().__init__(); self.db = db
        self.setWindowTitle("Productivity Planner")
        self.resize(1200, 760)
        container = QWidget(); self.setCentralWidget(container)
        root = QHBoxLayout(container)
        sidebar = QVBoxLayout(); root.addLayout(sidebar, 1)
        self.stack = QStackedWidget(); root.addWidget(self.stack, 4)

        self.dashboard = DashboardView(db)
        self.pendings = PendingsView(db, self.refresh_all)
        self.todo = TodoView(db, self.refresh_all)
        self.calendar = CalendarView(db, self.add_from_calendar)
        self.settings = SettingsView()
        for view in [self.dashboard, self.pendings, self.todo, self.calendar, self.settings]:
            self.stack.addWidget(view)

        for i, name in enumerate(["Dashboard", "Pendings", "To-Do", "Calendar", "Settings"]):
            b = QPushButton(name)
            b.clicked.connect(lambda _, idx=i: self.stack.setCurrentIndex(idx))
            sidebar.addWidget(b)
        sidebar.addStretch()

    def add_from_calendar(self, item_type: str, selected_date: str):
        if item_type == "pending":
            d = PendingDialog(self)
            d.due.setDate(QDate.fromString(selected_date, "yyyy-MM-dd"))
            if d.exec():
                values = d.values();
                if values["title"]:
                    self.db.add_pending(values)
        else:
            d = TodoDialog(self)
            d.due.setDate(QDate.fromString(selected_date, "yyyy-MM-dd"))
            if d.exec():
                values = d.values()
                if values["task_text"]:
                    self.db.add_todo(values)
        self.refresh_all()
        self.pendings.load()
        self.todo.load()

    def refresh_all(self):
        self.dashboard.refresh()
        self.calendar.highlight_dates()
        self.calendar.refresh_for_date()
