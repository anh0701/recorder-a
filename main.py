import sys
from PySide6.QtWidgets import QApplication
from views.overlay import Overlay
from views.recording_root import RecordingRootWindow
from views.stop_bar import StopBarWindow
from models.recorder import Recorder

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
    recorder = Recorder(rect)
    recorder.start()

    recording_root = RecordingRootWindow(rect)
    stop_bar = StopBarWindow(rect.x() + 10, rect.y() + 10, stop_app)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    overlay = Overlay(on_region_selected)
    sys.exit(app.exec())
