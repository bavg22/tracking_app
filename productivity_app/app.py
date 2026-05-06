import sys
from PySide6.QtWidgets import QApplication

from database import Database
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet('''
        QWidget { font-family: "Segoe UI"; font-size: 13px; background: #f8fafc; color: #0f172a; }
        QFrame#card { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 8px; }
        QPushButton { background: #e2e8f0; border: none; border-radius: 8px; padding: 8px 12px; }
        QPushButton:hover { background: #cbd5e1; }
        QLineEdit, QTextEdit, QComboBox, QDateEdit, QListWidget, QTableWidget, QCalendarWidget { background: #ffffff; border: 1px solid #cbd5e1; border-radius: 8px; }
    ''')
    db = Database()
    w = MainWindow(db)
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
