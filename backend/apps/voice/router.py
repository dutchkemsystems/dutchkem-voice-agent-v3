import base64
import logging
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Request
from fastapi.responses import StreamingResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from apps.voice.schemas import (
    CloneResponse,
    SynthesizeRequest,
    SynthesizeResponse,
    ListProfilesResponse,
    VoiceProfileResponse,
    TTSRequest,
    TTSResponse,
    TTSStreamRequest,
)
from apps.voice.service import voice_service
from apps.voice.tts_service import tts_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/voice", tags=["voice"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/clone", response_model=CloneResponse)
@limiter.limit("10/hour")
async def clone_voice(
    request: Request,
    audio: UploadFile = File(...),
    user_id: str = Form(...),
    name: str = Form(default=""),
):
    if not audio.filename:
        raise HTTPException(status_code=400, detail="Audio filename is required")

    audio_data = await audio.read()
    if not audio_data:
        raise HTTPException(status_code=400, detail="Empty audio file")

    profile_id = await voice_service.create_profile(
        user_id=user_id,
        audio_data=audio_data,
        name=name,
    )
    return CloneResponse(profile_id=profile_id)


@router.post("/synthesize", response_model=SynthesizeResponse)
@limiter.limit("15/min")
async def synthesize_voice(request: Request, synthesize_request: SynthesizeRequest):
    try:
        audio_bytes = await voice_service.synthesize(
            text=synthesize_request.text,
            profile_id=synthesize_request.profile_id,
            exaggeration=synthesize_request.exaggeration,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
    return SynthesizeResponse(audio_base64=audio_b64)


@router.get("/profiles", response_model=ListProfilesResponse)
async def list_profiles(user_id: str | None = None):
    profiles = await voice_service.list_profiles(user_id=user_id)
    return ListProfilesResponse(profiles=[VoiceProfileResponse(**p) for p in profiles])


@router.post("/tts", response_model=TTSResponse)
async def text_to_speech(request: TTSRequest):
    """Convert text to speech with accent/dialect support."""
    try:
        audio_bytes = await tts_service.synthesize_async(
            text=request.text,
            voice=request.voice,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS synthesis failed: {str(e)}")

    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
    return TTSResponse(audio_base64=audio_b64, duration_ms=0)


@router.post("/tts/stream")
async def text_to_speech_stream(request: TTSStreamRequest):
    """Stream text to speech audio chunks."""

    async def generate():
        async for chunk in tts_service.stream_synthesize(
            text=request.text,
            voice=request.voice,
        ):
            yield chunk

    return StreamingResponse(
        generate(),
        media_type="audio/wav",
        headers={"Content-Disposition": "attachment; filename=speech.wav"},
    )
