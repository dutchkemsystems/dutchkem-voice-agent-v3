import pytest
import io
import uuid
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import UploadFile


# --- Voice Profile Tests ---


@pytest.mark.asyncio
async def test_clone_voice_returns_profile_id(client):
    """POST /voice/clone with audio file returns a profile_id."""
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
async def test_list_profiles_returns_list(client):
    """GET /voice/profiles returns a list."""
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


@pytest.mark.asyncio
async def test_synthesize_returns_audio(client):
    """POST /voice/synthesize with text and profile_id returns audio."""
    # First create a voice profile
    fake_audio = b"fake-wav-data"
    clone_resp = await client.post(
        "/voice/clone",
        files={"audio": ("test.wav", io.BytesIO(fake_audio), "audio/wav")},
        data={"user_id": str(uuid.uuid4())},
    )
    profile_id = clone_resp.json()["profile_id"]

    response = await client.post(
        "/voice/synthesize",
        json={
            "text": "Hello world",
            "profile_id": profile_id,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "audio_base64" in data
    assert isinstance(data["audio_base64"], str)


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
