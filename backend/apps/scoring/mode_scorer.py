import re
from typing import Dict

from apps.modes.registry import ModeConfig


class ModeAwareScorer:
    """Score responses with base + mode-specific override dimensions."""

    OPTIMAL_SPEECH_RATE = 150  # words per minute

    def __init__(self, mode: ModeConfig) -> None:
        self.mode = mode

    def score(self, question: str, answer: str, audio_features: Dict) -> Dict[str, float]:
        """Calculate scores for all dimensions."""
        scores = {}

        # Base dimensions
        scores["confidence"] = self._calculate_confidence(audio_features)
        scores["clarity"] = self._calculate_clarity(audio_features)
        scores["relevance"] = self._calculate_relevance(question, answer)

        # Mode-specific overrides
        for dimension in self.mode.scoring_overrides:
            scores[dimension] = self._calculate_override(dimension, question, answer, audio_features)

        # Calculate weighted overall
        scores["overall"] = self._calculate_overall(scores)

        return scores

    def _calculate_overall(self, scores: Dict[str, float]) -> float:
        """Calculate weighted overall score."""
        weights = {}
        base_dims = ["confidence", "clarity", "relevance"]
        for dim in base_dims:
            if dim in scores:
                weights[dim] = 1.0

        for dim, weight in self.mode.scoring_overrides.items():
            if dim in scores:
                weights[dim] = weight * 5

        total_weight = sum(weights.values())
        if total_weight == 0:
            return 0.0

        weighted_sum = sum(scores[dim] * weights[dim] for dim in weights)
        return weighted_sum / total_weight

    def _calculate_confidence(self, audio_features: Dict) -> float:
        volume_stability = 1.0 - min(audio_features.get("volume_variance", 0.5), 1.0)
        pitch_variation = min(audio_features.get("pitch_variation", 0.5), 1.0)
        speech_rate = audio_features.get("speech_rate", self.OPTIMAL_SPEECH_RATE)
        rate_score = 1.0 - min(
            abs(speech_rate - self.OPTIMAL_SPEECH_RATE) / self.OPTIMAL_SPEECH_RATE, 1.0
        )
        return volume_stability * 0.3 + pitch_variation * 0.3 + rate_score * 0.4

    def _calculate_clarity(self, audio_features: Dict) -> float:
        filler_words = audio_features.get("filler_words", 0)
        pause_count = audio_features.get("pause_count", 0)
        speech_rate = audio_features.get("speech_rate", self.OPTIMAL_SPEECH_RATE)
        rate_score = 1.0 - min(
            abs(speech_rate - self.OPTIMAL_SPEECH_RATE) / self.OPTIMAL_SPEECH_RATE, 1.0
        )
        filler_penalty = min(filler_words * 0.05, 0.5)
        pause_penalty = min(pause_count * 0.05, 0.3)
        return max(0.0, min(
            rate_score * 0.4 + (1.0 - filler_penalty) * 0.35 + (1.0 - pause_penalty) * 0.25, 1.0
        ))

    def _calculate_relevance(self, question: str, answer: str) -> float:
        if not answer or not answer.strip():
            return 0.0
        if not question or not question.strip():
            return 0.0
        stop_words = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
            "have", "has", "had", "do", "does", "did", "will", "would", "could",
            "should", "may", "might", "shall", "can", "to", "of", "in", "for",
            "on", "with", "at", "by", "from", "as", "into", "about", "what",
            "how", "why", "when", "where", "who", "whom", "which", "that",
            "this", "these", "those", "it", "its", "your", "you", "i", "my",
        }
        q_words = set(w for w in re.findall(r"[a-z0-9]+", question.lower()) if w not in stop_words and len(w) > 1)
        a_words = set(w for w in re.findall(r"[a-z0-9]+", answer.lower()) if w not in stop_words and len(w) > 1)
        if not q_words:
            return 0.0
        overlap = len(q_words & a_words) / len(q_words)
        length_bonus = min(len(answer.split()) / 10, 1.0) * 0.2
        return min(overlap + length_bonus, 1.0)

    def _calculate_override(
        self, dimension: str, question: str, answer: str, audio_features: Dict
    ) -> float:
        """Calculate a mode-specific dimension score."""
        if dimension in ("persuasion", "objection_handling"):
            word_count = len(answer.split())
            return min(word_count / 30, 1.0)
        elif dimension in ("teaching_clarity", "knowledge_transfer"):
            example_signals = ["for example", "such as", "like when", "instance"]
            has_example = any(s in answer.lower() for s in example_signals)
            return 0.8 if has_example else 0.5
        elif dimension == "empathy":
            empathy_signals = ["understand", "sorry", "help", "appreciate"]
            count = sum(1 for s in empathy_signals if s in answer.lower())
            return min(count / 3, 1.0)
        elif dimension in ("executive_presence", "strategic_thinking"):
            data_signals = ["percent", "increase", "revenue", "growth", "metric"]
            count = sum(1 for s in data_signals if s in answer.lower())
            return min(count / 3, 1.0)
        elif dimension == "resolution_quality":
            solution_signals = ["solution", "fix", "resolve", "recommend"]
            count = sum(1 for s in solution_signals if s in answer.lower())
            return min(count / 2, 1.0)
        elif dimension in ("stakeholder_management", "patience", "documentation"):
            return 0.6
        else:
            return 0.5
