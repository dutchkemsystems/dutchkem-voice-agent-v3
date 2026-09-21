import pytest
import numpy as np
from unittest.mock import patch, MagicMock, AsyncMock


# --- Model Tests ---


def test_face_profile_schema_creation():
    from apps.proctoring.schemas import FaceProfileCreate

    profile = FaceProfileCreate(user_id="user-123", photo_path="/tmp/face.jpg")
    assert profile.user_id == "user-123"
    assert profile.photo_path == "/tmp/face.jpg"


def test_face_verify_schema():
    from apps.proctoring.schemas import FaceVerifyRequest

    req = FaceVerifyRequest(user_id="user-123", image_data="base64data")
    assert req.user_id == "user-123"


def test_liveness_response_schema():
    from apps.proctoring.schemas import LivenessResponse

    resp = LivenessResponse(
        is_live=True, confidence=0.95, blink_detected=True, head_movement=True
    )
    assert resp.is_live is True
    assert resp.confidence == 0.95


# --- FaceService Tests (mocked InsightFace) ---


class TestFaceService:
    def test_detect_and_embed_returns_faces(self):
        from apps.proctoring import face_service
        from apps.proctoring.face_service import FaceService

        service = FaceService()
        mock_face = MagicMock()
        mock_face.bbox = np.array([0, 0, 100, 100])
        mock_face.embedding = np.random.rand(512)
        mock_face.age = 25
        mock_face.gender = 1

        with (
            patch.object(face_service, "HAS_INSIGHTFACE", True),
            patch.object(service, "_get_app") as mock_app,
        ):
            mock_analysis = MagicMock()
            mock_analysis.get.return_value = [mock_face]
            mock_app.return_value = mock_analysis

            image = np.zeros((480, 640, 3), dtype=np.uint8)
            results = service.detect_and_embed(image)

            assert len(results) == 1
            assert "bbox" in results[0]
            assert "embedding" in results[0]
            assert "age" in results[0]
            assert "gender" in results[0]

    def test_verify_same_person(self):
        from apps.proctoring.face_service import FaceService

        service = FaceService()
        embedding = np.random.rand(512).tolist()

        with patch.object(service, "detect_and_embed") as mock_detect:
            mock_detect.return_value = [
                {
                    "bbox": [0, 0, 100, 100],
                    "embedding": embedding,
                    "age": 25,
                    "gender": "M",
                }
            ]

            img1 = np.zeros((480, 640, 3), dtype=np.uint8)
            img2 = np.zeros((480, 640, 3), dtype=np.uint8)
            result = service.verify(img1, img2)

            assert result["verified"] is True
            assert result["confidence"] > 0.99

    def test_verify_different_persons(self):
        from apps.proctoring.face_service import FaceService

        service = FaceService()

        with patch.object(service, "detect_and_embed") as mock_detect:
            emb1 = np.zeros(512).tolist()
            emb2 = np.ones(512).tolist()
            mock_detect.side_effect = [
                [
                    {
                        "bbox": [0, 0, 100, 100],
                        "embedding": emb1,
                        "age": 25,
                        "gender": "M",
                    }
                ],
                [
                    {
                        "bbox": [0, 0, 100, 100],
                        "embedding": emb2,
                        "age": 30,
                        "gender": "F",
                    }
                ],
            ]

            img1 = np.zeros((480, 640, 3), dtype=np.uint8)
            img2 = np.zeros((480, 640, 3), dtype=np.uint8)
            result = service.verify(img1, img2)

            assert result["verified"] is False
            assert result["confidence"] < 0.5

    def test_verify_no_face_returns_false(self):
        from apps.proctoring.face_service import FaceService

        service = FaceService()

        with patch.object(service, "detect_and_embed") as mock_detect:
            mock_detect.return_value = []

            img1 = np.zeros((480, 640, 3), dtype=np.uint8)
            img2 = np.zeros((480, 640, 3), dtype=np.uint8)
            result = service.verify(img1, img2)

            assert result["verified"] is False
            assert result["confidence"] == 0.0


# --- LivenessDetector Tests ---


