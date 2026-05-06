from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class SettingsView(QWidget):
    def __init__(self):
        super().__init__()
        l = QVBoxLayout(self)
        l.addWidget(QLabel("Settings (MVP placeholder)\n- Local SQLite storage\n- Light theme active"))
