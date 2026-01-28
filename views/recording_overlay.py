from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPainter, QPen, QColor


class RecordingOverlay(QWidget):
    def __init__(self, rect: QRect, on_stop):
        super().__init__()
        self.on_stop = on_stop
        self.rect_local = QRect(0, 0, rect.width(), rect.height())

        # ===== Window setup =====
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFocusPolicy(Qt.StrongFocus)

        self.setGeometry(rect)

        # ===== STOP BAR =====
        self.stop_bar = QWidget(self)
        self.stop_bar.setFixedSize(180, 50)
        self.stop_bar.move(10, 10)
        self.stop_bar.setStyleSheet("""
            QWidget {
                background: rgba(30,30,30,220);
                border-radius: 8px;
            }
            QLabel {
                color: red;
                font-weight: bold;
            }
            QPushButton {
                color: white;
                background: rgba(255,80,80,200);
                border: none;
                padding: 6px 12px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background: rgba(255,100,100,220);
            }
        """)

        layout = QHBoxLayout(self.stop_bar)
        layout.setContentsMargins(10, 6, 10, 6)

        label = QLabel("● REC")
        btn = QPushButton("STOP")
        btn.clicked.connect(self.on_stop)

        layout.addWidget(label)
        layout.addStretch()
        layout.addWidget(btn)

        self.show()
        self.raise_()
        self.activateWindow()
        self.setFocus()

    # ===== DRAW FRAME =====
    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen(QColor(255, 80, 80), 3)
        painter.setPen(pen)
        painter.drawRect(self.rect_local)

    # ===== KEY SHORTCUT =====
    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Escape, Qt.Key_Q):
            self.on_stop()
