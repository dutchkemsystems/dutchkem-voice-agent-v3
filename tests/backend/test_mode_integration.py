"""
Integration tests for post-hire mode system.
Tests the full flow: registry -> session engine -> API endpoints.
"""
import pytest
from httpx import AsyncClient, ASGITransport

from apps.modes.registry import ModeRegistry, ModeConfig
from apps.orchestrator.session_engine import SessionEngine
from apps.scoring.mode_scorer import ModeAwareScorer
from apps.coaching.mode_coach import ModeAwareCoach
from apps.interview.agents import (
    ClientMeetingAgent,
    MentoringAgent,
    PerformanceReviewAgent,
    BoardPresentationAgent,
    SalesAgent,
    TrainingAgent,
    InternalCommsAgent,
    CustomerSupportAgent,
)
from backend.config.app import app


class TestModeRegistryIntegration:
    """Test ModeRegistry provides complete mode coverage."""

    def test_all_nine_modes_registered(self):
        modes = ModeRegistry.get_all()
        assert len(modes) == 9

    def test_all_modes_have_required_fields(self):
        for mode in ModeRegistry.get_all():
            assert mode.mode_id
            assert mode.display_name
            assert mode.description
            assert mode.icon
            assert mode.agent_classes
            assert mode.default_agent

    def test_each_mode_has_corresponding_agent(self):
        """Each mode should reference at least one agent class (PascalCase)."""
        agent_map = {
            "interview": ["HRAgent", "TechnicalAgent", "CodingAgent", "ManagerAgent"],
            "client_meeting": ["ClientMeetingAgent"],
            "mentoring": ["MentoringAgent"],
            "performance_review": ["PerformanceReviewAgent"],
            "board_presentation": ["BoardPresentationAgent"],
            "sales": ["SalesAgent"],
            "training": ["TrainingAgent"],
            "internal_comms": ["InternalCommsAgent"],
            "customer_support": ["CustomerSupportAgent"],
        }
        for mode in ModeRegistry.get_all():
            expected = agent_map.get(mode.mode_id, [])
            assert len(expected) > 0, f"Mode {mode.mode_id} has no expected agents defined"
            for agent_name in expected:
                assert agent_name in mode.agent_classes, (
                    f"Mode {mode.mode_id} missing agent {agent_name}; "
                    f"got {mode.agent_classes}"
                )

    def test_modes_have_allowed_transitions(self):
        """Each mode (except some) should have transition rules."""
        for mode in ModeRegistry.get_all():
            assert isinstance(mode.allowed_transitions, list)


class TestSessionEngineModeIntegration:
    """Test SessionEngine works with valid transitions."""

    def test_session_starts_with_interview_mode(self):
        engine = SessionEngine()
        assert engine.current_mode.mode_id == "interview"

    def test_switch_to_allowed_modes_from_interview(self):
        engine = SessionEngine()
        # Interview allows: client_meeting, mentoring, training
        for mode_id in ["client_meeting", "mentoring", "training"]:
            result = engine.switch_mode(mode_id)
            assert result is True, f"Failed to switch to {mode_id}"
            assert engine.current_mode.mode_id == mode_id
            # Reset back to interview for next iteration
            engine.switch_mode("interview")

    def test_switch_to_disallowed_mode_fails(self):
        engine = SessionEngine()
        # Interview does NOT allow switching directly to sales
        result = engine.switch_mode("sales")
        assert result is False

    def test_invalid_mode_returns_false(self):
        engine = SessionEngine()
        result = engine.switch_mode("nonexistent_mode")
        assert result is False

    def test_scorer_updates_on_valid_switch(self):
        engine = SessionEngine()
        engine.switch_mode("client_meeting")
        assert engine.current_mode.mode_id == "client_meeting"
        assert engine.scorer.mode.mode_id == "client_meeting"

    def test_coach_updates_on_valid_switch(self):
        engine = SessionEngine()
        engine.switch_mode("training")
        assert engine.coach.mode.mode_id == "training"

    def test_process_response_in_training_mode(self):
        engine = SessionEngine()
        engine.switch_mode("training")
        result = engine.process_response(
            question="How do I use the system?",
            answer="You can click the button here.",
            audio_features={"energy": 0.7, "pace": 1.0},
        )
        assert result["mode"] == "training"
        assert "scores" in result
        assert "coaching_tip" in result

    def test_switch_chain_interview_to_client_to_internal(self):
        """Test multi-step switch: interview -> client_meeting -> internal_comms."""
        engine = SessionEngine()
        # Step 1: interview -> client_meeting
        assert engine.switch_mode("client_meeting") is True
        assert engine.current_mode.mode_id == "client_meeting"
        # Step 2: client_meeting -> internal_comms (allowed)
        assert engine.switch_mode("internal_comms") is True
        assert engine.current_mode.mode_id == "internal_comms"


