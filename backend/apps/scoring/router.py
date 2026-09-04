from fastapi import APIRouter, HTTPException
from apps.scoring.realtime_scorer import RealtimeScorer
from apps.scoring.schemas import (
    ScoreRequest,
    ScoreResponse,
    SkillGapRequest,
    SkillGapResponse,
    PerformanceMetricsRequest,
    PerformanceMetricsResponse,
    SessionSummaryResponse,
)
from apps.analytics.skill_gap_analyzer import SkillGapAnalyzer

router = APIRouter(prefix="/scoring", tags=["scoring"])

# Module-level scorer and analyzer instances (reset per-session via endpoints)
_scorer = RealtimeScorer()
_analyzer = SkillGapAnalyzer()


@router.post("/score", response_model=ScoreResponse)
async def score_response(request: ScoreRequest):
    """Score a single interview response in real-time."""
    score = _scorer.score_response(
        question=request.question,
        answer=request.answer,
        audio_features=request.audio_features,
    )
    return ScoreResponse(
        confidence=score.confidence,
        clarity=score.clarity,
        relevance=score.relevance,
        response_time=score.response_time,
        overall=score.overall,
        category=request.category,
    )


@router.get("/session/summary", response_model=SessionSummaryResponse)
async def get_session_summary():
    """Get summary of the current scoring session."""
    summary = _scorer.get_session_summary()
    return SessionSummaryResponse(**summary)


@router.post("/session/reset")
async def reset_session():
    """Reset the current scoring session."""
    global _scorer
    _scorer = RealtimeScorer()
    return {"status": "ok", "message": "Session reset"}


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


@router.post("/performance", response_model=PerformanceMetricsResponse)
async def get_performance_metrics(request: PerformanceMetricsRequest):
    """Calculate performance metrics across multiple sessions."""
    metrics = _analyzer.calculate_performance_metrics(request.session_scores)
    return PerformanceMetricsResponse(
        total_sessions=metrics.total_sessions,
        average_score=metrics.average_score,
        improvement_rate=metrics.improvement_rate,
        strongest_category=metrics.strongest_category,
        weakest_category=metrics.weakest_category,
    )
