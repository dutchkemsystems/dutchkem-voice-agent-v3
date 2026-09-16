from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, List

from apps.analytics.skill_gap_analyzer import SkillGapAnalyzer
from apps.scoring.models import SkillGapReport

router = APIRouter(prefix="/analytics", tags=["analytics"])

_analyzer = SkillGapAnalyzer()


class SkillGapRequest(BaseModel):
    scores: List[Dict]


class SkillGapResponse(BaseModel):
    category: str
    current_score: float
    target_score: float
    gap: float
    recommendations: List[str]


class PerformanceRequest(BaseModel):
    session_scores: List[List[Dict]]


class PerformanceResponse(BaseModel):
    total_sessions: int
    average_score: float
    improvement_rate: float
    strongest_category: str
    weakest_category: str


@router.post("/skill-gaps", response_model=list[SkillGapResponse])
async def analyze_skill_gaps(request: SkillGapRequest):
    """Analyze skill gaps across interview categories."""
    reports = _analyzer.analyze(request.scores)
    return [
        SkillGapResponse(
            category=r.category,
            current_score=r.current_score,
            target_score=r.target_score,
            gap=r.gap,
            recommendations=r.recommendations,
        )
        for r in reports
    ]


@router.post("/performance", response_model=PerformanceResponse)
async def get_performance_metrics(request: PerformanceRequest):
    """Calculate performance metrics across multiple sessions."""
    metrics = _analyzer.calculate_performance_metrics(request.session_scores)
    return PerformanceResponse(
        total_sessions=metrics.total_sessions,
        average_score=metrics.average_score,
        improvement_rate=metrics.improvement_rate,
        strongest_category=metrics.strongest_category,
        weakest_category=metrics.weakest_category,
    )


@router.get("/dashboard")
async def get_dashboard_stats():
    """Get aggregated dashboard statistics."""
    from config.database import async_session
    from sqlalchemy import select, func
    from apps.voice.models import VoiceProfile
    from apps.proctoring.models import FaceProfile

    async with async_session() as db:
        voice_count = await db.execute(select(func.count(VoiceProfile.id)))
        face_count = await db.execute(select(func.count(FaceProfile.id)))

    return {
        "voice_profiles": voice_count.scalar() or 0,
        "face_registrations": face_count.scalar() or 0,
        "interviews_completed": 0,
        "deepfake_detections": 0,
    }
