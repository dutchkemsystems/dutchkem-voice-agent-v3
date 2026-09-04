import pytest
from unittest.mock import AsyncMock
from apps.interview.agents.client_meeting_agent import ClientMeetingAgent
from apps.interview.agents.mentoring_agent import MentoringAgent
from apps.interview.agents.performance_review_agent import PerformanceReviewAgent
from apps.interview.agents.board_presentation_agent import BoardPresentationAgent
from apps.interview.agents.sales_agent import SalesAgent
from apps.interview.agents.training_agent import TrainingAgent
from apps.interview.agents.internal_comms_agent import InternalCommsAgent
from apps.interview.agents.customer_support_agent import CustomerSupportAgent
from apps.interview.agents.base_agent import InterviewQuestion


@pytest.fixture
def mock_llm():
    return AsyncMock()


class TestClientMeetingAgent:
    def test_can_handle_client_keywords(self, mock_llm):
        agent = ClientMeetingAgent(user_profile={}, company_context={}, llm_service=mock_llm)
        q = InterviewQuestion(text="What's the project update for the client?", category="general", difficulty="medium")
        assert agent.can_handle(q) is True

    def test_cannot_handle_interview_keywords(self, mock_llm):
        agent = ClientMeetingAgent(user_profile={}, company_context={}, llm_service=mock_llm)
        q = InterviewQuestion(text="Tell me about your strengths", category="general", difficulty="medium")
        assert agent.can_handle(q) is False

    def test_agent_type(self, mock_llm):
        agent = ClientMeetingAgent(user_profile={}, company_context={}, llm_service=mock_llm)
        assert agent.AGENT_TYPE == "client_meeting"


class TestMentoringAgent:
    def test_can_handle_mentoring_keywords(self, mock_llm):
        agent = MentoringAgent(user_profile={}, company_context={}, llm_service=mock_llm)
        q = InterviewQuestion(text="Can you explain how async/await works?", category="general", difficulty="medium")
        assert agent.can_handle(q) is True

    def test_agent_type(self, mock_llm):
        agent = MentoringAgent(user_profile={}, company_context={}, llm_service=mock_llm)
        assert agent.AGENT_TYPE == "mentoring"


class TestPerformanceReviewAgent:
    def test_can_handle_review_keywords(self, mock_llm):
        agent = PerformanceReviewAgent(user_profile={}, company_context={}, llm_service=mock_llm)
        q = InterviewQuestion(text="Let's discuss my achievements this quarter", category="general", difficulty="medium")
        assert agent.can_handle(q) is True

    def test_agent_type(self, mock_llm):
        agent = PerformanceReviewAgent(user_profile={}, company_context={}, llm_service=mock_llm)
        assert agent.AGENT_TYPE == "performance_review"


class TestBoardPresentationAgent:
    def test_can_handle_board_keywords(self, mock_llm):
        agent = BoardPresentationAgent(user_profile={}, company_context={}, llm_service=mock_llm)
        q = InterviewQuestion(text="What's the strategic outlook for next quarter?", category="general", difficulty="medium")
        assert agent.can_handle(q) is True

    def test_agent_type(self, mock_llm):
        agent = BoardPresentationAgent(user_profile={}, company_context={}, llm_service=mock_llm)
        assert agent.AGENT_TYPE == "board_presentation"


class TestSalesAgent:
    def test_can_handle_sales_keywords(self, mock_llm):
        agent = SalesAgent(user_profile={}, company_context={}, llm_service=mock_llm)
        q = InterviewQuestion(text="What's the pricing for your enterprise plan?", category="general", difficulty="medium")
        assert agent.can_handle(q) is True

    def test_agent_type(self, mock_llm):
        agent = SalesAgent(user_profile={}, company_context={}, llm_service=mock_llm)
        assert agent.AGENT_TYPE == "sales"


class TestTrainingAgent:
    def test_can_handle_training_keywords(self, mock_llm):
        agent = TrainingAgent(user_profile={}, company_context={}, llm_service=mock_llm)
        q = InterviewQuestion(text="Can you walk me through the onboarding process?", category="general", difficulty="medium")
        assert agent.can_handle(q) is True

    def test_agent_type(self, mock_llm):
        agent = TrainingAgent(user_profile={}, company_context={}, llm_service=mock_llm)
        assert agent.AGENT_TYPE == "training"


class TestInternalCommsAgent:
    def test_can_handle_comms_keywords(self, mock_llm):
        agent = InternalCommsAgent(user_profile={}, company_context={}, llm_service=mock_llm)
        q = InterviewQuestion(text="Let's do a standup update", category="general", difficulty="medium")
        assert agent.can_handle(q) is True

    def test_agent_type(self, mock_llm):
        agent = InternalCommsAgent(user_profile={}, company_context={}, llm_service=mock_llm)
        assert agent.AGENT_TYPE == "internal_comms"


class TestCustomerSupportAgent:
    def test_can_handle_support_keywords(self, mock_llm):
        agent = CustomerSupportAgent(user_profile={}, company_context={}, llm_service=mock_llm)
        q = InterviewQuestion(text="I have a bug in the login flow", category="general", difficulty="medium")
        assert agent.can_handle(q) is True

    def test_agent_type(self, mock_llm):
        agent = CustomerSupportAgent(user_profile={}, company_context={}, llm_service=mock_llm)
        assert agent.AGENT_TYPE == "customer_support"
