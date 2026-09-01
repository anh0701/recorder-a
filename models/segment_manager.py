import shutil
import subprocess
import tempfile
from pathlib import Path


class SegmentManager:

    def __init__(self):

        self.directory = None
        self.segments = []
        self.index = 0

    def create_directory(self):

        self.directory = Path(
            tempfile.mkdtemp(
                prefix="screen_recorder_"
            )
        )

        self.segments.clear()
        self.index = 0

        print(
            "[RECORDER] temporary directory:",
            self.directory
        )

    def create_segment(self):

        if self.directory is None:
            raise RuntimeError(
                "Segment directory is not initialized."
            )

        segment = (
            self.directory
            / f"segment_{self.index:04d}.mkv"
        )

        self.index += 1

        return segment

    def add_segment(self, segment: Path):

        if not self.is_valid(segment):
            print(
                "[RECORDER] invalid segment:",
                segment
            )

            return False

        self.segments.append(segment)

        print(
            "[RECORDER] segment saved:",
            segment,
            f"({segment.stat().st_size} bytes)"
        )

        return True

    def is_valid(self, segment: Path):

        if not segment.exists():
            print(
                "[RECORDER] segment does not exist:",
                segment
            )

            return False

        if segment.stat().st_size <= 0:
            print(
                "[RECORDER] segment is empty:",
                segment
            )

            return False

        return self._validate_video(segment)

    def _validate_video(self, segment: Path):

        command = [
            "ffprobe",
            "-v",
            "error",

            "-select_streams",
            "v:0",

            "-show_entries",
            "stream=codec_name,width,height,r_frame_rate",

            "-show_entries",
            "format=duration",

            "-of",
            "default=noprint_wrappers=1",

            str(segment),
        ]

        try:

            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            if result.returncode != 0:

                print(
                    "[RECORDER] ffprobe failed:",
                    segment
                )

                print(
                    "[FFPROBE ERROR]",
                    result.stderr
                )

                return False

            if not result.stdout.strip():

                print(
                    "[RECORDER] no video information:",
                    segment
                )

                return False

            print(
                "[RECORDER] video validation:",
                result.stdout.strip()
            )

            return True

        except Exception as e:

            print(
                "[RECORDER] ffprobe error:",
                e
            )

            return False

    def cleanup(self):

        if self.directory is None:
            return

        try:

            if self.directory.exists():

                shutil.rmtree(
                    self.directory,
                    ignore_errors=True
                )

                print(
                    "[RECORDER] temporary files cleaned"
                )

        finally:

            self.directory = None
            self.segments.clear()
            self.index = 0