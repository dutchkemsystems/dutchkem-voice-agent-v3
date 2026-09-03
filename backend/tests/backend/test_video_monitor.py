import pytest
import numpy as np
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock


# --- VideoMonitor Initialization Tests ---

def test_video_monitor_init_defaults():
    from apps.background.video_monitor import VideoMonitor
    monitor = VideoMonitor()
    assert monitor.camera_index == 0
    assert monitor.is_running is False
    assert monitor.on_user_detected is None
    assert monitor.on_user_lost is None
    assert monitor.cap is None


def test_video_monitor_init_custom_index():
    from apps.background.video_monitor import VideoMonitor
    monitor = VideoMonitor(camera_index=2)
    assert monitor.camera_index == 2


def test_video_monitor_init_privacy_mode_off():
    from apps.background.video_monitor import VideoMonitor
    monitor = VideoMonitor()
    assert monitor.privacy_mode is False


def test_video_monitor_init_frame_interval():
    from apps.background.video_monitor import VideoMonitor
    monitor = VideoMonitor()
    assert monitor.frame_interval > 0


# --- VideoMonitor Start/Stop Tests ---

@pytest.mark.asyncio
async def test_video_monitor_start_opens_camera():
    from apps.background.video_monitor import VideoMonitor
    monitor = VideoMonitor()

    mock_cap = MagicMock()
    mock_cap.read.return_value = (False, None)

    with patch("apps.background.video_monitor.cv2") as mock_cv2:
        mock_cv2.VideoCapture.return_value = mock_cap
        task = asyncio.create_task(monitor.start())
        await asyncio.sleep(0.05)
        monitor.stop()
        await asyncio.sleep(0.05)

        mock_cv2.VideoCapture.assert_called_once_with(0)


@pytest.mark.asyncio
async def test_video_monitor_stop_sets_running_false():
    from apps.background.video_monitor import VideoMonitor
    monitor = VideoMonitor()

    mock_cap = MagicMock()
    mock_cap.read.return_value = (False, None)

    with patch("apps.background.video_monitor.cv2") as mock_cv2:
        mock_cv2.VideoCapture.return_value = mock_cap
        task = asyncio.create_task(monitor.start())
        await asyncio.sleep(0.05)
        assert monitor.is_running is True
        monitor.stop()
        await asyncio.sleep(0.05)
        assert monitor.is_running is False


@pytest.mark.asyncio
async def test_video_monitor_stop_releases_cap():
    from apps.background.video_monitor import VideoMonitor
    monitor = VideoMonitor()

    mock_cap = MagicMock()
    mock_cap.read.return_value = (False, None)

    with patch("apps.background.video_monitor.cv2") as mock_cv2:
        mock_cv2.VideoCapture.return_value = mock_cap
        task = asyncio.create_task(monitor.start())
        await asyncio.sleep(0.05)
        monitor.stop()
        await asyncio.sleep(0.05)
        mock_cap.release.assert_called_once()


# --- VideoMonitor Frame Processing Tests ---

@pytest.mark.asyncio
async def test_video_monitor_processes_frames():
    from apps.background.video_monitor import VideoMonitor
    monitor = VideoMonitor()

    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    frames_to_return = [frame, frame]

    def read_side_effect():
        if frames_to_return:
            return (True, frames_to_return.pop(0))
        monitor.is_running = False
        return (False, None)

    mock_cap = MagicMock()
    mock_cap.read.side_effect = read_side_effect

    processed_frames = []

    async def mock_process(f):
        processed_frames.append(f)

    with patch("apps.background.video_monitor.cv2") as mock_cv2:
        mock_cv2.VideoCapture.return_value = mock_cap
        monitor._process_frame = mock_process
        await monitor.start()

        assert len(processed_frames) == 2


