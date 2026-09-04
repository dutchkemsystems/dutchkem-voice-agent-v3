import pytest
from apps.scoring.mode_scorer import ModeAwareScorer
from apps.modes.registry import ModeConfig


class TestModeAwareScorer:
    def test_init_with_mode(self):
        config = ModeConfig(
            mode_id="test",
            display_name="Test",
            description="Test",
            icon="test",
            agent_classes=["HRAgent"],
            default_agent="HRAgent",
        )
        scorer = ModeAwareScorer(config)
        assert scorer.mode == config

    def test_score_returns_base_dimensions(self):
        config = ModeConfig(
            mode_id="test",
            display_name="Test",
            description="Test",
            icon="test",
            agent_classes=["HRAgent"],
            default_agent="HRAgent",
        )
        scorer = ModeAwareScorer(config)
        result = scorer.score(
            question="Tell me about yourself",
            answer="I am a software engineer",
            audio_features={"_answer": "I am a software engineer"},
        )
        assert "confidence" in result
        assert "clarity" in result
        assert "relevance" in result

    def test_score_includes_overrides(self):
        config = ModeConfig(
            mode_id="sales",
            display_name="Sales",
            description="Test",
            icon="test",
            agent_classes=["SalesAgent"],
            default_agent="SalesAgent",
            scoring_overrides={"persuasion": 0.25, "objection_handling": 0.20},
        )
        scorer = ModeAwareScorer(config)
        result = scorer.score(
            question="What's the pricing?",
            answer="Our enterprise plan starts at $99/month",
            audio_features={"_answer": "Our enterprise plan starts at $99/month"},
        )
        assert "persuasion" in result
        assert "objection_handling" in result

    def test_score_weighted_average(self):
        config = ModeConfig(
            mode_id="sales",
            display_name="Sales",
            description="Test",
            icon="test",
            agent_classes=["SalesAgent"],
            default_agent="SalesAgent",
            scoring_overrides={"persuasion": 0.25},
        )
        scorer = ModeAwareScorer(config)
        result = scorer.score(
            question="Tell me about the product",
            answer="It's a great product",
            audio_features={"_answer": "It's a great product"},
        )
        assert "overall" in result
        assert 0.0 <= result["overall"] <= 1.0

    def test_score_without_overrides(self):
        config = ModeConfig(
            mode_id="interview",
            display_name="Interview",
            description="Test",
            icon="test",
            agent_classes=["HRAgent"],
            default_agent="HRAgent",
            scoring_overrides={},
        )
        scorer = ModeAwareScorer(config)
        result = scorer.score(
            question="Tell me about yourself",
            answer="I am a software engineer",
            audio_features={"_answer": "I am a software engineer"},
        )
        assert "overall" in result
        assert 0.0 <= result["overall"] <= 1.0
