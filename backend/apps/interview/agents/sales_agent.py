from apps.interview.agents.base_agent import BaseInterviewAgent, InterviewQuestion, InterviewAnswer


class SalesAgent(BaseInterviewAgent):
    KEYWORDS = ["pitch", "demo", "pricing", "proposal", "close", "objection", "competitor", "value", "ROI", "contract"]
    AGENT_TYPE = "sales"

    def can_handle(self, question: InterviewQuestion) -> bool:
        text = question.text.lower()
        return any(kw in text for kw in self.KEYWORDS)

    async def generate_answer(self, question: InterviewQuestion) -> InterviewAnswer:
        return InterviewAnswer(
            text=f"I'd love to show you how '{question.text}' fits into our value proposition. Let me walk you through the key benefits.",
            confidence=0.86,
            follow_ups=["What's your biggest concern?", "Would you like to see a case study?"],
            agent_type=self.AGENT_TYPE,
        )
