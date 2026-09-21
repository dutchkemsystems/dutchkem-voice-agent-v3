import uuid
from datetime import datetime, timezone
from typing import Dict

from fastapi import APIRouter, HTTPException

from apps.interview.models import (
    InterviewSessionCreate,
    InterviewSessionResponse,
    InterviewQuestionRequest,
    InterviewAnswerResponse,
    InterviewAudioRequest,
    InterviewAudioResponse,
)
from apps.interview.engine import AutonomousInterviewEngine
from apps.interview.agents.base_agent import InterviewQuestion

router = APIRouter(prefix="/interview", tags=["interview"])

# In-memory session store — lightweight, no DB needed
_sessions: Dict[str, AutonomousInterviewEngine] = {}


@router.post("/start", response_model=InterviewSessionResponse)
async def start_session(request: InterviewSessionCreate = InterviewSessionCreate()):
    """Start a new interview session."""
    session_id = str(uuid.uuid4())
    engine = AutonomousInterviewEngine(
        user_profile=request.user_profile,
        company_context=request.company_context,
    )
    await engine.start_interview()
    _sessions[session_id] = engine
    return InterviewSessionResponse(
        id=session_id,
        status="active",
        started_at=datetime.now(timezone.utc).isoformat(),
    )


@router.post("/{session_id}/stop", response_model=InterviewSessionResponse)
async def stop_session(session_id: str):
    """Stop an interview session."""
    engine = _sessions.get(session_id)
    if engine is None:
        raise HTTPException(status_code=404, detail="Session not found")
    await engine.stop_interview()
    del _sessions[session_id]
    return InterviewSessionResponse(
        id=session_id,
        status="completed",
        ended_at=datetime.now(timezone.utc).isoformat(),
    )


@router.post("/question", response_model=InterviewAnswerResponse)
async def submit_question(request: InterviewQuestionRequest):
    """Submit a text question to the interview engine."""
    engine = _sessions.get(request.session_id)
    if engine is None:
        raise HTTPException(status_code=404, detail="Session not found")

    question = InterviewQuestion(
        text=request.text,
        category=request.category,
        difficulty=request.difficulty,
    )
    answer = await engine._route_and_get_answer(question)
    return InterviewAnswerResponse(
        text=answer.text,
        confidence=answer.confidence,
        agent_type=answer.agent_type,
        follow_ups=answer.follow_ups,
    )


@router.post("/audio", response_model=InterviewAudioResponse)
async def process_audio(request: InterviewAudioRequest):
    """Process audio input through the interview engine."""
    engine = _sessions.get(request.session_id)
    if engine is None:
        raise HTTPException(status_code=404, detail="Session not found")

    import base64

    audio_data = base64.b64decode(request.audio_base64)
    result = await engine.process_audio(audio_data)
    return InterviewAudioResponse(
        action=result.get("action", "waiting"),
        transcript=result.get("transcript"),
        answer=result.get("answer"),
        confidence=result.get("confidence"),
        avatar=result.get("avatar"),
    )


@router.get("/{session_id}/stats")
async def get_session_stats(session_id: str):
    """Get stats for an active session."""
    engine = _sessions.get(session_id)
    if engine is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return engine.get_session_stats()


@router.get("/health")
async def interview_health():
    """Check interview service health."""
    return {"status": "ok", "active_sessions": len(_sessions)}
