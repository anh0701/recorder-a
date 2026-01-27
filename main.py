import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, QEvent, Qt

from overlay import Overlay
from recorder import Recorder

recorder = None


class KeyCatcher(QObject):
    def eventFilter(self, obj, event):
        global recorder
        if event.type() == QEvent.KeyPress:
            if event.key() in (Qt.Key_Escape, Qt.Key_Q):
                print("STOP RECORD")
                if recorder:
                    recorder.stop()
                QApplication.quit()
                return True
        return False


def on_region_selected(rect):
    global recorder
    print("Final selected region:", rect)
    recorder = Recorder(rect)
    recorder.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    key_catcher = KeyCatcher()
    app.installEventFilter(key_catcher)

    overlay = Overlay(on_done=on_region_selected)
    overlay.show()

    sys.exit(app.exec())
