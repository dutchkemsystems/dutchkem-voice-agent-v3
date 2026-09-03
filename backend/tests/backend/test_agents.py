import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from apps.interview.agents.base_agent import BaseInterviewAgent, InterviewQuestion, InterviewAnswer
from apps.interview.agents.hr_agent import HRAgent
from apps.interview.agents.manager_agent import ManagerAgent
from apps.interview.agents.technical_agent import TechnicalAgent
from apps.interview.agents.coding_agent import CodingAgent
from apps.interview.orchestrator import InterviewOrchestrator


# ─── Shared fixtures ───

@pytest.fixture
def mock_llm():
    llm = AsyncMock()
    llm.generate_interview_answer = AsyncMock(return_value="Sample answer from LLM")
    return llm


@pytest.fixture
def user_profile():
    return {
        "name": "Jane Doe",
        "position": "Senior Engineer",
        "company": "Acme Corp",
        "resume_summary": "10 years Python, 5 years system design",
        "achievements": "Led team of 8, shipped 3 products",
        "technical_skills": "Python, Go, Kubernetes, AWS",
        "management_style": "Servant leader",
        "languages": "Python, JavaScript, Go",
    }


@pytest.fixture
def company_context():
    return {
        "name": "TechStart Inc",
        "industry": "SaaS",
        "values": ["innovation", "collaboration"],
    }


# ═══════════════════════════════════════════════════
# Dataclass tests
# ═══════════════════════════════════════════════════

class TestInterviewQuestion:
    def test_creation(self):
        q = InterviewQuestion(text="Why this company?", category="hr", difficulty="easy")
        assert q.text == "Why this company?"
        assert q.category == "hr"
        assert q.difficulty == "easy"
        assert q.context is None

    def test_creation_with_context(self):
        q = InterviewQuestion(
            text="Tell me about a time",
            category="behavioral",
            difficulty="medium",
            context="Previous role context",
        )
        assert q.context == "Previous role context"


class TestInterviewAnswer:
    def test_creation(self):
        a = InterviewAnswer(
            text="Answer text",
            confidence=0.9,
            follow_ups=["Follow up?"],
            agent_type="hr",
        )
        assert a.text == "Answer text"
        assert a.confidence == 0.9
        assert a.follow_ups == ["Follow up?"]
        assert a.agent_type == "hr"


# ═══════════════════════════════════════════════════
# Base agent tests
# ═══════════════════════════════════════════════════

class TestBaseInterviewAgent:
    def test_cannot_instantiate_directly(self):
        with pytest.raises(TypeError):
            BaseInterviewAgent({}, {}, MagicMock())

    def test_update_history(self, mock_llm, user_profile, company_context):
        agent = HRAgent(user_profile, company_context, mock_llm)
        agent.update_history("Question 1", "Answer 1")
        assert len(agent.conversation_history) == 1
        assert agent.conversation_history[0]["question"] == "Question 1"
        assert agent.conversation_history[0]["answer"] == "Answer 1"

    def test_update_history_multiple(self, mock_llm, user_profile, company_context):
        agent = HRAgent(user_profile, company_context, mock_llm)
        agent.update_history("Q1", "A1")
        agent.update_history("Q2", "A2")
        agent.update_history("Q3", "A3")
        assert len(agent.conversation_history) == 3


# ═══════════════════════════════════════════════════
# HR Agent tests
# ═══════════════════════════════════════════════════

