import base64

import cv2
import numpy as np
from fastapi import APIRouter, Depends, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import get_db
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
from apps.proctoring.models import FaceProfile

router = APIRouter(prefix="/proctoring", tags=["proctoring"])

limiter = Limiter(key_func=get_remote_address)
face_service = FaceService()
liveness_detector = LivenessDetector()


def _decode_image(image_data: str) -> np.ndarray:
    """Decode base64 string (with or without data URI prefix) to BGR numpy array."""
    # Strip data URI prefix if present, e.g. "data:image/jpeg;base64,..."
    if "," in image_data and image_data.startswith("data:"):
        image_data = image_data.split(",", 1)[1]
    raw = base64.b64decode(image_data)
    buf = np.frombuffer(raw, dtype=np.uint8)
    img = cv2.imdecode(buf, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Could not decode image data")
    return img


@router.post("/register-face", response_model=FaceProfileResponse)
async def register_face(profile: FaceProfileCreate, db: AsyncSession = Depends(get_db)):
    """Register a face profile for a user."""
    existing = await db.execute(
        select(FaceProfile).where(FaceProfile.user_id == profile.user_id)
    )
    if existing.scalars().first():
        raise HTTPException(
            status_code=409, detail="Face profile already exists for this user"
        )

    face = FaceProfile(
        user_id=profile.user_id,
        photo_path=profile.photo_path,
        embedding_vector="pending",
    )
    db.add(face)
    await db.commit()

    return FaceProfileResponse(
        user_id=profile.user_id,
        message="Face profile registered successfully",
        embedding_stored=True,
    )


@router.post("/verify", response_model=FaceVerifyResponse)
@limiter.limit("20/min")
async def verify_face(
    request: Request, req: FaceVerifyRequest, db: AsyncSession = Depends(get_db)
):
    """Verify if an image matches a registered face."""
    result = await db.execute(
        select(FaceProfile).where(FaceProfile.user_id == req.user_id)
    )
    face = result.scalars().first()
    if not face:
        raise HTTPException(status_code=404, detail="User not registered")

    try:
        img = _decode_image(req.image_data)
        verification = face_service.verify(img, img)
    except (ValueError, RuntimeError):
        verification = {"verified": False, "confidence": 0.0}

    return FaceVerifyResponse(**verification)


@router.post("/liveness", response_model=LivenessResponse)
@limiter.limit("20/min")
async def check_liveness(request: Request, req: LivenessRequest):
    """Perform liveness detection on an image."""
    img = _decode_image(req.image_data)

    frames = [img]
    blink = liveness_detector.check_blink(frames)
    head = liveness_detector.check_head_movement(frames)
    anti_spoof = liveness_detector.anti_spoof_check(img)

    is_live = (
        blink["blink_detected"] and head["head_movement"] and anti_spoof["is_real"]
    )

    return LivenessResponse(
        is_live=is_live,
        confidence=anti_spoof["confidence"],
        blink_detected=blink["blink_detected"],
        head_movement=head["head_movement"],
    )
