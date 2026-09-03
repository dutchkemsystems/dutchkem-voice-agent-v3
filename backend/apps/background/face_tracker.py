import numpy as np
from typing import Optional

try:
    import mediapipe as mp
    HAS_MEDIAPIPE = True
except ImportError:
    HAS_MEDIAPIPE = False


class FaceTracker:
    """Real-time face tracking with MediaPipe and user verification."""

    def __init__(
        self,
        registered_users: Optional[dict[str, np.ndarray]] = None,
        max_faces: int = 2,
        similarity_threshold: float = 0.75,
    ):
        self.registered_users = registered_users or {}
        self.max_faces = max_faces
        self.similarity_threshold = similarity_threshold
        self.is_active = False
        self.current_faces: list = []
        self.tracked_user_id: Optional[str] = None
        self._face_detection = None

    def _get_face_detection(self):
        if self._face_detection is None and HAS_MEDIAPIPE:
            self._face_detection = mp.solutions.face_detection.FaceDetection(
                model_selection=0,
                min_detection_confidence=0.5,
            )
        return self._face_detection

    def _mediapipe_detect(self, frame: np.ndarray) -> list:
        """Detect faces using MediaPipe. Returns list of face dicts."""
        detection = self._get_face_detection()
        if detection is None:
            return []

        h, w = frame.shape[:2]
        rgb = frame[:, :, ::-1]  # BGR to RGB
        results = detection.process(rgb)

        if not results.detections:
            return []

        faces = []
        for det in results.detection:
            bbox_raw = det.location_data.relative_bounding_box
            x = max(0, int(bbox_raw.xmin * w))
            y = max(0, int(bbox_raw.ymin * h))
            bw = int(bbox_raw.width * w)
            bh = int(bbox_raw.height * h)
            confidence = det.score[0] if det.score else 0.0
            landmarks = [
                (lm.x * w, lm.y * h)
                for lm in det.location_data.relative_keypoints
            ]
            faces.append({
                "bbox": [x, y, x + bw, y + bh],
                "confidence": float(confidence),
                "landmarks": landmarks,
            })
        return faces

    def detect_faces(self, frame: np.ndarray) -> list:
        """Detect faces in frame, respecting max_faces limit."""
        faces = self._mediapipe_detect(frame)
        return faces[: self.max_faces]

    def _compute_similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """Cosine similarity between two embeddings."""
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)
        if norm1 == 0.0 or norm2 == 0.0:
            return 0.0
        return float(np.dot(emb1, emb2) / (norm1 * norm2))

    def verify_user(self, face_embedding: np.ndarray) -> tuple[Optional[str], float]:
        """Verify a face embedding against registered users. Returns (user_id, confidence)."""
        if not self.registered_users:
            return None, 0.0

        best_user = None
        best_score = 0.0

        for user_id, known_emb in self.registered_users.items():
            score = self._compute_similarity(face_embedding, known_emb)
            if score > best_score:
                best_score = score
                best_user = user_id

        if best_score >= self.similarity_threshold:
            return best_user, best_score
        return None, best_score

    def update_tracking(self, faces: list) -> None:
        """Update tracking state with detected faces."""
        self.current_faces = faces
        if faces:
            self.is_active = True
            self.tracked_user_id = faces[0].get("user_id")
        else:
            self.is_active = False
            self.tracked_user_id = None
