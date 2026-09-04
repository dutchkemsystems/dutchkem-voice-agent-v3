from typing import Dict, List


class FeedbackGenerator:
    """Generates comprehensive post-interview feedback."""

    STRENGTH_THRESHOLD = 0.7
    IMPROVEMENT_THRESHOLD = 0.5

    def generate_feedback(self, scores: List[Dict[str, float]]) -> Dict:
        if not scores:
            return {
                "overall_rating": 0,
                "strengths": [],
                "areas_for_improvement": [],
                "specific_tips": [],
                "summary": "No scores recorded yet.",
            }

        keys = scores[0].keys()
        avg_scores: Dict[str, float] = {
            k: sum(s[k] for s in scores) / len(scores) for k in keys
        }
        overall_avg = sum(avg_scores.values()) / len(avg_scores)

        strengths = [k for k, v in avg_scores.items() if v > self.STRENGTH_THRESHOLD]
        improvements = [k for k, v in avg_scores.items() if v < self.IMPROVEMENT_THRESHOLD]

        specific_tips = self._build_tips(avg_scores)

        return {
            "overall_rating": round(overall_avg * 100, 1),
            "strengths": strengths,
            "areas_for_improvement": improvements,
            "specific_tips": specific_tips,
            "summary": self._generate_summary(avg_scores),
        }

    def _build_tips(self, avg_scores: Dict[str, float]) -> List[str]:
        from apps.coaching.coach import InterviewCoach

        coach = InterviewCoach()
        weakest_area = min(avg_scores, key=avg_scores.get)
        tips = coach.tips.get(weakest_area, [])
        if tips:
            return [tips[0]]
        return ["You're doing great! Keep it up."]

    def _generate_summary(self, scores: Dict[str, float]) -> str:
        overall = sum(scores.values()) / len(scores)
        if overall > 0.8:
            return "Excellent performance! You demonstrated strong confidence and clarity."
        elif overall > 0.6:
            return "Good performance with room for improvement in some areas."
        else:
            return "Keep practicing! Focus on building confidence and structuring your answers."
