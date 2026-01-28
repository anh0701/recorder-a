from datetime import datetime
from pathlib import Path

class Settings:
    FPS = 30
    # OUTPUT_FILE = "record.mp4"

    MODE_FREE = "free"
    MODE_RATIO = "ratio"

    RATIO_16_9 = 16 / 9
    RATIO_9_16 = 9 / 16
    RATIO_1_1 = 1

    APP_NAME = "MyRecorder"

    @staticmethod
    def output_file():
        home = Path.home()

        # Videos (Windows/Linux) | Movies (macOS)
        base_dir = home / "Videos"
        if not base_dir.exists():
            base_dir = home / "Movies"

        today = datetime.now().strftime("%Y-%m-%d")
        time_now = datetime.now().strftime("%H-%M-%S")

        output_dir = base_dir / Settings.APP_NAME / today
        output_dir.mkdir(parents=True, exist_ok=True)

        return str(output_dir / f"record_{time_now}.mp4")


TEST_MODE = False
