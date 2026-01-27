import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QKeySequence, QShortcut

from overlay import Overlay
from recorder import Recorder

recorder = None


def stop_app():
    global recorder
    print("STOP CALLED")
    if recorder:
        recorder.stop()
        recorder = None
    QApplication.quit()


def on_region_selected(rect):
    global recorder
    recorder = Recorder(rect)
    recorder.start()

    # ESC
    esc = QShortcut(QKeySequence("Escape"), app)
    esc.activated.connect(stop_app)

    # Q
    q = QShortcut(QKeySequence("Q"), app)
    q.activated.connect(stop_app)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    Overlay(on_done=on_region_selected)

    sys.exit(app.exec())
