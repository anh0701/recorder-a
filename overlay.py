from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QRect, QPoint
from PySide6.QtGui import QPainter, QPen, QColor, QFont

from settings import Settings
from mode_bar import ModeBar


class Overlay(QWidget):
    def __init__(self, on_done):
        super().__init__()
        self.on_done = on_done

        # ===== Selection state =====
        self.start = QPoint()
        self.end = QPoint()
        self.dragging = False

        # ===== Mode state =====
        self.mode = Settings.MODE_FREE
        self.ratio = None

        # ===== Window setup =====
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setCursor(Qt.CrossCursor)
        self.setFocusPolicy(Qt.StrongFocus)

        # ===== Show & focus =====
        self.showFullScreen()
        self.raise_()
        self.activateWindow()
        self.setFocus()

        # ===== Mode Bar UI =====
        self.mode_bar = ModeBar(self.set_mode)
        self.mode_bar.setParent(self)
        self.mode_bar.move(20, 20)
        self.mode_bar.show()

    # ================= INPUT =================

    def mousePressEvent(self, event):
        if self.mode_bar.geometry().contains(event.position().toPoint()):
            return

        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.start = event.position().toPoint()
            self.end = self.start
            self.update()

    def mouseMoveEvent(self, event):
        if not self.dragging:
            return

        pos = event.position().toPoint()
        dx = pos.x() - self.start.x()
        dy = pos.y() - self.start.y()

        if self.mode == Settings.MODE_FREE:
            self.end = pos
        else:
            # MODE_RATIO
            if abs(dx) > abs(dy):
                dy = int(abs(dx) / self.ratio) * (1 if dy >= 0 else -1)
            else:
                dx = int(abs(dy) * self.ratio) * (1 if dx >= 0 else -1)

            self.end = QPoint(
                self.start.x() + dx,
                self.start.y() + dy
            )

        self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.dragging:
            self.dragging = False
            rect = self.selection_rect()

            self.hide()
            self.on_done(rect)
            self.deleteLater()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            # Cancel selection
            self.dragging = False
            self.hide()
            self.deleteLater()

    # ================= MODE =================

    def set_mode(self, value):
        if value == Settings.MODE_FREE:
            self.mode = Settings.MODE_FREE
            self.ratio = None
        else:
            self.mode = Settings.MODE_RATIO
            self.ratio = value

        self.update()

    # ================= DRAW =================

    def selection_rect(self):
        return QRect(self.start, self.end).normalized()

    def paintEvent(self, event):
        painter = QPainter(self)

        # Dark overlay
        painter.fillRect(self.rect(), QColor(0, 0, 0, 120))

        # Selection rectangle
        if self.dragging:
            pen = QPen(QColor(255, 80, 80), 2)
            painter.setPen(pen)
            painter.drawRect(self.selection_rect())

        # Text
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Arial", 12))

        painter.drawText(20, self.height() - 20, self.get_mode_text())

        if self.dragging:
            painter.drawText(
                self.end.x() + 10,
                self.end.y() - 10,
                self.get_size_text()
            )

    def get_mode_text(self):
        if self.mode == Settings.MODE_FREE:
            return "MODE: FREE"
        return f"MODE: RATIO {self.ratio:.2f}"

    def get_size_text(self):
        r = self.selection_rect()
        return f"{r.width()} x {r.height()}"