class TestAgentClassIntegration:
    """Test all agent classes can be instantiated."""

    @pytest.fixture
    def mock_llm(self):
        from unittest.mock import AsyncMock
        return AsyncMock()

    def test_client_meeting_agent(self, mock_llm):
        agent = ClientMeetingAgent(user_profile={}, company_context={}, llm_service=mock_llm)
        assert agent.AGENT_TYPE == "client_meeting"

    def test_mentoring_agent(self, mock_llm):
        agent = MentoringAgent(user_profile={}, company_context={}, llm_service=mock_llm)
        assert agent.AGENT_TYPE == "mentoring"

    def test_performance_review_agent(self, mock_llm):
        agent = PerformanceReviewAgent(user_profile={}, company_context={}, llm_service=mock_llm)
        assert agent.AGENT_TYPE == "performance_review"

    def test_board_presentation_agent(self, mock_llm):
        agent = BoardPresentationAgent(user_profile={}, company_context={}, llm_service=mock_llm)
        assert agent.AGENT_TYPE == "board_presentation"

    def test_sales_agent(self, mock_llm):
        agent = SalesAgent(user_profile={}, company_context={}, llm_service=mock_llm)
        assert agent.AGENT_TYPE == "sales"

    def test_training_agent(self, mock_llm):
        agent = TrainingAgent(user_profile={}, company_context={}, llm_service=mock_llm)
        assert agent.AGENT_TYPE == "training"

    def test_internal_comms_agent(self, mock_llm):
        agent = InternalCommsAgent(user_profile={}, company_context={}, llm_service=mock_llm)
        assert agent.AGENT_TYPE == "internal_comms"

    def test_customer_support_agent(self, mock_llm):
        agent = CustomerSupportAgent(user_profile={}, company_context={}, llm_service=mock_llm)
        assert agent.AGENT_TYPE == "customer_support"


class TestAPIEndpointIntegration:
    """Test API endpoints via HTTP client."""

    @pytest.fixture
    def anyio_backend(self):
        return "asyncio"

    @pytest.mark.anyio
    async def test_list_modes_returns_all_nine(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/modes/")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 9

    @pytest.mark.anyio
    async def test_get_mode_then_switch_to_it(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Get sales mode
            get_resp = await client.get("/api/modes/sales")
            assert get_resp.status_code == 200
            mode = get_resp.json()
            assert mode["mode_id"] == "sales"

            # Switch to it
            switch_resp = await client.post(
                "/api/modes/switch",
                json={"mode_id": "sales"},
            )
            assert switch_resp.status_code == 200
            result = switch_resp.json()
            assert result["success"] is True
            assert result["mode"]["mode_id"] == "sales"

    @pytest.mark.anyio
    async def test_full_mode_cycle(self):
        """Test: list -> get -> switch -> get -> switch back."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # List all modes
            list_resp = await client.get("/api/modes/")
            modes = list_resp.json()["modes"]
            assert len(modes) == 9

            # Get first non-interview mode
            target = next(m for m in modes if m["mode_id"] != "interview")
            get_resp = await client.get(f"/api/modes/{target['mode_id']}")
            assert get_resp.status_code == 200

            # Switch to it
            switch_resp = await client.post(
                "/api/modes/switch",
                json={"mode_id": target["mode_id"]},
            )
            assert switch_resp.status_code == 200
            assert switch_resp.json()["success"] is True

            # Switch back to interview
            switch_back = await client.post(
                "/api/modes/switch",
                json={"mode_id": "interview"},
            )
            assert switch_back.status_code == 200
            assert switch_back.json()["mode"]["mode_id"] == "interview"

    @pytest.mark.anyio
    async def test_get_nonexistent_mode_returns_404(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/modes/does_not_exist")
        assert response.status_code == 404

    @pytest.mark.anyio
    async def test_switch_invalid_mode_returns_400(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/modes/switch",
                json={"mode_id": "invalid_mode"},
            )
        assert response.status_code == 400
