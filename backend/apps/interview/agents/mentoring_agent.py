from apps.interview.agents.base_agent import BaseInterviewAgent, InterviewQuestion, InterviewAnswer


class MentoringAgent(BaseInterviewAgent):
    KEYWORDS = ["mentor", "guide", "explain", "how does", "learn", "career", "code review", "best practice"]
    AGENT_TYPE = "mentoring"

    def can_handle(self, question: InterviewQuestion) -> bool:
        text = question.text.lower()
        return any(kw in text for kw in self.KEYWORDS)

    async def generate_answer(self, question: InterviewQuestion) -> InterviewAnswer:
        return InterviewAnswer(
            text=f"Great question about '{question.text}'. Let me break this down step by step with a practical example.",
            confidence=0.85,
            follow_ups=["Would you like me to go deeper on any part?", "Can you try applying this to your current project?"],
            agent_type=self.AGENT_TYPE,
        )
