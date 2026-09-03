import pytest
import numpy as np
from unittest.mock import patch, MagicMock


# --- VoiceDeepfakeDetector Tests ---

class TestVoiceDeepfakeDetector:
    """Tests for voice deepfake detection via spectral, prosody, and breathing analysis."""

    def test_returns_is_deepfake_field(self):
        from apps.deepfake.voice_detector import VoiceDeepfakeDetector
        detector = VoiceDeepfakeDetector()
        audio = np.random.rand(16000).astype(np.float32)
        result = detector.detect(audio, sample_rate=16000)
        assert "is_deepfake" in result
        assert "confidence" in result
        assert "details" in result

    def test_detects_clean_audio_as_real(self):
        from apps.deepfake.voice_detector import VoiceDeepfakeDetector
        detector = VoiceDeepfakeDetector()
        # Generate low-frequency dominated audio (human-like)
        t = np.linspace(0, 1, 16000, dtype=np.float32)
        audio = np.sin(2 * np.pi * 200 * t) * 0.5
        result = detector.detect(audio, sample_rate=16000)
        assert result["is_deepfake"] is False
        assert result["confidence"] > 0.5

    def test_detects_high_freq_anomaly_as_fake(self):
        from apps.deepfake.voice_detector import VoiceDeepfakeDetector
        detector = VoiceDeepfakeDetector()
        # Generate audio with excessive high-frequency content near Nyquist (synthetic artifact)
        t = np.linspace(0, 1, 16000, dtype=np.float32)
        audio = np.sin(2 * np.pi * 7500 * t) * 0.8
        result = detector.detect(audio, sample_rate=16000)
        assert result["is_deepfake"] is True
        assert result["confidence"] < 0.8

    def test_spectral_features_extracted(self):
        from apps.deepfake.voice_detector import VoiceDeepfakeDetector
        detector = VoiceDeepfakeDetector()
        audio = np.random.rand(16000).astype(np.float32)
        result = detector.detect(audio, sample_rate=16000)
        assert "spectral" in result["details"]
        assert "anomaly_score" in result["details"]["spectral"]
        assert "high_freq_energy" in result["details"]["spectral"]

    def test_prosody_features_extracted(self):
        from apps.deepfake.voice_detector import VoiceDeepfakeDetector
        detector = VoiceDeepfakeDetector()
        audio = np.random.rand(16000).astype(np.float32)
        result = detector.detect(audio, sample_rate=16000)
        assert "prosody" in result["details"]
        assert "unnatural_score" in result["details"]["prosody"]

    def test_breathing_features_extracted(self):
        from apps.deepfake.voice_detector import VoiceDeepfakeDetector
        detector = VoiceDeepfakeDetector()
        audio = np.random.rand(16000).astype(np.float32)
        result = detector.detect(audio, sample_rate=16000)
        assert "breathing" in result["details"]
        assert "absence_score" in result["details"]["breathing"]

    def test_confidence_between_0_and_1(self):
        from apps.deepfake.voice_detector import VoiceDeepfakeDetector
        detector = VoiceDeepfakeDetector()
        audio = np.random.rand(16000).astype(np.float32)
        result = detector.detect(audio, sample_rate=16000)
        assert 0.0 <= result["confidence"] <= 1.0


# --- VideoDeepfakeDetector Tests ---

class TestVideoDeepfakeDetector:
    """Tests for video deepfake detection via temporal and visual analysis."""

    def test_returns_is_deepfake_field(self):
        from apps.deepfake.video_detector import VideoDeepfakeDetector
        detector = VideoDeepfakeDetector()
        frames = [np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8) for _ in range(10)]
        result = detector.detect(frames)
        assert "is_deepfake" in result
        assert "confidence" in result
        assert "details" in result

    def test_detects_consistent_frames_as_real(self):
        from apps.deepfake.video_detector import VideoDeepfakeDetector
        detector = VideoDeepfakeDetector()
        # Identical frames = real (no manipulation artifacts)
        frame = np.ones((480, 640, 3), dtype=np.uint8) * 128
        frames = [frame.copy() for _ in range(10)]
        result = detector.detect(frames)
        assert result["is_deepfake"] is False

    def test_detects_flickering_as_fake(self):
        from apps.deepfake.video_detector import VideoDeepfakeDetector
        detector = VideoDeepfakeDetector()
        # Irregular brightness changes = high temporal CV = deepfake artifact
        rng = np.random.RandomState(42)
        frames = []
        for i in range(20):
            # Vary brightness irregularly: some frames very bright, some very dark, some medium
            brightness = int(rng.choice([10, 50, 128, 200, 250]))
            frame = rng.randint(
                max(0, brightness - 20), min(255, brightness + 20), (480, 640, 3), dtype=np.uint8
            )
            frames.append(frame)
        result = detector.detect(frames)
        assert result["is_deepfake"] is True

    def test_temporal_consistency_extracted(self):
        from apps.deepfake.video_detector import VideoDeepfakeDetector
        detector = VideoDeepfakeDetector()
        frames = [np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8) for _ in range(10)]
        result = detector.detect(frames)
        assert "temporal" in result["details"]
        assert "consistency_score" in result["details"]["temporal"]

    def test_edge_artifacts_extracted(self):
        from apps.deepfake.video_detector import VideoDeepfakeDetector
        detector = VideoDeepfakeDetector()
        frames = [np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8) for _ in range(10)]
        result = detector.detect(frames)
        assert "edge" in result["details"]
        assert "artifact_score" in result["details"]["edge"]

    def test_confidence_between_0_and_1(self):
        from apps.deepfake.video_detector import VideoDeepfakeDetector
        detector = VideoDeepfakeDetector()
        frames = [np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8) for _ in range(10)]
        result = detector.detect(frames)
        assert 0.0 <= result["confidence"] <= 1.0

    def test_empty_frames_returns_error(self):
        from apps.deepfake.video_detector import VideoDeepfakeDetector
        detector = VideoDeepfakeDetector()
        result = detector.detect([])
        assert result["is_deepfake"] is False
        assert result["confidence"] == 0.0


