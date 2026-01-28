from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPainter, QPen, QColor


class RecordingRootWindow(QWidget):
    def __init__(self, rect: QRect):
        super().__init__()
        self.rect_local = QRect(0, 0, rect.width(), rect.height())

        self.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnTopHint |
            Qt.WindowTransparentForInput
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        # self.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        self.setGeometry(rect)
        self.show()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setPen(QPen(QColor(255, 80, 80), 3))
        p.drawRect(self.rect_local)
