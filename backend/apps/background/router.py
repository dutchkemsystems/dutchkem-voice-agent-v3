from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Optional

from apps.background.service_manager import BackgroundServiceManager

router = APIRouter(prefix="/background", tags=["background"])

_manager = BackgroundServiceManager()


class AnalyzeTranscriptRequest(BaseModel):
    transcript: str


class PerformanceModeRequest(BaseModel):
    mode: str


@router.get("/status")
async def get_status():
    """Get background monitoring status."""
    return _manager.get_stats()


@router.get("/system-stats")
async def get_system_stats():
    """Get system resource usage."""
    return _manager.get_system_stats()


@router.post("/analyze-transcript")
async def analyze_transcript(request: AnalyzeTranscriptRequest):
    """Analyze a transcript segment for interview triggers."""
    result = _manager.analyze_transcript(request.transcript)
    return result


@router.post("/performance-mode")
async def set_performance_mode(request: PerformanceModeRequest):
    """Set monitoring performance mode."""
    try:
        _manager.set_performance_mode(request.mode)
        return {"status": "ok", "mode": request.mode}
    except ValueError as e:
        return {"status": "error", "detail": str(e)}


@router.get("/battery-warnings")
async def get_battery_warnings():
    """Check battery status and return warnings."""
    return {"warnings": _manager.check_battery_warnings()}
