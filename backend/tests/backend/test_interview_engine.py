import pytest
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime

from apps.interview.engine import AutonomousInterviewEngine
from apps.interview.adaptive import AdaptiveDifficulty, DifficultyLevel, PerformanceMetrics
from apps.interview.response_generator import ResponseGenerator, InterviewResponse
from apps.interview.agents.base_agent import InterviewQuestion, InterviewAnswer
from apps.interview.orchestrator import InterviewOrchestrator
from apps.background.trigger_detector import InterviewTriggerDetector, InterviewPhase


# ═══════════════════════════════════════════════════
# Shared fixtures
# ═══════════════════════════════════════════════════

@pytest.fixture
def user_profile():
    return {
        "name": "Jane Doe",
        "position": "Senior Engineer",
        "company": "Acme Corp",
        "resume_summary": "10 years Python, 5 years system design",
        "achievements": "Led team of 8, shipped 3 products",
        "technical_skills": "Python, Go, Kubernetes, AWS",
        "voice_profile_id": "af_heart",
    }


@pytest.fixture
def company_context():
    return {
        "name": "TechStart Inc",
        "industry": "SaaS",
        "values": ["innovation", "collaboration"],
        "position": "Senior Software Engineer",
    }


@pytest.fixture
def mock_stt():
    stt = AsyncMock()
    stt.transcribe_async = AsyncMock(return_value="Tell me about yourself")
    return stt


@pytest.fixture
def mock_tts():
    tts = AsyncMock()
    tts.synthesize_async = AsyncMock(return_value=b"fake-audio-bytes")
    return tts


@pytest.fixture
def mock_face():
    face = MagicMock()
    face.detect_and_embed = MagicMock(return_value=[{"bbox": [0, 0, 100, 100], "embedding": [0.1] * 512}])
    return face


@pytest.fixture
def mock_llm():
    llm = AsyncMock()
    llm.generate_interview_answer = AsyncMock(return_value="Sample LLM answer")
    return llm


@pytest.fixture
def mock_orchestrator(mock_llm, user_profile, company_context):
    orch = AsyncMock(spec=InterviewOrchestrator)
    orch.user_profile = user_profile
    orch.company_context = company_context
    orch.process_question = AsyncMock(return_value=InterviewAnswer(
        text="I am a senior engineer with 10 years of experience.",
        confidence=0.85,
        follow_ups=["Can you elaborate on your leadership?"],
        agent_type="hr",
    ))
    return orch


# ═══════════════════════════════════════════════════
# AdaptiveDifficulty tests
# ═══════════════════════════════════════════════════

class TestDifficultyLevel:
    def test_enum_values(self):
        assert DifficultyLevel.EASY.value == "easy"
        assert DifficultyLevel.MEDIUM.value == "medium"
        assert DifficultyLevel.HARD.value == "hard"


class TestPerformanceMetrics:
    def test_creation(self):
        m = PerformanceMetrics(
            confidence=0.8,
            response_time=2.5,
            follow_ups_count=3,
            questions_answered=5,
        )
        assert m.confidence == 0.8
        assert m.response_time == 2.5
        assert m.follow_ups_count == 3
        assert m.questions_answered == 5

    def test_defaults(self):
        m = PerformanceMetrics()
        assert m.confidence == 0.0
        assert m.response_time == 0.0
        assert m.follow_ups_count == 0
        assert m.questions_answered == 0


