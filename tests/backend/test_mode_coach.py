import pytest
from apps.coaching.mode_coach import ModeAwareCoach
from apps.modes.registry import ModeConfig


class TestModeAwareCoach:
    def test_interview_coach_returns_confidence_tip(self):
        config = ModeConfig(
            mode_id="interview",
            display_name="Interview",
            description="Test",
            icon="test",
            agent_classes=["HRAgent"],
            default_agent="HRAgent",
            coaching_tips={
                "confidence": ["Speak slowly", "Maintain volume"],
                "clarity": ["Use STAR method"],
                "relevance": ["Address the question"],
            },
        )
        coach = ModeAwareCoach(config)
        tip = coach.get_tip({"confidence": 0.3, "clarity": 0.8, "relevance": 0.7})
        assert tip in ["Speak slowly", "Maintain volume"]

    def test_sales_coach_returns_persuasion_tip(self):
        config = ModeConfig(
            mode_id="sales",
            display_name="Sales",
            description="Test",
            icon="test",
            agent_classes=["SalesAgent"],
            default_agent="SalesAgent",
            coaching_tips={
                "confidence": ["Be bold"],
                "persuasion": ["Use social proof"],
                "objection_handling": ["Reframe concerns"],
            },
        )
        coach = ModeAwareCoach(config)
        tip = coach.get_tip({"confidence": 0.8, "persuasion": 0.3, "objection_handling": 0.7})
        assert tip == "Use social proof"

    def test_coach_returns_positive_when_balanced(self):
        config = ModeConfig(
            mode_id="test",
            display_name="Test",
            description="Test",
            icon="test",
            agent_classes=["HRAgent"],
            default_agent="HRAgent",
            coaching_tips={
                "confidence": ["Tip A"],
                "clarity": ["Tip B"],
            },
        )
        coach = ModeAwareCoach(config)
        tip = coach.get_tip({"confidence": 0.8, "clarity": 0.8})
        assert tip is not None
        assert isinstance(tip, str)

    def test_coach_handles_empty_scores(self):
        config = ModeConfig(
            mode_id="test",
            display_name="Test",
            description="Test",
            icon="test",
            agent_classes=["HRAgent"],
            default_agent="HRAgent",
            coaching_tips={"confidence": ["Tip"]},
        )
        coach = ModeAwareCoach(config)
        tip = coach.get_tip({})
        assert tip == "You're doing great! Keep it up."

    def test_coach_generates_feedback(self):
        config = ModeConfig(
            mode_id="test",
            display_name="Test",
            description="Test",
            icon="test",
            agent_classes=["HRAgent"],
            default_agent="HRAgent",
            coaching_tips={"confidence": ["Tip"]},
            feedback_templates={
                "positive": "Great {dimension}!",
                "improvement": "Work on {dimension}.",
            },
        )
        coach = ModeAwareCoach(config)
        feedback = coach.generate_feedback({"confidence": 0.3, "clarity": 0.8})
        assert isinstance(feedback, dict)
        assert "strengths" in feedback
        assert "improvements" in feedback
        assert "tips" in feedback