class TestLivenessDetector:
    def test_detect_blink(self):
        from apps.proctoring.liveness_detector import LivenessDetector

        detector = LivenessDetector()

        # Simulate frames with blink: eyes open then closed then open
        frame1 = np.zeros((480, 640, 3), dtype=np.uint8)
        frame2 = np.zeros((480, 640, 3), dtype=np.uint8)
        frame3 = np.zeros((480, 640, 3), dtype=np.uint8)

        with patch.object(detector, "_detect_landmarks") as mock_landmarks:
            # eye_aspect_ratio > threshold, then < threshold, then > threshold
            mock_landmarks.side_effect = [
                {"left_ear": 0.35, "right_ear": 0.35},  # open
                {"left_ear": 0.10, "right_ear": 0.10},  # closed (blink)
                {"left_ear": 0.35, "right_ear": 0.35},  # open
            ]

            result = detector.check_blink([frame1, frame2, frame3])
            assert result["blink_detected"] is True

    def test_no_blink_detected(self):
        from apps.proctoring.liveness_detector import LivenessDetector

        detector = LivenessDetector()

        frames = [np.zeros((480, 640, 3), dtype=np.uint8) for _ in range(5)]

        with patch.object(detector, "_detect_landmarks") as mock_landmarks:
            mock_landmarks.return_value = {"left_ear": 0.35, "right_ear": 0.35}

            result = detector.check_blink(frames)
            assert result["blink_detected"] is False

    def test_head_movement_detection(self):
        from apps.proctoring.liveness_detector import LivenessDetector

        detector = LivenessDetector()

        frame1 = np.zeros((480, 640, 3), dtype=np.uint8)
        frame2 = np.zeros((480, 640, 3), dtype=np.uint8)

        with patch.object(detector, "_get_head_pose") as mock_pose:
            mock_pose.side_effect = [
                {"yaw": 0, "pitch": 0, "roll": 0},
                {"yaw": 15, "pitch": 5, "roll": 0},  # moved
            ]

            result = detector.check_head_movement([frame1, frame2])
            assert result["head_movement"] is True

    def test_anti_spoofing_real_face(self):
        from apps.proctoring.liveness_detector import LivenessDetector

        detector = LivenessDetector()

        image = np.zeros((480, 640, 3), dtype=np.uint8)

        with patch.object(detector, "_analyze_texture") as mock_texture:
            mock_texture.return_value = {"real_score": 0.95}

            result = detector.anti_spoof_check(image)
            assert result["is_real"] is True
            assert result["confidence"] > 0.9

    def test_anti_spoofing_photo_attack(self):
        from apps.proctoring.liveness_detector import LivenessDetector

        detector = LivenessDetector()

        image = np.zeros((480, 640, 3), dtype=np.uint8)

        with patch.object(detector, "_analyze_texture") as mock_texture:
            mock_texture.return_value = {"real_score": 0.2}

            result = detector.anti_spoof_check(image)
            assert result["is_real"] is False


# --- Router/API Tests ---


@pytest.mark.asyncio
async def test_register_face_endpoint(client):
    from config.app import app
    from config.database import get_db

    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None
    mock_db.execute.return_value = mock_result

    async def override_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db
    try:
        response = await client.post(
            "/proctoring/register-face",
            json={"user_id": "user-123", "photo_path": "/tmp/face.jpg"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "user_id" in data
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_verify_face_endpoint(client):
    from config.app import app
    from config.database import get_db

    mock_db = AsyncMock()
    mock_face = MagicMock()
    mock_face.user_id = "user-123"
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = mock_face
    mock_db.execute.return_value = mock_result

    async def override_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db
    try:
        response = await client.post(
            "/proctoring/verify",
            json={"user_id": "user-123", "image_data": "base64data"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "verified" in data
        assert "confidence" in data
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_liveness_endpoint(client):
    import base64
    from unittest.mock import patch

    # Valid base64-encoded 1x1 white PNG (minimal valid image for liveness check)
    tiny_png = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
        b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00"
        b"\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00"
        b"\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    valid_b64 = base64.b64encode(tiny_png).decode()

    import numpy as np

    dummy_frame = np.zeros((1, 1, 3), dtype=np.uint8)

    with (
        patch("apps.proctoring.router._decode_image", return_value=dummy_frame),
        patch("apps.proctoring.router.liveness_detector") as mock_ld,
    ):
        mock_ld.check_blink.return_value = {"blink_detected": True}
        mock_ld.check_head_movement.return_value = {"head_movement": True}
        mock_ld.anti_spoof_check.return_value = {"is_real": True, "confidence": 0.95}

        response = await client.post(
            "/proctoring/liveness",
            json={"user_id": "user-123", "image_data": valid_b64},
        )
        assert response.status_code == 200
        data = response.json()
        assert "is_live" in data
        assert "blink_detected" in data
        assert "head_movement" in data
