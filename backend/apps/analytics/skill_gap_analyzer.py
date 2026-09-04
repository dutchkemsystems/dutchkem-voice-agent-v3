from typing import Dict, List

from apps.scoring.models import PerformanceMetrics, SkillGapReport

DEFAULT_TARGET_SCORES: Dict[str, float] = {
    "technical": 0.75,
    "hr": 0.80,
    "managerial": 0.70,
    "coding": 0.75,
}

RECOMMENDATIONS: Dict[str, List[str]] = {
    "technical": [
        "Practice system design questions",
        "Review data structures and algorithms",
        "Study distributed systems concepts",
    ],
    "hr": [
        "Prepare STAR-method behavioural answers",
        "Practice common HR interview questions",
        "Work on self-introduction narrative",
    ],
    "managerial": [
        "Prepare leadership scenario examples",
        "Practice stakeholder management stories",
        "Review conflict resolution strategies",
    ],
    "coding": [
        "Practice coding challenges daily",
        "Review code review best practices",
        "Study language-specific idioms",
    ],
}

FALLBACK_RECOMMENDATIONS = [
    "Review fundamentals for this category",
    "Practice more interview questions in this area",
    "Seek feedback on past responses",
]


class SkillGapAnalyzer:
    """Analyse skill gaps across interview categories and calculate performance metrics."""

    def __init__(self, target_scores: Dict[str, float] | None = None) -> None:
        self.target_scores = target_scores or dict(DEFAULT_TARGET_SCORES)

    def _get_target(self, category: str) -> float:
        return self.target_scores.get(category, 0.75)

    def _get_recommendations(self, category: str) -> List[str]:
        return RECOMMENDATIONS.get(category, FALLBACK_RECOMMENDATIONS)

    def analyze(self, scores: List[Dict]) -> List[SkillGapReport]:
        """Analyse a list of score dicts (each with 'category' and 'overall').

        Args:
            scores: List of dicts, each with at least 'category' (str) and
                    'overall' (float, 0-100 scale).

        Returns:
            List of SkillGapReport, one per category with a gap.
        """
        if not scores:
            return []

        categories: Dict[str, List[float]] = {}
        for entry in scores:
            cat = entry["category"]
            overall = entry["overall"]
            categories.setdefault(cat, []).append(overall)

        reports: List[SkillGapReport] = []
        for category, cat_scores in categories.items():
            avg = sum(cat_scores) / len(cat_scores)
            avg_normalised = avg / 100.0  # Convert 0-100 → 0-1
            target = self._get_target(category)
            gap = target - avg_normalised

            if gap > 0:
                reports.append(SkillGapReport(
                    category=category,
                    current_score=round(avg_normalised, 4),
                    target_score=target,
                    gap=round(gap, 4),
                    recommendations=self._get_recommendations(category),
                ))

        return reports

    def calculate_performance_metrics(
        self, session_scores: List[List[Dict]]
    ) -> PerformanceMetrics:
        """Calculate performance metrics across multiple sessions.

        Args:
            session_scores: List of sessions, each a list of score dicts.

        Returns:
            PerformanceMetrics with aggregated stats.
        """
        if not session_scores:
            return PerformanceMetrics(
                total_sessions=0,
                average_score=0.0,
                improvement_rate=0.0,
                strongest_category="",
                weakest_category="",
            )

        all_averages: List[float] = []
        category_totals: Dict[str, List[float]] = {}

        for session in session_scores:
            session_avg = 0.0
            if session:
                session_avg = sum(s["overall"] for s in session) / len(session)
            all_averages.append(session_avg)

            for entry in session:
                cat = entry["category"]
                category_totals.setdefault(cat, []).append(entry["overall"])

        overall_avg = sum(all_averages) / len(all_averages) if all_averages else 0.0

        improvement_rate = 0.0
        if len(all_averages) >= 2:
            improvement_rate = all_averages[-1] - all_averages[0]

        strongest = ""
        weakest = ""
        cat_avgs: Dict[str, float] = {}
        for cat, vals in category_totals.items():
            cat_avgs[cat] = sum(vals) / len(vals)

        if cat_avgs:
            strongest = max(cat_avgs, key=cat_avgs.get)  # type: ignore[arg-type]
            weakest = min(cat_avgs, key=cat_avgs.get)  # type: ignore[arg-type]

        return PerformanceMetrics(
            total_sessions=len(session_scores),
            average_score=round(overall_avg, 2),
            improvement_rate=round(improvement_rate, 2),
            strongest_category=strongest,
            weakest_category=weakest,
        )