class TestHRAgent:
    def test_can_handle_tell_me_about(self, mock_llm, user_profile, company_context):
        agent = HRAgent(user_profile, company_context, mock_llm)
        q = InterviewQuestion(text="Tell me about yourself", category="hr", difficulty="easy")
        assert agent.can_handle(q) is True

    def test_can_handle_why_want(self, mock_llm, user_profile, company_context):
        agent = HRAgent(user_profile, company_context, mock_llm)
        q = InterviewQuestion(text="Why do you want this role?", category="hr", difficulty="easy")
        assert agent.can_handle(q) is True

    def test_can_handle_strengths(self, mock_llm, user_profile, company_context):
        agent = HRAgent(user_profile, company_context, mock_llm)
        q = InterviewQuestion(text="What are your strengths?", category="hr", difficulty="easy")
        assert agent.can_handle(q) is True

    def test_can_handle_weaknesses(self, mock_llm, user_profile, company_context):
        agent = HRAgent(user_profile, company_context, mock_llm)
        q = InterviewQuestion(text="Tell me about your weaknesses", category="hr", difficulty="medium")
        assert agent.can_handle(q) is True

    def test_can_handle_team(self, mock_llm, user_profile, company_context):
        agent = HRAgent(user_profile, company_context, mock_llm)
        q = InterviewQuestion(text="How do you work in a team?", category="hr", difficulty="easy")
        assert agent.can_handle(q) is True

    def test_can_handle_leadership(self, mock_llm, user_profile, company_context):
        agent = HRAgent(user_profile, company_context, mock_llm)
        q = InterviewQuestion(text="Describe your leadership style", category="hr", difficulty="medium")
        assert agent.can_handle(q) is True

    def test_can_handle_conflict(self, mock_llm, user_profile, company_context):
        agent = HRAgent(user_profile, company_context, mock_llm)
        q = InterviewQuestion(text="How do you handle conflict?", category="hr", difficulty="medium")
        assert agent.can_handle(q) is True

    def test_can_handle_pressure(self, mock_llm, user_profile, company_context):
        agent = HRAgent(user_profile, company_context, mock_llm)
        q = InterviewQuestion(text="Working under pressure?", category="hr", difficulty="medium")
        assert agent.can_handle(q) is True

    def test_can_handle_deadline(self, mock_llm, user_profile, company_context):
        agent = HRAgent(user_profile, company_context, mock_llm)
        q = InterviewQuestion(text="How do you meet deadlines?", category="hr", difficulty="easy")
        assert agent.can_handle(q) is True

    def test_cannot_handle_technical(self, mock_llm, user_profile, company_context):
        agent = HRAgent(user_profile, company_context, mock_llm)
        q = InterviewQuestion(text="Explain binary search", category="technical", difficulty="medium")
        assert agent.can_handle(q) is False

    def test_cannot_handle_coding(self, mock_llm, user_profile, company_context):
        agent = HRAgent(user_profile, company_context, mock_llm)
        q = InterviewQuestion(text="Write a function to sort an array", category="coding", difficulty="medium")
        assert agent.can_handle(q) is False

    @pytest.mark.asyncio
    async def test_generate_answer(self, mock_llm, user_profile, company_context):
        agent = HRAgent(user_profile, company_context, mock_llm)
        q = InterviewQuestion(text="Tell me about yourself", category="hr", difficulty="easy")
        answer = await agent.generate_answer(q)
        assert isinstance(answer, InterviewAnswer)
        assert answer.text == "Sample answer from LLM"
        assert answer.agent_type == "hr"
        assert answer.confidence > 0
        assert isinstance(answer.follow_ups, list)
        mock_llm.generate_interview_answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_answer_passes_conversation_history(self, mock_llm, user_profile, company_context):
        agent = HRAgent(user_profile, company_context, mock_llm)
        agent.update_history("Q1", "A1")
        q = InterviewQuestion(text="Tell me about yourself", category="hr", difficulty="easy")
        await agent.generate_answer(q)
        call_kwargs = mock_llm.generate_interview_answer.call_args
        assert call_kwargs[1]["conversation_history"] == [{"question": "Q1", "answer": "A1"}]

    @pytest.mark.asyncio
    async def test_generate_answer_passes_question_type(self, mock_llm, user_profile, company_context):
        agent = HRAgent(user_profile, company_context, mock_llm)
        q = InterviewQuestion(text="Tell me about yourself", category="hr", difficulty="easy")
        await agent.generate_answer(q)
        call_kwargs = mock_llm.generate_interview_answer.call_args
        assert call_kwargs[1]["question_type"] == "hr"


# ═══════════════════════════════════════════════════
# Manager Agent tests
# ═══════════════════════════════════════════════════

