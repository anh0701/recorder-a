from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
from enum import Enum
import json

TEST_MODE = True

class AudioMode(Enum):
    NONE = "none"
    SYSTEM = "system"
    MIC = "mic"
    BOTH = "both"

# CONFIG_FILE = Path.home() / ".myrecorder.json"

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "config"
CONFIG_DIR.mkdir(exist_ok=True)
CONFIG_FILE = CONFIG_DIR / "settings.json"

@dataclass
class Settings:
    # FPS = 30
    # OUTPUT_FILE = "record.mp4"
    fps: int = 30
    audio_mode: AudioMode = AudioMode.NONE
    output_dir: Path | None = None

    MODE_FREE = "free"
    MODE_RATIO = "ratio"
    CAPTURE_ONE_SCREEN = "one_screen"
    CAPTURE_ALL_SCREEN = "all_screen"

    RATIO_16_9 = 16 / 9
    RATIO_9_16 = 9 / 16
    RATIO_1_1 = 1

    APP_NAME = "MyRecorder"

    def __post_init__(self):
        self.capture_scope = None
        self.screen_index = 0
        
        if self.output_dir is None:
            self.output_dir = self._default_output_dir()

    def _default_output_dir(self) -> Path:
        home = Path.home()
        base = home / "Videos"
        if not base.exists():
            base = home / "Movies"
        return base / self.APP_NAME

    def generate_output_file(self) -> Path:
        today = datetime.now().strftime("%Y-%m-%d")
        now = datetime.now().strftime("%H-%M-%S")

        out = self.output_dir / today
        out.mkdir(parents=True, exist_ok=True)

        return out / f"record_{now}.mp4"

def load_settings() -> Settings:
    if not CONFIG_FILE.exists():
        return Settings()

    data = json.loads(CONFIG_FILE.read_text())
    return Settings(
        fps=data.get("fps", 30),
        audio_mode=AudioMode(data.get("audio_mode", "none")),
        output_dir=Path(data.get("output_dir")),
    )


def save_settings(settings: Settings):
    data = {
        "fps": settings.fps,
        "audio_mode": settings.audio_mode.value,
        "output_dir": str(settings.output_dir),
    }
    CONFIG_FILE.write_text(json.dumps(data, indent=2))


