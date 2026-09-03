from .base_agent import BaseInterviewAgent, InterviewQuestion, InterviewAnswer


class HRAgent(BaseInterviewAgent):
    HR_KEYWORDS = [
        "tell me about yourself", "why do you want", "strengths", "weaknesses",
        "team", "leadership", "conflict", "pressure", "deadline",
    ]

    def can_handle(self, question: InterviewQuestion) -> bool:
        text = question.text.lower()
        return any(kw in text for kw in self.HR_KEYWORDS)

    async def generate_answer(self, question: InterviewQuestion) -> InterviewAnswer:
        answer_text = await self.llm_service.generate_interview_answer(
            question=question.text,
            question_type="hr",
            candidate_profile=self.user_profile,
            conversation_history=self.conversation_history,
        )
        return InterviewAnswer(
            text=answer_text,
            confidence=0.85,
            follow_ups=["Can you give a specific example?", "What was the outcome?"],
            agent_type="hr",
        )