@pytest.mark.asyncio
async def test_video_monitor_user_detected_callback():
    from apps.background.video_monitor import VideoMonitor
    monitor = VideoMonitor()

    callback_called = []

    def on_user_detected(user_id):
        callback_called.append(user_id)

    monitor.on_user_detected = on_user_detected

    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    frames_to_return = [frame]

    def read_side_effect():
        if frames_to_return:
            return (True, frames_to_return.pop(0))
        monitor.is_running = False
        return (False, None)

    mock_cap = MagicMock()
    mock_cap.read.side_effect = read_side_effect

    with patch("apps.background.video_monitor.cv2") as mock_cv2:
        mock_cv2.VideoCapture.return_value = mock_cap
        with patch.object(monitor.face_tracker, "detect_faces") as mock_detect:
            mock_detect.return_value = [{"bbox": [0, 0, 100, 100]}]
            with patch.object(monitor, "_verify_user_from_face") as mock_verify:
                mock_verify.return_value = ("user-123", 0.95)
                await monitor.start()

    assert "user-123" in callback_called


# --- VideoMonitor Privacy Mode Tests ---

def test_video_monitor_privacy_mode_toggle():
    from apps.background.video_monitor import VideoMonitor
    monitor = VideoMonitor()
    assert monitor.privacy_mode is False
    monitor.set_privacy_mode(True)
    assert monitor.privacy_mode is True
    monitor.set_privacy_mode(False)
    assert monitor.privacy_mode is False


@pytest.mark.asyncio
async def test_video_monitor_privacy_blurs_background():
    from apps.background.video_monitor import VideoMonitor
    monitor = VideoMonitor()
    monitor.set_privacy_mode(True)

    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    result = monitor._apply_privacy_filter(frame)

    assert result.shape == frame.shape
    assert result.dtype == np.uint8


# --- VideoMonitor Frame Rate Tests ---

def test_video_monitor_frame_interval_configurable():
    from apps.background.video_monitor import VideoMonitor
    monitor = VideoMonitor(target_fps=15)
    expected_interval = 1.0 / 15.0
    assert abs(monitor.frame_interval - expected_interval) < 0.001


def test_video_monitor_default_fps():
    from apps.background.video_monitor import VideoMonitor
    monitor = VideoMonitor()
    expected_interval = 1.0 / 30.0
    assert abs(monitor.frame_interval - expected_interval) < 0.001


# --- FaceTracker Initialization Tests ---

def test_face_tracker_init():
    from apps.background.face_tracker import FaceTracker
    tracker = FaceTracker()
    assert tracker.is_active is False
    assert tracker.current_faces == []
    assert tracker.tracked_user_id is None


def test_face_tracker_init_with_registered_users():
    from apps.background.face_tracker import FaceTracker
    users = {"user-1": np.random.rand(128), "user-2": np.random.rand(128)}
    tracker = FaceTracker(registered_users=users)
    assert len(tracker.registered_users) == 2


# --- FaceTracker Detection Tests ---

def test_face_tracker_detect_faces_returns_list():
    from apps.background.face_tracker import FaceTracker
    tracker = FaceTracker()

    frame = np.zeros((480, 640, 3), dtype=np.uint8)

    with patch.object(tracker, "_mediapipe_detect") as mock_detect:
        mock_detect.return_value = [
            {"bbox": [100, 100, 200, 200], "confidence": 0.98, "landmarks": []}
        ]
        faces = tracker.detect_faces(frame)

        assert len(faces) == 1
        assert faces[0]["confidence"] > 0.9


def test_face_tracker_detect_faces_empty():
    from apps.background.face_tracker import FaceTracker
    tracker = FaceTracker()

    frame = np.zeros((480, 640, 3), dtype=np.uint8)

    with patch.object(tracker, "_mediapipe_detect") as mock_detect:
        mock_detect.return_value = []
        faces = tracker.detect_faces(frame)

        assert len(faces) == 0


def test_face_tracker_detect_faces_max_count():
    from apps.background.face_tracker import FaceTracker
    tracker = FaceTracker(max_faces=2)

    frame = np.zeros((480, 640, 3), dtype=np.uint8)

    with patch.object(tracker, "_mediapipe_detect") as mock_detect:
        mock_detect.return_value = [
            {"bbox": [10, 10, 50, 50], "confidence": 0.95, "landmarks": []},
            {"bbox": [60, 60, 100, 100], "confidence": 0.90, "landmarks": []},
            {"bbox": [110, 110, 150, 150], "confidence": 0.85, "landmarks": []},
        ]
        faces = tracker.detect_faces(frame)

        assert len(faces) == 2


