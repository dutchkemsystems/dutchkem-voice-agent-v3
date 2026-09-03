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
