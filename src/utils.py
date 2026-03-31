"""
utils.py
Shared helper utilities: overlay rendering, webcam helpers, FPS counter.
"""

import time
import cv2
import numpy as np


# ── Colour palette ────────────────────────────────────────────────────────────
COLOUR_BG      = (20,  20,  20)
COLOUR_GREEN   = (0,  220,  90)
COLOUR_YELLOW  = (0,  200, 255)
COLOUR_WHITE   = (240, 240, 240)
COLOUR_RED     = (60,   60, 220)
COLOUR_OVERLAY = (0,    0,   0)


class FPSCounter:
    """Simple rolling-average FPS counter."""

    def __init__(self, window: int = 30):
        self._times: list[float] = []
        self._window = window

    def tick(self) -> float:
        now = time.time()
        self._times.append(now)
        if len(self._times) > self._window:
            self._times.pop(0)
        if len(self._times) < 2:
            return 0.0
        return (len(self._times) - 1) / (self._times[-1] - self._times[0])


def draw_overlay(frame: np.ndarray, gesture: str | None,
                 action_label: str | None, fps: float) -> np.ndarray:
    """
    Draw a semi-transparent HUD on top of the webcam frame.
    Returns the annotated frame (in-place modification + return).
    """
    h, w = frame.shape[:2]

    # ── Semi-transparent top banner ───────────────────────────────────────────
    banner_h = 60
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, banner_h), COLOUR_OVERLAY, -1)
    cv2.addWeighted(overlay, 0.55, frame, 0.45, 0, frame)

    # Title
    cv2.putText(frame, "Hand Gesture YouTube Controller",
                (12, 38), cv2.FONT_HERSHEY_DUPLEX, 0.75,
                COLOUR_WHITE, 1, cv2.LINE_AA)

    # FPS badge (top-right)
    fps_text = f"FPS: {fps:.0f}"
    (tw, _), _ = cv2.getTextSize(fps_text, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1)
    cv2.putText(frame, fps_text, (w - tw - 12, 38),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, COLOUR_YELLOW, 1, cv2.LINE_AA)

    # ── Bottom action panel ───────────────────────────────────────────────────
    panel_h = 80
    overlay2 = frame.copy()
    cv2.rectangle(overlay2, (0, h - panel_h), (w, h), COLOUR_OVERLAY, -1)
    cv2.addWeighted(overlay2, 0.60, frame, 0.40, 0, frame)

    # Gesture name
    gesture_display = gesture if gesture else "—"
    cv2.putText(frame, f"Gesture: {gesture_display}",
                (12, h - panel_h + 28), cv2.FONT_HERSHEY_SIMPLEX,
                0.65, COLOUR_YELLOW, 1, cv2.LINE_AA)

    # Action label (larger, green)
    if action_label:
        cv2.putText(frame, action_label,
                    (12, h - panel_h + 60), cv2.FONT_HERSHEY_DUPLEX,
                    0.85, COLOUR_GREEN, 2, cv2.LINE_AA)
    else:
        cv2.putText(frame, "No action",
                    (12, h - panel_h + 60), cv2.FONT_HERSHEY_SIMPLEX,
                    0.65, (120, 120, 120), 1, cv2.LINE_AA)

    # ── Gesture legend (bottom-right) ─────────────────────────────────────────
    legend = [
        ("✊ Fist",      "Pause"),
        ("✋ Open Hand", "Play"),
    ]
    line_h = 18
    legend_x = w - 200
    legend_y = h - panel_h + 10
    for i, (g, a) in enumerate(legend):
        y = legend_y + i * line_h
        cv2.putText(frame, f"{g} → {a}", (legend_x, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42,
                    (180, 180, 180), 1, cv2.LINE_AA)

    # ── Quit hint ─────────────────────────────────────────────────────────────
    cv2.putText(frame, "Press Q to quit",
                (12, h - 6), cv2.FONT_HERSHEY_SIMPLEX,
                0.42, (100, 100, 100), 1, cv2.LINE_AA)

    return frame


def open_webcam(index: int = 0) -> cv2.VideoCapture:
    """
    Open the default webcam. Raises RuntimeError on failure.
    Tries indices 0–2 automatically if the requested one fails.
    """
    indices_to_try = [index] + [i for i in range(3) if i != index]
    for idx in indices_to_try:
        cap = cv2.VideoCapture(idx)
        if cap.isOpened():
            # Request a reasonable resolution
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            cap.set(cv2.CAP_PROP_FPS, 30)
            print(f"[INFO] Webcam opened on index {idx}")
            return cap
        cap.release()
    raise RuntimeError(
        "Could not open any webcam. "
        "Make sure a camera is connected and not used by another application."
    )