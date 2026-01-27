import subprocess
import signal
from settings import Settings


class Recorder:
    def __init__(self, rect):
        self.x = rect.x()
        self.y = rect.y()
        self.w = rect.width()
        self.h = rect.height()
        self.process = None

    def start(self):
        cmd = [
            "ffmpeg",
            "-y",
            "-video_size", f"{self.w}x{self.h}",
            "-framerate", str(Settings.FPS),
            "-f", "x11grab",
            "-i", f":0.0+{self.x},{self.y}",
            Settings.OUTPUT_FILE
        ]

        self.process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE
        )

    def stop(self):
        if self.process:
            self.process.send_signal(signal.SIGINT)
            self.process.wait()
