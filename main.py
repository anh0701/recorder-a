import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import QRect

from views.overlay import Overlay
from views.recording_root import RecordingRootWindow
from views.stop_bar import StopBarWindow

from models.recorder import Recorder
from models.settings import (
    Settings,
    load_settings,
    CaptureMode,
)


settings = load_settings()

overlay = None
recorder = None
recording_root = None
stop_bar = None


def stop_app():
    global recorder
    global recording_root
    global stop_bar

    if recorder:
        recorder.stop()

    if recording_root:
        recording_root.close()

    if stop_bar:
        stop_bar.close()

    QApplication.quit()


def create_stop_bar(x, y):

    global stop_bar
    global recorder

    stop_bar = StopBarWindow(
        x,
        y,
        stop_app
    )

    # Connect Pause / Resume
    if recorder:

        stop_bar.pauseRequested.connect(
            recorder.pause
        )

        stop_bar.resumeRequested.connect(
            recorder.resume
        )


def on_region_selected(rect):

    global recorder
    global recording_root

    if rect is None:
        recorder = Recorder(
            None,
            settings
        )

    else:
        recorder = Recorder(
            rect,
            settings
        )

    recorder.start()

    if (
        settings.capture_scope
        == CaptureMode.ONE_SCREEN
    ):

        screen = (
            QGuiApplication.screens()
            [settings.screen_index]
        )

        geo = screen.geometry()

        recording_root = RecordingRootWindow(
            geo,
            draw_border=False
        )

        create_stop_bar(
            geo.x() + 10,
            geo.y() + 10
        )

    elif (
        settings.capture_scope
        == CaptureMode.ALL_SCREEN
    ):

        screens = (
            QGuiApplication.screens()
        )

        xs = [
            s.geometry().x()
            for s in screens
        ]

        ys = [
            s.geometry().y()
            for s in screens
        ]

        rs = [
            s.geometry().right()
            for s in screens
        ]

        bs = [
            s.geometry().bottom()
            for s in screens
        ]

        x = min(xs)
        y = min(ys)

        w = max(rs) - x + 1
        h = max(bs) - y + 1

        rect = QRect(
            x,
            y,
            w,
            h
        )

        recording_root = RecordingRootWindow(
            rect,
            draw_border=False
        )

        create_stop_bar(
            x + 10,
            y + 10
        )

    else:

        recording_root = RecordingRootWindow(
            rect,
            draw_border=True
        )

        create_stop_bar(
            rect.x() + 10,
            rect.y() + 10
        )


if __name__ == "__main__":

    app = QApplication(sys.argv)

    overlay = Overlay(
        on_region_selected,
        settings=settings
    )

    sys.exit(
        app.exec()
    )