from apps.interview.agents.base_agent import BaseInterviewAgent, InterviewQuestion, InterviewAnswer


class ClientMeetingAgent(BaseInterviewAgent):
    KEYWORDS = ["client", "project update", "deliverables", "timeline", "stakeholder", "budget", "scope", "requirements"]
    AGENT_TYPE = "client_meeting"

    def can_handle(self, question: InterviewQuestion) -> bool:
        text = question.text.lower()
        return any(kw in text for kw in self.KEYWORDS)

    async def generate_answer(self, question: InterviewQuestion) -> InterviewAnswer:
        return InterviewAnswer(
            text=f"Regarding '{question.text}': As your representative, I'll provide a clear status update on deliverables and timelines.",
            confidence=0.82,
            follow_ups=["What specific metrics would you like to see?", "Any concerns about the timeline?"],
            agent_type=self.AGENT_TYPE,
        )
