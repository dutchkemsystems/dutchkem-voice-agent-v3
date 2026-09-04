from pydantic import BaseModel, Field
from typing import Dict, List, Optional


class ScoreRequest(BaseModel):
    """Request to score a single interview response."""
    question: str = Field(..., min_length=1, description="The interview question")
    answer: str = Field(..., min_length=1, description="The candidate's answer")
    audio_features: Dict[str, float] = Field(
        default_factory=dict,
        description="Audio features: volume_variance, pitch_variation, speech_rate, filler_words, pause_count, response_time",
    )
    category: str = Field(default="general", description="Question category (hr, technical, coding, managerial, general)")


class ScoreResponse(BaseModel):
    """Response with scoring results."""
    confidence: float
    clarity: float
    relevance: float
    response_time: float
    overall: float
    category: str


class SkillGapRequest(BaseModel):
    """Request to analyze skill gaps."""
    scores: List[Dict] = Field(
        ...,
        description="List of score dicts, each with 'category' (str) and 'overall' (float, 0-100)",
    )


class SkillGapResponse(BaseModel):
    """Response with skill gap analysis."""
    category: str
    current_score: float
    target_score: float
    gap: float
    recommendations: List[str]


class PerformanceMetricsRequest(BaseModel):
    """Request to calculate performance metrics across sessions."""
    session_scores: List[List[Dict]] = Field(
        ...,
        description="List of sessions, each a list of score dicts with 'category' and 'overall'",
    )


class PerformanceMetricsResponse(BaseModel):
    """Response with performance metrics."""
    total_sessions: int
    average_score: float
    improvement_rate: float
    strongest_category: str
    weakest_category: str


class SessionSummaryResponse(BaseModel):
    """Response with session summary."""
    average_score: float
    best_score: Optional[float]
    worst_score: Optional[float]
    total_responses: int
