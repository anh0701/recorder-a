from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPainter, QPen, QColor

BORDER = 2   
SAFE   = 1  


class RecordingRootWindow(QWidget):
    def __init__(self, rect: QRect, draw_border: bool = True):
        super().__init__()
        self.draw_border = draw_border

        self.setGeometry(
            rect.x() - BORDER - SAFE,
            rect.y() - BORDER - SAFE,
            rect.width() + 2 * (BORDER + SAFE),
            rect.height() + 2 * (BORDER + SAFE),
        )

        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.WindowTransparentForInput
        )
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.show()

    def paintEvent(self, _):
        if not self.draw_border:
            return
        p = QPainter(self)

        pen = QPen(QColor(255, 80, 80))
        pen.setWidth(BORDER)
        p.setPen(pen)

        p.drawRect(
            BORDER,
            BORDER,
            self.width() - 2 * BORDER,
            self.height() - 2 * BORDER
        )
