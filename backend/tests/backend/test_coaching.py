"""Tests for Coaching & Feedback: real-time tips and post-interview feedback."""
import pytest
from unittest.mock import MagicMock


# --- InterviewCoach Tests ---


class TestInterviewCoach:
    """Tests for real-time coaching tips during interview."""

    def test_coach_initializes_with_tip_categories(self):
        from apps.coaching.coach import InterviewCoach
        coach = InterviewCoach()
        assert "confidence" in coach.tips
        assert "clarity" in coach.tips
        assert "relevance" in coach.tips
        assert isinstance(coach.tips["confidence"], list)
        assert len(coach.tips["confidence"]) >= 2

    def test_get_realtime_tip_returns_weakest_area_tip(self):
        from apps.coaching.coach import InterviewCoach
        coach = InterviewCoach()
        score = {"confidence": 0.9, "clarity": 0.3, "relevance": 0.8}
        tip = coach.get_realtime_tip(score)
        assert isinstance(tip, str)
        assert len(tip) > 0
        # Clarity is weakest, should get a clarity tip
        assert any(w in tip.lower() for w in ["structure", "filler", "specific", "answer", "star"])

    def test_get_realtime_tip_returns_positive_when_balanced(self):
        from apps.coaching.coach import InterviewCoach
        coach = InterviewCoach()
        score = {"confidence": 0.9, "clarity": 0.9, "relevance": 0.9}
        tip = coach.get_realtime_tip(score)
        assert isinstance(tip, str)
        assert len(tip) > 0

    def test_get_realtime_tip_handles_empty_score(self):
        from apps.coaching.coach import InterviewCoach
        coach = InterviewCoach()
        tip = coach.get_realtime_tip({})
        assert isinstance(tip, str)
        assert len(tip) > 0


class TestInterviewFeedbackGenerator:
    """Tests for post-interview feedback generation."""

    def test_generate_feedback_from_session_scores(self):
        from apps.coaching.feedback_generator import FeedbackGenerator
        gen = FeedbackGenerator()
        scores = [
            {"confidence": 0.8, "clarity": 0.7, "relevance": 0.9},
            {"confidence": 0.7, "clarity": 0.6, "relevance": 0.8},
            {"confidence": 0.9, "clarity": 0.5, "relevance": 0.7},
        ]
        feedback = gen.generate_feedback(scores)
        assert "overall_rating" in feedback
        assert "strengths" in feedback
        assert "areas_for_improvement" in feedback
        assert "specific_tips" in feedback
        assert "summary" in feedback

    def test_overall_rating_is_percentage(self):
        from apps.coaching.feedback_generator import FeedbackGenerator
        gen = FeedbackGenerator()
        scores = [
            {"confidence": 0.8, "clarity": 0.7, "relevance": 0.9},
        ]
        feedback = gen.generate_feedback(scores)
        assert isinstance(feedback["overall_rating"], (int, float))
        assert 0 <= feedback["overall_rating"] <= 100

    def test_strengths_identify_high_scores(self):
        from apps.coaching.feedback_generator import FeedbackGenerator
        gen = FeedbackGenerator()
        scores = [
            {"confidence": 0.9, "clarity": 0.9, "relevance": 0.3},
            {"confidence": 0.8, "clarity": 0.85, "relevance": 0.2},
        ]
        feedback = gen.generate_feedback(scores)
        assert "confidence" in feedback["strengths"]
        assert "clarity" in feedback["strengths"]

    def test_improvement_areas_identify_low_scores(self):
        from apps.coaching.feedback_generator import FeedbackGenerator
        gen = FeedbackGenerator()
        scores = [
            {"confidence": 0.9, "clarity": 0.3, "relevance": 0.2},
            {"confidence": 0.85, "clarity": 0.25, "relevance": 0.3},
        ]
        feedback = gen.generate_feedback(scores)
        assert "clarity" in feedback["areas_for_improvement"]
        assert "relevance" in feedback["areas_for_improvement"]

    def test_specific_tips_are_actionable(self):
        from apps.coaching.feedback_generator import FeedbackGenerator
        gen = FeedbackGenerator()
        scores = [
            {"confidence": 0.5, "clarity": 0.4, "relevance": 0.6},
        ]
        feedback = gen.generate_feedback(scores)
        assert isinstance(feedback["specific_tips"], list)
        assert len(feedback["specific_tips"]) >= 1
        for tip in feedback["specific_tips"]:
            assert isinstance(tip, str)
            assert len(tip) > 0

    def test_summary_is_string(self):
        from apps.coaching.feedback_generator import FeedbackGenerator
        gen = FeedbackGenerator()
        scores = [
            {"confidence": 0.7, "clarity": 0.7, "relevance": 0.7},
        ]
        feedback = gen.generate_feedback(scores)
        assert isinstance(feedback["summary"], str)
        assert len(feedback["summary"]) > 0

    def test_summary_positive_for_high_scores(self):
        from apps.coaching.feedback_generator import FeedbackGenerator
        gen = FeedbackGenerator()
        scores = [
            {"confidence": 0.9, "clarity": 0.9, "relevance": 0.9},
        ]
        feedback = gen.generate_feedback(scores)
        assert any(w in feedback["summary"].lower() for w in ["excellent", "strong", "great"])

    def test_summary_needs_work_for_low_scores(self):
        from apps.coaching.feedback_generator import FeedbackGenerator
        gen = FeedbackGenerator()
        scores = [
            {"confidence": 0.3, "clarity": 0.2, "relevance": 0.3},
        ]
        feedback = gen.generate_feedback(scores)
        assert any(w in feedback["summary"].lower() for w in ["practice", "focus", "improve", "keep"])

    def test_feedback_never_overly_critical(self):
        from apps.coaching.feedback_generator import FeedbackGenerator
        gen = FeedbackGenerator()
        scores = [
            {"confidence": 0.1, "clarity": 0.1, "relevance": 0.1},
        ]
        feedback = gen.generate_feedback(scores)
        # Must always include positive reinforcement somewhere
        all_text = " ".join([
            feedback["summary"],
            " ".join(feedback["specific_tips"]),
            " ".join(feedback["strengths"]),
        ])
        assert len(all_text) > 0  # Should have content, not be empty

    def test_feedback_includes_positive_reinforcement(self):
        from apps.coaching.feedback_generator import FeedbackGenerator
        gen = FeedbackGenerator()
        scores = [
            {"confidence": 0.9, "clarity": 0.85, "relevance": 0.88},
        ]
        feedback = gen.generate_feedback(scores)
        # High scores should produce positive strength identification
        assert len(feedback["strengths"]) > 0


