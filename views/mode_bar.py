from PySide6.QtWidgets import QWidget, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt
from models.settings import Settings


class ModeBar(QWidget):
    def __init__(self, on_change):
        super().__init__()
        self.on_change = on_change

        self.setFixedHeight(40)
        self.setStyleSheet("""
            QWidget {
                background: rgba(30, 30, 30, 200);
                border-radius: 6px;
            }
            QPushButton {
                color: white;
                background: transparent;
                border: none;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background: rgba(255,255,255,40);
            }
            QPushButton:checked {
                background: rgba(255,80,80,180);
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(4)

        self.btn_free = self._btn("FREE", Settings.MODE_FREE)
        self.btn_169 = self._btn("16:9", Settings.RATIO_16_9)
        self.btn_916 = self._btn("9:16", Settings.RATIO_9_16)
        self.btn_11  = self._btn("1:1",  Settings.RATIO_1_1)

        for b in (self.btn_free, self.btn_169, self.btn_916, self.btn_11):
            layout.addWidget(b)

        self.btn_free.setChecked(True)

    def _btn(self, text, value):
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.clicked.connect(lambda: self.select(value))
        return btn

    def select(self, value):
        for b in self.findChildren(QPushButton):
            b.setChecked(False)

        sender = self.sender()
        sender.setChecked(True)

        self.on_change(value)
