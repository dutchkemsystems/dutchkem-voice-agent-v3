import pytest
from apps.scoring.realtime_scorer import RealtimeScorer, InterviewScore
from apps.scoring.models import (
    ScoreBreakdown,
    SessionAnalytics,
    SkillGapReport,
    PerformanceMetrics,
)
from apps.analytics.skill_gap_analyzer import SkillGapAnalyzer


# ═══════════════════════════════════════════════════
# InterviewScore dataclass
# ═══════════════════════════════════════════════════

class TestInterviewScore:
    def test_creation(self):
        score = InterviewScore(
            confidence=0.8,
            clarity=0.9,
            relevance=0.7,
            response_time=5.0,
            overall=78.5,
        )
        assert score.confidence == 0.8
        assert score.clarity == 0.9
        assert score.relevance == 0.7
        assert score.response_time == 5.0
        assert score.overall == 78.5

    def test_defaults(self):
        score = InterviewScore(
            confidence=0.0,
            clarity=0.0,
            relevance=0.0,
            response_time=0.0,
            overall=0.0,
        )
        assert score.confidence == 0.0
        assert score.overall == 0.0


# ═══════════════════════════════════════════════════
# RealtimeScorer
# ═══════════════════════════════════════════════════

class TestRealtimeScorerInit:
    def test_init(self):
        scorer = RealtimeScorer()
        assert scorer.scores == []

    def test_init_with_no_args(self):
        scorer = RealtimeScorer()
        assert hasattr(scorer, "scores")
        assert len(scorer.scores) == 0


class TestRealtimeScorerConfidence:
    def test_high_volume_stability_high_confidence(self):
        scorer = RealtimeScorer()
        audio_features = {
            "volume_variance": 0.05,
            "pitch_variation": 0.8,
            "speech_rate": 140,
        }
        score = scorer.score_response("Question", "Answer", audio_features)
        assert score.confidence > 0.5

    def test_low_volume_stability_low_confidence(self):
        scorer = RealtimeScorer()
        audio_features = {
            "volume_variance": 0.9,
            "pitch_variation": 0.1,
            "speech_rate": 140,
        }
        score = scorer.score_response("Question", "Answer", audio_features)
        assert score.confidence < 0.5

    def test_optimal_speech_rate(self):
        scorer = RealtimeScorer()
        audio_features = {
            "volume_variance": 0.1,
            "pitch_variation": 0.5,
            "speech_rate": 140,
        }
        score = scorer.score_response("Question", "Answer", audio_features)
        assert score.confidence > 0.0

    def test_very_fast_speech_rate(self):
        scorer = RealtimeScorer()
        audio_features = {
            "volume_variance": 0.1,
            "pitch_variation": 0.5,
            "speech_rate": 300,
        }
        score = scorer.score_response("Question", "Answer", audio_features)
        assert score.confidence < 0.8


class TestRealtimeScorerClarity:
    def test_clarity_from_audio_features(self):
        scorer = RealtimeScorer()
        audio_features = {
            "volume_variance": 0.1,
            "pitch_variation": 0.7,
            "speech_rate": 140,
            "filler_words": 0,
            "pause_count": 1,
        }
        score = scorer.score_response("Question", "Answer", audio_features)
        assert 0.0 <= score.clarity <= 1.0

    def test_low_clarity_with_fillers(self):
        scorer = RealtimeScorer()
        audio_features = {
            "volume_variance": 0.1,
            "pitch_variation": 0.5,
            "speech_rate": 140,
            "filler_words": 10,
            "pause_count": 5,
        }
        score_low = scorer.score_response("Question", "Answer", audio_features)
        scorer2 = RealtimeScorer()
        audio_features2 = {
            "volume_variance": 0.1,
            "pitch_variation": 0.5,
            "speech_rate": 140,
            "filler_words": 0,
            "pause_count": 1,
        }
        score_high = scorer2.score_response("Question", "Answer", audio_features2)
        assert score_high.clarity >= score_low.clarity


