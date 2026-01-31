from PySide6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QButtonGroup, QFrame
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

        self.setFixedHeight(60)
        self.setMinimumWidth(500)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setAutoFillBackground(True)

        self._dragging = False
        self._drag_offset = None
        self.setCursor(Qt.OpenHandCursor)

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
        self.group.idClicked.connect(self._on_mode_clicked)

        self.id_to_value = {}

        modes = [
            # id, text, value
            (0, "FREE",      Settings.MODE_FREE),
            (1, "16:9",      Settings.RATIO_16_9),
            (2, "9:16",      Settings.RATIO_9_16),
            (3, "1:1",       Settings.RATIO_1_1),

            ("sep", None, None),

            (4, "1 Screen",  Settings.CAPTURE_ONE_SCREEN),
            (5, "All Screen",Settings.CAPTURE_ALL_SCREEN),
        ]

        for item in modes:
            if item[0] == "sep":
                sep = QFrame()
                sep.setFrameShape(QFrame.VLine)
                sep.setStyleSheet("color: rgba(255,255,255,60);")
                layout.addWidget(sep)
                continue

            id_, text, value = item
            btn = QPushButton(text)
            btn.setCheckable(True)
            layout.addWidget(btn)

            self.group.addButton(btn, id_)
            self.id_to_value[id_] = value

        # default = FREE
        self.group.button(0).setChecked(True)

        layout.addStretch()

        settings_btn = QPushButton("⚙")
        settings_btn.setToolTip("Settings")
        settings_btn.clicked.connect(self.open_settings)
        layout.addWidget(settings_btn)

        layout.addSpacing(12)

        self.btn_close = QPushButton("✕")
        self.btn_close.setFixedSize(28, 28)
        self.btn_close.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 30);
                color: white;
                font-size: 14px;
                font-weight: 600;
                border-radius: 14px;
            }
            QPushButton:hover { background-color: rgb(232, 17, 35); }
            QPushButton:pressed { background-color: rgb(200, 15, 30); }
        """)
        self.btn_close.setToolTip("Close app")
        self.btn_close.clicked.connect(self.closeRequested.emit)
        self.btn_close.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.btn_close)

    def _on_mode_clicked(self, id_: int):
        value = self.id_to_value[id_]

        self.settings.capture_scope = None

        if value in (
            Settings.CAPTURE_ONE_SCREEN,
            Settings.CAPTURE_ALL_SCREEN
        ):
            self.settings.capture_scope = value
            self.on_change(value)
            return

        # FREE / RATIO
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

    def mousePressEvent(self, event):
        child = self.childAt(event.position().toPoint())
        if isinstance(child, QPushButton):
            return

        if event.button() == Qt.LeftButton:
            self._dragging = True
            self._drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.setCursor(Qt.ClosedHandCursor)
            event.accept()

    def mouseMoveEvent(self, event):
        if self._dragging and self._drag_offset:
            new_pos = event.globalPosition().toPoint() - self._drag_offset
            parent = self.parentWidget()
            if parent:
                max_x = parent.width() - self.width()
                max_y = parent.height() - self.height()
                new_pos.setX(max(0, min(new_pos.x(), max_x)))
                new_pos.setY(max(0, min(new_pos.y(), max_y)))
            self.move(new_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._dragging = False
            self._drag_offset = None
            self.setCursor(Qt.OpenHandCursor)
            event.accept()
