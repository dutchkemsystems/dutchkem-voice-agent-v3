import pytest
from apps.modes.registry import ModeConfig, ModeRegistry


class TestModeConfig:
    def test_creation_minimal(self):
        config = ModeConfig(
            mode_id="test",
            display_name="Test Mode",
            description="A test mode",
            icon="test",
            agent_classes=["HRAgent"],
            default_agent="HRAgent",
        )
        assert config.mode_id == "test"
        assert config.display_name == "Test Mode"
        assert config.agent_classes == ["HRAgent"]

    def test_creation_with_defaults(self):
        config = ModeConfig(
            mode_id="test",
            display_name="Test",
            description="Test",
            icon="test",
            agent_classes=["HRAgent"],
            default_agent="HRAgent",
        )
        assert config.trigger_keywords == []
        assert config.scoring_overrides == {}
        assert config.coaching_tips == {}
        assert config.required_context == []
        assert config.allowed_transitions == []
        assert config.transition_permissions == []
        assert config.auto_detect_enabled is True
        assert config.ui_components == ["transcript_panel"]
        assert config.default_view == "transcript"

    def test_creation_full(self):
        config = ModeConfig(
            mode_id="sales",
            display_name="Sales",
            description="Pitch products",
            icon="trending-up",
            agent_classes=["SalesAgent"],
            default_agent="SalesAgent",
            trigger_keywords=["pitch", "demo"],
            scoring_overrides={"persuasion": 0.25},
            coaching_tips={"confidence": ["Be bold"]},
            required_context=["product_info"],
            allowed_transitions=["client_meeting"],
            transition_permissions=["admin"],
            auto_detect_enabled=False,
            ui_components=["transcript_panel", "deal_pipeline"],
            default_view="deal_pipeline",
            on_enter_prompt="Sales mode activated",
            on_exit_prompt="Sales session ended",
            system_prompt="You are a sales professional",
            response_style="friendly",
        )
        assert config.mode_id == "sales"
        assert config.trigger_keywords == ["pitch", "demo"]
        assert config.scoring_overrides == {"persuasion": 0.25}
        assert config.required_context == ["product_info"]
        assert config.auto_detect_enabled is False

    def test_to_dict(self):
        config = ModeConfig(
            mode_id="test",
            display_name="Test",
            description="Test",
            icon="test",
            agent_classes=["HRAgent"],
            default_agent="HRAgent",
        )
        d = config.to_dict()
        assert isinstance(d, dict)
        assert d["mode_id"] == "test"
        assert d["agent_classes"] == ["HRAgent"]


class TestModeRegistry:
    def test_get_all_modes(self):
        modes = ModeRegistry.get_all()
        assert len(modes) == 9
        mode_ids = [m.mode_id for m in modes]
        assert "interview" in mode_ids
        assert "client_meeting" in mode_ids
        assert "mentoring" in mode_ids
        assert "performance_review" in mode_ids
        assert "board_presentation" in mode_ids
        assert "sales" in mode_ids
        assert "training" in mode_ids
        assert "internal_comms" in mode_ids
        assert "customer_support" in mode_ids

    def test_get_mode_by_id(self):
        mode = ModeRegistry.get("interview")
        assert mode is not None
        assert mode.mode_id == "interview"
        assert mode.display_name == "Interview"

    def test_get_nonexistent_mode(self):
        mode = ModeRegistry.get("nonexistent")
        assert mode is None

    def test_get_mode_ids(self):
        ids = ModeRegistry.get_ids()
        assert isinstance(ids, list)
        assert len(ids) == 9

    def test_interview_mode_has_correct_agents(self):
        mode = ModeRegistry.get("interview")
        assert "HRAgent" in mode.agent_classes
        assert "TechnicalAgent" in mode.agent_classes
        assert "CodingAgent" in mode.agent_classes
        assert "ManagerAgent" in mode.agent_classes

    def test_sales_mode_has_dedicated_agent(self):
        mode = ModeRegistry.get("sales")
        assert mode.agent_classes == ["SalesAgent"]

    def test_board_mode_has_required_context(self):
        mode = ModeRegistry.get("board_presentation")
        assert "agenda" in mode.required_context
        assert "financial_data" in mode.required_context

    def test_modes_have_coaching_tips(self):
        for mode in ModeRegistry.get_all():
            assert isinstance(mode.coaching_tips, dict)
            assert len(mode.coaching_tips) > 0
