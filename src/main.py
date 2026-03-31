"""
src/main.py
Entry point for the Hand Gesture Media Controller.

Usage (from project root):
    python src/main.py
    python src/main.py --camera 1 --cooldown 0.8
"""

import argparse
import sys
import time
import cv2

from gesture_detector import GestureDetector
from controls import YouTubeController
from utils import FPSCounter, draw_overlay


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Control any media player with hand gestures."
    )
    parser.add_argument("--camera",   type=int,   default=0,   help="Webcam index (default: 0)")
    parser.add_argument("--cooldown", type=float, default=1.0, help="Seconds between triggers (default: 1.0)")
    parser.add_argument("--width",    type=int,   default=640, help="Capture width (default: 640)")
    parser.add_argument("--height",   type=int,   default=480, help="Capture height (default: 480)")
    return parser.parse_args()


def find_working_camera(preferred: int = 0):
    """Scan camera indices 0-3 and return first working VideoCapture."""
    print("[INFO] Scanning for available cameras...")
    backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY] if sys.platform == "win32" else [cv2.CAP_ANY]

    for backend in backends:
        name = {cv2.CAP_DSHOW: "DirectShow", cv2.CAP_MSMF: "MediaFoundation"}.get(backend, "Auto")
        for idx in [preferred] + [i for i in range(4) if i != preferred]:
            cap = cv2.VideoCapture(idx + backend)
            if not cap.isOpened():
                cap.release()
                continue
            time.sleep(0.2)
            ret, frame = cap.read()
            if ret and frame is not None:
                print(f"[INFO] Camera {idx} ready  [{name}]")
                return cap, idx
            cap.release()

    raise RuntimeError(
        "No working camera found.\n"
        "  • Check the camera is connected and not used by another app\n"
        "  • Try:  python src/main.py --camera 1"
    )


class GestureMediaApp:
    """Main application — wires detector, controller, and display loop."""

    WINDOW_TITLE = "Hand Gesture Media Controller"

    def __init__(self, camera_index=0, cooldown=1.0, width=640, height=480):
        self.camera_index = camera_index
        self.cooldown     = cooldown
        self.width        = width
        self.height       = height

        print("[INFO] Initializing gesture detector...")
        self.detector    = GestureDetector()
        self.controller  = YouTubeController(cooldown_seconds=cooldown)
        self.fps_counter = FPSCounter()
        self.cap         = None

    def _open_camera(self):
        if sys.platform == "win32":
            self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
        else:
            self.cap = cv2.VideoCapture(self.camera_index)

        if not self.cap.isOpened():
            self.cap, _ = find_working_camera(self.camera_index)

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,  self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"[INFO] Camera ready: {w}x{h}")

    def _release(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()
        self.detector.release()
        cv2.destroyAllWindows()
        print("[INFO] Resources released.")

    def run(self):
        print("\n" + "="*50)
        print("  Hand Gesture Media Controller")
        print("="*50)
        print("  ✊ Fist       →  Pause")
        print("  ✋ Open hand  →  Play")
        print("  Press Q or Esc to quit")
        print("="*50 + "\n")

        try:
            self._open_camera()
        except RuntimeError as exc:
            print(f"[ERROR] {exc}", file=sys.stderr)
            sys.exit(1)

        action_label  = None
        fail_count    = 0

        while True:
            ret, frame = self.cap.read()
            if not ret or frame is None:
                fail_count += 1
                if fail_count > 30:
                    print("[ERROR] Camera lost. Exiting.")
                    break
                time.sleep(0.05)
                continue
            fail_count = 0

            frame     = cv2.flip(frame, 1)
            annotated, gesture = self.detector.process_frame(frame)
            result    = self.controller.handle_gesture(gesture)
            if result:
                action_label = result

            fps       = self.fps_counter.tick()
            annotated = draw_overlay(annotated, gesture, action_label, fps)

            cv2.imshow(self.WINDOW_TITLE, annotated)
            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), ord("Q"), 27):
                break
            if cv2.getWindowProperty(self.WINDOW_TITLE, cv2.WND_PROP_VISIBLE) < 1:
                break

        self._release()


def main():
    args = parse_args()
    GestureMediaApp(
        camera_index=args.camera,
        cooldown=args.cooldown,
        width=args.width,
        height=args.height,
    ).run()


if __name__ == "__main__":
    main()