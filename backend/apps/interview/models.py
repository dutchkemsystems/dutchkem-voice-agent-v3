from pydantic import BaseModel
from typing import Dict, List, Optional


class InterviewSessionCreate(BaseModel):
    user_profile: Dict = {}
    company_context: Dict = {}


class InterviewSessionResponse(BaseModel):
    id: str
    status: str
    started_at: Optional[str] = None
    ended_at: Optional[str] = None


class InterviewQuestionRequest(BaseModel):
    session_id: str
    text: str
    category: str = "general"
    difficulty: str = "medium"


class InterviewAnswerResponse(BaseModel):
    text: str
    confidence: float
    agent_type: str
    follow_ups: List[str] = []
    avatar_data: Optional[Dict] = None


class InterviewAudioRequest(BaseModel):
    session_id: str
    audio_base64: str


class InterviewAudioResponse(BaseModel):
    action: str
    transcript: Optional[str] = None
    answer: Optional[str] = None
    confidence: Optional[float] = None
    avatar: Optional[Dict] = None
