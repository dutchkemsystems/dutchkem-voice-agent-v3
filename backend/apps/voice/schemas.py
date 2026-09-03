from pydantic import BaseModel, Field
import uuid
from datetime import datetime


class VoiceProfileResponse(BaseModel):
    profile_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    name: str = ""
    reference_audio_path: str = ""
    embedding: list[float] | None = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class SynthesizeRequest(BaseModel):
    text: str
    profile_id: str
    exaggeration: float = 0.5


class SynthesizeResponse(BaseModel):
    audio_base64: str
    duration_ms: int = 0


class CloneResponse(BaseModel):
    profile_id: str


class ListProfilesResponse(BaseModel):
    profiles: list[VoiceProfileResponse]


class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    voice: str = Field(default="af_heart", description="Voice name or accent (nigerian, ghanaian, uk, us, japanese)")


class TTSResponse(BaseModel):
    audio_base64: str
    duration_ms: int = 0


class TTSStreamRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    voice: str = Field(default="af_heart")
