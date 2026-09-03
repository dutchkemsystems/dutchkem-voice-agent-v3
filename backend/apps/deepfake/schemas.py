from pydantic import BaseModel, Field


class VoiceDetectionRequest(BaseModel):
    audio_path: str
    sample_rate: int = 16000


class VideoDetectionRequest(BaseModel):
    video_path: str


class DetectionResponse(BaseModel):
    is_deepfake: bool
    confidence: float = Field(ge=0.0, le=1.0)
    details: dict = Field(default_factory=dict)


class CombinedDetectionRequest(BaseModel):
    audio_path: str
    video_path: str
    sample_rate: int = 16000
