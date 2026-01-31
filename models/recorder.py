import subprocess
import signal
from models.settings import AudioMode, Settings, TEST_MODE, CaptureMode
from models.audio_manager import AudioManager
from PySide6.QtGui import QGuiApplication


class Recorder:
    def __init__(self, rect, settings: Settings):
        self.rect = rect
        if rect:
            self.x = rect.x()
            self.y = rect.y()
            self.w = rect.width()
            self.h = rect.height()

        self.settings = settings
        self.process = None
        self.audio = AudioManager()

    def start(self):
        if TEST_MODE:
            if self.rect:
                print(
                    f"[TEST] start {self.w}x{self.h} "
                    f"@ {self.x},{self.y}, "
                    f"fps={self.settings.fps}, "
                    f"audio={self.settings.audio_mode}"
                )
                return
            else:
                print(
                    f"[TEST] start "
                    f"fps={self.settings.fps}, "
                    f"audio={self.settings.audio_mode}"
                )
                return

        output_file = self.settings.generate_output_file()

        if self.settings.capture_scope == CaptureMode.ONE_SCREEN:
            screen = QGuiApplication.screens()[self.settings.screen_index]
            geo = screen.geometry()
            x, y = geo.x(), geo.y()
            w, h = geo.width(), geo.height()
        elif self.settings.capture_scope == CaptureMode.ALL_SCREEN:
            screens = QGuiApplication.screens()
            xs = [s.geometry().x() for s in screens]
            ys = [s.geometry().y() for s in screens]
            rs = [s.geometry().right() for s in screens]
            bs = [s.geometry().bottom() for s in screens]

            x, y = min(xs), min(ys)
            w = max(rs) - x + 1
            h = max(bs) - y + 1
        else:
            x, y, w, h = self.x, self.y, self.w, self.h

        cmd = [
            "ffmpeg",
            "-y",
            "-video_size", f"{w}x{h}",
            "-framerate", str(self.settings.fps),
            "-f", "x11grab",
            "-i", f":0.0+{x},{y}",
        ]

        if self.settings.audio_mode != AudioMode.NONE:
            audio_source = self.audio.prepare(self.settings.audio_mode)
            cmd += ["-f", "pulse", "-i", audio_source]

        cmd.append(str(output_file))

        print("[FFMPEG CMD]", " ".join(cmd))

        self.process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE
        )

    def stop(self):
        if TEST_MODE:
            print("[TEST] stop")
            return

        if self.process:
            try:
                self.process.terminate()
                self.process.wait()
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
            finally:
                self.process = None
        
        self.audio.cleanup()


