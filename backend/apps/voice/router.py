import base64
import logging
from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from apps.voice.schemas import (
    CloneResponse,
    SynthesizeRequest,
    SynthesizeResponse,
    ListProfilesResponse,
    VoiceProfileResponse,
)
from apps.voice.service import voice_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/voice", tags=["voice"])


@router.post("/clone", response_model=CloneResponse)
async def clone_voice(
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
async def synthesize_voice(request: SynthesizeRequest):
    try:
        audio_bytes = await voice_service.synthesize(
            text=request.text,
            profile_id=request.profile_id,
            exaggeration=request.exaggeration,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
    return SynthesizeResponse(audio_base64=audio_b64)


@router.get("/profiles", response_model=ListProfilesResponse)
async def list_profiles(user_id: str | None = None):
    profiles = await voice_service.list_profiles(user_id=user_id)
    return ListProfilesResponse(
        profiles=[VoiceProfileResponse(**p) for p in profiles]
    )
