from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QListWidget,
    QListWidgetItem, QMessageBox, QDialog, QFormLayout, QDateEdit
)
from PySide6.QtCore import QDate


class TodoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New To-Do")
        form = QFormLayout(self)
        self.task = QLineEdit()
        self.category = QLineEdit()
        self.due = QDateEdit()
        self.due.setCalendarPopup(True)
        self.due.setDisplayFormat("yyyy-MM-dd")
        self.due.setDate(QDate.currentDate())
        self.no_due = QPushButton("No due date")
        self.no_due.clicked.connect(lambda: self.due.setDate(QDate()))
        save = QPushButton("Save")
        save.clicked.connect(self.accept)
        form.addRow("Task", self.task)
        form.addRow("Category", self.category)
        form.addRow("Due date", self.due)
        form.addRow(self.no_due)
        form.addRow(save)

    def values(self):
        due = self.due.date().toString("yyyy-MM-dd") if self.due.date().isValid() else None
        return {"task_text": self.task.text().strip(), "category": self.category.text().strip(), "due_date": due}


class TodoView(QWidget):
    def __init__(self, db, refresh_cb):
        super().__init__(); self.db = db; self.refresh_cb = refresh_cb
        l = QVBoxLayout(self)
        top = QHBoxLayout(); self.input = QLineEdit(); self.input.setPlaceholderText("Quick task")
        self.add_btn = QPushButton("Add Quick")
        self.add_detail_btn = QPushButton("Add Detailed")
        top.addWidget(self.input); top.addWidget(self.add_btn); top.addWidget(self.add_detail_btn)
        l.addLayout(top)
        self.list = QListWidget(); self.list.setDragDropMode(QListWidget.InternalMove)
        l.addWidget(self.list)
        actions = QHBoxLayout(); self.del_btn = QPushButton("Delete Selected"); self.clear_btn = QPushButton("Clear Completed")
        actions.addWidget(self.del_btn); actions.addWidget(self.clear_btn); l.addLayout(actions)
        self.add_btn.clicked.connect(self.add_todo); self.add_detail_btn.clicked.connect(self.add_detailed_todo)
        self.del_btn.clicked.connect(self.delete_selected); self.clear_btn.clicked.connect(self.clear_done)
        self.list.itemChanged.connect(self.toggle_done)
        self.list.model().rowsMoved.connect(self.save_order)
        self.load()

    def load(self):
        self.list.blockSignals(True); self.list.clear()
        for t in self.db.get_todos():
            suffix = []
            if t["category"]: suffix.append(f"#{t['category']}")
            if t["due_date"]: suffix.append(t["due_date"])
            text = t["task_text"] + (f"   ({' | '.join(suffix)})" if suffix else "")
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, t["id"])
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsEditable | Qt.ItemIsDragEnabled)
            item.setCheckState(Qt.Checked if t["is_done"] else Qt.Unchecked)
            self.list.addItem(item)
        self.list.blockSignals(False)

    def add_todo(self):
        text = self.input.text().strip()
        if not text: return QMessageBox.warning(self, "Validation", "Task text cannot be empty")
        self.db.add_todo({"task_text": text, "due_date": None, "category": ""}); self.input.clear(); self.load(); self.refresh_cb()

    def add_detailed_todo(self):
        d = TodoDialog(self)
        if d.exec():
            values = d.values()
            if not values["task_text"]: return QMessageBox.warning(self, "Validation", "Task text cannot be empty")
            self.db.add_todo(values); self.load(); self.refresh_cb()

    def toggle_done(self, item):
        self.db.update_todo_status(item.data(Qt.UserRole), item.checkState() == Qt.Checked); self.refresh_cb()

    def delete_selected(self):
        item = self.list.currentItem()
        if item and QMessageBox.question(self, "Confirm", "Delete selected to-do?") == QMessageBox.Yes:
            self.db.delete_todo(item.data(Qt.UserRole)); self.load(); self.refresh_cb()

    def clear_done(self):
        self.db.clear_completed_todos(); self.load(); self.refresh_cb()

    def save_order(self):
        ids = [self.list.item(i).data(Qt.UserRole) for i in range(self.list.count())]
        self.db.update_todo_order(ids)