class TestRealtimeScorerRelevance:
    def test_relevant_answer(self):
        scorer = RealtimeScorer()
        question = "What are your strengths?"
        answer = "My strengths include problem solving, leadership, and communication skills."
        audio_features = {"response_time": 3.0}
        score = scorer.score_response(question, answer, audio_features)
        assert score.relevance > 0.0

    def test_irrelevant_answer(self):
        scorer = RealtimeScorer()
        question = "What are your strengths?"
        answer = "I like to eat pizza on Fridays."
        audio_features = {"response_time": 3.0}
        score_irrelevant = scorer.score_response(question, answer, audio_features)
        scorer2 = RealtimeScorer()
        answer_relevant = "My strengths include problem solving, leadership, and communication skills."
        score_relevant = scorer2.score_response(question, answer_relevant, audio_features)
        assert score_relevant.relevance >= score_irrelevant.relevance

    def test_empty_answer(self):
        scorer = RealtimeScorer()
        audio_features = {"response_time": 0.0}
        score = scorer.score_response("Question", "", audio_features)
        assert score.relevance == 0.0


class TestRealtimeScorerOverall:
    def test_overall_weighted_correctly(self):
        scorer = RealtimeScorer()
        audio_features = {
            "volume_variance": 0.1,
            "pitch_variation": 0.8,
            "speech_rate": 140,
            "filler_words": 0,
            "pause_count": 1,
            "response_time": 3.0,
        }
        score = scorer.score_response("Tell me about yourself", "I am a software engineer.", audio_features)
        # overall = confidence*30 + clarity*30 + relevance*40
        expected = score.confidence * 30 + score.clarity * 30 + score.relevance * 40
        assert abs(score.overall - expected) < 0.01

    def test_overall_range(self):
        scorer = RealtimeScorer()
        audio_features = {
            "volume_variance": 0.1,
            "pitch_variation": 0.8,
            "speech_rate": 140,
            "filler_words": 0,
            "pause_count": 1,
            "response_time": 3.0,
        }
        score = scorer.score_response("Q", "A", audio_features)
        assert 0.0 <= score.overall <= 100.0


class TestRealtimeScorerSession:
    def test_get_average_empty(self):
        scorer = RealtimeScorer()
        assert scorer.get_average_score() == 0.0

    def test_get_average_single(self):
        scorer = RealtimeScorer()
        audio_features = {
            "volume_variance": 0.1,
            "pitch_variation": 0.8,
            "speech_rate": 140,
            "filler_words": 0,
            "pause_count": 1,
            "response_time": 3.0,
        }
        score = scorer.score_response("Q", "A", audio_features)
        assert scorer.get_average_score() == score.overall

    def test_get_average_multiple(self):
        scorer = RealtimeScorer()
        audio_features = {
            "volume_variance": 0.1,
            "pitch_variation": 0.8,
            "speech_rate": 140,
            "filler_words": 0,
            "pause_count": 1,
            "response_time": 3.0,
        }
        s1 = scorer.score_response("Q1", "A1", audio_features)
        s2 = scorer.score_response("Q2", "A2", audio_features)
        s3 = scorer.score_response("Q3", "A3", audio_features)
        expected_avg = (s1.overall + s2.overall + s3.overall) / 3
        assert abs(scorer.get_average_score() - expected_avg) < 0.01

    def test_get_best_score(self):
        scorer = RealtimeScorer()
        audio_features1 = {
            "volume_variance": 0.8,
            "pitch_variation": 0.1,
            "speech_rate": 300,
            "filler_words": 10,
            "pause_count": 5,
            "response_time": 10.0,
        }
        audio_features2 = {
            "volume_variance": 0.05,
            "pitch_variation": 0.9,
            "speech_rate": 140,
            "filler_words": 0,
            "pause_count": 0,
            "response_time": 3.0,
        }
        s1 = scorer.score_response("Q1", "A1", audio_features1)
        s2 = scorer.score_response("Q2", "A2", audio_features2)
        best = scorer.get_best_score()
        assert best.overall >= s1.overall
        assert best.overall >= s2.overall

    def test_get_worst_score(self):
        scorer = RealtimeScorer()
        audio_features1 = {
            "volume_variance": 0.8,
            "pitch_variation": 0.1,
            "speech_rate": 300,
            "filler_words": 10,
            "pause_count": 5,
            "response_time": 10.0,
        }
        audio_features2 = {
            "volume_variance": 0.05,
            "pitch_variation": 0.9,
            "speech_rate": 140,
            "filler_words": 0,
            "pause_count": 0,
            "response_time": 3.0,
        }
        s1 = scorer.score_response("Q1", "A1", audio_features1)
        s2 = scorer.score_response("Q2", "A2", audio_features2)
        worst = scorer.get_worst_score()
        assert worst.overall <= s1.overall
        assert worst.overall <= s2.overall

    def test_get_score_count(self):
        scorer = RealtimeScorer()
        assert scorer.get_score_count() == 0
        audio_features = {"response_time": 3.0}
        scorer.score_response("Q", "A", audio_features)
        assert scorer.get_score_count() == 1
        scorer.score_response("Q2", "A2", audio_features)
        assert scorer.get_score_count() == 2

    def test_get_session_summary(self):
        scorer = RealtimeScorer()
        audio_features = {
            "volume_variance": 0.1,
            "pitch_variation": 0.8,
            "speech_rate": 140,
            "filler_words": 0,
            "pause_count": 1,
            "response_time": 3.0,
        }
        scorer.score_response("Q1", "A1", audio_features)
        scorer.score_response("Q2", "A2", audio_features)
        summary = scorer.get_session_summary()
        assert "average_score" in summary
        assert "best_score" in summary
        assert "worst_score" in summary
        assert "total_responses" in summary
        assert summary["total_responses"] == 2


