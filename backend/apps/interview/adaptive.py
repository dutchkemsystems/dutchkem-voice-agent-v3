from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional


class DifficultyLevel(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


@dataclass
class PerformanceMetrics:
    confidence: float = 0.0
    response_time: float = 0.0
    follow_ups_count: int = 0
    questions_answered: int = 0


_PROMOTE_THRESHOLD = 4
_DEMOTE_THRESHOLD = 4
_PROMOTE_CONFIDENCE = 0.75
_DEMOTE_CONFIDENCE = 0.45
_PROMOTE_RESPONSE_TIME = 2.5
_DEMOTE_RESPONSE_TIME = 4.0
_MIN_RESPONSES_FOR_ADJUST = 3

_EASY_CATEGORIES = ["hr", "general"]
_MEDIUM_CATEGORIES = ["hr", "managerial", "general"]
_HARD_CATEGORIES = ["technical", "coding", "managerial"]


class AdaptiveDifficulty:
    """Adjusts interview difficulty based on candidate performance."""

    def __init__(self, starting_difficulty: DifficultyLevel = DifficultyLevel.MEDIUM):
        self.current_difficulty = starting_difficulty
        self.metrics = PerformanceMetrics()
        self._confidence_sum = 0.0
        self._follow_ups_sum = 0

    def record_response(
        self,
        confidence: float,
        response_time: float,
        follow_ups_count: int,
    ) -> None:
        self.metrics.questions_answered += 1
        self._confidence_sum += confidence
        self._follow_ups_sum += follow_ups_count
        self.metrics.confidence = self._confidence_sum / self.metrics.questions_answered
        self.metrics.follow_ups_count = self._follow_ups_sum
        self.metrics.response_time = response_time

    def adjust_difficulty(self) -> Dict:
        """Adjust difficulty based on accumulated metrics.

        Returns dict with 'difficulty', 'changed', and optionally 'previous'.
        """
        n = self.metrics.questions_answered
        if n < _MIN_RESPONSES_FOR_ADJUST:
            return {
                "difficulty": self.current_difficulty,
                "changed": False,
            }

        avg_confidence = self.metrics.confidence
        previous = self.current_difficulty

        if avg_confidence >= _PROMOTE_CONFIDENCE and n >= _PROMOTE_THRESHOLD:
            if self.current_difficulty == DifficultyLevel.EASY:
                self.current_difficulty = DifficultyLevel.MEDIUM
            elif self.current_difficulty == DifficultyLevel.MEDIUM:
                self.current_difficulty = DifficultyLevel.HARD
        elif avg_confidence <= _DEMOTE_CONFIDENCE and n >= _DEMOTE_THRESHOLD:
            if self.current_difficulty == DifficultyLevel.HARD:
                self.current_difficulty = DifficultyLevel.MEDIUM
            elif self.current_difficulty == DifficultyLevel.MEDIUM:
                self.current_difficulty = DifficultyLevel.EASY

        changed = self.current_difficulty != previous
        result = {
            "difficulty": self.current_difficulty,
            "changed": changed,
        }
        if changed:
            result["previous"] = previous
        return result

    def get_recommended_categories(self) -> List[str]:
        if self.current_difficulty == DifficultyLevel.EASY:
            return _EASY_CATEGORIES
        elif self.current_difficulty == DifficultyLevel.HARD:
            return _HARD_CATEGORIES
        return _MEDIUM_CATEGORIES

    def get_performance_summary(self) -> Dict:
        return {
            "total_questions": self.metrics.questions_answered,
            "average_confidence": self.metrics.confidence,
            "total_follow_ups": self.metrics.follow_ups_count,
            "current_difficulty": self.current_difficulty.value,
        }

    def reset(self) -> None:
        self.current_difficulty = DifficultyLevel.MEDIUM
        self.metrics = PerformanceMetrics()
        self._confidence_sum = 0.0
        self._follow_ups_sum = 0
