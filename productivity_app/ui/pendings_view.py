from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QComboBox,
    QTableWidget, QTableWidgetItem, QMessageBox, QDialog, QFormLayout, QTextEdit, QDateEdit
)
from PySide6.QtCore import QDate


class PendingDialog(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle("Pending")
        form = QFormLayout(self)
        self.title = QLineEdit(data["title"] if data else "")
        self.desc = QTextEdit(data["description"] if data else "")
        self.due = QDateEdit(); self.due.setCalendarPopup(True); self.due.setDisplayFormat("yyyy-MM-dd")
        self.due.setDate(QDate.currentDate())
        if data and data["due_date"]:
            self.due.setDate(QDate.fromString(data["due_date"], "yyyy-MM-dd"))
        self.priority = QComboBox(); self.priority.addItems(["Low", "Medium", "High"])
        self.status = QComboBox(); self.status.addItems(["Pending", "In Progress", "Done"])
        self.category = QLineEdit(data["category"] if data else "")
        if data:
            self.priority.setCurrentText(data["priority"])
            self.status.setCurrentText(data["status"])
        form.addRow("Title", self.title); form.addRow("Description", self.desc); form.addRow("Due", self.due)
        form.addRow("Priority", self.priority); form.addRow("Status", self.status); form.addRow("Category", self.category)
        btn = QPushButton("Save"); btn.clicked.connect(self.accept); form.addRow(btn)

    def values(self):
        return {
            "title": self.title.text().strip(),
            "description": self.desc.toPlainText().strip(),
            "due_date": self.due.date().toString("yyyy-MM-dd"),
            "priority": self.priority.currentText(),
            "status": self.status.currentText(),
            "category": self.category.text().strip(),
        }


class PendingsView(QWidget):
    def __init__(self, db, refresh_cb):
        super().__init__(); self.db = db; self.refresh_cb = refresh_cb
        layout = QVBoxLayout(self)
        top = QHBoxLayout()
        self.search = QLineEdit(); self.search.setPlaceholderText("Search...")
        self.status = QComboBox(); self.status.addItems(["All", "Pending", "In Progress", "Done"])
        self.priority = QComboBox(); self.priority.addItems(["All", "Low", "Medium", "High"])
        add_btn = QPushButton("Add Pending")
        for w in [self.search, self.status, self.priority, add_btn]: top.addWidget(w)
        layout.addLayout(top)
        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels(["Title", "Description", "Due", "Priority", "Status", "Category", "Created", "Updated"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table)
        actions = QHBoxLayout()
        self.edit_btn, self.done_btn, self.del_btn = QPushButton("Edit"), QPushButton("Mark Done"), QPushButton("Delete")
        for b in [self.edit_btn, self.done_btn, self.del_btn]: actions.addWidget(b)
        layout.addLayout(actions)
        add_btn.clicked.connect(self.add_item); self.edit_btn.clicked.connect(self.edit_item)
        self.done_btn.clicked.connect(self.done_item); self.del_btn.clicked.connect(self.delete_item)
        self.search.textChanged.connect(self.load); self.status.currentTextChanged.connect(self.load); self.priority.currentTextChanged.connect(self.load)
        self.rows = []
        self.load()

    def selected_id(self):
        r = self.table.currentRow()
        return self.rows[r]["id"] if r >= 0 else None

    def load(self):
        self.rows = self.db.get_pendings(self.status.currentText(), self.priority.currentText(), self.search.text().strip())
        self.table.setRowCount(len(self.rows))
        for i, row in enumerate(self.rows):
            for j, k in enumerate(["title", "description", "due_date", "priority", "status", "category", "created_at", "updated_at"]):
                item = QTableWidgetItem(str(row[k] or ""))
                if k == "status" and row[k] == "Done": item.setForeground(Qt.darkGreen)
                if k == "due_date" and row[k] and row["status"] != "Done" and row[k] < QDate.currentDate().toString("yyyy-MM-dd"):
                    item.setForeground(Qt.red)
                self.table.setItem(i, j, item)

    def add_item(self):
        d = PendingDialog(self)
        if d.exec():
            values = d.values()
            if not values["title"]: return QMessageBox.warning(self, "Validation", "Title cannot be empty")
            self.db.add_pending(values); self.load(); self.refresh_cb()

    def edit_item(self):
        sid = self.selected_id();
        if not sid: return
        row = next(r for r in self.rows if r["id"] == sid)
        d = PendingDialog(self, row)
        if d.exec():
            values = d.values()
            if not values["title"]: return QMessageBox.warning(self, "Validation", "Title cannot be empty")
            self.db.update_pending(sid, values); self.load(); self.refresh_cb()

    def done_item(self):
        sid = self.selected_id();
        if sid:
            row = next(r for r in self.rows if r["id"] == sid)
            row = dict(row); row["status"] = "Done"
            self.db.update_pending(sid, row); self.load(); self.refresh_cb()

    def delete_item(self):
        sid = self.selected_id();
        if sid and QMessageBox.question(self, "Confirm", "Delete selected pending?") == QMessageBox.Yes:
            self.db.delete_pending(sid); self.load(); self.refresh_cb()
