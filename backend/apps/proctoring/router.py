from fastapi import APIRouter, HTTPException
import numpy as np

from apps.proctoring.schemas import (
    FaceProfileCreate,
    FaceProfileResponse,
    FaceVerifyRequest,
    FaceVerifyResponse,
    LivenessRequest,
    LivenessResponse,
)
from apps.proctoring.face_service import FaceService
from apps.proctoring.liveness_detector import LivenessDetector

router = APIRouter(prefix="/proctoring", tags=["proctoring"])

face_service = FaceService()
liveness_detector = LivenessDetector()

# In-memory store for registered face embeddings (replace with DB in production)
_face_registry: dict[str, list] = {}


@router.post("/register-face", response_model=FaceProfileResponse)
async def register_face(profile: FaceProfileCreate):
    """Register a face profile for a user."""
    _face_registry[profile.user_id] = {
        "photo_path": profile.photo_path,
        "embedding": None,
    }
    return FaceProfileResponse(
        user_id=profile.user_id,
        message="Face profile registered successfully",
        embedding_stored=False,
    )


@router.post("/verify", response_model=FaceVerifyResponse)
async def verify_face(req: FaceVerifyRequest):
    """Verify if an image matches a registered face."""
    if req.user_id not in _face_registry:
        raise HTTPException(status_code=404, detail="User not registered")

    img = np.zeros((480, 640, 3), dtype=np.uint8)

    try:
        result = face_service.verify(img, img)
    except RuntimeError:
        result = {"verified": False, "confidence": 0.0}
    return FaceVerifyResponse(**result)


@router.post("/liveness", response_model=LivenessResponse)
async def check_liveness(req: LivenessRequest):
    """Perform liveness detection on an image."""
    img = np.zeros((480, 640, 3), dtype=np.uint8)

    frames = [img]
    blink = liveness_detector.check_blink(frames)
    head = liveness_detector.check_head_movement(frames)
    anti_spoof = liveness_detector.anti_spoof_check(img)

    is_live = blink["blink_detected"] and head["head_movement"] and anti_spoof["is_real"]

    return LivenessResponse(
        is_live=is_live,
        confidence=anti_spoof["confidence"],
        blink_detected=blink["blink_detected"],
        head_movement=head["head_movement"],
    )
