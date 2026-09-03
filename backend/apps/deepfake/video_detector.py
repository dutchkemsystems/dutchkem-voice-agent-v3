import numpy as np
from typing import Dict, List


class VideoDeepfakeDetector:
    """Detect video deepfake manipulation via temporal and edge artifact analysis."""

    def __init__(self, flicker_threshold: float = 0.3):
        self.flicker_threshold = flicker_threshold

    def detect(self, frames: List[np.ndarray]) -> Dict:
        """Detect video deepfake manipulation."""
        if not frames:
            return {
                "is_deepfake": False,
                "confidence": 0.0,
                "details": {
                    "temporal": {"consistency_score": 0.0},
                    "edge": {"artifact_score": 0.0},
                },
            }

        temporal_features = self._analyze_temporal_consistency(frames)
        edge_features = self._analyze_edge_artifacts(frames)

        is_fake = (
            temporal_features["consistency_score"] > self.flicker_threshold
            or edge_features["artifact_score"] > self.flicker_threshold
        )

        max_score = max(
            temporal_features["consistency_score"],
            edge_features["artifact_score"],
        )

        return {
            "is_deepfake": is_fake,
            "confidence": 1.0 - max_score,
            "details": {
                "temporal": temporal_features,
                "edge": edge_features,
            },
        }

    def _analyze_temporal_consistency(self, frames: List[np.ndarray]) -> Dict:
        """Analyze frame-to-frame consistency for temporal artifacts."""
        if len(frames) < 2:
            return {"consistency_score": 0.0, "mean_diff": 0.0}

        diffs = []
        for i in range(1, len(frames)):
            prev_gray = self._to_gray(frames[i - 1])
            curr_gray = self._to_gray(frames[i])
            diff = float(np.mean(np.abs(curr_gray - prev_gray)))
            diffs.append(diff)

        diffs_array = np.array(diffs)
        mean_diff = float(np.mean(diffs_array))
        std_diff = float(np.std(diffs_array))

        if mean_diff == 0:
            consistency_score = 0.0
        else:
            cv = std_diff / mean_diff
            consistency_score = min(float(cv), 1.0)

        return {"consistency_score": consistency_score, "mean_diff": mean_diff}

    def _analyze_edge_artifacts(self, frames: List[np.ndarray]) -> Dict:
        """Detect edge inconsistencies typical of face-swap deepfakes."""
        if not frames:
            return {"artifact_score": 0.0, "edge_variance": 0.0}

        edge_variances = []
        for frame in frames:
            gray = self._to_gray(frame)
            magnitude = self._edge_magnitude(gray)
            edge_variances.append(float(np.var(magnitude)))

        if len(edge_variances) < 2:
            return {"artifact_score": 0.0, "edge_variance": 0.0}

        edge_var_array = np.array(edge_variances)
        mean_var = float(np.mean(edge_var_array))
        std_var = float(np.std(edge_var_array))

        if mean_var == 0:
            artifact_score = 0.0
        else:
            cv = std_var / mean_var
            artifact_score = min(float(cv), 1.0)

        return {"artifact_score": artifact_score, "edge_variance": mean_var}

    def _to_gray(self, frame: np.ndarray) -> np.ndarray:
        """Convert RGB frame to grayscale."""
        if frame.ndim == 2:
            return frame.astype(np.float32)
        return np.mean(frame.astype(np.float32), axis=2)

    def _edge_magnitude(self, gray: np.ndarray) -> np.ndarray:
        """Compute edge magnitude using vectorized Sobel-like differencing."""
        if gray.shape[0] < 2 or gray.shape[1] < 2:
            return np.zeros_like(gray)

        dx = np.abs(gray[:, 1:].astype(np.float32) - gray[:, :-1].astype(np.float32))
        dy = np.abs(gray[1:, :].astype(np.float32) - gray[:-1, :].astype(np.float32))

        min_h = min(dx.shape[0], dy.shape[0])
        min_w = min(dx.shape[1], dy.shape[1])

        magnitude = np.sqrt(dx[:min_h, :min_w] ** 2 + dy[:min_h, :min_w] ** 2)
        return magnitude
