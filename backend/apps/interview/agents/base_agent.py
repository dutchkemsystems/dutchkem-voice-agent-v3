from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class InterviewQuestion:
    text: str
    category: str
    difficulty: str  # easy, medium, hard
    context: Optional[str] = None


@dataclass
class InterviewAnswer:
    text: str
    confidence: float
    follow_ups: List[str]
    agent_type: str


class BaseInterviewAgent(ABC):
    def __init__(self, user_profile: Dict, company_context: Dict, llm_service):
        self.user_profile = user_profile
        self.company_context = company_context
        self.llm_service = llm_service
        self.conversation_history: List[Dict] = []

    @abstractmethod
    def can_handle(self, question: InterviewQuestion) -> bool:
        pass

    @abstractmethod
    async def generate_answer(self, question: InterviewQuestion) -> InterviewAnswer:
        pass

    def update_history(self, question: str, answer: str):
        self.conversation_history.append({
            "question": question,
            "answer": answer,
        })
