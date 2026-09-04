from dataclasses import dataclass, field
from typing import Dict, List, Optional
import math


@dataclass
class InterviewScore:
    """Score for a single interview response."""
    confidence: float  # 0-1
    clarity: float  # 0-1
    relevance: float  # 0-1
    response_time: float  # seconds
    overall: float  # 0-100


class RealtimeScorer:
    """Score interview responses in real-time using audio features and semantic relevance."""

    CONFIDENCE_WEIGHT = 0.30
    CLARITY_WEIGHT = 0.30
    RELEVANCE_WEIGHT = 0.40

    OPTIMAL_SPEECH_RATE = 140  # words per minute

    def __init__(self) -> None:
        self.scores: List[InterviewScore] = []

    def score_response(
        self,
        question: str,
        answer: str,
        audio_features: Dict,
    ) -> InterviewScore:
        """Score an interview response in real-time."""
        confidence = self._calculate_confidence(audio_features)
        clarity = self._calculate_clarity(audio_features)
        relevance = self._calculate_relevance(question, answer)
        response_time = audio_features.get("response_time", 0.0)

        overall = (
            confidence * self.CONFIDENCE_WEIGHT
            + clarity * self.CLARITY_WEIGHT
            + relevance * self.RELEVANCE_WEIGHT
        ) * 100

        score = InterviewScore(
            confidence=confidence,
            clarity=clarity,
            relevance=relevance,
            response_time=response_time,
            overall=overall,
        )
        self.scores.append(score)
        return score

    def _calculate_confidence(self, audio_features: Dict) -> float:
        """Calculate confidence from voice features.

        Uses volume stability, pitch variation, and speech rate.
        """
        volume_stability = 1.0 - min(audio_features.get("volume_variance", 0.5), 1.0)
        pitch_variation = min(audio_features.get("pitch_variation", 0.5), 1.0)
        speech_rate = audio_features.get("speech_rate", self.OPTIMAL_SPEECH_RATE)

        rate_score = 1.0 - min(
            abs(speech_rate - self.OPTIMAL_SPEECH_RATE) / self.OPTIMAL_SPEECH_RATE,
            1.0,
        )

        return (
            volume_stability * 0.3
            + pitch_variation * 0.3
            + rate_score * 0.4
        )

    def _calculate_clarity(self, audio_features: Dict) -> float:
        """Calculate clarity from speech patterns.

        Penalises filler words and excessive pauses.
        """
        filler_words = audio_features.get("filler_words", 0)
        pause_count = audio_features.get("pause_count", 0)
        speech_rate = audio_features.get("speech_rate", self.OPTIMAL_SPEECH_RATE)

        rate_score = 1.0 - min(
            abs(speech_rate - self.OPTIMAL_SPEECH_RATE) / self.OPTIMAL_SPEECH_RATE,
            1.0,
        )

        filler_penalty = min(filler_words * 0.05, 0.5)
        pause_penalty = min(pause_count * 0.05, 0.3)

        clarity = rate_score * 0.4 + (1.0 - filler_penalty) * 0.35 + (1.0 - pause_penalty) * 0.25
        return max(0.0, min(clarity, 1.0))

    def _calculate_relevance(self, question: str, answer: str) -> float:
        """Calculate relevance using keyword overlap between question and answer."""
        if not answer or not answer.strip():
            return 0.0
        if not question or not question.strip():
            return 0.0

        q_words = set(self._tokenize(question))
        a_words = set(self._tokenize(answer))

        if not q_words:
            return 0.0

        overlap = q_words & a_words
        relevance = len(overlap) / len(q_words)

        answer_length_bonus = min(len(answer.split()) / 10, 1.0) * 0.2

        return min(relevance + answer_length_bonus, 1.0)

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        """Simple whitespace + lowercase tokenizer, stripping punctuation."""
        stop_words = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
            "have", "has", "had", "do", "does", "did", "will", "would", "could",
            "should", "may", "might", "shall", "can", "to", "of", "in", "for",
            "on", "with", "at", "by", "from", "as", "into", "about", "what",
            "how", "why", "when", "where", "who", "whom", "which", "that",
            "this", "these", "those", "it", "its", "your", "you", "i", "my",
            "me", "we", "they", "he", "she", "and", "or", "but", "if", "not",
        }
        import re
        words = re.findall(r"[a-z0-9]+", text.lower())
        return [w for w in words if w not in stop_words and len(w) > 1]

    def get_average_score(self) -> float:
        """Get average overall score across all responses."""
        if not self.scores:
            return 0.0
        return sum(s.overall for s in self.scores) / len(self.scores)

    def get_best_score(self) -> Optional[InterviewScore]:
        """Get the highest-scoring response."""
        if not self.scores:
            return None
        return max(self.scores, key=lambda s: s.overall)

    def get_worst_score(self) -> Optional[InterviewScore]:
        """Get the lowest-scoring response."""
        if not self.scores:
            return None
        return min(self.scores, key=lambda s: s.overall)

    def get_score_count(self) -> int:
        """Get total number of scored responses."""
        return len(self.scores)

    def get_session_summary(self) -> Dict:
        """Get a summary dict of the scoring session."""
        if not self.scores:
            return {
                "average_score": 0.0,
                "best_score": None,
                "worst_score": None,
                "total_responses": 0,
            }
        return {
            "average_score": self.get_average_score(),
            "best_score": self.get_best_score().overall if self.get_best_score() else 0.0,
            "worst_score": self.get_worst_score().overall if self.get_worst_score() else 0.0,
            "total_responses": self.get_score_count(),
        }
