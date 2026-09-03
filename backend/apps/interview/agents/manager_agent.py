from .base_agent import BaseInterviewAgent, InterviewQuestion, InterviewAnswer


class ManagerAgent(BaseInterviewAgent):
    MANAGER_KEYWORDS = [
        "scenario", "prioritize", "cross-functional", "budget", "stakeholder",
    ]

    def can_handle(self, question: InterviewQuestion) -> bool:
        text = question.text.lower()
        return any(kw in text for kw in self.MANAGER_KEYWORDS)

    async def generate_answer(self, question: InterviewQuestion) -> InterviewAnswer:
        answer_text = await self.llm_service.generate_interview_answer(
            question=question.text,
            question_type="managerial",
            candidate_profile=self.user_profile,
            conversation_history=self.conversation_history,
        )
        return InterviewAnswer(
            text=answer_text,
            confidence=0.80,
            follow_ups=[
                "How did that impact the team?",
                "What would you do differently?",
            ],
            agent_type="managerial",
        )
