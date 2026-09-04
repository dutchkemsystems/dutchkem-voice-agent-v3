from apps.interview.agents.base_agent import BaseInterviewAgent, InterviewQuestion, InterviewAnswer


class CustomerSupportAgent(BaseInterviewAgent):
    KEYWORDS = ["support", "help", "issue", "problem", "bug", "complaint", "ticket", "troubleshoot", "resolve"]
    AGENT_TYPE = "customer_support"

    def can_handle(self, question: InterviewQuestion) -> bool:
        text = question.text.lower()
        return any(kw in text for kw in self.KEYWORDS)

    async def generate_answer(self, question: InterviewQuestion) -> InterviewAnswer:
        return InterviewAnswer(
            text=f"I understand you're experiencing '{question.text}'. Let me help resolve this step by step.",
            confidence=0.87,
            follow_ups=["Can you describe the exact error?", "When did this issue start?"],
            agent_type=self.AGENT_TYPE,
        )
