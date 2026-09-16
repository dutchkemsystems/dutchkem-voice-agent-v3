import pytest
import io
import uuid
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import UploadFile


# --- Voice Profile Tests ---


@pytest.mark.asyncio
@patch("apps.voice.service.async_session")
async def test_clone_voice_returns_profile_id(mock_session_cls, client):
    """POST /voice/clone with audio file returns a profile_id."""
    mock_db = AsyncMock()
    mock_session_cls.return_value.__aenter__ = AsyncMock(return_value=mock_db)
    mock_session_cls.return_value.__aexit__ = AsyncMock(return_value=False)

    fake_audio = b"fake-wav-data"
    response = await client.post(
        "/voice/clone",
        files={"audio": ("test.wav", io.BytesIO(fake_audio), "audio/wav")},
        data={"user_id": str(uuid.uuid4())},
    )
    assert response.status_code == 200
    data = response.json()
    assert "profile_id" in data
    assert isinstance(data["profile_id"], str)


@pytest.mark.asyncio
async def test_clone_voice_rejects_missing_audio(client):
    """POST /voice/clone without audio returns 422."""
    response = await client.post(
        "/voice/clone",
        data={"user_id": str(uuid.uuid4())},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
@patch("apps.voice.service.async_session")
async def test_list_profiles_returns_list(mock_session_cls, client):
    """GET /voice/profiles returns a list."""
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result
    mock_session_cls.return_value.__aenter__ = AsyncMock(return_value=mock_db)
    mock_session_cls.return_value.__aexit__ = AsyncMock(return_value=False)

    response = await client.get("/voice/profiles")
    assert response.status_code == 200
    data = response.json()
    assert "profiles" in data
    assert isinstance(data["profiles"], list)


@pytest.mark.asyncio
async def test_synthesize_requires_text_and_profile_id(client):
    """POST /voice/synthesize without required fields returns 422."""
    response = await client.post("/voice/synthesize", json={})
    assert response.status_code == 422


# --- Schema Validation Tests ---


def test_voice_profile_schema_valid():
    from apps.voice.schemas import VoiceProfileResponse
    profile = VoiceProfileResponse(
        profile_id=str(uuid.uuid4()),
        user_id=str(uuid.uuid4()),
        name="Test Profile",
        created_at="2024-01-01T00:00:00",
    )
    assert profile.profile_id


def test_synthesize_request_schema_valid():
    from apps.voice.schemas import SynthesizeRequest
    req = SynthesizeRequest(
        text="Hello",
        profile_id=str(uuid.uuid4()),
    )
    assert req.text == "Hello"


# --- Service Tests ---


def test_chatterbox_engine_has_required_methods():
    from apps.voice.chatterbox_engine import ChatterboxEngine
    engine = ChatterboxEngine()
    assert hasattr(engine, "clone_and_synthesize")
    assert hasattr(engine, "load_model")


def test_f5tts_engine_has_required_methods():
    from apps.voice.f5tts_engine import F5TTSEngine
    engine = F5TTSEngine()
    assert hasattr(engine, "synthesize")
    assert hasattr(engine, "load_model")


def test_voice_service_has_required_methods():
    from apps.voice.service import VoiceService
    service = VoiceService()
    assert hasattr(service, "create_profile")
    assert hasattr(service, "synthesize")
    assert hasattr(service, "list_profiles")
    assert hasattr(service, "get_profile")
