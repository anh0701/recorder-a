from pathlib import Path

from PySide6.QtGui import QGuiApplication

from models.audio_manager import AudioManager
from models.settings import (
    AudioMode,
    CaptureMode,
    Settings,
    TEST_MODE,
)

from .ffmpeg_manager import FFmpegManager
from .segment_manager import SegmentManager
from .video_merger import VideoMerger


class Recorder:

    def __init__(
        self,
        rect,
        settings: Settings,
    ):

        self.rect = rect
        self.settings = settings

        self.recording = False
        self.paused = False

        self.output_file = None

        self.capture_x = 0
        self.capture_y = 0
        self.capture_w = 0
        self.capture_h = 0

        self.audio = AudioManager()
        self.audio_source = None

        self.segment_manager = SegmentManager()

        self.ffmpeg = None
        self.current_segment = None


    def start(self):

        if TEST_MODE:
            self._start_test_mode()
            return

        if self.recording:
            print("[RECORDER] already recording")
            return

        self.output_file = Path(
            self.settings.generate_output_file()
        )

        self._determine_capture_area()

        self.segment_manager.create_directory()

        self._prepare_audio()

        if not self._start_new_segment():

            self._cleanup()

            raise RuntimeError(
                "Failed to start FFmpeg recording."
            )

        self.recording = True
        self.paused = False

        print("[RECORDER] recording started")

    def pause(self):

        if TEST_MODE:
            print("[TEST] pause")
            self.paused = True
            return

        if not self.recording or self.paused:
            return

        print("[RECORDER] pausing...")

        self._stop_current_segment()

        self.paused = True

        print("[RECORDER] paused")

    def resume(self):

        if TEST_MODE:
            print("[TEST] resume")
            self.paused = False
            return

        if not self.recording or not self.paused:
            return

        print("[RECORDER] resuming...")

        if not self._start_new_segment():

            print(
                "[RECORDER] failed to resume recording."
            )

            return

        self.paused = False

        print("[RECORDER] resumed")

    def stop(self):

        if TEST_MODE:
            self._stop_test_mode()
            return

        if not self.recording:
            return

        print("[RECORDER] stopping...")

        self._stop_current_segment()

        if not self.segment_manager.segments:

            print(
                "[RECORDER] no valid recording segments."
            )

            self._finish()
            return

        success = self._merge_segments()

        self.recording = False
        self.paused = False

        if success:

            self.segment_manager.cleanup()

        else:

            print(
                "[RECORDER] keeping temporary files:",
                self.segment_manager.directory
            )

        self._cleanup_audio()

        print("[RECORDER] stopped")


    def _start_new_segment(self):

        try:

            segment = (
                self.segment_manager
                .create_segment()
            )

            self.ffmpeg = FFmpegManager(
                capture_x=self.capture_x,
                capture_y=self.capture_y,
                capture_w=self.capture_w,
                capture_h=self.capture_h,
                fps=self.settings.fps,
                audio_source=self.audio_source,
            )

            if not self.ffmpeg.start(segment):

                self.ffmpeg = None
                return False

            self.current_segment = segment

            print(
                "[RECORDER] segment started:",
                segment
            )

            return True

        except Exception as e:

            print(
                "[RECORDER] failed to start segment:",
                e
            )

            self.ffmpeg = None
            return False

    def _stop_current_segment(self):

        if self.ffmpeg is None:
            return

        segment = self.current_segment

        exit_code = self.ffmpeg.stop()

        self.ffmpeg = None
        self.current_segment = None

        print(
            "[RECORDER] segment exit code:",
            exit_code
        )

        if segment is None:
            return

        # Không quyết định segment hợp lệ
        # chỉ dựa vào exit code.
        self.segment_manager.add_segment(
            segment
        )


    def _merge_segments(self):

        try:

            VideoMerger.merge(
                segments=self.segment_manager.segments,
                segment_directory=self.segment_manager.directory,
                output_file=self.output_file,
            )

            return True

        except Exception as e:

            print(
                "[RECORDER] merge error:",
                e
            )

            return False


    def _prepare_audio(self):

        if self.settings.audio_mode == AudioMode.NONE:
            return

        self.audio_source = self.audio.prepare(
            self.settings.audio_mode
        )

        print(
            "[RECORDER] audio source:",
            self.audio_source
        )

    def _cleanup_audio(self):

        try:

            self.audio.cleanup()

        except Exception as e:

            print(
                "[RECORDER] audio cleanup error:",
                e
            )

        self.audio_source = None


    def _determine_capture_area(self):

        scope = self.settings.capture_scope

        if scope == CaptureMode.ONE_SCREEN:

            self._set_single_screen_area()

        elif scope == CaptureMode.ALL_SCREEN:

            self._set_all_screen_area()

        else:

            self._set_rectangle_area()

        print(
            "[RECORDER] capture area:",
            f"{self.capture_w}x{self.capture_h}",
            f"@ {self.capture_x},{self.capture_y}"
        )

    def _set_single_screen_area(self):

        screens = QGuiApplication.screens()

        index = self.settings.screen_index

        if index < 0 or index >= len(screens):

            raise ValueError(
                f"Invalid screen index: {index}"
            )

        self._apply_geometry(
            screens[index].geometry()
        )

    def _set_all_screen_area(self):

        screens = QGuiApplication.screens()

        if not screens:
            raise RuntimeError(
                "No screen detected."
            )

        geometries = [
            screen.geometry()
            for screen in screens
        ]

        left = min(
            geo.x()
            for geo in geometries
        )

        top = min(
            geo.y()
            for geo in geometries
        )

        right = max(
            geo.right()
            for geo in geometries
        )

        bottom = max(
            geo.bottom()
            for geo in geometries
        )

        self.capture_x = left
        self.capture_y = top

        self.capture_w = (
            right - left + 1
        )

        self.capture_h = (
            bottom - top + 1
        )

    def _set_rectangle_area(self):

        if not self.rect:
            raise RuntimeError(
                "Capture rectangle is not available."
            )

        self._apply_geometry(
            self.rect
        )

    def _apply_geometry(self, geometry):

        self.capture_x = geometry.x()
        self.capture_y = geometry.y()

        self.capture_w = geometry.width()
        self.capture_h = geometry.height()


    def _cleanup(self):

        self.segment_manager.cleanup()

        self._cleanup_audio()

        self.ffmpeg = None
        self.current_segment = None

    def _finish(self):

        self.recording = False
        self.paused = False

        self._cleanup()

        print("[RECORDER] stopped")


    def _start_test_mode(self):

        if self.rect:

            print(
                f"[TEST] start "
                f"{self.rect.width()}x"
                f"{self.rect.height()} "
                f"@ {self.rect.x()},"
                f"{self.rect.y()}, "
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

    def _stop_test_mode(self):

        print("[TEST] stop")

        self.recording = False
        self.paused = False


    def is_recording(self):
        return self.recording

    def is_paused(self):
        return self.paused

    def get_output_file(self):
        return self.output_file