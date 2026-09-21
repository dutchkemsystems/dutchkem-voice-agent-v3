import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient, ASGITransport
from config.app import app
from config.database import get_db


# ---------------------------------------------------------------------------
# Autouse fixtures — wired into the app for every E2E test
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _override_db_dependency():
    """Replace get_db with an in-memory async mock so no real DB is touched."""

    async def _mock_get_db():
        session = AsyncMock()
        session.execute = AsyncMock()
        session.commit = AsyncMock()
        session.rollback = AsyncMock()
        session.close = AsyncMock()
        yield session

    app.dependency_overrides[get_db] = _mock_get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def _patch_voice_service_list_profiles():
    """Voice service uses async_session directly (not DI), so patch at import."""
    with patch(
        "apps.voice.router.voice_service.list_profiles", new_callable=AsyncMock
    ) as mock_lp:
        mock_lp.return_value = []
        yield mock_lp


@pytest.fixture(autouse=True)
def _patch_interview_engine():
    """Interview /start creates AutonomousInterviewEngine — mock its DB-heavy methods."""
    with patch("apps.interview.router.AutonomousInterviewEngine") as MockEngine:
        instance = MockEngine.return_value
        instance.start_interview = AsyncMock()
        instance.stop_interview = AsyncMock()
        instance.get_stats = AsyncMock(return_value={})
        yield MockEngine


# ---------------------------------------------------------------------------
# Session / client
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def event_loop():
    import asyncio

    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_db_session():
    session = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    return session


@pytest.fixture
def mock_redis():
    redis = AsyncMock()
    redis.get = AsyncMock(return_value=None)
    redis.set = AsyncMock(return_value=True)
    redis.delete = AsyncMock(return_value=True)
    redis.exists = AsyncMock(return_value=0)
    redis.expire = AsyncMock(return_value=True)
    return redis


@pytest.fixture
def mock_mongodb():
    db = MagicMock()
    db.__getitem__ = MagicMock(
        return_value=MagicMock(
            find_one=AsyncMock(return_value=None),
            find=AsyncMock(return_value=[]),
            insert_one=AsyncMock(inserted_id="mock_id"),
            update_one=AsyncMock(modified_count=1),
            delete_one=AsyncMock(deleted_count=1),
        )
    )
    return db


@pytest.fixture
def mock_voice_service():
    service = MagicMock()
    service.clone_voice = AsyncMock(
        return_value={
            "clone_id": "clone_test_001",
            "status": "completed",
            "quality_score": 0.92,
        }
    )
    service.synthesize = AsyncMock(return_value=b"mock-audio-bytes")
    service.detect_language = AsyncMock(
        return_value={"language": "en", "confidence": 0.95}
    )
    return service


@pytest.fixture
def mock_stt_service():
    service = MagicMock()
    service.transcribe = AsyncMock(
        return_value={
            "text": "Hello, this is a test transcription.",
            "language": "en",
            "confidence": 0.93,
            "segments": [
                {
                    "start": 0.0,
                    "end": 2.5,
                    "text": "Hello, this is a test transcription.",
                }
            ],
        }
    )
    return service


@pytest.fixture
def mock_interview_service():
    service = MagicMock()
    service.start_interview = AsyncMock(
        return_value={
            "interview_id": "intv_test_001",
            "status": "started",
            "questions": [],
        }
    )
    service.process_response = AsyncMock(
        return_value={
            "question_id": "q_001",
            "answer_evaluated": True,
            "score": 0.85,
            "next_question": "Tell me about your experience.",
        }
    )
    service.end_interview = AsyncMock(
        return_value={
            "interview_id": "intv_test_001",
            "status": "completed",
            "duration_seconds": 1200,
        }
    )
    return service


@pytest.fixture
def mock_scoring_service():
    service = MagicMock()
    service.calculate_score = AsyncMock(
        return_value={
            "candidate_id": "cand_001",
            "overall_score": 0.82,
            "breakdown": {
                "communication": 0.88,
                "technical": 0.75,
                "cultural_fit": 0.84,
            },
            "percentile": 78,
        }
    )
    return service


@pytest.fixture
def mock_deepfake_service():
    service = MagicMock()
    service.analyze = AsyncMock(
        return_value={
            "is_authentic": True,
            "confidence": 0.97,
            "flags": [],
            "analysis_time_ms": 245,
        }
    )
    return service


@pytest.fixture
def mock_trigger_service():
    service = MagicMock()
    service.detect_triggers = AsyncMock(
        return_value={
            "triggers": [],
            "risk_level": "low",
        }
    )
    service.activate_proctoring = AsyncMock(
        return_value={
            "active": True,
            "mode": "enhanced",
        }
    )
    return service


@pytest.fixture
def mock_orchestrator_service():
    service = MagicMock()
    service.route_to_agent = AsyncMock(
        return_value={
            "agent_id": "agent_001",
            "agent_type": "interviewer",
            "assigned": True,
        }
    )
    service.get_agent_status = AsyncMock(
        return_value={
            "agent_id": "agent_001",
            "status": "idle",
            "load": 0.2,
        }
    )
    return service


@pytest.fixture
def sample_interview_payload():
    return {
        "candidate_id": "cand_001",
        "position": "Senior Software Engineer",
        "interview_type": "technical",
        "language": "en",
    }


@pytest.fixture
def sample_voice_clone_payload():
    return {
        "reference_audio_b64": "base64encodedaudiodata==",
        "language": "en",
        "quality": "high",
    }


@pytest.fixture
def sample_transcription_payload():
    return {
        "audio_b64": "base64encodedaudiodata==",
        "language": "en",
        "model": "fast",
    }


@pytest.fixture
def sample_scoring_payload():
    return {
        "interview_id": "intv_test_001",
        "candidate_id": "cand_001",
        "responses": [
            {
                "question_id": "q_001",
                "answer": "I have 5 years of experience",
                "duration_seconds": 30,
            }
        ],
    }
