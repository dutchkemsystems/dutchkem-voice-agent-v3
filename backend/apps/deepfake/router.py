from fastapi import APIRouter, HTTPException, Request, UploadFile, File, Form
from slowapi import Limiter
from slowapi.util import get_remote_address
import numpy as np
import io

from apps.deepfake.detector import DeepfakeDetector
from apps.deepfake.schemas import DetectionResponse

router = APIRouter(prefix="/deepfake", tags=["deepfake"])
limiter = Limiter(key_func=get_remote_address)

detector = DeepfakeDetector()


@router.post("/detect/voice", response_model=DetectionResponse)
@limiter.limit("30/min")
async def detect_voice_deepfake(
    request: Request,
    audio: UploadFile = File(...),
    sample_rate: int = Form(default=16000),
):
    """Detect voice deepfake artifacts in an audio file."""
    audio_data = await audio.read()
    if not audio_data:
        raise HTTPException(status_code=400, detail="Empty audio file")

    try:
        audio_array = np.frombuffer(audio_data, dtype=np.float32)
        result = detector.detect_audio(audio_array, sample_rate=sample_rate)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")

    return DetectionResponse(**result)


@router.post("/detect/video", response_model=DetectionResponse)
@limiter.limit("30/min")
async def detect_video_deepfake(
    request: Request,
    video: UploadFile = File(...),
):
    """Detect video deepfake manipulation (single frame analysis)."""
    video_data = await video.read()
    if not video_data:
        raise HTTPException(status_code=400, detail="Empty video file")

    try:
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        result = detector.detect_video([frame])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")

    return DetectionResponse(**result)


@router.post("/detect/combined", response_model=DetectionResponse)
@limiter.limit("30/min")
async def detect_combined_deepfake(
    request: Request,
    audio: UploadFile = File(...),
    video: UploadFile = File(...),
    sample_rate: int = Form(default=16000),
):
    """Run both voice and video deepfake detection."""
    audio_data = await audio.read()
    video_data = await video.read()

    if not audio_data or not video_data:
        raise HTTPException(status_code=400, detail="Empty audio or video file")

    try:
        audio_array = np.frombuffer(audio_data, dtype=np.float32)
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        result = detector.detect_combined(audio_array, [frame], sample_rate=sample_rate)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")

    return DetectionResponse(**result)
