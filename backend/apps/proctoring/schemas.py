from pydantic import BaseModel


class FaceProfileCreate(BaseModel):
    user_id: str
    photo_path: str


class FaceProfileResponse(BaseModel):
    user_id: str
    message: str
    embedding_stored: bool


class FaceVerifyRequest(BaseModel):
    user_id: str
    image_data: str


class FaceVerifyResponse(BaseModel):
    verified: bool
    confidence: float


class LivenessRequest(BaseModel):
    user_id: str
    image_data: str


class LivenessResponse(BaseModel):
    is_live: bool
    confidence: float
    blink_detected: bool
    head_movement: bool
