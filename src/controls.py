"""
controls.py
Two gestures only:
  FIST      → Pause  (only if currently playing)
  OPEN HAND → Play   (only if currently paused)
"""

import time
import sys
import subprocess
import pyautogui

pyautogui.PAUSE = 0.0

from gesture_detector import GestureDetector

VK_MEDIA_PLAY_PAUSE = 0xB3
KEYEVENTF_KEYUP     = 0x0002

if sys.platform == "win32":
    import ctypes, ctypes.wintypes
    _user32 = ctypes.windll.user32

    def _send_media_key(vk):
        ctypes.windll.user32.keybd_event(vk, 0, 0, 0)
        time.sleep(0.05)
        ctypes.windll.user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)

def _send_play_pause():
    if sys.platform == "win32":
        _send_media_key(VK_MEDIA_PLAY_PAUSE)
    elif sys.platform == "darwin":
        subprocess.run(["osascript", "-e",
            'tell application "System Events" to key code 100'],
            capture_output=True)
    else:
        for cmd in [["playerctl", "play-pause"],
                    ["xdotool", "key", "XF86AudioPlay"]]:
            try:
                if subprocess.run(cmd, capture_output=True, timeout=2).returncode == 0:
                    return
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue


_STATE_UNKNOWN = "unknown"
_STATE_PLAYING = "playing"
_STATE_PAUSED  = "paused"


class YouTubeController:
    """
    FIST      → Pause  (ignored if already paused)
    OPEN HAND → Play   (ignored if already playing)
    Fires once — hand must change before same gesture fires again.
    """

    STABLE_SECONDS = 0.30
    COOLDOWN       = 1.0

    def __init__(self, cooldown_seconds: float = 1.0):
        self.COOLDOWN          = cooldown_seconds
        self._state            = _STATE_UNKNOWN
        self._last_seen        = ""
        self._stable_since     = 0.0
        self._fired            = ""
        self._last_action_time = 0.0
        self.last_action_label = ""

    def _ready(self) -> bool:
        return (time.time() - self._last_action_time) >= self.COOLDOWN

    def handle_gesture(self, gesture) -> str | None:
        now = time.time()
        g = gesture if gesture and gesture != GestureDetector.GESTURE_UNKNOWN else ""

        # Track stability
        if g != self._last_seen:
            self._last_seen    = g
            self._stable_since = now
            if g != self._fired:
                self._fired = ""

        if not g:
            return self.last_action_label

        # Already fired this gesture — wait for hand to change
        if g == self._fired:
            return self.last_action_label

        # Must hold gesture steady
        if (now - self._stable_since) < self.STABLE_SECONDS:
            return self.last_action_label

        # Cooldown
        if not self._ready():
            return self.last_action_label

        label = None

        if g == GestureDetector.GESTURE_FIST:
            if self._state != _STATE_PAUSED:
                _send_play_pause()
                self._state = _STATE_PAUSED
                label = "⏸  Paused"
                print("[ACTION] PAUSE sent")
            else:
                label = "⏸  Already paused"
                print("[ACTION] FIST ignored — already paused")

        elif g == GestureDetector.GESTURE_OPEN:
            if self._state != _STATE_PLAYING:
                _send_play_pause()
                self._state = _STATE_PLAYING
                label = "▶  Playing"
                print("[ACTION] PLAY sent")
            else:
                label = "▶  Already playing"
                print("[ACTION] OPEN ignored — already playing")

        if label:
            self._fired          = g
            self._last_action_time = now
            self.last_action_label = label

        return self.last_action_label