class TestManagerAgent:
    def test_can_handle_scenario(self, mock_llm, user_profile, company_context):
        agent = ManagerAgent(user_profile, company_context, mock_llm)
        q = InterviewQuestion(text="Describe a scenario where your team failed", category="managerial", difficulty="hard")
        assert agent.can_handle(q) is True

    def test_can_handle_prioritize(self, mock_llm, user_profile, company_context):
        agent = ManagerAgent(user_profile, company_context, mock_llm)
        q = InterviewQuestion(text="How do you prioritize tasks?", category="managerial", difficulty="medium")
        assert agent.can_handle(q) is True

    def test_can_handle_cross_functional(self, mock_llm, user_profile, company_context):
        agent = ManagerAgent(user_profile, company_context, mock_llm)
        q = InterviewQuestion(text="Working with cross-functional teams", category="managerial", difficulty="medium")
        assert agent.can_handle(q) is True

    def test_can_handle_budget(self, mock_llm, user_profile, company_context):
        agent = ManagerAgent(user_profile, company_context, mock_llm)
        q = InterviewQuestion(text="Managing a budget", category="managerial", difficulty="medium")
        assert agent.can_handle(q) is True

    def test_can_handle_stakeholder(self, mock_llm, user_profile, company_context):
        agent = ManagerAgent(user_profile, company_context, mock_llm)
        q = InterviewQuestion(text="Stakeholder management strategy", category="managerial", difficulty="medium")
        assert agent.can_handle(q) is True

    def test_cannot_handle_hr(self, mock_llm, user_profile, company_context):
        agent = ManagerAgent(user_profile, company_context, mock_llm)
        q = InterviewQuestion(text="Tell me about yourself", category="hr", difficulty="easy")
        assert agent.can_handle(q) is False

    def test_cannot_handle_coding(self, mock_llm, user_profile, company_context):
        agent = ManagerAgent(user_profile, company_context, mock_llm)
        q = InterviewQuestion(text="Write a function to merge two sorted lists", category="coding", difficulty="medium")
        assert agent.can_handle(q) is False

    @pytest.mark.asyncio
    async def test_generate_answer(self, mock_llm, user_profile, company_context):
        agent = ManagerAgent(user_profile, company_context, mock_llm)
        q = InterviewQuestion(text="Describe your management approach", category="managerial", difficulty="medium")
        answer = await agent.generate_answer(q)
        assert isinstance(answer, InterviewAnswer)
        assert answer.agent_type == "managerial"
        mock_llm.generate_interview_answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_answer_passes_correct_type(self, mock_llm, user_profile, company_context):
        agent = ManagerAgent(user_profile, company_context, mock_llm)
        q = InterviewQuestion(text="How do you handle conflict resolution?", category="managerial", difficulty="hard")
        await agent.generate_answer(q)
        call_kwargs = mock_llm.generate_interview_answer.call_args
        assert call_kwargs[1]["question_type"] == "managerial"


# ═══════════════════════════════════════════════════
# Technical Agent tests
# ═══════════════════════════════════════════════════

class TestTechnicalAgent:
    def test_can_handle_system_design(self, mock_llm, user_profile, company_context):
        agent = TechnicalAgent(user_profile, company_context, mock_llm)
        q = InterviewQuestion(text="Design a URL shortener", category="technical", difficulty="hard")
        assert agent.can_handle(q) is True

    def test_can_handle_architecture(self, mock_llm, user_profile, company_context):
        agent = TechnicalAgent(user_profile, company_context, mock_llm)
        q = InterviewQuestion(text="Describe microservices architecture", category="technical", difficulty="medium")
        assert agent.can_handle(q) is True

    def test_can_handle_explain(self, mock_llm, user_profile, company_context):
        agent = TechnicalAgent(user_profile, company_context, mock_llm)
        q = InterviewQuestion(text="Explain how TCP/IP works", category="technical", difficulty="medium")
        assert agent.can_handle(q) is True

    def test_can_handle_database(self, mock_llm, user_profile, company_context):
        agent = TechnicalAgent(user_profile, company_context, mock_llm)
        q = InterviewQuestion(text="What is database normalization?", category="technical", difficulty="easy")
        assert agent.can_handle(q) is True

    def test_can_handle_api(self, mock_llm, user_profile, company_context):
        agent = TechnicalAgent(user_profile, company_context, mock_llm)
        q = InterviewQuestion(text="Design a REST API for user management", category="technical", difficulty="medium")
        assert agent.can_handle(q) is True

    def test_cannot_handle_hr(self, mock_llm, user_profile, company_context):
        agent = TechnicalAgent(user_profile, company_context, mock_llm)
        q = InterviewQuestion(text="Tell me about yourself", category="hr", difficulty="easy")
        assert agent.can_handle(q) is False

    def test_cannot_handle_managerial(self, mock_llm, user_profile, company_context):
        agent = TechnicalAgent(user_profile, company_context, mock_llm)
        q = InterviewQuestion(text="How do you prioritize sprint work?", category="managerial", difficulty="medium")
        assert agent.can_handle(q) is False

    @pytest.mark.asyncio
    async def test_generate_answer(self, mock_llm, user_profile, company_context):
        agent = TechnicalAgent(user_profile, company_context, mock_llm)
        q = InterviewQuestion(text="Explain distributed consensus", category="technical", difficulty="hard")
        answer = await agent.generate_answer(q)
        assert isinstance(answer, InterviewAnswer)
        assert answer.agent_type == "technical"
        mock_llm.generate_interview_answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_answer_passes_correct_type(self, mock_llm, user_profile, company_context):
        agent = TechnicalAgent(user_profile, company_context, mock_llm)
        q = InterviewQuestion(text="How does garbage collection work?", category="technical", difficulty="medium")
        await agent.generate_answer(q)
        call_kwargs = mock_llm.generate_interview_answer.call_args
        assert call_kwargs[1]["question_type"] == "technical"


