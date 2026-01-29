from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QSpinBox, QComboBox, QPushButton,
    QFileDialog
)
from pathlib import Path
from models.settings import Settings, AudioMode, save_settings


class SettingsWindow(QWidget):
    def __init__(self, settings: Settings):
        super().__init__()
        self.settings = settings

        self.setWindowTitle("Settings")
        self.setFixedSize(300, 260)

        layout = QVBoxLayout(self)

        # ===== FPS =====
        layout.addWidget(QLabel("FPS"))
        self.fps_spin = QSpinBox()
        self.fps_spin.setRange(5, 120)
        self.fps_spin.setValue(self.settings.fps)
        layout.addWidget(self.fps_spin)

        # ===== AUDIO MODE =====
        layout.addWidget(QLabel("Audio"))
        self.audio_box = QComboBox()
        self.audio_box.addItem("None", AudioMode.NONE)
        self.audio_box.addItem("System", AudioMode.SYSTEM)
        self.audio_box.addItem("Mic", AudioMode.MIC)
        self.audio_box.addItem("System + Mic", AudioMode.BOTH)

        idx = self.audio_box.findData(self.settings.audio_mode)
        if idx >= 0:
            self.audio_box.setCurrentIndex(idx)

        layout.addWidget(self.audio_box)

        # ===== OUTPUT DIR =====
        layout.addWidget(QLabel("Output folder"))
        self.out_btn = QPushButton(str(self.settings.output_dir))
        self.out_btn.clicked.connect(self.choose_output_dir)
        layout.addWidget(self.out_btn)

        # ===== SAVE =====
        save_btn = QPushButton("Save")
        layout.addStretch()
        layout.addWidget(save_btn)

        save_btn.clicked.connect(self.save)

    def choose_output_dir(self):
        path = QFileDialog.getExistingDirectory(
            self,
            "Select output folder",
            str(self.settings.output_dir)
        )
        if path:
            self.settings.output_dir = Path(path)
            self.out_btn.setText(path)

    def save(self):
        self.settings.fps = self.fps_spin.value()
        self.settings.audio_mode = self.audio_box.currentData()

        save_settings(self.settings)
        self.close()
