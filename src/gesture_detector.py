"""
gesture_detector.py
Only two gestures: FIST and OPEN_HAND.
"""

import cv2

try:
    import mediapipe as mp
    _hands_module   = mp.solutions.hands
    _drawing_module = mp.solutions.drawing_utils
    _drawing_styles = mp.solutions.drawing_styles
    _USE_NEW_API = False
    print("[INFO] Using MediaPipe legacy solutions API")
except AttributeError:
    import mediapipe as mp
    from mediapipe.tasks import python as mp_python
    from mediapipe.tasks.python import vision as mp_vision
    from mediapipe.tasks.python.vision import HandLandmarker, HandLandmarkerOptions
    _USE_NEW_API = True
    print("[INFO] Using MediaPipe Tasks API (new)")

_FINGER_TIPS = [8, 12, 16, 20]
_FINGER_PIPS = [6, 10, 14, 18]
_THUMB_TIP   = 4
_THUMB_MCP   = 2

_HAND_CONNECTIONS = [
    (0,1),(1,2),(2,3),(3,4),
    (0,5),(5,6),(6,7),(7,8),
    (5,9),(9,10),(10,11),(11,12),
    (9,13),(13,14),(14,15),(15,16),
    (13,17),(17,18),(18,19),(19,20),
    (0,17),
]


def _classify(lm) -> str:
    # Count how many of the 4 fingers are extended (tip above PIP)
    fingers_up = sum(lm[tip].y < lm[pip].y for tip, pip in zip(_FINGER_TIPS, _FINGER_PIPS))
    thumb_extended = abs(lm[_THUMB_TIP].x - lm[_THUMB_MCP].x) > 0.06

    # FIST: all fingers curled
    if fingers_up == 0:
        return GestureDetector.GESTURE_FIST

    # OPEN HAND: all 4 fingers up
    if fingers_up == 4:
        return GestureDetector.GESTURE_OPEN

    return GestureDetector.GESTURE_UNKNOWN


def _draw_landmarks_new(frame, landmarks):
    h, w = frame.shape[:2]
    pts = [(int(lm.x * w), int(lm.y * h)) for lm in landmarks]
    for a, b in _HAND_CONNECTIONS:
        cv2.line(frame, pts[a], pts[b], (0, 200, 80), 2)
    for p in pts:
        cv2.circle(frame, p, 4, (0, 255, 180), -1)
        cv2.circle(frame, p, 4, (0, 100, 60),   1)


class GestureDetector:

    GESTURE_FIST    = "FIST"
    GESTURE_OPEN    = "OPEN_HAND"
    GESTURE_UNKNOWN = "UNKNOWN"

    def __init__(self, max_hands=1, detection_confidence=0.7, tracking_confidence=0.5):
        self._use_new_api = _USE_NEW_API

        if not _USE_NEW_API:
            self._hands    = _hands_module.Hands(
                static_image_mode=False,
                max_num_hands=max_hands,
                min_detection_confidence=detection_confidence,
                min_tracking_confidence=tracking_confidence,
            )
            self._drawing  = _drawing_module
            self._styles   = _drawing_styles
            self._mp_hands = _hands_module
        else:
            import urllib.request, os, tempfile
            model_path = os.path.join(tempfile.gettempdir(), "hand_landmarker.task")
            if not os.path.exists(model_path):
                print("[INFO] Downloading hand_landmarker.task (~8 MB)…")
                url = (
                    "https://storage.googleapis.com/mediapipe-models/"
                    "hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
                )
                urllib.request.urlretrieve(url, model_path)
                print("[INFO] Model downloaded.")

            options = HandLandmarkerOptions(
                base_options=mp_python.BaseOptions(model_asset_path=model_path),
                num_hands=max_hands,
                min_hand_detection_confidence=detection_confidence,
                min_hand_presence_confidence=detection_confidence,
                min_tracking_confidence=tracking_confidence,
                running_mode=mp_vision.RunningMode.IMAGE,
            )
            self._landmarker   = HandLandmarker.create_from_options(options)
            self._mp_image_cls = mp.Image
            self._mp_image_fmt = mp.ImageFormat.SRGB

    def process_frame(self, frame):
        if not self._use_new_api:
            return self._process_legacy(frame)
        return self._process_new(frame)

    def _process_legacy(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        results = self._hands.process(rgb)
        rgb.flags.writeable = True
        gesture   = None
        annotated = frame.copy()
        if results.multi_hand_landmarks:
            for hand_lm in results.multi_hand_landmarks:
                self._drawing.draw_landmarks(
                    annotated, hand_lm,
                    self._mp_hands.HAND_CONNECTIONS,
                    self._styles.get_default_hand_landmarks_style(),
                    self._styles.get_default_hand_connections_style(),
                )
                gesture = _classify(hand_lm.landmark)
        return annotated, gesture

    def _process_new(self, frame):
        rgb    = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_img = self._mp_image_cls(image_format=self._mp_image_fmt, data=rgb)
        result = self._landmarker.detect(mp_img)
        gesture   = None
        annotated = frame.copy()
        if result.hand_landmarks:
            for hand_lm in result.hand_landmarks:
                _draw_landmarks_new(annotated, hand_lm)
                gesture = _classify(hand_lm)
        return annotated, gesture

    def release(self):
        if not self._use_new_api:
            self._hands.close()
        else:
            self._landmarker.close()