# ═══════════════════════════════════════════════════
# Coding Agent tests
# ═══════════════════════════════════════════════════

class TestCodingAgent:
    def test_can_handle_write_function(self, mock_llm, user_profile, company_context):
        agent = CodingAgent(user_profile, company_context, mock_llm)
        q = InterviewQuestion(text="Write a function to reverse a linked list", category="coding", difficulty="medium")
        assert agent.can_handle(q) is True

    def test_can_handle_implement(self, mock_llm, user_profile, company_context):
        agent = CodingAgent(user_profile, company_context, mock_llm)
        q = InterviewQuestion(text="Implement a LRU cache", category="coding", difficulty="hard")
        assert agent.can_handle(q) is True

    def test_can_handle_algo(self, mock_llm, user_profile, company_context):
        agent = CodingAgent(user_profile, company_context, mock_llm)
        q = InterviewQuestion(text="Solve the two sum problem", category="coding", difficulty="easy")
        assert agent.can_handle(q) is True

    def test_can_handle_code_review(self, mock_llm, user_profile, company_context):
        agent = CodingAgent(user_profile, company_context, mock_llm)
        q = InterviewQuestion(text="Review this code for bugs", category="coding", difficulty="medium")
        assert agent.can_handle(q) is True

    def test_cannot_handle_hr(self, mock_llm, user_profile, company_context):
        agent = CodingAgent(user_profile, company_context, mock_llm)
        q = InterviewQuestion(text="Tell me about yourself", category="hr", difficulty="easy")
        assert agent.can_handle(q) is False

    def test_cannot_handle_technical_concept(self, mock_llm, user_profile, company_context):
        agent = CodingAgent(user_profile, company_context, mock_llm)
        q = InterviewQuestion(text="Explain CAP theorem", category="technical", difficulty="hard")
        assert agent.can_handle(q) is False

    @pytest.mark.asyncio
    async def test_generate_answer(self, mock_llm, user_profile, company_context):
        agent = CodingAgent(user_profile, company_context, mock_llm)
        q = InterviewQuestion(text="Write a function to merge two sorted arrays", category="coding", difficulty="medium")
        answer = await agent.generate_answer(q)
        assert isinstance(answer, InterviewAnswer)
        assert answer.agent_type == "coding"
        mock_llm.generate_interview_answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_answer_passes_correct_type(self, mock_llm, user_profile, company_context):
        agent = CodingAgent(user_profile, company_context, mock_llm)
        q = InterviewQuestion(text="Implement binary search", category="coding", difficulty="easy")
        await agent.generate_answer(q)
        call_kwargs = mock_llm.generate_interview_answer.call_args
        assert call_kwargs[1]["question_type"] == "coding"


# ═══════════════════════════════════════════════════
# Orchestrator tests
# ═══════════════════════════════════════════════════

