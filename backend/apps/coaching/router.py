from typing import Dict, List

from fastapi import APIRouter
from pydantic import BaseModel

from apps.coaching.coach import InterviewCoach, CoachingSession
from apps.coaching.feedback_generator import FeedbackGenerator

router = APIRouter(prefix="/coaching", tags=["coaching"])

_coach = InterviewCoach()
_feedback_gen = FeedbackGenerator()
_sessions: Dict[str, CoachingSession] = {}


class ScoreRequest(BaseModel):
    confidence: float
    clarity: float
    relevance: float


class TipResponse(BaseModel):
    tip: str
    weakest_area: str


class FeedbackRequest(BaseModel):
    scores: List[Dict[str, float]]


class FeedbackResponse(BaseModel):
    overall_rating: float
    strengths: List[str]
    areas_for_improvement: List[str]
    specific_tips: List[str]
    summary: str


class SessionStartResponse(BaseModel):
    session_id: str
    message: str


class SessionScoreRequest(BaseModel):
    session_id: str
    confidence: float
    clarity: float
    relevance: float


class SessionEndRequest(BaseModel):
    session_id: str


@router.post("/tip", response_model=TipResponse)
async def get_realtime_tip(score: ScoreRequest):
    """Get a real-time coaching tip based on current performance."""
    score_dict = {
        "confidence": score.confidence,
        "clarity": score.clarity,
        "relevance": score.relevance,
    }
    weakest = min(score_dict, key=score_dict.get)
    tip = _coach.get_realtime_tip(score_dict)
    return TipResponse(tip=tip, weakest_area=weakest)


@router.post("/feedback", response_model=FeedbackResponse)
async def get_feedback(req: FeedbackRequest):
    """Generate comprehensive post-interview feedback."""
    feedback = _feedback_gen.generate_feedback(req.scores)
    return FeedbackResponse(**feedback)


@router.post("/session/start", response_model=SessionStartResponse)
async def start_session():
    """Start a new coaching session."""
    import uuid

    session_id = str(uuid.uuid4())
    _sessions[session_id] = CoachingSession()
    return SessionStartResponse(
        session_id=session_id,
        message="Coaching session started",
    )


@router.post("/session/score")
async def record_session_score(req: SessionScoreRequest):
    """Record a score in an active coaching session."""
    session = _sessions.get(req.session_id)
    if not session:
        return {"error": "Session not found"}
    session.record_score(
        {
            "confidence": req.confidence,
            "clarity": req.clarity,
            "relevance": req.relevance,
        }
    )
    return {"recorded": True, "count": session.get_score_count()}


@router.post("/session/end", response_model=FeedbackResponse)
async def end_session(req: SessionEndRequest):
    """End a coaching session and get final feedback."""
    session = _sessions.pop(req.session_id, None)
    if not session:
        return FeedbackResponse(
            overall_rating=0,
            strengths=[],
            areas_for_improvement=[],
            specific_tips=[],
            summary="Session not found.",
        )
    feedback = session.get_final_feedback()
    return FeedbackResponse(**feedback)
