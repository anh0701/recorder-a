import sys
from PySide6.QtWidgets import QApplication
from views.recording_overlay import RecordingOverlay
from views.overlay import Overlay

from models.recorder import Recorder

recorder = None
recording_overlay = None


def stop_app():
    global recorder, recording_overlay

    print("STOP CALLED")

    if recorder:
        recorder.stop()
        recorder = None

    if recording_overlay:
        recording_overlay.close()
        recording_overlay = None

    QApplication.quit()


def on_region_selected(rect):
    global recorder, recording_overlay

    recorder = Recorder(rect)
    recorder.start()

    recording_overlay = RecordingOverlay(
        rect=rect,
        on_stop=stop_app
    )


if __name__ == "__main__":
    app = QApplication(sys.argv)

    Overlay(on_done=on_region_selected)

    sys.exit(app.exec())
