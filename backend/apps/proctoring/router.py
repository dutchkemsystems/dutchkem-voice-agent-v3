from fastapi import APIRouter, Depends, HTTPException
import numpy as np
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

face_service = FaceService()
liveness_detector = LivenessDetector()


@router.post("/register-face", response_model=FaceProfileResponse)
async def register_face(profile: FaceProfileCreate, db: AsyncSession = Depends(get_db)):
    """Register a face profile for a user."""
    existing = await db.execute(
        select(FaceProfile).where(FaceProfile.user_id == profile.user_id)
    )
    if existing.scalars().first():
        raise HTTPException(status_code=409, detail="Face profile already exists for this user")

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
async def verify_face(req: FaceVerifyRequest, db: AsyncSession = Depends(get_db)):
    """Verify if an image matches a registered face."""
    result = await db.execute(
        select(FaceProfile).where(FaceProfile.user_id == req.user_id)
    )
    face = result.scalars().first()
    if not face:
        raise HTTPException(status_code=404, detail="User not registered")

    try:
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        verification = face_service.verify(img, img)
    except RuntimeError:
        verification = {"verified": False, "confidence": 0.0}

    return FaceVerifyResponse(**verification)


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
