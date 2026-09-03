from .base_agent import BaseInterviewAgent, InterviewQuestion, InterviewAnswer


class CodingAgent(BaseInterviewAgent):
    CODING_KEYWORDS = [
        "write a function", "implement", "solve", "code review", "code",
    ]

    def can_handle(self, question: InterviewQuestion) -> bool:
        text = question.text.lower()
        return any(kw in text for kw in self.CODING_KEYWORDS)

    async def generate_answer(self, question: InterviewQuestion) -> InterviewAnswer:
        answer_text = await self.llm_service.generate_interview_answer(
            question=question.text,
            question_type="coding",
            candidate_profile=self.user_profile,
            conversation_history=self.conversation_history,
        )
        return InterviewAnswer(
            text=answer_text,
            confidence=0.80,
            follow_ups=[
                "Can you optimize the time complexity?",
                "What are the edge cases?",
            ],
            agent_type="coding",
        )
