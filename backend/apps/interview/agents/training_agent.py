from apps.interview.agents.base_agent import BaseInterviewAgent, InterviewQuestion, InterviewAnswer


class TrainingAgent(BaseInterviewAgent):
    KEYWORDS = ["training", "onboarding", "orientation", "learn", "teach", "process", "documentation", "handbook"]
    AGENT_TYPE = "training"

    def can_handle(self, question: InterviewQuestion) -> bool:
        text = question.text.lower()
        return any(kw in text for kw in self.KEYWORDS)

    async def generate_answer(self, question: InterviewQuestion) -> InterviewAnswer:
        return InterviewAnswer(
            text=f"Let me explain '{question.text}' step by step. First, we'll cover the concept, then I'll show you a practical example.",
            confidence=0.84,
            follow_ups=["Does that make sense?", "Would you like to try a practice exercise?"],
            agent_type=self.AGENT_TYPE,
        )
