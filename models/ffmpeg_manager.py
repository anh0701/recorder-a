import signal
import subprocess
from pathlib import Path


class FFmpegManager:

    def __init__(
        self,
        capture_x: int,
        capture_y: int,
        capture_w: int,
        capture_h: int,
        fps: int,
        audio_source=None,
    ):
        self.capture_x = capture_x
        self.capture_y = capture_y
        self.capture_w = capture_w
        self.capture_h = capture_h
        self.fps = fps
        self.audio_source = audio_source

        self.process = None

    def start(self, output_file: Path):

        command = self._build_command(output_file)

        print(
            "[FFMPEG START]",
            " ".join(command)
        )

        try:
            self.process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
            )

            return True

        except Exception as e:
            print(
                "[RECORDER] failed to start FFmpeg:",
                e
            )

            self.process = None
            return False

    def stop(self):

        process = self.process

        if process is None:
            return None

        self.process = None

        if process.poll() is not None:
            print(
                "[RECORDER] FFmpeg already exited:",
                process.returncode
            )

            return process.returncode

        try:
            print(
                "[RECORDER] stopping FFmpeg..."
            )

            # FFmpeg sẽ tự finalize container.
            if process.stdin:
                try:
                    process.stdin.write(b"q\n")
                    process.stdin.flush()
                except (BrokenPipeError, OSError):
                    pass

            process.wait(timeout=10)

        except subprocess.TimeoutExpired:

            print(
                "[RECORDER] FFmpeg did not stop after q."
            )

            try:
                process.send_signal(signal.SIGINT)
                process.wait(timeout=5)

            except subprocess.TimeoutExpired:

                print(
                    "[RECORDER] FFmpeg still running, terminating..."
                )

                try:
                    process.terminate()
                    process.wait(timeout=3)

                except subprocess.TimeoutExpired:

                    print(
                        "[RECORDER] FFmpeg still running, killing..."
                    )

                    process.kill()
                    process.wait()

        except Exception as e:

            print(
                "[RECORDER] error stopping FFmpeg:",
                e
            )

        print(
            "[RECORDER] FFmpeg exit code:",
            process.returncode
        )

        return process.returncode

    def is_running(self):

        return (
            self.process is not None
            and self.process.poll() is None
        )

    def _build_command(self, output_file: Path):

        command = [
            "ffmpeg",
            "-y",

            # Capture
            "-f",
            "x11grab",

            "-video_size",
            f"{self.capture_w}x{self.capture_h}",

            "-framerate",
            str(self.fps),

            "-i",
            f":0.0+{self.capture_x},{self.capture_y}",
        ]

        # Audio
        if self.audio_source:

            command += [
                "-f",
                "pulse",

                "-i",
                self.audio_source,
            ]

        # Video
        command += [
            "-map",
            "0:v:0",

            "-c:v",
            "libx264",

            "-preset",
            "ultrafast",

            "-crf",
            "18",

            "-pix_fmt",
            "yuv420p",

            "-vf",
            "pad=ceil(iw/2)*2:ceil(ih/2)*2",
        ]

        # Audio
        if self.audio_source:

            command += [
                "-map",
                "1:a:0",

                "-c:a",
                "aac",

                "-b:a",
                "192k",

                "-ar",
                "48000",

                "-ac",
                "2",
            ]

        # Temporary segments are MKV.
        command += [
            "-f",
            "matroska",

            str(output_file),
        ]

        return command