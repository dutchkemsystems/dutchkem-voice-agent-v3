import asyncio
import numpy as np
from typing import Callable, Optional

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False

from apps.background.face_tracker import FaceTracker


def _blur_numpy(frame: np.ndarray, ksize: int = 51) -> np.ndarray:
    """Numpy-based box blur fallback when cv2 is unavailable."""
    h, w, c = frame.shape
    pad = ksize // 2
    padded = np.pad(frame, ((pad, pad), (pad, pad), (0, 0)), mode="edge")
    result = np.zeros_like(frame, dtype=np.float64)
    for dy in range(ksize):
        for dx in range(ksize):
            result += padded[dy : dy + h, dx : dx + w].astype(np.float64)
    return (result / (ksize * ksize)).astype(np.uint8)


def _resize_numpy(frame: np.ndarray, width: int) -> np.ndarray:
    """Numpy-based nearest-neighbor resize fallback."""
    h, w = frame.shape[:2]
    scale = width / w
    new_h = max(1, int(h * scale))
    row_idx = (np.arange(new_h) / scale).astype(int).clip(0, h - 1)
    col_idx = (np.arange(width) / scale).astype(int).clip(0, w - 1)
    return frame[np.ix_(row_idx, col_idx)]


class VideoMonitor:
    """Continuous video monitoring with face detection, user verification, and privacy mode."""

    def __init__(
        self,
        camera_index: int = 0,
        target_fps: int = 30,
        max_width: int = 640,
        face_tracker: Optional[FaceTracker] = None,
    ):
        self.camera_index = camera_index
        self.target_fps = target_fps
        self.frame_interval = 1.0 / target_fps
        self.max_width = max_width
        self.cap = None
        self.is_running = False
        self.privacy_mode = False
        self.on_user_detected: Optional[Callable] = None
        self.on_user_lost: Optional[Callable] = None
        self.face_tracker = face_tracker or FaceTracker()

    async def start(self):
        """Start continuous video monitoring."""
        if not HAS_CV2:
            raise RuntimeError("opencv-python is required for video capture")
        self.cap = cv2.VideoCapture(self.camera_index)
        self.is_running = True

        while self.is_running:
            ret, frame = self.cap.read()
            if ret:
                await self._process_frame(frame)
            await asyncio.sleep(self.frame_interval)

    def stop(self):
        """Stop video monitoring."""
        self.is_running = False
        if self.cap:
            self.cap.release()

    async def _process_frame(self, frame: np.ndarray):
        """Process a single video frame: detect faces, verify user, track state."""
        if self.privacy_mode:
            frame = self._apply_privacy_filter(frame)

        downscaled = self._downscale_frame(frame)
        faces = self.face_tracker.detect_faces(downscaled)

        verified_faces = []
        for face in faces:
            user_id, confidence = self._verify_user_from_face(face)
            face["user_id"] = user_id
            face["verification_confidence"] = confidence
            verified_faces.append(face)

        self.face_tracker.update_tracking(verified_faces)

        if verified_faces and self.on_user_detected:
            first_user = verified_faces[0].get("user_id")
            if first_user:
                self.on_user_detected(first_user)

        if not verified_faces and self.on_user_lost:
            self.on_user_lost()

    def _verify_user_from_face(self, face: dict) -> tuple:
        """Stub: in production, compute embedding from face crop and verify."""
        return None, 0.0

    def _verify_user(self, frame: np.ndarray) -> tuple:
        """Verify registered user in frame. Returns (user_id, confidence)."""
        faces = self.face_tracker.detect_faces(frame)
        if not faces:
            return None, 0.0
        return self._verify_user_from_face(faces[0])

    def _detect_faces(self, frame: np.ndarray) -> list:
        """Detect faces in frame."""
        return self.face_tracker.detect_faces(frame)

    def set_privacy_mode(self, enabled: bool):
        """Toggle privacy mode (background blur)."""
        self.privacy_mode = enabled

    def _apply_privacy_filter(self, frame: np.ndarray) -> np.ndarray:
        """Apply privacy filter: blur background."""
        if HAS_CV2:
            return cv2.GaussianBlur(frame, (51, 51), 0)
        return _blur_numpy(frame, ksize=51)

    def _downscale_frame(self, frame: np.ndarray) -> np.ndarray:
        """Downscale frame to max_width for faster processing."""
        h, w = frame.shape[:2]
        if w <= self.max_width:
            return frame
        if HAS_CV2:
            scale = self.max_width / w
            new_h = int(h * scale)
            return cv2.resize(frame, (self.max_width, new_h))
        return _resize_numpy(frame, self.max_width)
