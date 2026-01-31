from PySide6.QtWidgets import QWidget, QLabel, QMessageBox, QApplication
from PySide6.QtCore import Qt, QRect, QPoint, QTimer
from PySide6.QtGui import QPainter, QPen, QColor
from models.settings import Settings, CaptureMode
from views.mode_bar import ModeBar
from PySide6.QtGui import QGuiApplication
import sys

class Overlay(QWidget):
    def __init__(self, on_done, settings):
        super().__init__()
        self.on_done = on_done
        self.settings = settings
        self.start = QPoint()
        self.end = QPoint()
        self.dragging = False
        self.mode = CaptureMode.FREE
        self.ratio = None
        self.min_size = 10

        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint | 
            Qt.Tool
        )
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.showFullScreen()

        self.mode_bar = ModeBar(self.set_mode, self.settings)
        self.mode_bar.closeRequested.connect(self.confirm_exit)
        self.mode_bar.setParent(self)
        self.mode_bar.move(20, 20)
        self.mode_bar.show()

        self.hint = QLabel("Click and drag to select the recording area", self)
        self.hint.setStyleSheet("""
            background-color: rgba(30, 30, 30, 220);
            color: white;
            border: 1px solid rgb(255, 80, 80);
            border-radius: 6px;
            padding: 6px 10px;
            font-size: 12px;
        """)
        self.hint.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.hint.hide()
    
    def confirm_exit(self):
        ret = QMessageBox.question(
            self,
            "Exit",
            "Do you want to exit the application?",
            QMessageBox.Yes | QMessageBox.No
        )
        if ret == QMessageBox.Yes:
            QApplication.quit()

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

        if self.mode != CaptureMode.FREE:
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
        if not self.dragging:
            return
        
        if self.dragging:
            self.dragging = False
            rect = QRect(self.start, self.end).normalized()
            rect = self.clamp_rect_to_screen(rect)

            if rect.width() < self.min_size or rect.height() < self.min_size:
                self.show_hint(e.position().toPoint())
                self.update()
                return
            
            self.close()
            self.on_done(rect)

    def set_mode(self, value: CaptureMode):
        if value == CaptureMode.FREE:
            self.mode = CaptureMode.FREE
            self.ratio = None

        elif value in (CaptureMode.ONE_SCREEN, CaptureMode.ALL_SCREEN):
            self.settings.capture_scope = value
            self.close()
            self.on_done(None)

        elif value == CaptureMode.RATIO_16_9:
            self.mode = value
            self.ratio = 16 / 9

        elif value == CaptureMode.RATIO_9_16:
            self.mode = value
            self.ratio = 9 / 16

        elif value == CaptureMode.RATIO_1_1:
            self.mode = value
            self.ratio = 1.0
    
    def clamp_rect_to_screen(self, rect: QRect) -> QRect:
        screen = QGuiApplication.primaryScreen()
        screen_rect = screen.geometry()

        x = max(rect.x(), screen_rect.x())
        y = max(rect.y(), screen_rect.y())

        w = min(rect.width(), screen_rect.right() - x + 1)
        h = min(rect.height(), screen_rect.bottom() - y + 1)

        return QRect(x, y, w, h)

    def show_hint(self, pos: QPoint):
        self.hint.adjustSize()

        self.hint.move(pos + QPoint(12, 12))
        self.hint.show()
        self.hint.raise_()

        QTimer.singleShot(1500, self.hint.hide)

