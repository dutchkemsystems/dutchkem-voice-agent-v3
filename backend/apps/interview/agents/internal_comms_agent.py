from apps.interview.agents.base_agent import BaseInterviewAgent, InterviewQuestion, InterviewAnswer


class InternalCommsAgent(BaseInterviewAgent):
    KEYWORDS = ["standup", "team update", "all-hands", "project update", "decision", "sync", "retrospective", "planning"]
    AGENT_TYPE = "internal_comms"

    def can_handle(self, question: InterviewQuestion) -> bool:
        text = question.text.lower()
        return any(kw in text for kw in self.KEYWORDS)

    async def generate_answer(self, question: InterviewQuestion) -> InterviewAnswer:
        return InterviewAnswer(
            text=f"Regarding '{question.text}': Here's a concise update on status, blockers, and next steps.",
            confidence=0.81,
            follow_ups=["Any blockers?", "Who needs to follow up on this?"],
            agent_type=self.AGENT_TYPE,
        )
