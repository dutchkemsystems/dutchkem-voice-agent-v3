from apps.interview.agents.base_agent import BaseInterviewAgent, InterviewQuestion, InterviewAnswer


class PerformanceReviewAgent(BaseInterviewAgent):
    KEYWORDS = ["performance review", "self-assessment", "achievements", "goals", "growth", "quarterly", "annual", "metrics"]
    AGENT_TYPE = "performance_review"

    def can_handle(self, question: InterviewQuestion) -> bool:
        text = question.text.lower()
        return any(kw in text for kw in self.KEYWORDS)

    async def generate_answer(self, question: InterviewQuestion) -> InterviewAnswer:
        return InterviewAnswer(
            text=f"Reflecting on '{question.text}': I delivered measurable outcomes across key metrics and identified growth areas for next quarter.",
            confidence=0.83,
            follow_ups=["What specific metrics should we focus on?", "How does this align with team goals?"],
            agent_type=self.AGENT_TYPE,
        )