class TestAdaptiveDifficulty:
    def test_init_default(self):
        ad = AdaptiveDifficulty()
        assert ad.current_difficulty == DifficultyLevel.MEDIUM
        assert ad.metrics.questions_answered == 0

    def test_init_custom_start(self):
        ad = AdaptiveDifficulty(starting_difficulty=DifficultyLevel.EASY)
        assert ad.current_difficulty == DifficultyLevel.EASY

    def test_record_response_increases_count(self):
        ad = AdaptiveDifficulty()
        ad.record_response(confidence=0.8, response_time=2.0, follow_ups_count=2)
        assert ad.metrics.questions_answered == 1

    def test_record_response_accumulates_metrics(self):
        ad = AdaptiveDifficulty()
        ad.record_response(confidence=0.9, response_time=1.5, follow_ups_count=1)
        ad.record_response(confidence=0.7, response_time=3.0, follow_ups_count=3)
        assert ad.metrics.questions_answered == 2
        assert ad.metrics.confidence == 0.8  # average of 0.9 and 0.7
        assert ad.metrics.follow_ups_count == 4  # sum

    def test_adjust_difficulty_stays_medium_initially(self):
        ad = AdaptiveDifficulty()
        ad.record_response(confidence=0.8, response_time=2.0, follow_ups_count=2)
        result = ad.adjust_difficulty()
        assert result["difficulty"] == DifficultyLevel.MEDIUM
        assert result["changed"] is False

    def test_adjust_difficulty_promotes_to_hard(self):
        ad = AdaptiveDifficulty()
        for _ in range(5):
            ad.record_response(confidence=0.9, response_time=1.5, follow_ups_count=2)
        result = ad.adjust_difficulty()
        assert result["difficulty"] == DifficultyLevel.HARD
        assert result["changed"] is True
        assert result["previous"] == DifficultyLevel.MEDIUM

    def test_adjust_difficulty_demotes_to_easy(self):
        ad = AdaptiveDifficulty()
        for _ in range(5):
            ad.record_response(confidence=0.3, response_time=5.0, follow_ups_count=0)
        result = ad.adjust_difficulty()
        assert result["difficulty"] == DifficultyLevel.EASY
        assert result["changed"] is True

    def test_adjust_difficulty_minimum_before_change(self):
        ad = AdaptiveDifficulty()
        ad.record_response(confidence=0.9, response_time=1.0, follow_ups_count=1)
        result = ad.adjust_difficulty()
        assert result["changed"] is False  # Only 1 response, not enough

    def test_get_recommended_category(self):
        ad = AdaptiveDifficulty()
        ad.current_difficulty = DifficultyLevel.HARD
        categories = ad.get_recommended_categories()
        assert "technical" in categories or "coding" in categories

    def test_get_recommended_categories_easy(self):
        ad = AdaptiveDifficulty()
        ad.current_difficulty = DifficultyLevel.EASY
        categories = ad.get_recommended_categories()
        assert "hr" in categories

    def test_reset(self):
        ad = AdaptiveDifficulty()
        ad.record_response(confidence=0.9, response_time=1.0, follow_ups_count=1)
        ad.adjust_difficulty()
        ad.reset()
        assert ad.current_difficulty == DifficultyLevel.MEDIUM
        assert ad.metrics.questions_answered == 0

    def test_get_performance_summary(self):
        ad = AdaptiveDifficulty()
        ad.record_response(confidence=0.8, response_time=2.0, follow_ups_count=2)
        summary = ad.get_performance_summary()
        assert summary["total_questions"] == 1
        assert summary["average_confidence"] == 0.8
        assert summary["current_difficulty"] == DifficultyLevel.MEDIUM.value


# ═══════════════════════════════════════════════════
# ResponseGenerator tests
# ═══════════════════════════════════════════════════

class TestInterviewResponse:
    def test_creation(self):
        r = InterviewResponse(
            text="Hello",
            audio=b"audio",
            avatar_data={"expression": "neutral"},
            confidence=0.9,
            agent_type="hr",
        )
        assert r.text == "Hello"
        assert r.audio == b"audio"
        assert r.avatar_data == {"expression": "neutral"}
        assert r.confidence == 0.9
        assert r.agent_type == "hr"

    def test_defaults(self):
        r = InterviewResponse(text="Hi")
        assert r.audio is None
        assert r.avatar_data is None
        assert r.confidence == 0.0
        assert r.agent_type is None


