from PySide6.QtWidgets import QWidget, QPushButton, QHBoxLayout
from models.settings import Settings


class ModeBar(QWidget):
    def __init__(self, on_change):
        super().__init__()
        self.on_change = on_change
        self.setFixedHeight(40)

        self.setStyleSheet("""
            QWidget { background: rgba(30,30,30,220); border-radius: 6px; }
            QPushButton { color: white; background: transparent; border: none; padding: 6px 12px; }
            QPushButton:hover { background: rgba(255,255,255,40); }
            QPushButton:checked { background: rgba(255,80,80,180); }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)

        self.buttons = []
        for text, value in [
            ("FREE", Settings.MODE_FREE),
            ("16:9", Settings.RATIO_16_9),
            ("9:16", Settings.RATIO_9_16),
            ("1:1",  Settings.RATIO_1_1),
        ]:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.clicked.connect(lambda _, v=value: self.select(v))
            layout.addWidget(btn)
            self.buttons.append(btn)

        self.buttons[0].setChecked(True)

    def select(self, value):
        for b in self.buttons:
            b.setChecked(False)
        self.sender().setChecked(True)
        self.on_change(value)
