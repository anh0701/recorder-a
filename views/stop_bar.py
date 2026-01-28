from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout
from PySide6.QtCore import Qt


class StopBarWindow(QWidget):
    def __init__(self, x, y, on_stop):
        super().__init__()
        self.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnTopHint | 
            Qt.Tool
        )

        self.setStyleSheet("""
            QWidget { background: rgba(30,30,30,220); border-radius: 8px; }
            QLabel { color: red; font-weight: bold; }
            QPushButton { 
                background: rgba(255,80,80,200); 
                color: white; 
                border: none;
                padding: 6px 12px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background: rgba(255,100,100,220);
            }
        """)

        layout = QHBoxLayout(self)
        layout.addWidget(QLabel("● REC"))
        layout.addStretch()

        btn = QPushButton("STOP")
        btn.clicked.connect(on_stop)
        layout.addWidget(btn)

        self.move(x, y)
        self.show()