# --- DeepfakeDetector (Combined Pipeline) Tests ---

class TestDeepfakeDetectorPipeline:
    """Tests for the combined deepfake detection pipeline."""

    def test_detect_audio_delegates_to_voice_detector(self):
        from apps.deepfake.detector import DeepfakeDetector
        pipeline = DeepfakeDetector()
        audio = np.random.rand(16000).astype(np.float32)
        result = pipeline.detect_audio(audio, sample_rate=16000)
        assert "is_deepfake" in result
        assert "confidence" in result

    def test_detect_video_delegates_to_video_detector(self):
        from apps.deepfake.detector import DeepfakeDetector
        pipeline = DeepfakeDetector()
        frames = [np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8) for _ in range(10)]
        result = pipeline.detect_video(frames)
        assert "is_deepfake" in result
        assert "confidence" in result

    def test_detect_combined_uses_both(self):
        from apps.deepfake.detector import DeepfakeDetector
        pipeline = DeepfakeDetector()
        audio = np.random.rand(16000).astype(np.float32)
        frames = [np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8) for _ in range(10)]
        result = pipeline.detect_combined(audio, frames, sample_rate=16000)
        assert "is_deepfake" in result
        assert "confidence" in result
        assert "voice" in result["details"]
        assert "video" in result["details"]

    def test_combined_marks_fake_if_either_is_fake(self):
        from apps.deepfake.detector import DeepfakeDetector
        from apps.deepfake.voice_detector import VoiceDeepfakeDetector
        from apps.deepfake.video_detector import VideoDeepfakeDetector
        pipeline = DeepfakeDetector()

        audio = np.random.rand(16000).astype(np.float32)
        frames = [np.ones((480, 640, 3), dtype=np.uint8) * 128 for _ in range(10)]

        # Patch voice detector to return fake
        with patch.object(VoiceDeepfakeDetector, 'detect', return_value={
            "is_deepfake": True, "confidence": 0.2, "details": {}
        }), patch.object(VideoDeepfakeDetector, 'detect', return_value={
            "is_deepfake": False, "confidence": 0.9, "details": {}
        }):
            result = pipeline.detect_combined(audio, frames, sample_rate=16000)
            assert result["is_deepfake"] is True

    def test_combined_confidence_is_average(self):
        from apps.deepfake.detector import DeepfakeDetector
        pipeline = DeepfakeDetector()
        audio = np.random.rand(16000).astype(np.float32)
        frames = [np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8) for _ in range(10)]
        result = pipeline.detect_combined(audio, frames, sample_rate=16000)
        voice_conf = result["details"]["voice"]["confidence"]
        video_conf = result["details"]["video"]["confidence"]
        expected_conf = (voice_conf + video_conf) / 2.0
        assert abs(result["confidence"] - expected_conf) < 0.01


# --- Schema Tests ---

class TestDeepfakeSchemas:
    """Tests for Pydantic schemas used by the deepfake detection service."""

    def test_voice_detection_request(self):
        from apps.deepfake.schemas import VoiceDetectionRequest
        req = VoiceDetectionRequest(audio_path="/tmp/audio.wav", sample_rate=16000)
        assert req.audio_path == "/tmp/audio.wav"
        assert req.sample_rate == 16000

    def test_video_detection_request(self):
        from apps.deepfake.schemas import VideoDetectionRequest
        req = VideoDetectionRequest(video_path="/tmp/video.mp4")
        assert req.video_path == "/tmp/video.mp4"

    def test_detection_response(self):
        from apps.deepfake.schemas import DetectionResponse
        resp = DetectionResponse(
            is_deepfake=True,
            confidence=0.75,
            details={"reason": "spectral anomaly"}
        )
        assert resp.is_deepfake is True
        assert resp.confidence == 0.75

    def test_combined_detection_request(self):
        from apps.deepfake.schemas import CombinedDetectionRequest
        req = CombinedDetectionRequest(
            audio_path="/tmp/audio.wav",
            video_path="/tmp/video.mp4",
            sample_rate=16000
        )
        assert req.audio_path == "/tmp/audio.wav"
        assert req.video_path == "/tmp/video.mp4"
