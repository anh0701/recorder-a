from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QMessageBox,
    QApplication,
)
from PySide6.QtCore import (
    Qt,
    QRect,
    QPoint,
    QTimer,
)
from PySide6.QtGui import (
    QPainter,
    QPen,
    QColor,
    QGuiApplication,
)
from models.settings import Settings, CaptureMode
from views.mode_bar import ModeBar


class Overlay(QWidget):
    def __init__(self, on_done, settings: Settings):
        super().__init__()

        self.on_done = on_done
        self.settings = settings

        # Selection state

        self.start = QPoint()
        self.end = QPoint()

        self.dragging = False

        self.mode = CaptureMode.FREE
        self.ratio = None

        self.min_size = 10

        # Window

        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
        )

        self.setAttribute(
            Qt.WA_DeleteOnClose,
            True
        )

        self.setAttribute(
            Qt.WA_TranslucentBackground,
            True
        )

        self.showFullScreen()

        # Mode bar

        self.mode_bar = ModeBar(
            self.set_mode,
            self.settings
        )

        self.mode_bar.closeRequested.connect(
            self.confirm_exit
        )

        self.mode_bar.setParent(self)
        self.mode_bar.move(20, 20)
        self.mode_bar.show()

        # Initial hint

        self.hint = QLabel(
            "Click and drag to select the recording area",
            self
        )

        self.hint.setStyleSheet("""
            background-color: rgba(30, 30, 30, 220);
            color: white;
            border: 1px solid rgb(255, 80, 80);
            border-radius: 6px;
            padding: 6px 10px;
            font-size: 12px;
        """)

        self.hint.setAttribute(
            Qt.WA_TransparentForMouseEvents
        )

        self.hint.hide()

        # Size label

        self.size_label = QLabel(self)

        self.size_label.setStyleSheet("""
            background-color: rgba(30, 30, 30, 220);
            color: white;
            border-radius: 5px;
            padding: 4px 8px;
            font-size: 12px;
        """)

        self.size_label.setAttribute(
            Qt.WA_TransparentForMouseEvents
        )

        self.size_label.hide()

    # Exit

    def confirm_exit(self):
        ret = QMessageBox.question(
            self,
            "Exit",
            "Do you want to exit the application?",
            QMessageBox.Yes | QMessageBox.No
        )

        if ret == QMessageBox.Yes:
            QApplication.quit()

    # Mouse events

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton:
            return

        # Hide previous hint
        self.hint.hide()

        self.dragging = True

        self.start = event.position().toPoint()
        self.end = self.start

        self.size_label.hide()

        self.update()

    def mouseMoveEvent(self, event):
        if not self.dragging:
            return

        pos = event.position().toPoint()

        screen_rect = self.get_screen_rect()

        # Keep cursor inside current screen
        pos.setX(
            max(
                screen_rect.left(),
                min(pos.x(), screen_rect.right())
            )
        )

        pos.setY(
            max(
                screen_rect.top(),
                min(pos.y(), screen_rect.bottom())
            )
        )

        # Free selection

        if self.mode == CaptureMode.FREE:
            self.end = pos

        # Fixed aspect ratio

        else:
            self.end = self.calculate_ratio_endpoint(
                pos,
                screen_rect
            )

        # Repaint immediately
        self.update()

        # Update size indicator
        self.update_size_label()

    def mouseReleaseEvent(self, event):
        if event.button() != Qt.LeftButton:
            return

        if not self.dragging:
            return

        self.dragging = False

        rect = QRect(
            self.start,
            self.end
        ).normalized()

        rect = self.clamp_rect_to_screen(rect)

        # Hide realtime size label
        self.size_label.hide()

        # Invalid selection

        if (
            rect.width() < self.min_size
            or rect.height() < self.min_size
        ):
            self.show_hint(
                event.position().toPoint()
            )

            self.update()

            return

        # Valid selection

        self.close()

        self.on_done(rect)

    # Aspect ratio

    def calculate_ratio_endpoint(
        self,
        pos: QPoint,
        screen_rect: QRect
    ) -> QPoint:

        dx = pos.x() - self.start.x()
        dy = pos.y() - self.start.y()

        if dx == 0 and dy == 0:
            return self.start

        ratio = self.ratio

        if ratio is None or ratio <= 0:
            return pos

        abs_dx = abs(dx)
        abs_dy = abs(dy)

        # Determine which dimension controls the size.

        if abs_dx / max(abs_dy, 1) > ratio:
            # Width is controlling dimension
            width = abs_dx
            height = int(width / ratio)
        else:
            # Height is controlling dimension
            height = abs_dy
            width = int(height * ratio)

        # Preserve drag direction
        direction_x = 1 if dx >= 0 else -1
        direction_y = 1 if dy >= 0 else -1

        width = max(width, self.min_size)
        height = max(height, self.min_size)

        # Limit size based on available space

        max_width = self.get_max_width(
            direction_x,
            screen_rect
        )

        max_height = self.get_max_height(
            direction_y,
            screen_rect
        )

        # We need to respect both width and height limits.
        max_width_by_height = int(
            max_height * ratio
        )

        max_height_by_width = int(
            max_width / ratio
        )

        max_allowed_width = min(
            max_width,
            max_width_by_height
        )

        max_allowed_height = min(
            max_height,
            max_height_by_width
        )

        if width > max_allowed_width:
            width = max_allowed_width
            height = int(width / ratio)

        if height > max_allowed_height:
            height = max_allowed_height
            width = int(height * ratio)

        width = max(width, 1)
        height = max(height, 1)

        # Calculate final endpoint

        end_x = (
            self.start.x()
            + direction_x * width
        )

        end_y = (
            self.start.y()
            + direction_y * height
        )

        return QPoint(
            end_x,
            end_y
        )

    # Maximum available size

    def get_max_width(
        self,
        direction: int,
        screen_rect: QRect
    ) -> int:

        if direction >= 0:
            return (
                screen_rect.right()
                - self.start.x()
                + 1
            )

        return (
            self.start.x()
            - screen_rect.left()
            + 1
        )

    def get_max_height(
        self,
        direction: int,
        screen_rect: QRect
    ) -> int:

        if direction >= 0:
            return (
                screen_rect.bottom()
                - self.start.y()
                + 1
            )

        return (
            self.start.y()
            - screen_rect.top()
            + 1
        )

    # Painting

    def paintEvent(self, event):
        if not self.dragging:
            return

        rect = QRect(
            self.start,
            self.end
        ).normalized()

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        # 1. Dark overlay

        painter.fillRect(
            self.rect(),
            QColor(0, 0, 0, 120)
        )

        # 2. Clear selected area

        painter.setCompositionMode(
            QPainter.CompositionMode_Clear
        )

        painter.fillRect(
            rect,
            Qt.transparent
        )

        # 3. Draw border

        painter.setCompositionMode(
            QPainter.CompositionMode_SourceOver
        )

        pen = QPen(
            QColor(255, 80, 80)
        )

        pen.setWidth(2)

        painter.setPen(pen)

        painter.drawRect(rect)

        painter.end()

    # Size label

    def update_size_label(self):
        if not self.dragging:
            return

        rect = QRect(
            self.start,
            self.end
        ).normalized()

        if (
            rect.width() <= 0
            or rect.height() <= 0
        ):
            self.size_label.hide()
            return

        self.size_label.setText(
            f"{rect.width()} × {rect.height()}"
        )

        self.size_label.adjustSize()

        # Put label underneath the selection
        x = (
            rect.center().x()
            - self.size_label.width() // 2
        )

        y = rect.bottom() + 8

        # If there is not enough space underneath,
        # put it above the selection.
        if (
            y + self.size_label.height()
            > self.height()
        ):
            y = (
                rect.top()
                - self.size_label.height()
                - 8
            )

        # Keep label inside overlay
        x = max(
            5,
            min(
                x,
                self.width()
                - self.size_label.width()
                - 5
            )
        )

        y = max(
            5,
            min(
                y,
                self.height()
                - self.size_label.height()
                - 5
            )
        )

        self.size_label.move(
            x,
            y
        )

        self.size_label.show()
        self.size_label.raise_()

    # Mode

    def set_mode(self, value: CaptureMode):

        if value == CaptureMode.FREE:

            self.mode = CaptureMode.FREE
            self.ratio = None

            self.reset_selection()

        elif value == CaptureMode.ONE_SCREEN:

            self.settings.capture_scope = value

            self.close()

            self.on_done(None)

        elif value == CaptureMode.ALL_SCREEN:

            self.settings.capture_scope = value

            self.close()

            self.on_done(None)

        elif value == CaptureMode.RATIO_16_9:

            self.mode = value
            self.ratio = 16 / 9

            self.reset_selection()

        elif value == CaptureMode.RATIO_9_16:

            self.mode = value
            self.ratio = 9 / 16

            self.reset_selection()

        elif value == CaptureMode.RATIO_1_1:

            self.mode = value
            self.ratio = 1.0

            self.reset_selection()

    # Reset selection

    def reset_selection(self):
        self.dragging = False

        self.start = QPoint()
        self.end = QPoint()

        self.size_label.hide()
        self.hint.hide()

        self.update()

    # Screen helpers
    
    def get_screen_rect(self) -> QRect:

        screen = self.screen()

        if screen is None:
            screen = QGuiApplication.primaryScreen()

        if screen is None:
            return self.rect()

        return screen.geometry()

    def clamp_rect_to_screen(
        self,
        rect: QRect
    ) -> QRect:

        screen_rect = self.get_screen_rect()

        x = max(
            rect.x(),
            screen_rect.x()
        )

        y = max(
            rect.y(),
            screen_rect.y()
        )

        right = min(
            rect.right(),
            screen_rect.right()
        )

        bottom = min(
            rect.bottom(),
            screen_rect.bottom()
        )

        if right < x or bottom < y:
            return QRect()

        return QRect(
            x,
            y,
            right - x + 1,
            bottom - y + 1
        )

    # Invalid selection hint

    def show_hint(self, pos: QPoint):

        self.hint.adjustSize()

        x = pos.x() + 12
        y = pos.y() + 12

        # Keep hint inside window
        x = max(
            5,
            min(
                x,
                self.width()
                - self.hint.width()
                - 5
            )
        )

        y = max(
            5,
            min(
                y,
                self.height()
                - self.hint.height()
                - 5
            )
        )

        self.hint.move(
            x,
            y
        )

        self.hint.show()
        self.hint.raise_()

        QTimer.singleShot(
            1500,
            self.hint.hide
        )