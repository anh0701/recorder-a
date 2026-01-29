from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QSpinBox, QComboBox, QPushButton,
    QFileDialog, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor
from pathlib import Path
from functools import partial

from models.settings import Settings, AudioMode, save_settings


class SettingsWindow(QWidget):
    def __init__(self, settings: Settings, parent=None):
        super().__init__(parent)
        self.settings = settings

        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint)
        self.setFixedSize(320, 300)

        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setAutoFillBackground(True)

        # ===== STYLE =====
        self.setStyleSheet("""
        QWidget {
            background-color: #1b1b1b;
            color: #e0e0e0;
            font-size: 14px;
            border-radius: 10px;
        }

        QLabel {
            color: #9e9e9e;
        }

        QSpinBox, QComboBox, QPushButton {
            background-color: #262626;
            border: 1px solid #3a3a3a;
            border-radius: 8px;
            padding: 6px 8px;
            font-size: 15px;
        }

        QSpinBox::up-button, QSpinBox::down-button {
            width: 18px;
            background: #303030;
            border-left: 1px solid #444;
        }

        QSpinBox::up-button:hover, QSpinBox::down-button:hover {
            background: #3d3d3d;
        }

        QSpinBox:focus, QComboBox:focus {
            border: 1px solid #4aa3ff;
        }

        QPushButton:hover {
            background-color: #3f3f3f;
        }
        """)

        # ===== SHADOW =====
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 180))
        self.setGraphicsEffect(shadow)

        # ===== MAIN LAYOUT =====
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        # ===== HEADER =====
        header = QHBoxLayout()

        title = QLabel("Settings")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(28, 28)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet("""
        QPushButton {
            border: none;
            background: transparent;
            font-size: 16px;
            color: #aaa;
        }
        QPushButton:hover {
            color: #ff5c5c;
        }
        """)

        header.addWidget(title)
        header.addStretch()
        header.addWidget(close_btn)
        layout.addLayout(header)

        # ===== FPS =====
        layout.addWidget(QLabel("FPS"))

        fps_row = QHBoxLayout()
        fps_row.setSpacing(6)

        self.fps_spin = QSpinBox()
        self.fps_spin.setRange(5, 240)
        self.fps_spin.setValue(self.settings.fps)
        self.fps_spin.setFixedWidth(90)
        fps_row.addWidget(self.fps_spin)

        for v in (30, 60, 120):
            btn = QPushButton(str(v))
            btn.setFixedSize(44, 30)
            btn.clicked.connect(partial(self.fps_spin.setValue, v))
            fps_row.addWidget(btn)

        fps_row.addStretch()
        layout.addLayout(fps_row)

        # ===== AUDIO =====
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
        self.out_btn = QPushButton()
        self.out_btn.setFixedHeight(32)
        self.out_btn.clicked.connect(self.choose_output_dir)
        layout.addWidget(self.out_btn)
        self.update_output_text()

        # ===== SAVE =====
        layout.addStretch()
        save_btn = QPushButton("Save")
        save_btn.setFixedHeight(38)
        save_btn.setStyleSheet("""
        QPushButton {
            background-color: #4aa3ff;
            color: black;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #6bb6ff;
        }
        """)
        save_btn.clicked.connect(self.save)
        layout.addWidget(save_btn)

        # ===== ANIMATION =====
        self.setWindowOpacity(0)
        self.anim = QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(180)
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        self.anim.start()

    # ===== HELPERS =====
    def update_output_text(self):
        path = str(self.settings.output_dir)
        metrics = self.out_btn.fontMetrics()
        self.out_btn.setText(
            metrics.elidedText(path, Qt.ElideMiddle, 280)
        )

    # ===== ACTIONS =====
    def choose_output_dir(self):
        path = QFileDialog.getExistingDirectory(
            self,
            "Select output folder",
            str(self.settings.output_dir)
        )
        if path:
            self.settings.output_dir = Path(path)
            self.update_output_text()

    def save(self):
        self.settings.fps = self.fps_spin.value()
        self.settings.audio_mode = self.audio_box.currentData()
        save_settings(self.settings)
        self.close()

    # ===== UX =====
    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()

    def focusOutEvent(self, event):
        self.close()
