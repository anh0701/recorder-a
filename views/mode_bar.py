from PySide6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QButtonGroup
from models.settings import Settings
from views.settings_window import SettingsWindow
from PySide6.QtCore import Qt, Signal

class ModeBar(QWidget):
    closeRequested = Signal()

    def __init__(self, on_change, settings):
        super().__init__()
        self.on_change = on_change
        self.settings_win = None
        self.settings = settings
        self.setFixedHeight(40)

        self.setStyleSheet("""
            QWidget { background: rgba(30,30,30,220); border-radius: 6px; }
            QPushButton { color: white; background: transparent; border: none; padding: 6px 12px; }
            QPushButton:hover { background: rgba(255,255,255,40); }
            QPushButton:checked { background: rgba(255,80,80,180); }
            QToolTip {
                background-color: rgba(30,30,30,220);
                color: white;
                border: 1px solid #555;
                padding: 4px 8px;
                border-radius: 4px;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(8)

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

        layout.addStretch()
        settings_btn = QPushButton("⚙")
        settings_btn.setToolTip("Settings")
        settings_btn.clicked.connect(self.open_settings)
        layout.addWidget(settings_btn)

        layout.addSpacing(12)
        self.btn_close = QPushButton("✕")
        self.btn_close.setFixedSize(30, 30)
        self.btn_close.setStyleSheet("""
            QPushButton {
                border: none;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(255, 0, 0, 180);
                border-radius: 4px;
            }
            """)
        self.btn_close.setToolTip("Close app")
        self.btn_close.clicked.connect(self.closeRequested.emit)
        self.btn_close.setCursor(Qt.PointingHandCursor)

        layout.addWidget(self.btn_close)

    def _on_clicked(self, id_: int):
        value = self.id_to_value[id_]
        self.on_change(value)
    
    def open_settings(self):
        overlay = self.parentWidget()   

        if self.settings_win is None:
            self.settings_win = SettingsWindow(self.settings, parent=overlay)

            pos = self.mapTo(overlay, self.rect().bottomLeft())
            self.settings_win.move(pos.x(), pos.y() + 6)

            self.settings_win.show()
            self.settings_win.raise_()
        else:
            self.settings_win.raise_()
            self.settings_win.show()



