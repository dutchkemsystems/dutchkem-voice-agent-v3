from apps.interview.agents.base_agent import BaseInterviewAgent, InterviewQuestion, InterviewAnswer


class BoardPresentationAgent(BaseInterviewAgent):
    KEYWORDS = ["board", "strategic", "executive", "quarterly review", "investors", "revenue", "growth", "market", "risk"]
    AGENT_TYPE = "board_presentation"

    def can_handle(self, question: InterviewQuestion) -> bool:
        text = question.text.lower()
        return any(kw in text for kw in self.KEYWORDS)

    async def generate_answer(self, question: InterviewQuestion) -> InterviewAnswer:
        return InterviewAnswer(
            text=f"Regarding '{question.text}': Let me present the strategic overview with key metrics and risk assessment.",
            confidence=0.88,
            follow_ups=["What's the projected ROI?", "How does this compare to last quarter?"],
            agent_type=self.AGENT_TYPE,
        )
