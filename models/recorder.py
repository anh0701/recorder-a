import subprocess
import signal

from models.settings import (
    AudioMode,
    Settings,
    TEST_MODE,
    CaptureMode,
)

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

        # Recording state
        self.paused = False

    def start(self):

        if TEST_MODE:

            if self.rect:
                print(
                    f"[TEST] start {self.w}x{self.h} "
                    f"@ {self.x},{self.y}, "
                    f"fps={self.settings.fps}, "
                    f"audio={self.settings.audio_mode}"
                )

            else:
                print(
                    f"[TEST] start "
                    f"fps={self.settings.fps}, "
                    f"audio={self.settings.audio_mode}"
                )

            return

        output_file = (
            self.settings.generate_output_file()
        )

        # Determine capture area

        if (
            self.settings.capture_scope
            == CaptureMode.ONE_SCREEN
        ):

            screen = (
                QGuiApplication.screens()
                [self.settings.screen_index]
            )

            geo = screen.geometry()

            x = geo.x()
            y = geo.y()
            w = geo.width()
            h = geo.height()

        elif (
            self.settings.capture_scope
            == CaptureMode.ALL_SCREEN
        ):

            screens = QGuiApplication.screens()

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

        else:

            x = self.x
            y = self.y
            w = self.w
            h = self.h

        # FFmpeg command

        cmd = [
            "ffmpeg",
            "-y",

            "-video_size",
            f"{w}x{h}",

            "-framerate",
            str(self.settings.fps),

            "-f",
            "x11grab",

            "-i", f":0.0+{x},{y}",

            # H.264 requires even dimensions
            "-vf",
            "pad=ceil(iw/2)*2:ceil(ih/2)*2",

            "-c:v",
            "libx264",

            "-crf",
            "18",

            "-preset",
            "ultrafast",

            "-pix_fmt",
            "yuv420p",
        ]

        # Audio

        if (
            self.settings.audio_mode
            != AudioMode.NONE
        ):

            audio_source = self.audio.prepare(
                self.settings.audio_mode
            )

            cmd += [
                "-f",
                "pulse",
                "-i",
                audio_source,
            ]

        cmd.append(
            str(output_file)
        )

        print("[FFMPEG CMD]", " ".join(cmd))

        # Start FFmpeg

        self.process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE
        )

        self.paused = False

    # PAUSE

    def pause(self):

        if TEST_MODE:
            print("[TEST] pause")
            self.paused = True
            return

        if not self.process:
            return

        if self.paused:
            return

        try:
            self.process.send_signal(
                signal.SIGSTOP
            )

            self.paused = True

            print("[RECORDER] paused")

        except Exception as e:
            print("[RECORDER] pause error:", e)

    # RESUME

    def resume(self):

        if TEST_MODE:
            print("[TEST] resume")
            self.paused = False
            return

        if not self.process:
            return

        if not self.paused:
            return

        try:
            self.process.send_signal(
                signal.SIGCONT
            )

            self.paused = False

            print("[RECORDER] resumed")

        except Exception as e:
            print("[RECORDER] resume error:", e)

    # STOP

    def stop(self):

        if TEST_MODE:
            print("[TEST] stop")
            return

        if self.process:

            try:

                # If FFmpeg is paused,
                # resume it before terminating.
                if self.paused:

                    self.process.send_signal(
                        signal.SIGCONT
                    )

                    self.paused = False

                self.process.terminate()

                self.process.wait(
                    timeout=5
                )

            except subprocess.TimeoutExpired:

                print("[RECORDER] FFmpeg did not exit, killing...")

                self.process.kill()

                self.process.wait()

            except Exception as e:

                print("[RECORDER] stop error:", e)

            finally:

                self.process = None
                self.paused = False

        self.audio.cleanup()