# ═══════════════════════════════════════════════════
# Scoring Models
# ═══════════════════════════════════════════════════

class TestScoreBreakdown:
    def test_creation(self):
        breakdown = ScoreBreakdown(
            confidence=0.8,
            clarity=0.9,
            relevance=0.7,
            response_time=5.0,
            overall=78.5,
            weights={"confidence": 0.3, "clarity": 0.3, "relevance": 0.4},
        )
        assert breakdown.confidence == 0.8
        assert breakdown.clarity == 0.9
        assert breakdown.relevance == 0.7
        assert breakdown.weights["relevance"] == 0.4

    def test_to_dict(self):
        breakdown = ScoreBreakdown(
            confidence=0.8,
            clarity=0.9,
            relevance=0.7,
            response_time=5.0,
            overall=78.5,
            weights={"confidence": 0.3, "clarity": 0.3, "relevance": 0.4},
        )
        d = breakdown.to_dict()
        assert isinstance(d, dict)
        assert d["confidence"] == 0.8
        assert d["overall"] == 78.5


class TestSessionAnalytics:
    def test_creation(self):
        analytics = SessionAnalytics(
            session_id="sess-123",
            total_questions=10,
            average_score=72.5,
            scores=[],
            duration_seconds=600,
        )
        assert analytics.session_id == "sess-123"
        assert analytics.total_questions == 10
        assert analytics.average_score == 72.5

    def test_to_dict(self):
        analytics = SessionAnalytics(
            session_id="sess-123",
            total_questions=10,
            average_score=72.5,
            scores=[],
            duration_seconds=600,
        )
        d = analytics.to_dict()
        assert isinstance(d, dict)
        assert d["session_id"] == "sess-123"


class TestSkillGapReport:
    def test_creation(self):
        report = SkillGapReport(
            category="technical",
            current_score=0.6,
            target_score=0.8,
            gap=0.2,
            recommendations=["Practice system design questions"],
        )
        assert report.category == "technical"
        assert report.gap == 0.2
        assert len(report.recommendations) == 1

    def test_to_dict(self):
        report = SkillGapReport(
            category="technical",
            current_score=0.6,
            target_score=0.8,
            gap=0.2,
            recommendations=["Practice system design questions"],
        )
        d = report.to_dict()
        assert isinstance(d, dict)
        assert d["gap"] == 0.2


