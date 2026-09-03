from .base_agent import BaseInterviewAgent, InterviewQuestion, InterviewAnswer


class TechnicalAgent(BaseInterviewAgent):
    TECHNICAL_KEYWORDS = [
        "system design", "design", "architecture", "explain", "database", "api",
    ]

    def can_handle(self, question: InterviewQuestion) -> bool:
        text = question.text.lower()
        return any(kw in text for kw in self.TECHNICAL_KEYWORDS)

    async def generate_answer(self, question: InterviewQuestion) -> InterviewAnswer:
        answer_text = await self.llm_service.generate_interview_answer(
            question=question.text,
            question_type="technical",
            candidate_profile=self.user_profile,
            conversation_history=self.conversation_history,
        )
        return InterviewAnswer(
            text=answer_text,
            confidence=0.80,
            follow_ups=[
                "Can you walk through the trade-offs?",
                "How would you scale this?",
            ],
            agent_type="technical",
        )
