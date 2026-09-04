from typing import Dict, List, Optional

from apps.modes.registry import ModeConfig


class ModeAwareCoach:
    """Provide mode-specific coaching tips and feedback."""

    def __init__(self, mode: ModeConfig) -> None:
        self.mode = mode

    def get_tip(self, scores: Dict[str, float]) -> str:
        """Get a coaching tip targeting the weakest dimension."""
        if not scores:
            return "You're doing great! Keep it up."

        weakest_dim = min(scores, key=scores.get)
        tips = self.mode.coaching_tips.get(weakest_dim, [])

        if tips:
            return tips[0]
        return "You're doing great! Keep it up."

    def generate_feedback(self, scores: Dict[str, float]) -> Dict:
        """Generate structured feedback from scores."""
        if not scores:
            return {"strengths": [], "improvements": [], "tips": [], "summary": "No data yet."}

        strengths = [dim for dim, score in scores.items() if score > 0.7]
        improvements = [dim for dim, score in scores.items() if score < 0.5]

        tips = []
        for dim in improvements:
            dim_tips = self.mode.coaching_tips.get(dim, [])
            if dim_tips:
                tips.append(dim_tips[0])

        overall = sum(scores.values()) / len(scores)
        if overall > 0.8:
            summary = self.mode.feedback_templates.get("positive", "Great performance!").format(
                dimension=max(scores, key=scores.get)
            )
        elif overall > 0.6:
            summary = "Good performance with room for improvement."
        else:
            summary = self.mode.feedback_templates.get("improvement", "Keep practicing!").format(
                dimension=min(scores, key=scores.get)
            )

        return {
            "strengths": strengths,
            "improvements": improvements,
            "tips": tips,
            "summary": summary,
        }
