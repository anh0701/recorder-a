from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QRect, QPoint
from PySide6.QtGui import QPainter, QPen, QColor
from models.settings import Settings
from views.mode_bar import ModeBar
from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import QRect


class Overlay(QWidget):
    def __init__(self, on_done, settings):
        super().__init__()
        self.on_done = on_done
        self.settings = settings
        self.start = QPoint()
        self.end = QPoint()
        self.dragging = False
        self.mode = Settings.MODE_FREE
        self.ratio = None

        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint | 
            Qt.Tool
        )
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.showFullScreen()

        self.mode_bar = ModeBar(self.set_mode, self.settings)
        self.mode_bar.setParent(self)
        self.mode_bar.move(20, 20)
        self.mode_bar.show()

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.dragging = True
            self.start = e.position().toPoint()
            self.end = self.start

    def mouseMoveEvent(self, e):
        if not self.dragging:
            return

        pos = e.position().toPoint()

        screen_rect = self.screen().geometry()
        pos.setX(max(screen_rect.left(), min(pos.x(), screen_rect.right())))
        pos.setY(max(screen_rect.top(),  min(pos.y(), screen_rect.bottom())))

        dx = pos.x() - self.start.x()
        dy = pos.y() - self.start.y()

        if self.mode != Settings.MODE_FREE:
            if abs(dx) > abs(dy):
                dy = int(abs(dx) / self.ratio) * (1 if dy >= 0 else -1)
            else:
                dx = int(abs(dy) * self.ratio) * (1 if dx >= 0 else -1)

            pos = QPoint(self.start.x() + dx, self.start.y() + dy)
            
            pos.setX(max(screen_rect.left(), min(pos.x(), screen_rect.right())))
            pos.setY(max(screen_rect.top(),  min(pos.y(), screen_rect.bottom())))

        self.end = pos
        self.update()

    def mouseReleaseEvent(self, e):
        if self.dragging:
            self.dragging = False
            rect = QRect(self.start, self.end).normalized()
            rect = self.clamp_rect_to_screen(rect)
            self.close()
            self.on_done(rect)

    def set_mode(self, value):
        if value == Settings.MODE_FREE:
            self.mode = Settings.MODE_FREE
            self.ratio = None
        else:
            self.mode = Settings.MODE_RATIO
            self.ratio = value

    def paintEvent(self, _):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(0, 0, 0, 120))
        if self.dragging:
            p.setPen(QPen(QColor(255, 80, 80), 2))
            p.drawRect(QRect(self.start, self.end).normalized())
    
    def clamp_rect_to_screen(self, rect: QRect) -> QRect:
        screen = QGuiApplication.primaryScreen()
        screen_rect = screen.geometry()

        x = max(rect.x(), screen_rect.x())
        y = max(rect.y(), screen_rect.y())

        w = min(rect.width(), screen_rect.right() - x + 1)
        h = min(rect.height(), screen_rect.bottom() - y + 1)

        return QRect(x, y, w, h)
