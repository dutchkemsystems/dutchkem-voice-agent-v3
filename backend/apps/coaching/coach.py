from typing import Dict, List


class InterviewCoach:
    """Provides real-time coaching tips during an interview."""

    def __init__(self):
        self.tips: Dict[str, List[str]] = {
            "confidence": [
                "Speak more slowly and clearly",
                "Maintain consistent volume",
                "Use positive language",
            ],
            "clarity": [
                "Structure your answers with STAR method",
                "Avoid filler words",
                "Be specific with examples",
            ],
            "relevance": [
                "Address the question directly",
                "Connect your experience to the role",
                "Show knowledge of the company",
            ],
        }

    def get_realtime_tip(self, score: Dict[str, float]) -> str:
        """Return a coaching tip targeting the weakest area in *score*."""
        if not score:
            return "You're doing great! Keep it up."
        weakest_area = min(score, key=score.get)
        tips = self.tips.get(weakest_area, [])
        if tips:
            return tips[0]
        return "You're doing great! Keep it up."


class CoachingSession:
    """Tracks scores across a session and produces final feedback."""

    def __init__(self):
        self._scores: List[Dict[str, float]] = []

    def record_score(self, score: Dict[str, float]) -> None:
        self._scores.append(score)

    def get_score_count(self) -> int:
        return len(self._scores)

    def get_average_scores(self) -> Dict[str, float]:
        if not self._scores:
            return {}
        keys = self._scores[0].keys()
        return {
            k: sum(s[k] for s in self._scores) / len(self._scores)
            for k in keys
        }

    def get_final_feedback(self) -> Dict:
        from apps.coaching.feedback_generator import FeedbackGenerator

        gen = FeedbackGenerator()
        return gen.generate_feedback(self._scores)

    def reset(self) -> None:
        self._scores.clear()
