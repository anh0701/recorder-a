# recorder

```sh
┌──────────────┐
│   UI Layer   │  ← chọn vùng / preset
└──────┬───────┘
       │ (x,y,w,h)
┌──────▼───────┐
│ Capture Core │  ← FFmpeg x11grab
└──────┬───────┘
       │
┌──────▼───────┐
│ Encoder      │  ← H.264
└──────────────┘

```

## Linux

1. Chạy trên X11

2. Quay region

3. Có 2 mode:

- Free select (kéo chuột tự do) - Mode A

- Fixed aspect ratio (9:16, 16:9, 1:1…) - Mode B

### Techstack

| Thành phần     | Dùng                        |
| -------------- | --------------------------- |
| GUI            | **PySide6 (Qt for Python)** |
| Capture        | `ffmpeg` (x11grab)          |
| Window overlay | Qt `QWidget`                |
| Draw rectangle | `QPainter`                  |
| Build          | `pyinstaller`               |
| Linux package  | AppImage                    |

<!-- 
app/
├─ main.py
│   └─ tạo QApplication
│   └─ khởi động Overlay
│
├─ views/
│   ├─ overlay.py
│   │   ├─ Overlay (toàn màn hình)
│   │   ├─ cho phép kéo chọn vùng quay
│   │   └─ emit rect    ────────────────┐
│   │                                   │
│   ├─ recording_root.py                │
│   │   ├─ RecordingRootWindow ◀───────┘
│   │   ├─ chỉ vẽ VIỀN (ngoài vùng quay)
│   │   ├─ KHÔNG tham gia record
│   │   └─ always-on-top + click-through
│   │
│   └─ mode_bar.py
│       └─ thanh điều khiển (start/stop)      
│
└─ models/
   ├─ recorder.py
   │    ├─ nhận rect gốc từ Overlay
   │    ├─ gọi ffmpeg
   │    └─ QUAY CHỈ rect (KHÔNG viền)
   └─ settings.py
       └─ lưu mode, fps, audio, ratio...

-->
