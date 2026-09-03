import numpy as np
from typing import Dict, List

from apps.deepfake.voice_detector import VoiceDeepfakeDetector
from apps.deepfake.video_detector import VideoDeepfakeDetector


class DeepfakeDetector:
    """Combined deepfake detection pipeline for voice and video."""

    def __init__(
        self,
        voice_detector: VoiceDeepfakeDetector | None = None,
        video_detector: VideoDeepfakeDetector | None = None,
    ):
        self.voice_detector = voice_detector or VoiceDeepfakeDetector()
        self.video_detector = video_detector or VideoDeepfakeDetector()

    def detect_audio(self, audio: np.ndarray, sample_rate: int = 16000) -> Dict:
        """Detect voice deepfake artifacts."""
        return self.voice_detector.detect(audio, sample_rate=sample_rate)

    def detect_video(self, frames: List[np.ndarray]) -> Dict:
        """Detect video deepfake manipulation."""
        return self.video_detector.detect(frames)

    def detect_combined(
        self,
        audio: np.ndarray,
        frames: List[np.ndarray],
        sample_rate: int = 16000,
    ) -> Dict:
        """Run both voice and video detection, combine results."""
        voice_result = self.voice_detector.detect(audio, sample_rate=sample_rate)
        video_result = self.video_detector.detect(frames)

        is_fake = voice_result["is_deepfake"] or video_result["is_deepfake"]
        avg_confidence = (voice_result["confidence"] + video_result["confidence"]) / 2.0

        return {
            "is_deepfake": is_fake,
            "confidence": avg_confidence,
            "details": {
                "voice": voice_result,
                "video": video_result,
            },
        }
