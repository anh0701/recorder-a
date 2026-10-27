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
            raise RuntimeError("No segments available.")

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        concat_file = segment_directory / "concat.txt"

        VideoMerger._create_concat_file(
            segments,
            concat_file,
        )

        merged_file = segment_directory / "merged.mp4"

        command = [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel", "warning",

            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),

            # Không encode lại video/audio.
            "-map", "0:v:0",
            "-map", "0:a:0?",
            "-c", "copy",

            # Đưa metadata MP4 lên đầu file.
            "-movflags", "+faststart",

            str(merged_file),
        ]

        print(
            "[FFMPEG MERGE]",
            " ".join(command),
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

        VideoMerger._validate_output(merged_file)

        if output_file.exists():
            output_file.unlink()

        shutil.move(
            str(merged_file),
            str(output_file),
        )

        print(
            "[RECORDER] final video:",
            output_file,
        )

    @staticmethod
    def _create_concat_file(
        segments,
        concat_file: Path,
    ):
        with open(
            concat_file,
            "w",
            encoding="utf-8",
        ) as file:
            for segment in segments:
                path = (
                    Path(segment)
                    .resolve()
                    .as_posix()
                )

                path = path.replace(
                    "'",
                    "'\\''",
                )

                file.write(
                    f"file '{path}'\n"
                )

        print(
            "[RECORDER] concat list:",
            concat_file,
        )

    @staticmethod
    def _validate_output(path: Path):
        if not path.exists():
            raise RuntimeError(
                "Merged video does not exist."
            )

        if path.stat().st_size <= 0:
            raise RuntimeError(
                "Merged video is empty."
            )

        command = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
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
                "Merged video failed validation: "
                + result.stderr
            )

        duration = result.stdout.strip()

        if not duration:
            raise RuntimeError(
                "Cannot determine merged video duration."
            )

        print(
            "[RECORDER] final duration:",
            duration,
            "seconds",
        )

    @staticmethod
    def _has_audio(path: Path):
        command = [
            "ffprobe",
            "-v", "error",
            "-select_streams", "a:0",
            "-show_entries", "stream=index",
            "-of", "csv=p=0",
            str(path),
        ]

        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        return (
            result.returncode == 0
            and bool(result.stdout.strip())
        )
