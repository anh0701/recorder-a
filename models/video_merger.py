import shutil
import subprocess
from pathlib import Path


class VideoMerger:

    @staticmethod
    def merge(
        segments,
        segment_directory: Path,
        output_file: Path,
    ):

        if not segments:
            raise RuntimeError(
                "No segments available."
            )

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        concat_file = (
            segment_directory
            / "concat.txt"
        )

        VideoMerger._create_concat_file(
            segments,
            concat_file,
        )

        merged_file = (
            segment_directory
            / "merged.mp4"
        )

        command = [
            "ffmpeg",
            "-y",

            "-f",
            "concat",

            "-safe",
            "0",

            "-i",
            str(concat_file),

            "-c:v",
            "libx264",

            "-preset",
            "veryfast",

            "-crf",
            "18",

            "-pix_fmt",
            "yuv420p",
        ]

        # Chỉ encode audio nếu segment có audio.
        has_audio = VideoMerger._has_audio(
            segments[0]
        )

        if has_audio:

            command += [
                "-c:a",
                "aac",

                "-b:a",
                "192k",

                "-ar",
                "48000",

                "-ac",
                "2",
            ]

        command += [
            "-movflags",
            "+faststart",

            str(merged_file),
        ]

        print(
            "[FFMPEG MERGE]",
            " ".join(command)
        )

        result = subprocess.run(
            command,
            check=False,
        )

        if result.returncode != 0:

            raise RuntimeError(
                "FFmpeg merge failed "
                f"with exit code {result.returncode}"
            )

        VideoMerger._validate_output(
            merged_file
        )

        if output_file.exists():

            try:
                output_file.unlink()

            except Exception as e:

                raise RuntimeError(
                    f"Cannot replace output file: {e}"
                )

        shutil.move(
            str(merged_file),
            str(output_file)
        )

        print(
            "[RECORDER] final video:",
            output_file
        )

    @staticmethod
    def _create_concat_file(
        segments,
        concat_file: Path,
    ):

        with open(
            concat_file,
            "w",
            encoding="utf-8"
        ) as file:

            for segment in segments:

                path = (
                    Path(segment)
                    .resolve()
                    .as_posix()
                )

                path = path.replace(
                    "'",
                    "'\\''"
                )

                file.write(
                    f"file '{path}'\n"
                )

        print(
            "[RECORDER] concat list:",
            concat_file
        )

    @staticmethod
    def _validate_output(path: Path):

        if not path.exists():
            raise RuntimeError(
                "Merged file does not exist."
            )

        if path.stat().st_size <= 0:
            raise RuntimeError(
                "Merged file is empty."
            )

        command = [
            "ffprobe",
            "-v",
            "error",

            "-show_entries",
            "format=duration",

            "-of",
            "default=noprint_wrappers=1:nokey=1",

            str(path),
        ]

        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        if result.returncode != 0:
            raise RuntimeError(
                "Merged video failed validation."
            )

        print(
            "[RECORDER] final duration:",
            result.stdout.strip(),
            "seconds"
        )


    @staticmethod
    def _has_audio(path: Path):

        command = [
            "ffprobe",
            "-v",
            "error",

            "-select_streams",
            "a:0",

            "-show_entries",
            "stream=index",

            "-of",
            "csv=p=0",

            str(path),
        ]

        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        return bool(
            result.stdout.strip()
        )