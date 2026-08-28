from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QMessageBox,
    QApplication,
)
from PySide6.QtCore import (
    Qt,
    QPoint,
    QTimer,
    QRect,
)
from PySide6.QtGui import (
    QPainter,
    QPen,
    QColor,
    QGuiApplication,
)

from models.settings import Settings, CaptureMode
from views.mode_bar import ModeBar
from views.selection import SelectionController
from views.selection_toolbar import SelectionToolbar


class Overlay(QWidget):

    HANDLE_SIZE = 10

    def __init__(self, on_done, settings: Settings):
        super().__init__()

        self.on_done = on_done
        self.settings = settings

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

        self.setMouseTracking(True)

        self.showFullScreen()

        # Selection controller

        self.selection_controller = (
            SelectionController(
                self.get_screen_rect(),
                min_size=20,
            )
        )

        self.mode = CaptureMode.FREE
        self.ratio = None

        # Creating a new selection
        self.creating = False


        self.mode_bar = ModeBar(
            self.set_mode,
            self.settings,
        )

        self.mode_bar.closeRequested.connect(
            self.confirm_exit
        )

        self.mode_bar.setParent(self)
        self.mode_bar.move(20, 20)
        self.mode_bar.show()


        self.hint = QLabel(
            "Click and drag to select the recording area",
            self,
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


        self.size_label = QLabel(
            self,
        )

        self.size_label.setStyleSheet("""
            background-color: rgba(30, 30, 30, 230);
            color: white;
            border-radius: 5px;
            padding: 4px 8px;
            font-size: 12px;
            font-weight: bold;
        """)

        self.size_label.setAttribute(
            Qt.WA_TransparentForMouseEvents
        )

        self.size_label.hide()


        self.selection_toolbar = (
            SelectionToolbar(self)
        )

        self.selection_toolbar.confirmed.connect(
            self.confirm_selection
        )

        self.selection_toolbar.cancelled.connect(
            self.cancel_selection
        )

        self.selection_toolbar.hide()

        self.setCursor(
            Qt.CrossCursor
        )


    def confirm_exit(self):

        ret = QMessageBox.question(
            self,
            "Exit",
            "Do you want to exit the application?",
            QMessageBox.Yes
            | QMessageBox.No,
        )

        if ret == QMessageBox.Yes:
            QApplication.quit()


    def mousePressEvent(self, event):

        if event.button() != Qt.LeftButton:
            return

        pos = event.position().toPoint()

        controller = self.selection_controller

        # Existing selection

        if controller.is_valid():

            # Try resize handle first
            handle = controller.get_handle_at(
                pos
            )

            if handle:

                controller.start_resize(
                    handle,
                    pos,
                )

                self.creating = False

                self.size_label.show()

                self.setCursor(
                    self.cursor_for_handle(
                        handle
                    )
                )

                event.accept()
                return

            # Try moving selection
            if controller.start_move(pos):

                self.creating = False

                self.setCursor(
                    Qt.ClosedHandCursor
                )

                event.accept()
                return

            # Clicked outside existing selection.
            # Start a new selection.

            controller.reset()

            self.selection_toolbar.hide_for_selection()
            self.size_label.hide()

        # Start creating selection

        self.hint.hide()

        self.creating = True

        self.create_start = pos

        controller.reset()

        self.selection_toolbar.hide_for_selection()

        self.update()

        event.accept()


    def mouseMoveEvent(self, event):

        pos = event.position().toPoint()

        controller = self.selection_controller

        # Not dragging

        if not self.creating and controller.action is None:

            if controller.is_valid():

                handle = controller.get_handle_at(
                    pos
                )

                if handle:

                    self.setCursor(
                        self.cursor_for_handle(
                            handle
                        )
                    )

                elif controller.selection.contains(pos):

                    self.setCursor(
                        Qt.OpenHandCursor
                    )

                else:

                    self.setCursor(
                        Qt.CrossCursor
                    )

            else:

                self.setCursor(
                    Qt.CrossCursor
                )

            return

        # Creating

        if self.creating:

            controller.create(
                self.create_start,
                pos,
            )

        # Moving

        elif controller.action == "move":

            controller.move(
                pos
            )

        # Resizing

        else:

            controller.resize(
                pos
            )

        self.update_size_label()

        self.update()

        event.accept()


    def mouseReleaseEvent(self, event):

        if event.button() != Qt.LeftButton:
            return

        controller = self.selection_controller

        # Finish creating
        self.creating = False

        # Finish move / resize
        controller.finish_action()

        # Invalid selection

        if not controller.is_valid():

            controller.reset()

            self.size_label.hide()

            self.selection_toolbar.hide_for_selection()

            self.show_hint(
                event.position().toPoint()
            )

            self.setCursor(
                Qt.CrossCursor
            )

            self.update()

            return

        # Valid selection
        # DO NOT start recording here.

        self.update_size_label()

        self.show_selection_toolbar()

        self.setCursor(
            Qt.OpenHandCursor
        )

        self.update()

        event.accept()


    def confirm_selection(self):

        controller = self.selection_controller

        if not controller.is_valid():
            return

        rect = controller.clamp_rect_to_screen(
            controller.selection
        )

        if (
            rect.width() < controller.min_size
            or rect.height() < controller.min_size
        ):
            return

        # Only now close overlay and start recording.

        self.close()

        self.on_done(
            rect
        )


    def cancel_selection(self):

        self.selection_controller.reset()

        self.creating = False

        self.size_label.hide()

        self.selection_toolbar.hide_for_selection()

        self.setCursor(
            Qt.CrossCursor
        )

        self.update()


    def show_selection_toolbar(self):

        controller = self.selection_controller

        if not controller.is_valid():
            return

        self.selection_toolbar.show_for_selection(
            controller.selection,
            self.size(),
        )

    def update_size_label(self):

        controller = self.selection_controller

        if not controller.is_valid():
            self.size_label.hide()
            return

        rect = controller.selection

        self.size_label.setText(
            f"{rect.width()} × {rect.height()}"
        )

        self.size_label.adjustSize()

        x = (
            rect.center().x()
            - self.size_label.width() // 2
        )

        y = (
            rect.bottom()
            + 10
        )

        # Put above when there is no room below
        if (
            y + self.size_label.height()
            > self.height()
        ):

            y = (
                rect.top()
                - self.size_label.height()
                - 10
            )

        x = max(
            5,
            min(
                x,
                self.width()
                - self.size_label.width()
                - 5,
            ),
        )

        y = max(
            5,
            min(
                y,
                self.height()
                - self.size_label.height()
                - 5,
            ),
        )

        self.size_label.move(
            x,
            y,
        )

        self.size_label.show()
        self.size_label.raise_()


    def paintEvent(self, event):

        painter = QPainter(
            self
        )

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        # Dark overlay

        painter.fillRect(
            self.rect(),
            QColor(
                0,
                0,
                0,
                120,
            ),
        )

        controller = self.selection_controller

        # Selection

        if controller.is_valid():

            rect = controller.selection

            # Clear selected area
            painter.setCompositionMode(
                QPainter.CompositionMode_Clear
            )

            painter.fillRect(
                rect,
                Qt.transparent,
            )

            painter.setCompositionMode(
                QPainter.CompositionMode_SourceOver
            )

            # Border
            pen = QPen(
                QColor(
                    255,
                    80,
                    80,
                )
            )

            pen.setWidth(2)

            painter.setPen(
                pen
            )

            painter.drawRect(
                rect
            )

            # Handles
            self.draw_handles(
                painter,
                rect,
            )

        # Initial selection being created

        elif self.creating:

            rect = controller.selection

            if (
                rect.width() > 0
                and rect.height() > 0
            ):

                painter.setCompositionMode(
                    QPainter.CompositionMode_Clear
                )

                painter.fillRect(
                    rect,
                    Qt.transparent,
                )

                painter.setCompositionMode(
                    QPainter.CompositionMode_SourceOver
                )

                pen = QPen(
                    QColor(
                        255,
                        80,
                        80,
                    )
                )

                pen.setWidth(2)

                painter.setPen(
                    pen
                )

                painter.drawRect(
                    rect
                )

        painter.end()


    def draw_handles(
        self,
        painter,
        rect,
    ):

        size = self.HANDLE_SIZE

        half = size // 2

        points = [
            QPoint(
                rect.left(),
                rect.top(),
            ),

            QPoint(
                rect.center().x(),
                rect.top(),
            ),

            QPoint(
                rect.right(),
                rect.top(),
            ),

            QPoint(
                rect.right(),
                rect.center().y(),
            ),

            QPoint(
                rect.right(),
                rect.bottom(),
            ),

            QPoint(
                rect.center().x(),
                rect.bottom(),
            ),

            QPoint(
                rect.left(),
                rect.bottom(),
            ),

            QPoint(
                rect.left(),
                rect.center().y(),
            ),
        ]

        painter.setPen(
            QPen(
                QColor(
                    255,
                    80,
                    80,
                ),
                1,
            )
        )

        painter.setBrush(
            QColor(
                255,
                255,
                255,
            )
        )

        for point in points:

            painter.drawRect(
                QRect(
                    point.x() - half,
                    point.y() - half,
                    size,
                    size,
                )
            )


    def cursor_for_handle(
        self,
        handle,
    ):

        if handle in (
            "nw",
            "se",
        ):
            return Qt.SizeFDiagCursor

        if handle in (
            "ne",
            "sw",
        ):
            return Qt.SizeBDiagCursor

        if handle in (
            "n",
            "s",
        ):
            return Qt.SizeVerCursor

        if handle in (
            "e",
            "w",
        ):
            return Qt.SizeHorCursor

        return Qt.ArrowCursor


    def set_mode(
        self,
        value: CaptureMode,
    ):


        if value == CaptureMode.FREE:

            self.mode = (
                CaptureMode.FREE
            )

            self.ratio = None

            self.selection_controller.set_mode(
                value,
                None,
            )

            self.creating = False

            self.size_label.hide()
            self.selection_toolbar.hide_for_selection()

            self.setCursor(
                Qt.CrossCursor
            )

            self.update()

            return


        if value == CaptureMode.ONE_SCREEN:

            self.settings.capture_scope = value

            self.close()

            self.on_done(
                None
            )

            return


        if value == CaptureMode.ALL_SCREEN:

            self.settings.capture_scope = value

            self.close()

            self.on_done(
                None
            )

            return


        if value == CaptureMode.RATIO_16_9:

            self.mode = value
            self.ratio = 16 / 9

            self.selection_controller.set_mode(
                value,
                self.ratio,
            )

            self.creating = False

            self.size_label.hide()
            self.selection_toolbar.hide_for_selection()

            self.setCursor(
                Qt.CrossCursor
            )

            self.update()

            return

        if value == CaptureMode.RATIO_9_16:

            self.mode = value
            self.ratio = 9 / 16

            self.selection_controller.set_mode(
                value,
                self.ratio,
            )

            self.creating = False

            self.size_label.hide()
            self.selection_toolbar.hide_for_selection()

            self.setCursor(
                Qt.CrossCursor
            )

            self.update()

            return

        if value == CaptureMode.RATIO_1_1:

            self.mode = value
            self.ratio = 1.0

            self.selection_controller.set_mode(
                value,
                self.ratio,
            )

            self.creating = False

            self.size_label.hide()
            self.selection_toolbar.hide_for_selection()

            self.setCursor(
                Qt.CrossCursor
            )

            self.update()

            return
        

    def get_screen_rect(self):

        screen = self.screen()

        if screen is None:

            screen = (
                QGuiApplication.primaryScreen()
            )

        if screen is None:
            return self.rect()

        return screen.geometry()


    def show_hint(
        self,
        pos: QPoint,
    ):

        self.hint.adjustSize()

        x = pos.x() + 12
        y = pos.y() + 12

        x = max(
            5,
            min(
                x,
                self.width()
                - self.hint.width()
                - 5,
            ),
        )

        y = max(
            5,
            min(
                y,
                self.height()
                - self.hint.height()
                - 5,
            ),
        )

        self.hint.move(
            x,
            y,
        )

        self.hint.show()
        self.hint.raise_()

        QTimer.singleShot(
            1500,
            self.hint.hide,
        )