# --- FaceTracker User Verification Tests ---

def test_face_tracker_verify_user_match():
    from apps.background.face_tracker import FaceTracker
    known_embedding = np.random.rand(128)
    tracker = FaceTracker(registered_users={"user-1": known_embedding})

    face_embedding = known_embedding + np.random.normal(0, 0.001, 128)

    with patch.object(tracker, "_compute_similarity") as mock_sim:
        mock_sim.return_value = 0.92
        user_id, confidence = tracker.verify_user(face_embedding)

        assert user_id == "user-1"
        assert confidence > 0.9


def test_face_tracker_verify_user_no_match():
    from apps.background.face_tracker import FaceTracker
    known_embedding = np.random.rand(128)
    tracker = FaceTracker(registered_users={"user-1": known_embedding})

    random_embedding = np.random.rand(128)

    with patch.object(tracker, "_compute_similarity") as mock_sim:
        mock_sim.return_value = 0.3
        user_id, confidence = tracker.verify_user(random_embedding)

        assert user_id is None
        assert confidence < 0.5


def test_face_tracker_verify_user_empty_registry():
    from apps.background.face_tracker import FaceTracker
    tracker = FaceTracker()

    embedding = np.random.rand(128)

    user_id, confidence = tracker.verify_user(embedding)

    assert user_id is None
    assert confidence == 0.0


# --- FaceTracker Tracking State Tests ---

def test_face_tracker_update_tracking():
    from apps.background.face_tracker import FaceTracker
    tracker = FaceTracker()

    faces = [
        {"bbox": [100, 100, 200, 200], "confidence": 0.95, "user_id": "user-1"},
    ]

    tracker.update_tracking(faces)

    assert tracker.is_active is True
    assert len(tracker.current_faces) == 1
    assert tracker.tracked_user_id == "user-1"


def test_face_tracker_update_tracking_no_faces():
    from apps.background.face_tracker import FaceTracker
    tracker = FaceTracker()
    tracker.is_active = True

    tracker.update_tracking([])

    assert tracker.is_active is False
    assert tracker.tracked_user_id is None


# --- FaceTracker Similarity Computation Tests ---

def test_compute_similarity_identical():
    from apps.background.face_tracker import FaceTracker
    tracker = FaceTracker()

    emb = np.random.rand(128)
    sim = tracker._compute_similarity(emb, emb)

    assert abs(sim - 1.0) < 0.001


def test_compute_similarity_orthogonal():
    from apps.background.face_tracker import FaceTracker
    tracker = FaceTracker()

    emb1 = np.array([1.0] + [0.0] * 127)
    emb2 = np.array([0.0] * 127 + [1.0])
    sim = tracker._compute_similarity(emb1, emb2)

    assert abs(sim) < 0.001


def test_compute_similarity_zero_vector():
    from apps.background.face_tracker import FaceTracker
    tracker = FaceTracker()

    emb1 = np.zeros(128)
    emb2 = np.random.rand(128)
    sim = tracker._compute_similarity(emb1, emb2)

    assert sim == 0.0


# --- Integration: VideoMonitor + FaceTracker ---

@pytest.mark.asyncio
async def test_video_monitor_uses_face_tracker():
    from apps.background.video_monitor import VideoMonitor
    from apps.background.face_tracker import FaceTracker

    tracker = FaceTracker()
    monitor = VideoMonitor(face_tracker=tracker)

    assert monitor.face_tracker is tracker


@pytest.mark.asyncio
async def test_video_monitor_frame_downscale():
    from apps.background.video_monitor import VideoMonitor
    monitor = VideoMonitor(max_width=320)

    frame = np.zeros((480, 640, 3), dtype=np.uint8)

    with patch("apps.background.video_monitor.cv2") as mock_cv2:
        mock_cv2.resize.return_value = np.zeros((240, 320, 3), dtype=np.uint8)
        result = monitor._downscale_frame(frame)

        assert result.shape[1] <= 320
        mock_cv2.resize.assert_called_once()
