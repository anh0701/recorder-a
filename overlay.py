from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QRect, QPoint
from PySide6.QtGui import QPainter, QPen, QColor
from settings import Settings


class Overlay(QWidget):
    def __init__(self, on_done):
        super().__init__()
        self.on_done = on_done

        self.start = QPoint()
        self.end = QPoint()
        self.dragging = False
        self.ratio = Settings.RATIO_FREE

        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setCursor(Qt.CrossCursor)
        self.showFullScreen()

    # ========= INPUT =========

    def mousePressEvent(self, event):
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

        if self.ratio is None:
            self.end = pos
        else:
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
        if event.button() == Qt.LeftButton:
            self.dragging = False
            rect = self.selection_rect()
            self.on_done(rect)
            self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

        elif event.key() == Qt.Key_F:
            self.ratio = Settings.RATIO_FREE
            print("Mode: FREE")

        elif event.key() == Qt.Key_1:
            self.ratio = Settings.RATIO_16_9
            print("Mode: 16:9")

        elif event.key() == Qt.Key_2:
            self.ratio = Settings.RATIO_9_16
            print("Mode: 9:16")

        elif event.key() == Qt.Key_3:
            self.ratio = Settings.RATIO_1_1
            print("Mode: 1:1")

    # ========= DRAW =========

    def selection_rect(self):
        return QRect(self.start, self.end).normalized()

    def paintEvent(self, event):
        painter = QPainter(self)

        # dark overlay
        painter.fillRect(self.rect(), QColor(0, 0, 0, 120))

        # selection box
        pen = QPen(QColor(255, 80, 80), 2)
        painter.setPen(pen)
        painter.drawRect(self.selection_rect())
