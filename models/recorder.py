import os
import signal
import shutil
import subprocess
import tempfile
from pathlib import Path

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
        self.recording = False

        # Final output
        self.output_file = None

        # Temporary segments
        self.segment_dir = None
        self.segments = []
        self.segment_index = 0

        # Capture area
        self.capture_x = 0
        self.capture_y = 0
        self.capture_w = 0
        self.capture_h = 0

        # Audio source
        self.audio_source = None


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

            self.recording = True
            self.paused = False

            return

        if self.recording:
            print("[RECORDER] already recording")
            return
        

        self.output_file = Path(
            self.settings.generate_output_file()
        )

        # Temporary directory
        #
        # /tmp/recorder_xxxxx/
        #     segment_0000.mp4
        #     segment_0001.mp4
        #     segment_0002.mp4

        self.segment_dir = Path(
            tempfile.mkdtemp(
                prefix="screen_recorder_"
            )
        )

        self.segments = []
        self.segment_index = 0

        print(
            "[RECORDER] temporary directory:",
            self.segment_dir
        )

        self._determine_capture_area()

        if (
            self.settings.audio_mode
            != AudioMode.NONE
        ):

            self.audio_source = self.audio.prepare(
                self.settings.audio_mode
            )

            print(
                "[RECORDER] audio source:",
                self.audio_source
            )


        success = self._start_segment()

        if not success:
            self._cleanup()

            raise RuntimeError(
                "Failed to start FFmpeg recording."
            )

        self.recording = True
        self.paused = False

        print("[RECORDER] recording started")

    # DETERMINE CAPTURE AREA

    def _determine_capture_area(self):

        if (
            self.settings.capture_scope
            == CaptureMode.ONE_SCREEN
        ):

            screens = QGuiApplication.screens()

            screen_index = (
                self.settings.screen_index
            )

            if (
                screen_index < 0
                or screen_index >= len(screens)
            ):
                raise ValueError(
                    f"Invalid screen index: {screen_index}"
                )

            screen = screens[screen_index]

            geo = screen.geometry()

            self.capture_x = geo.x()
            self.capture_y = geo.y()
            self.capture_w = geo.width()
            self.capture_h = geo.height()

        elif (
            self.settings.capture_scope
            == CaptureMode.ALL_SCREEN
        ):

            screens = QGuiApplication.screens()

            if not screens:
                raise RuntimeError(
                    "No screen detected."
                )

            xs = [
                screen.geometry().x()
                for screen in screens
            ]

            ys = [
                screen.geometry().y()
                for screen in screens
            ]

            rs = [
                screen.geometry().right()
                for screen in screens
            ]

            bs = [
                screen.geometry().bottom()
                for screen in screens
            ]

            self.capture_x = min(xs)
            self.capture_y = min(ys)

            self.capture_w = (
                max(rs)
                - self.capture_x
                + 1
            )

            self.capture_h = (
                max(bs)
                - self.capture_y
                + 1
            )

        else:

            if not self.rect:
                raise RuntimeError(
                    "Capture rectangle is not available."
                )

            self.capture_x = self.x
            self.capture_y = self.y
            self.capture_w = self.w
            self.capture_h = self.h

        print(
            "[RECORDER] capture area:",
            f"{self.capture_w}x{self.capture_h}",
            f"@ {self.capture_x},{self.capture_y}"
        )

    def _start_segment(self):

        if self.segment_dir is None:
            return False

        segment_file = (
            self.segment_dir
            / f"segment_{self.segment_index:04d}.mp4"
        )

        self.segment_index += 1

        cmd = [
            "ffmpeg",
            "-y",

            "-video_size",
            f"{self.capture_w}x{self.capture_h}",

            "-framerate",
            str(self.settings.fps),

            "-f",
            "x11grab",

            "-i",
            (
                f":0.0+"
                f"{self.capture_x},"
                f"{self.capture_y}"
            ),
        ]


        has_audio = (
            self.settings.audio_mode
            != AudioMode.NONE
            and self.audio_source
        )

        if has_audio:

            cmd += [
                "-f",
                "pulse",

                "-i",
                self.audio_source,
            ]


        cmd += [
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

        # Audio encoder

        if has_audio:

            cmd += [
                "-c:a",
                "aac",

                "-b:a",
                "192k",

                "-ar",
                "48000",

                "-ac",
                "2",
            ]

            # Make sure both streams are mapped explicitly.
            cmd += [
                "-map",
                "0:v:0",

                "-map",
                "1:a:0",
            ]

        else:

            cmd += [
                "-map",
                "0:v:0",
            ]

        cmd += [
            "-movflags",
            "+faststart",

            str(segment_file),
        ]

        print(
            "[FFMPEG SEGMENT]",
            " ".join(cmd)
        )

        try:

            self.process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
            )

        except Exception as e:

            print(
                "[RECORDER] failed to start FFmpeg:",
                e
            )

            self.process = None

            return False

        self.current_segment = segment_file

        print(
            "[RECORDER] segment started:",
            segment_file
        )

        return True


    def _stop_current_segment(self):

        if not self.process:
            return

        process = self.process

        self.process = None


        if process.poll() is not None:

            print(
                "[RECORDER] FFmpeg already exited:",
                process.returncode
            )

        else:

            try:

                process.send_signal(
                    signal.SIGINT
                )

                print(
                    "[RECORDER] stopping FFmpeg segment..."
                )

                process.wait(
                    timeout=5
                )

            except subprocess.TimeoutExpired:

                print(
                    "[RECORDER] FFmpeg did not exit "
                    "after SIGINT, terminating..."
                )

                try:
                    process.terminate()

                    process.wait(
                        timeout=3
                    )

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

                try:
                    process.kill()
                    process.wait()

                except Exception:
                    pass


        # Check generated segment

        segment = getattr(
            self,
            "current_segment",
            None
        )

        if segment is None:
            return

        if segment.exists():

            size = segment.stat().st_size

            if size > 0:

                self.segments.append(
                    segment
                )

                print(
                    "[RECORDER] segment saved:",
                    segment,
                    f"({size} bytes)"
                )

            else:

                print(
                    "[RECORDER] segment is empty:",
                    segment
                )

        else:

            print(
                "[RECORDER] segment file does not exist:",
                segment
            )

        self.current_segment = None


    def pause(self):

        if TEST_MODE:

            print("[TEST] pause")

            self.paused = True

            return

        if not self.recording:
            return

        if self.paused:
            return

        print("[RECORDER] pausing...")


        self._stop_current_segment()

        self.paused = True

        print(
            "[RECORDER] paused"
        )


    def resume(self):

        if TEST_MODE:

            print("[TEST] resume")

            self.paused = False

            return

        if not self.recording:
            return

        if not self.paused:
            return

        print("[RECORDER] resuming...")

        # Create a completely new segment.
        # This is the key to removing the pause duration
        # from the final video.

        success = self._start_segment()

        if not success:

            print(
                "[RECORDER] failed to resume recording."
            )

            return

        self.paused = False

        print(
            "[RECORDER] resumed"
        )


    def stop(self):

        if TEST_MODE:

            print("[TEST] stop")

            self.recording = False
            self.paused = False

            return

        if not self.recording:
            return

        print("[RECORDER] stopping...")


        if self.process:

            self._stop_current_segment()

        # No segments

        if not self.segments:

            print(
                "[RECORDER] no valid recording segments."
            )

            self.recording = False
            self.paused = False

            self._cleanup()

            return

        # Merge segments

        try:

            self._concat_segments()

        except Exception as e:

            print(
                "[RECORDER] concat error:",
                e
            )


        self.recording = False
        self.paused = False

        self._cleanup()

        # Cleanup audio

        try:

            self.audio.cleanup()

        except Exception as e:

            print(
                "[RECORDER] audio cleanup error:",
                e
            )

        self.audio_source = None

        print(
            "[RECORDER] stopped"
        )


    def _concat_segments(self):

        if not self.segments:
            return

        if self.output_file is None:
            raise RuntimeError(
                "Output file is not set."
            )

        output_file = Path(
            self.output_file
        )

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )


        concat_file = (
            self.segment_dir
            / "concat.txt"
        )

        # FFmpeg concat demuxer list
        # Paths are escaped for FFmpeg concat syntax.

        with open(
            concat_file,
            "w",
            encoding="utf-8"
        ) as f:

            for segment in self.segments:

                path = (
                    Path(segment)
                    .resolve()
                    .as_posix()
                )

                # Escape single quotes.
                path = path.replace(
                    "'",
                    "'\\''"
                )

                f.write(
                    f"file '{path}'\n"
                )

        print(
            "[RECORDER] concat list:",
            concat_file
        )


        concat_output = (
            self.segment_dir
            / "merged.mp4"
        )

        cmd = [
            "ffmpeg",
            "-y",

            "-f",
            "concat",

            "-safe",
            "0",

            "-i",
            str(concat_file),

            "-c",
            "copy",

            "-movflags",
            "+faststart",

            str(concat_output),
        ]

        print(
            "[FFMPEG CONCAT]",
            " ".join(cmd)
        )

        try:

            result = subprocess.run(
                cmd,
                check=False,
            )

        except Exception as e:

            raise RuntimeError(
                f"Failed to execute FFmpeg concat: {e}"
            )

        if result.returncode != 0:

            raise RuntimeError(
                "FFmpeg concat failed "
                f"with exit code {result.returncode}"
            )

        if not concat_output.exists():

            raise RuntimeError(
                "FFmpeg concat completed but "
                "merged file does not exist."
            )

        if concat_output.stat().st_size <= 0:

            raise RuntimeError(
                "FFmpeg concat produced an empty file."
            )

        # Move merged file to final output.

        if output_file.exists():

            try:
                output_file.unlink()

            except Exception as e:

                raise RuntimeError(
                    f"Cannot replace output file: {e}"
                )

        shutil.move(
            str(concat_output),
            str(output_file)
        )

        print(
            "[RECORDER] final video:",
            output_file
        )


    def _cleanup(self):

        if self.segment_dir is None:
            return

        try:

            if self.segment_dir.exists():

                shutil.rmtree(
                    self.segment_dir,
                    ignore_errors=True
                )

                print(
                    "[RECORDER] temporary files cleaned"
                )

        except Exception as e:

            print(
                "[RECORDER] cleanup error:",
                e
            )

        finally:

            self.segment_dir = None
            self.segments = []
            self.segment_index = 0
            self.current_segment = None


    def is_recording(self):

        return self.recording

    def is_paused(self):

        return self.paused

    def get_output_file(self):

        return self.output_file