class TestPerformanceMetrics:
    def test_creation(self):
        metrics = PerformanceMetrics(
            total_sessions=5,
            average_score=72.0,
            improvement_rate=0.15,
            strongest_category="hr",
            weakest_category="technical",
        )
        assert metrics.total_sessions == 5
        assert metrics.improvement_rate == 0.15

    def test_to_dict(self):
        metrics = PerformanceMetrics(
            total_sessions=5,
            average_score=72.0,
            improvement_rate=0.15,
            strongest_category="hr",
            weakest_category="technical",
        )
        d = metrics.to_dict()
        assert isinstance(d, dict)
        assert d["strongest_category"] == "hr"


# ═══════════════════════════════════════════════════
# SkillGapAnalyzer
# ═══════════════════════════════════════════════════

class TestSkillGapAnalyzerInit:
    def test_init(self):
        analyzer = SkillGapAnalyzer()
        assert analyzer is not None

    def test_init_with_custom_targets(self):
        targets = {"technical": 0.9, "hr": 0.7}
        analyzer = SkillGapAnalyzer(target_scores=targets)
        assert analyzer.target_scores["technical"] == 0.9


class TestSkillGapAnalyzerAnalysis:
    def test_analyze_scores_by_category(self):
        analyzer = SkillGapAnalyzer()
        scores = [
            {"category": "technical", "overall": 60.0},
            {"category": "technical", "overall": 70.0},
            {"category": "hr", "overall": 85.0},
            {"category": "hr", "overall": 90.0},
        ]
        report = analyzer.analyze(scores)
        assert isinstance(report, list)
        assert len(report) >= 1

    def test_report_identifies_gaps(self):
        analyzer = SkillGapAnalyzer()
        scores = [
            {"category": "technical", "overall": 40.0},
            {"category": "technical", "overall": 50.0},
        ]
        report = analyzer.analyze(scores)
        technical_gap = [r for r in report if r.category == "technical"]
        assert len(technical_gap) == 1
        assert technical_gap[0].current_score < technical_gap[0].target_score
        assert technical_gap[0].gap > 0

    def test_report_no_gap_when_above_target(self):
        analyzer = SkillGapAnalyzer(target_scores={"hr": 0.7})
        scores = [
            {"category": "hr", "overall": 95.0},
            {"category": "hr", "overall": 90.0},
        ]
        report = analyzer.analyze(scores)
        hr_gaps = [r for r in report if r.category == "hr"]
        if hr_gaps:
            assert hr_gaps[0].gap <= 0

    def test_empty_scores(self):
        analyzer = SkillGapAnalyzer()
        report = analyzer.analyze([])
        assert report == []

    def test_report_has_recommendations(self):
        analyzer = SkillGapAnalyzer()
        scores = [
            {"category": "coding", "overall": 30.0},
            {"category": "coding", "overall": 40.0},
        ]
        report = analyzer.analyze(scores)
        coding_gaps = [r for r in report if r.category == "coding"]
        assert len(coding_gaps) == 1
        assert len(coding_gaps[0].recommendations) > 0

    def test_performance_metrics(self):
        analyzer = SkillGapAnalyzer()
        session_scores = [
            [
                {"category": "technical", "overall": 60.0},
                {"category": "hr", "overall": 80.0},
            ],
            [
                {"category": "technical", "overall": 75.0},
                {"category": "hr", "overall": 85.0},
            ],
        ]
        metrics = analyzer.calculate_performance_metrics(session_scores)
        assert isinstance(metrics, PerformanceMetrics)
        assert metrics.total_sessions == 2
        assert metrics.average_score > 0
        assert metrics.strongest_category in ("technical", "hr")
        assert metrics.weakest_category in ("technical", "hr")

    def test_improvement_rate(self):
        analyzer = SkillGapAnalyzer()
        session_scores = [
            [
                {"category": "technical", "overall": 50.0},
            ],
            [
                {"category": "technical", "overall": 70.0},
            ],
        ]
        metrics = analyzer.calculate_performance_metrics(session_scores)
        assert metrics.improvement_rate > 0

    def test_decline_rate(self):
        analyzer = SkillGapAnalyzer()
        session_scores = [
            [
                {"category": "technical", "overall": 80.0},
            ],
            [
                {"category": "technical", "overall": 60.0},
            ],
        ]
        metrics = analyzer.calculate_performance_metrics(session_scores)
        assert metrics.improvement_rate < 0
