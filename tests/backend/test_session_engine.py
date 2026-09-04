import pytest
from apps.orchestrator.session_engine import SessionEngine
from apps.modes.registry import ModeRegistry


class TestSessionEngine:
    def test_init_default_mode(self):
        engine = SessionEngine()
        assert engine.current_mode.mode_id == "interview"

    def test_init_with_mode(self):
        engine = SessionEngine(mode_id="sales")
        assert engine.current_mode.mode_id == "sales"

    def test_switch_mode(self):
        engine = SessionEngine()
        result = engine.switch_mode("client_meeting")
        assert result is True
        assert engine.current_mode.mode_id == "client_meeting"

    def test_switch_invalid_mode(self):
        engine = SessionEngine()
        result = engine.switch_mode("nonexistent")
        assert result is False
        assert engine.current_mode.mode_id == "interview"

    def test_get_mode_config(self):
        engine = SessionEngine()
        config = engine.get_mode_config()
        assert config.mode_id == "interview"

    def test_get_available_modes(self):
        engine = SessionEngine()
        modes = engine.get_available_modes()
        assert len(modes) == 9

    def test_can_transition(self):
        engine = SessionEngine()
        assert engine.can_transition("client_meeting") is True
        assert engine.can_transition("sales") is False

    def test_session_stats(self):
        engine = SessionEngine()
        stats = engine.get_session_stats()
        assert "mode" in stats
        assert "duration" in stats
        assert "turns" in stats