class TestInterviewOrchestrator:
    def test_init(self, mock_llm, user_profile, company_context):
        orch = InterviewOrchestrator(user_profile, company_context, mock_llm)
        assert orch.user_profile == user_profile
        assert orch.company_context == company_context
        assert orch.llm_service == mock_llm
        assert len(orch.agents) == 4

    def test_agents_list(self, mock_llm, user_profile, company_context):
        orch = InterviewOrchestrator(user_profile, company_context, mock_llm)
        agent_types = [type(a).__name__ for a in orch.agents]
        assert "HRAgent" in agent_types
        assert "ManagerAgent" in agent_types
        assert "TechnicalAgent" in agent_types
        assert "CodingAgent" in agent_types

    def test_route_hr_question(self, mock_llm, user_profile, company_context):
        orch = InterviewOrchestrator(user_profile, company_context, mock_llm)
        q = InterviewQuestion(text="Tell me about yourself", category="hr", difficulty="easy")
        agent = orch.route(q)
        assert isinstance(agent, HRAgent)

    def test_route_managerial_question(self, mock_llm, user_profile, company_context):
        orch = InterviewOrchestrator(user_profile, company_context, mock_llm)
        q = InterviewQuestion(text="How do you handle stakeholder management?", category="managerial", difficulty="medium")
        agent = orch.route(q)
        assert isinstance(agent, ManagerAgent)

    def test_route_technical_question(self, mock_llm, user_profile, company_context):
        orch = InterviewOrchestrator(user_profile, company_context, mock_llm)
        q = InterviewQuestion(text="Explain distributed systems", category="technical", difficulty="hard")
        agent = orch.route(q)
        assert isinstance(agent, TechnicalAgent)

    def test_route_coding_question(self, mock_llm, user_profile, company_context):
        orch = InterviewOrchestrator(user_profile, company_context, mock_llm)
        q = InterviewQuestion(text="Write a function to find duplicates", category="coding", difficulty="medium")
        agent = orch.route(q)
        assert isinstance(agent, CodingAgent)

    def test_route_returns_none_for_unhandled(self, mock_llm, user_profile, company_context):
        orch = InterviewOrchestrator(user_profile, company_context, mock_llm)
        q = InterviewQuestion(text="What is the meaning of life?", category="philosophy", difficulty="hard")
        agent = orch.route(q)
        assert agent is None

    @pytest.mark.asyncio
    async def test_process_question(self, mock_llm, user_profile, company_context):
        orch = InterviewOrchestrator(user_profile, company_context, mock_llm)
        q = InterviewQuestion(text="Tell me about yourself", category="hr", difficulty="easy")
        answer = await orch.process_question(q)
        assert isinstance(answer, InterviewAnswer)
        assert answer.agent_type == "hr"
        assert answer.text == "Sample answer from LLM"

    @pytest.mark.asyncio
    async def test_process_question_returns_none_for_unhandled(self, mock_llm, user_profile, company_context):
        orch = InterviewOrchestrator(user_profile, company_context, mock_llm)
        q = InterviewQuestion(text="What is the meaning of life?", category="philosophy", difficulty="hard")
        answer = await orch.process_question(q)
        assert answer is None

    @pytest.mark.asyncio
    async def test_process_question_updates_history(self, mock_llm, user_profile, company_context):
        orch = InterviewOrchestrator(user_profile, company_context, mock_llm)
        q = InterviewQuestion(text="Tell me about yourself", category="hr", difficulty="easy")
        await orch.process_question(q)
        agent = orch.route(q)
        assert len(agent.conversation_history) == 1

    @pytest.mark.asyncio
    async def test_process_multiple_questions(self, mock_llm, user_profile, company_context):
        orch = InterviewOrchestrator(user_profile, company_context, mock_llm)
        questions = [
            InterviewQuestion(text="Tell me about yourself", category="hr", difficulty="easy"),
            InterviewQuestion(text="Design a URL shortener", category="technical", difficulty="hard"),
            InterviewQuestion(text="Write a function to sort", category="coding", difficulty="medium"),
        ]
        answers = await orch.process_session(questions)
        assert len(answers) == 3
        assert answers[0].agent_type == "hr"
        assert answers[1].agent_type == "technical"
        assert answers[2].agent_type == "coding"
