# ✋ Hand Gesture Media Controller

Control any media player on your laptop with just two hand gestures — no keyboard, no mouse.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-green)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10+-orange)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

---

## Gestures

| Gesture | Action |
|---|---|
| ✊ Fist — all fingers curled | ⏸ Pause |
| ✋ Open hand — all 4 fingers up | ▶ Play |

Works with **any** media player: VLC, Windows Media Player, YouTube, Netflix, Spotify, PotPlayer, MPV, and more.

---

## Folder Structure

```
hand-gesture-media-controller/
│
├── src/                        # All source code
│   ├── __init__.py
│   ├── main.py                 # Entry point & app class
│   ├── gesture_detector.py     # MediaPipe hand tracking + classification
│   ├── controls.py             # Gesture → media key mapping
│   └── utils.py                # FPS counter, HUD overlay, webcam helper
│
├── tests/                      # Unit tests
│   ├── __init__.py
│   └── test_gesture_detector.py
│
├── assets/                     # Images, GIFs for documentation
│   └── README.md
│
├── .vscode/                    # VS Code workspace settings
│   ├── settings.json
│   └── extensions.json
│
├── .gitignore
├── CHANGELOG.md
├── README.md
├── requirements.txt            # Runtime dependencies
└── requirements-dev.txt        # Dev/test dependencies
```

---

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/yourname/hand-gesture-media-controller.git
cd hand-gesture-media-controller
```

### 2. Create virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

> **Linux only:** `sudo apt install python3-tk python3-xlib`
>
> **macOS only:** Grant Camera + Accessibility permissions to Terminal in System Settings.

---

## Run

```bash
python src/main.py
```

### Options

| Flag | Default | Description |
|---|---|---|
| `--camera INDEX` | `0` | Webcam index |
| `--cooldown SECS` | `1.0` | Seconds between repeated triggers |
| `--width W` | `640` | Capture width |
| `--height H` | `480` | Capture height |

```bash
python src/main.py --camera 1 --cooldown 0.8
```

---

## Run Tests

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

---

## How to Use

1. Open any media player and start playing something
2. Run `python src/main.py`
3. Show your hand to the webcam:
   - ✊ **Fist** → pauses the media
   - ✋ **Open hand** → resumes the media
4. Press **Q** or **Esc** to quit

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Camera won't open | Try `--camera 1` or close other apps using it |
| Gestures don't control media | Make sure media is playing before running the script |
| Low FPS | Lower `--width 320 --height 240` |
| Pylance import warnings in VS Code | Press `Ctrl+Shift+P` → Python: Select Interpreter → pick venv |

---

## License

MIT