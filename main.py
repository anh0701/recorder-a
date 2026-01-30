import sys
from PySide6.QtWidgets import QApplication
from views.overlay import Overlay
from views.recording_root import RecordingRootWindow
from views.stop_bar import StopBarWindow
from models.recorder import Recorder
from models.settings import Settings, load_settings
from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import QRect

settings = load_settings()
overlay = None
recorder = None
recording_root = None
stop_bar = None


def stop_app():
    global recorder, recording_root, stop_bar
    if recorder:
        recorder.stop()
    if recording_root:
        recording_root.close()
    if stop_bar:
        stop_bar.close()
    QApplication.quit()


def on_region_selected(rect):
    global recorder, recording_root, stop_bar

    if rect is None:
        recorder = Recorder(None, settings)
    else:
        recorder = Recorder(rect, settings)

    recorder.start()

    if settings.capture_scope == Settings.CAPTURE_ONE_SCREEN:
        screen = QGuiApplication.screens()[settings.screen_index]
        geo = screen.geometry()
        recording_root = RecordingRootWindow(geo)
        stop_bar = StopBarWindow(geo.x() + 10, geo.y() + 10, stop_app)

    elif settings.capture_scope == Settings.CAPTURE_ALL_SCREEN:
        screens = QGuiApplication.screens()
        xs = [s.geometry().x() for s in screens]
        ys = [s.geometry().y() for s in screens]
        rs = [s.geometry().right() for s in screens]
        bs = [s.geometry().bottom() for s in screens]

        x, y = min(xs), min(ys)
        w = max(rs) - x + 1
        h = max(bs) - y + 1

        rect = QRect(x, y, w, h)
        recording_root = RecordingRootWindow(rect)
        stop_bar = StopBarWindow(x + 10, y + 10, stop_app)

    else:
        recording_root = RecordingRootWindow(rect)
        stop_bar = StopBarWindow(rect.x() + 10, rect.y() + 10, stop_app)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    overlay = Overlay(on_region_selected, settings=settings)
    sys.exit(app.exec())
