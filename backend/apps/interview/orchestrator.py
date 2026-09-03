from typing import Dict, List, Optional
from .agents import (
    HRAgent,
    ManagerAgent,
    TechnicalAgent,
    CodingAgent,
    InterviewQuestion,
    InterviewAnswer,
)


class InterviewOrchestrator:
    def __init__(self, user_profile: Dict, company_context: Dict, llm_service):
        self.user_profile = user_profile
        self.company_context = company_context
        self.llm_service = llm_service
        self.agents = [
            HRAgent(user_profile, company_context, llm_service),
            ManagerAgent(user_profile, company_context, llm_service),
            TechnicalAgent(user_profile, company_context, llm_service),
            CodingAgent(user_profile, company_context, llm_service),
        ]

    def route(self, question: InterviewQuestion) -> Optional:
        for agent in self.agents:
            if agent.can_handle(question):
                return agent
        return None

    async def process_question(self, question: InterviewQuestion) -> Optional[InterviewAnswer]:
        agent = self.route(question)
        if agent is None:
            return None
        answer = await agent.generate_answer(question)
        agent.update_history(question.text, answer.text)
        return answer

    async def process_session(self, questions: List[InterviewQuestion]) -> List[InterviewAnswer]:
        answers = []
        for q in questions:
            answer = await self.process_question(q)
            if answer is not None:
                answers.append(answer)
        return answers