class TestResponseGenerator:
    def test_init(self):
        rg = ResponseGenerator()
        assert rg is not None

    @pytest.mark.asyncio
    async def test_generate_from_answer(self, mock_tts):
        rg = ResponseGenerator()
        answer = InterviewAnswer(
            text="I am experienced",
            confidence=0.85,
            follow_ups=["Can you tell more?"],
            agent_type="hr",
        )
        response = await rg.generate(answer, tts_service=mock_tts)
        assert isinstance(response, InterviewResponse)
        assert response.text == "I am experienced"
        assert response.confidence == 0.85
        assert response.agent_type == "hr"
        mock_tts.synthesize_async.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_calls_tts_with_text(self, mock_tts):
        rg = ResponseGenerator()
        answer = InterviewAnswer(
            text="My answer",
            confidence=0.7,
            follow_ups=[],
            agent_type="technical",
        )
        await rg.generate(answer, tts_service=mock_tts)
        mock_tts.synthesize_async.assert_called_once_with("My answer", "af_heart")

    @pytest.mark.asyncio
    async def test_generate_includes_avatar_data(self, mock_tts):
        rg = ResponseGenerator()
        answer = InterviewAnswer(
            text="Answer",
            confidence=0.9,
            follow_ups=[],
            agent_type="hr",
        )
        response = await rg.generate(answer, tts_service=mock_tts)
        assert response.avatar_data is not None
        assert "expression" in response.avatar_data
        assert "gesture" in response.avatar_data

    @pytest.mark.asyncio
    async def test_generate_determines_expression_by_agent_type(self, mock_tts):
        rg = ResponseGenerator()
        for agent_type, expected_expression in [
            ("hr", "friendly"),
            ("technical", "focused"),
            ("managerial", "confident"),
            ("coding", "analytical"),
        ]:
            answer = InterviewAnswer(text="Answer", confidence=0.8, follow_ups=[], agent_type=agent_type)
            response = await rg.generate(answer, tts_service=mock_tts)
            assert response.avatar_data["expression"] == expected_expression

    @pytest.mark.asyncio
    async def test_generate_intro_response(self, mock_tts):
        rg = ResponseGenerator()
        response = await rg.generate_introduction(
            user_name="Jane Doe",
            position="Senior Engineer",
            company_name="Acme Corp",
            tts_service=mock_tts,
        )
        assert isinstance(response, InterviewResponse)
        assert "Jane Doe" in response.text
        assert response.audio is not None

    @pytest.mark.asyncio
    async def test_generate_closing_response(self, mock_tts):
        rg = ResponseGenerator()
        response = await rg.generate_closing(
            user_name="Jane Doe",
            company_name="Acme Corp",
            tts_service=mock_tts,
        )
        assert isinstance(response, InterviewResponse)
        assert "thank" in response.text.lower()
        assert response.audio is not None

    @pytest.mark.asyncio
    async def test_generate_follow_up_response(self, mock_tts):
        rg = ResponseGenerator()
        answer = InterviewAnswer(
            text="Main answer",
            confidence=0.8,
            follow_ups=["Follow up question"],
            agent_type="hr",
        )
        response = await rg.generate_with_follow_up(answer, tts_service=mock_tts)
        assert response.text == "Main answer"
        assert response.follow_up_text == "Follow up question"

    @pytest.mark.asyncio
    async def test_generate_handles_tts_error(self):
        rg = ResponseGenerator()
        tts = AsyncMock()
        tts.synthesize_async = AsyncMock(side_effect=RuntimeError("TTS failed"))
        answer = InterviewAnswer(text="Answer", confidence=0.5, follow_ups=[], agent_type="hr")
        response = await rg.generate(answer, tts_service=tts)
        assert response.text == "Answer"
        assert response.audio is None  # Graceful fallback

    def test_determine_expression_confident(self):
        rg = ResponseGenerator()
        assert rg._determine_expression(0.9, "hr") == "confident"
        assert rg._determine_expression(0.8, "technical") == "focused"

    def test_determine_expression_neutral(self):
        rg = ResponseGenerator()
        assert rg._determine_expression(0.5, "hr") == "neutral"
        assert rg._determine_expression(0.5, "technical") == "neutral"


# ═══════════════════════════════════════════════════
# AutonomousInterviewEngine tests
# ═══════════════════════════════════════════════════

