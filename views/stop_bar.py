from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QLabel,
    QHBoxLayout,
)
from PySide6.QtCore import (
    Qt,
    QTimer,
    QPoint,
    Signal,
)
from PySide6.QtGui import (
    QEnterEvent,
    QPainter,
    QPen,
    QBrush,
)


class StopBarWindow(QWidget):

    pauseRequested = Signal()
    resumeRequested = Signal()

    def __init__(
        self,
        x,
        y,
        on_stop,
    ):
        super().__init__()

        self.on_stop = on_stop

        self.paused = False

        self.elapsed_seconds = 0

        self.dragging = False

        self.drag_start = QPoint()
        self.window_start = QPoint()

        self.idle_timeout = 3000

        # Mode
        # False = full
        # True = compact
        self.compact_mode = False

        # Window

        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
        )

        self.setAttribute(
            Qt.WA_TranslucentBackground
        )

        self.setMouseTracking(True)


        self.setStyleSheet("""
            QLabel {
                color: white;
                font-weight: bold;
            }

            QLabel#recLabel {
                color: rgb(255, 75, 75);
            }

            QPushButton {
                background: rgba(255, 255, 255, 25);
                color: white;
                border: 1px solid rgba(255, 255, 255, 70);
                padding: 5px 9px;
                border-radius: 6px;
            }

            QPushButton:hover {
                background: rgba(255, 255, 255, 55);
                border: 1px solid rgba(255, 255, 255, 130);
            }

            QPushButton#stopButton {
                background: rgb(220, 55, 55);
                color: white;
                border: 1px solid rgb(255, 110, 110);
            }

            QPushButton#stopButton:hover {
                background: rgb(240, 70, 70);
            }
        """)

        self.setObjectName(
            "StopBar"
        )

        # Layout

        self.layout = QHBoxLayout(
            self
        )

        self.layout.setContentsMargins(
            10,
            6,
            10,
            6,
        )

        self.layout.setSpacing(6)

        # REC label

        self.rec_label = QLabel(
            "● REC"
        )

        self.rec_label.setObjectName(
            "recLabel"
        )

        self.layout.addWidget(
            self.rec_label
        )

        # Timer

        self.timer_label = QLabel(
            "00:00:00"
        )

        self.layout.addWidget(
            self.timer_label
        )

        # Pause button

        self.pause_button = QPushButton(
            "⏸"
        )

        self.pause_button.setFixedWidth(
            34
        )

        self.pause_button.clicked.connect(
            self.toggle_pause
        )

        self.layout.addWidget(
            self.pause_button
        )

        # Stop button

        self.stop_button = QPushButton(
            "STOP"
        )

        self.stop_button.setObjectName(
            "stopButton"
        )

        self.stop_button.clicked.connect(
            self.on_stop
        )

        self.layout.addWidget(
            self.stop_button
        )

        # Recording timer

        self.record_timer = QTimer(
            self
        )

        self.record_timer.setInterval(
            1000
        )

        self.record_timer.timeout.connect(
            self.update_timer
        )

        self.record_timer.start()

        # Idle timer

        self.idle_timer = QTimer(
            self
        )

        self.idle_timer.setSingleShot(
            True
        )

        self.idle_timer.setInterval(
            self.idle_timeout
        )

        self.idle_timer.timeout.connect(
            self.enter_compact_mode
        )

        # Start counting idle time
        self.restart_idle_timer()

        # Position

        self.move(x, y)

        self.show()

    def paintEvent(self, event):

        painter = QPainter(
            self
        )

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        # Leave a little space for the border
        rect = self.rect().adjusted(
            1,
            1,
            -1,
            -1,
        )

        if self.compact_mode:

            painter.setBrush(
                QBrush(
                    Qt.black
                )
            )

            painter.setPen(
                QPen(
                    Qt.white,
                    1
                )
            )

            radius = 8

        else:

            painter.setBrush(
                QBrush(
                    Qt.black
                )
            )

            painter.setPen(
                QPen(
                    Qt.white,
                    2
                )
            )

            radius = 10

        painter.drawRoundedRect(
            rect,
            radius,
            radius,
        )

        painter.end()


    def update_timer(self):

        if self.paused:
            return

        self.elapsed_seconds += 1

        hours = (
            self.elapsed_seconds // 3600
        )

        minutes = (
            (self.elapsed_seconds % 3600)
            // 60
        )

        seconds = (
            self.elapsed_seconds % 60
        )

        self.timer_label.setText(
            f"{hours:02d}:"
            f"{minutes:02d}:"
            f"{seconds:02d}"
        )


    def toggle_pause(self):

        self.show_full_mode()

        if self.paused:
            self.resume()

        else:
            self.pause()

    def pause(self):

        if self.paused:
            return

        self.paused = True

        self.rec_label.setText(
            "⏸ PAUSED"
        )

        self.pause_button.setText(
            "▶"
        )

        self.pauseRequested.emit()

        self.restart_idle_timer()

    def resume(self):

        if not self.paused:
            return

        self.paused = False

        self.rec_label.setText(
            "● REC"
        )

        self.pause_button.setText(
            "⏸"
        )

        self.resumeRequested.emit()

        self.restart_idle_timer()


    def enter_compact_mode(self):

        # Don't compact while dragging
        if self.dragging:
            self.restart_idle_timer()
            return

        # Don't compact while mouse is inside
        if self.underMouse():
            self.restart_idle_timer()
            return

        # Change mode

        self.compact_mode = True

        # Hide controls
        self.pause_button.hide()
        self.stop_button.hide()
        self.rec_label.hide()

        # Keep timer visible
        self.timer_label.show()

        # Compact text style
        self.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 200);
                font-weight: bold;
            }
        """)

        self.adjustSize()

        self.update()


    def show_full_mode(self):

        # Change mode

        self.compact_mode = False

        # Show controls

        self.pause_button.show()
        self.stop_button.show()
        self.rec_label.show()

        # Full text style

        self.setStyleSheet("""
            QLabel {
                color: white;
                font-weight: bold;
            }

            QLabel#recLabel {
                color: rgb(255, 70, 70);
            }

            QPushButton {
                background: rgba(255, 255, 255, 25);
                color: white;
                border: none;
                padding: 5px 9px;
                border-radius: 6px;
            }

            QPushButton:hover {
                background: rgba(255, 255, 255, 55);
                border: none;
            }

            QPushButton#stopButton {
                background: rgb(220, 55, 55);
                color: white;
                border: 1px solid rgb(255, 120, 120);
            }

            QPushButton#stopButton:hover {
                background: rgb(240, 70, 70);
            }
        """)

        self.adjustSize()

        self.update()


    def restart_idle_timer(self):

        self.show_full_mode()

        self.idle_timer.start()


    def enterEvent(self, event):

        self.show_full_mode()

        self.restart_idle_timer()

        super().enterEvent(event)


    def mousePressEvent(self, event):

        self.show_full_mode()
        self.restart_idle_timer()

        if event.button() != Qt.LeftButton:
            return

        # Don't drag when clicking buttons
        child = self.childAt(
            event.position().toPoint()
        )

        if isinstance(
            child,
            QPushButton
        ):
            return

        self.dragging = True

        self.drag_start = (
            event.globalPosition()
            .toPoint()
        )

        self.window_start = (self.pos())

        event.accept()


    def mouseMoveEvent(self, event):

        self.restart_idle_timer()

        if not self.dragging:
            return

        current = (
            event.globalPosition()
            .toPoint()
        )

        delta = (
            current
            - self.drag_start
        )

        self.move(
            self.window_start
            + delta
        )

        event.accept()


    def mouseReleaseEvent(self, event):

        if event.button() == Qt.LeftButton:

            self.dragging = False

            self.restart_idle_timer()

        event.accept()
        
    def closeEvent(self, event):

        self.record_timer.stop()
        self.idle_timer.stop()

        super().closeEvent(event)