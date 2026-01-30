import subprocess
import signal
from models.settings import AudioMode, Settings, TEST_MODE
from models.audio_manager import AudioManager

class Recorder:
    def __init__(self, rect, settings: Settings):
        self.x = rect.x()
        self.y = rect.y()
        self.w = rect.width()
        self.h = rect.height()

        self.settings = settings
        self.process = None
        self.audio = AudioManager()

    def start(self):
        if TEST_MODE:
            print(
                f"[TEST] start {self.w}x{self.h} "
                f"@ {self.x},{self.y}, "
                f"fps={self.settings.fps}, "
                f"audio={self.settings.audio_mode}"
            )
            return

        output_file = self.settings.generate_output_file()

        cmd = [
            "ffmpeg",
            "-y",
            "-video_size", f"{self.w}x{self.h}",
            "-framerate", str(self.settings.fps),
            "-f", "x11grab",
            "-i", f":0.0+{self.x},{self.y}",
        ]

        if self.settings.audio_mode != AudioMode.NONE:
            audio_source = self.audio.prepare(self.settings.audio_mode)
            cmd += ["-f", "pulse", "-i", audio_source]

        cmd.append(str(output_file))

        self.process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE
        )

    def stop(self):
        if TEST_MODE:
            print("[TEST] stop")
            return

        if self.process:
            self.process.send_signal(signal.SIGINT)
            self.process.wait()
            self.process = None
        
        self.audio.cleanup()
