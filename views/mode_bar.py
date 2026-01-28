from PySide6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QButtonGroup
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

        self.group = QButtonGroup(self)
        self.group.setExclusive(True)
        self.group.idClicked.connect(self._on_clicked)

        self.id_to_value = {}

        modes = [
            (0, "FREE", Settings.MODE_FREE),
            (1, "16:9", Settings.RATIO_16_9),
            (2, "9:16", Settings.RATIO_9_16),
            (3, "1:1",  Settings.RATIO_1_1),
        ]

        for id_, text, value in modes:
            btn = QPushButton(text)
            btn.setCheckable(True)
            layout.addWidget(btn)

            self.group.addButton(btn, id_)
            self.id_to_value[id_] = value

        self.group.button(0).setChecked(True)

    def _on_clicked(self, id_: int):
        value = self.id_to_value[id_]
        self.on_change(value)
