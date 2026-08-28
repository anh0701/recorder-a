from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QHBoxLayout,
)
from PySide6.QtCore import Signal


class SelectionToolbar(QWidget):

    confirmed = Signal()
    cancelled = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setStyleSheet("""
            QWidget {
                background: rgba(30, 30, 30, 235);
                border: 1px solid rgba(255, 255, 255, 60);
                border-radius: 8px;
            }

            QPushButton {
                color: white;
                background: rgba(255, 255, 255, 25);
                border: 1px solid rgba(255, 255, 255, 70);
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
            }

            QPushButton:hover {
                background: rgba(255, 255, 255, 50);
            }

            QPushButton#confirmButton {
                background: rgb(220, 55, 55);
                border: 1px solid rgb(255, 100, 100);
                font-weight: bold;
            }

            QPushButton#confirmButton:hover {
                background: rgb(240, 70, 70);
            }
        """)

        layout = QHBoxLayout(self)

        layout.setContentsMargins(
            6,
            5,
            6,
            5,
        )

        layout.setSpacing(6)

        # Cancel

        self.cancel_button = QPushButton(
            "✕ Cancel"
        )

        self.cancel_button.clicked.connect(
            self.cancelled.emit
        )

        layout.addWidget(
            self.cancel_button
        )

        # Confirm

        self.confirm_button = QPushButton(
            "✓ Start Recording"
        )

        self.confirm_button.setObjectName(
            "confirmButton"
        )

        self.confirm_button.clicked.connect(
            self.confirmed.emit
        )

        layout.addWidget(
            self.confirm_button
        )

        self.adjustSize()

    def show_for_selection(
        self,
        selection,
        parent_size,
    ):

        self.adjustSize()

        x = (
            selection.center().x()
            - self.width() // 2
        )

        y = (
            selection.bottom()
            + 45
        )

        # If there isn't enough room below,
        # place toolbar above.

        if (
            y + self.height()
            > parent_size.height()
        ):

            y = (
                selection.top()
                - self.height()
                - 45
            )

        x = max(
            5,
            min(
                x,
                parent_size.width()
                - self.width()
                - 5,
            ),
        )

        y = max(
            5,
            min(
                y,
                parent_size.height()
                - self.height()
                - 5,
            ),
        )

        self.move(
            x,
            y,
        )

        self.show()
        self.raise_()

    def hide_for_selection(self):

        self.hide()