from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ScoreBreakdown:
    """Detailed breakdown of a score with weights."""
    confidence: float
    clarity: float
    relevance: float
    response_time: float
    overall: float
    weights: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "confidence": self.confidence,
            "clarity": self.clarity,
            "relevance": self.relevance,
            "response_time": self.response_time,
            "overall": self.overall,
            "weights": self.weights,
        }


@dataclass
class SessionAnalytics:
    """Analytics for a complete interview session."""
    session_id: str
    total_questions: int
    average_score: float
    scores: List[float]
    duration_seconds: float

    def to_dict(self) -> Dict:
        return {
            "session_id": self.session_id,
            "total_questions": self.total_questions,
            "average_score": self.average_score,
            "scores": self.scores,
            "duration_seconds": self.duration_seconds,
        }


@dataclass
class SkillGapReport:
    """Report on a specific skill gap."""
    category: str
    current_score: float
    target_score: float
    gap: float
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "category": self.category,
            "current_score": self.current_score,
            "target_score": self.target_score,
            "gap": self.gap,
            "recommendations": self.recommendations,
        }


@dataclass
class PerformanceMetrics:
    """Overall performance metrics across sessions."""
    total_sessions: int
    average_score: float
    improvement_rate: float
    strongest_category: str
    weakest_category: str

    def to_dict(self) -> Dict:
        return {
            "total_sessions": self.total_sessions,
            "average_score": self.average_score,
            "improvement_rate": self.improvement_rate,
            "strongest_category": self.strongest_category,
            "weakest_category": self.weakest_category,
        }