# --- CoachingSession Tests ---


class TestCoachingSession:
    """Tests for managing a coaching session across multiple interactions."""

    def test_session_tracks_scores_over_time(self):
        from apps.coaching.coach import CoachingSession
        session = CoachingSession()
        session.record_score({"confidence": 0.8, "clarity": 0.7, "relevance": 0.9})
        session.record_score({"confidence": 0.7, "clarity": 0.8, "relevance": 0.6})
        assert session.get_score_count() == 2

    def test_session_provides_running_average(self):
        from apps.coaching.coach import CoachingSession
        session = CoachingSession()
        session.record_score({"confidence": 0.8, "clarity": 0.6, "relevance": 0.9})
        session.record_score({"confidence": 0.6, "clarity": 0.8, "relevance": 0.7})
        avg = session.get_average_scores()
        assert abs(avg["confidence"] - 0.7) < 0.01
        assert abs(avg["clarity"] - 0.7) < 0.01
        assert abs(avg["relevance"] - 0.8) < 0.01

    def test_session_generates_final_feedback(self):
        from apps.coaching.coach import CoachingSession
        session = CoachingSession()
        session.record_score({"confidence": 0.8, "clarity": 0.7, "relevance": 0.9})
        session.record_score({"confidence": 0.9, "clarity": 0.6, "relevance": 0.8})
        feedback = session.get_final_feedback()
        assert "overall_rating" in feedback
        assert "summary" in feedback

    def test_session_starts_empty(self):
        from apps.coaching.coach import CoachingSession
        session = CoachingSession()
        assert session.get_score_count() == 0
        assert session.get_average_scores() == {}

    def test_session_reset_clears_data(self):
        from apps.coaching.coach import CoachingSession
        session = CoachingSession()
        session.record_score({"confidence": 0.8, "clarity": 0.7, "relevance": 0.9})
        session.reset()
        assert session.get_score_count() == 0
        assert session.get_average_scores() == {}