class TestAutonomousInterviewEngine:
    def test_init(self, user_profile, company_context):
        engine = AutonomousInterviewEngine(user_profile, company_context)
        assert engine.user_profile == user_profile
        assert engine.company_context == company_context
        assert engine.is_active is False
        assert isinstance(engine.trigger_detector, InterviewTriggerDetector)
        assert isinstance(engine.adaptive, AdaptiveDifficulty)
        assert isinstance(engine.response_generator, ResponseGenerator)

    def test_init_injectable_dependencies(
        self, user_profile, company_context, mock_stt, mock_tts, mock_face, mock_orchestrator
    ):
        engine = AutonomousInterviewEngine(
            user_profile,
            company_context,
            stt_service=mock_stt,
            tts_service=mock_tts,
            face_service=mock_face,
            orchestrator=mock_orchestrator,
        )
        assert engine.stt_service is mock_stt
        assert engine.tts_service is mock_tts
        assert engine.face_service is mock_face
        assert engine.orchestrator is mock_orchestrator

    @pytest.mark.asyncio
    async def test_process_audio_waiting_mode(
        self, user_profile, company_context, mock_stt, mock_tts
    ):
        engine = AutonomousInterviewEngine(
            user_profile, company_context, stt_service=mock_stt, tts_service=mock_tts
        )
        mock_stt.transcribe_async = AsyncMock(return_value="Hey, how's the weather?")
        result = await engine.process_audio(b"audio-bytes")
        assert result["action"] == "waiting"
        assert result["phase"] == "idle"

    @pytest.mark.asyncio
    async def test_process_audio_activates_interview(
        self, user_profile, company_context, mock_stt, mock_tts
    ):
        engine = AutonomousInterviewEngine(
            user_profile, company_context, stt_service=mock_stt, tts_service=mock_tts
        )
        engine.trigger_detector.phase = InterviewPhase.ACTIVE
        mock_stt.transcribe_async = AsyncMock(return_value="Tell me about yourself")
        result = await engine.process_audio(b"audio-bytes")
        assert result["action"] == "introduce"
        assert engine.is_active is True

    @pytest.mark.asyncio
    async def test_process_audio_active_generates_response(
        self, user_profile, company_context, mock_stt, mock_tts, mock_orchestrator
    ):
        engine = AutonomousInterviewEngine(
            user_profile,
            company_context,
            stt_service=mock_stt,
            tts_service=mock_tts,
            orchestrator=mock_orchestrator,
        )
        engine.is_active = True
        mock_stt.transcribe_async = AsyncMock(return_value="What are your strengths?")
        result = await engine.process_audio(b"audio-bytes")
        assert result["action"] == "respond"
        assert result["transcript"] == "What are your strengths?"
        assert result["answer"] == "I am a senior engineer with 10 years of experience."
        assert result["confidence"] == 0.85

    @pytest.mark.asyncio
    async def test_process_audio_active_generates_audio(
        self, user_profile, company_context, mock_stt, mock_tts, mock_orchestrator
    ):
        engine = AutonomousInterviewEngine(
            user_profile,
            company_context,
            stt_service=mock_stt,
            tts_service=mock_tts,
            orchestrator=mock_orchestrator,
        )
        engine.is_active = True
        mock_stt.transcribe_async = AsyncMock(return_value="Tell me about a time you failed")
        result = await engine.process_audio(b"audio-bytes")
        assert result["audio"] == b"fake-audio-bytes"

    @pytest.mark.asyncio
    async def test_process_audio_active_includes_avatar(
        self, user_profile, company_context, mock_stt, mock_tts, mock_orchestrator
    ):
        engine = AutonomousInterviewEngine(
            user_profile,
            company_context,
            stt_service=mock_stt,
            tts_service=mock_tts,
            orchestrator=mock_orchestrator,
        )
        engine.is_active = True
        mock_stt.transcribe_async = AsyncMock(return_value="How do you lead teams?")
        result = await engine.process_audio(b"audio-bytes")
        assert result["avatar"] is not None
        assert "expression" in result["avatar"]

    @pytest.mark.asyncio
    async def test_start_interview(self, user_profile, company_context):
        engine = AutonomousInterviewEngine(user_profile, company_context)
        assert engine.is_active is False
        await engine.start_interview()
        assert engine.is_active is True

    @pytest.mark.asyncio
    async def test_stop_interview(self, user_profile, company_context):
        engine = AutonomousInterviewEngine(user_profile, company_context)
        engine.is_active = True
        await engine.stop_interview()
        assert engine.is_active is False

    def test_get_session_stats(self, user_profile, company_context):
        engine = AutonomousInterviewEngine(user_profile, company_context)
        stats = engine.get_session_stats()
        assert stats["total_questions"] == 0
        assert stats["is_active"] is False
        assert stats["current_difficulty"] == DifficultyLevel.MEDIUM.value

    @pytest.mark.asyncio
    async def test_generate_introduction(self, user_profile, company_context, mock_tts):
        engine = AutonomousInterviewEngine(
            user_profile, company_context, tts_service=mock_tts
        )
        result = await engine._generate_introduction()
        assert result["action"] == "introduce"
        assert "Jane Doe" in result["answer"]
        assert result["audio"] == b"fake-audio-bytes"

    @pytest.mark.asyncio
    async def test_generate_closing(
        self, user_profile, company_context, mock_tts
    ):
        engine = AutonomousInterviewEngine(
            user_profile, company_context, tts_service=mock_tts
        )
        result = await engine._generate_closing()
        assert result["action"] == "closing"
        assert "thank" in result["answer"].lower()

    @pytest.mark.asyncio
    async def test_generate_follow_up_question(
        self, user_profile, company_context, mock_orchestrator
    ):
        engine = AutonomousInterviewEngine(
            user_profile, company_context, orchestrator=mock_orchestrator
        )
        result = await engine.generate_follow_up("What are your strengths?")
        assert isinstance(result, dict)
        assert "question" in result

    def test_categorize_question_hr(self, user_profile, company_context):
        engine = AutonomousInterviewEngine(user_profile, company_context)
        q = engine._categorize_question("Tell me about yourself")
        assert q.category == "hr"

    def test_categorize_question_technical(self, user_profile, company_context):
        engine = AutonomousInterviewEngine(user_profile, company_context)
        q = engine._categorize_question("Explain distributed systems")
        assert q.category == "technical"

    def test_categorize_question_coding(self, user_profile, company_context):
        engine = AutonomousInterviewEngine(user_profile, company_context)
        q = engine._categorize_question("Write a function to sort")
        assert q.category == "coding"

    def test_categorize_question_managerial(self, user_profile, company_context):
        engine = AutonomousInterviewEngine(user_profile, company_context)
        q = engine._categorize_question("How do you manage stakeholders?")
        assert q.category == "managerial"

    def test_categorize_question_generic(self, user_profile, company_context):
        engine = AutonomousInterviewEngine(user_profile, company_context)
        q = engine._categorize_question("What is the meaning of life?")
        assert q.category == "general"

    def test_is_running_false_initially(self, user_profile, company_context):
        engine = AutonomousInterviewEngine(user_profile, company_context)
        assert engine.is_running() is False

    def test_is_running_true_when_active(self, user_profile, company_context):
        engine = AutonomousInterviewEngine(user_profile, company_context)
        engine.is_active = True
        assert engine.is_running() is True

    @pytest.mark.asyncio
    async def test_process_audio_updates_stats(
        self, user_profile, company_context, mock_stt, mock_tts, mock_orchestrator
    ):
        engine = AutonomousInterviewEngine(
            user_profile,
            company_context,
            stt_service=mock_stt,
            tts_service=mock_tts,
            orchestrator=mock_orchestrator,
        )
        engine.is_active = True
        mock_stt.transcribe_async = AsyncMock(return_value="What is system design?")
        await engine.process_audio(b"audio-bytes")
        stats = engine.get_session_stats()
        assert stats["total_questions"] == 1

    @pytest.mark.asyncio
    async def test_process_audio_records_adaptive_metrics(
        self, user_profile, company_context, mock_stt, mock_tts, mock_orchestrator
    ):
        engine = AutonomousInterviewEngine(
            user_profile,
            company_context,
            stt_service=mock_stt,
            tts_service=mock_tts,
            orchestrator=mock_orchestrator,
        )
        engine.is_active = True
        mock_stt.transcribe_async = AsyncMock(return_value="Tell me about leadership")
        await engine.process_audio(b"audio-bytes")
        assert engine.adaptive.metrics.questions_answered == 1

    @pytest.mark.asyncio
    async def test_reset_session(self, user_profile, company_context):
        engine = AutonomousInterviewEngine(user_profile, company_context)
        engine.is_active = True
        engine.session_stats["total_questions"] = 5
        await engine.reset_session()
        assert engine.is_active is False
        assert engine.session_stats["total_questions"] == 0

    @pytest.mark.asyncio
    async def test_multiple_questions_tracking(
        self, user_profile, company_context, mock_stt, mock_tts, mock_orchestrator
    ):
        engine = AutonomousInterviewEngine(
            user_profile,
            company_context,
            stt_service=mock_stt,
            tts_service=mock_tts,
            orchestrator=mock_orchestrator,
        )
        engine.is_active = True
        mock_stt.transcribe_async = AsyncMock(return_value="Tell me about yourself")
        await engine.process_audio(b"audio1")
        mock_stt.transcribe_async = AsyncMock(return_value="What are your strengths?")
        await engine.process_audio(b"audio2")
        mock_stt.transcribe_async = AsyncMock(return_value="How do you handle pressure?")
        await engine.process_audio(b"audio3")
        stats = engine.get_session_stats()
        assert stats["total_questions"] == 3
