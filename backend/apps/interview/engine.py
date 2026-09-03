import logging
import time
from typing import Dict, List, Optional

from apps.interview.adaptive import AdaptiveDifficulty, DifficultyLevel
from apps.interview.response_generator import ResponseGenerator, InterviewResponse
from apps.interview.agents.base_agent import InterviewQuestion, InterviewAnswer
from apps.interview.orchestrator import InterviewOrchestrator
from apps.background.trigger_detector import InterviewTriggerDetector, InterviewPhase

logger = logging.getLogger(__name__)

_CATEGORY_KEYWORDS = {
    "hr": [
        "tell me about yourself", "why do you want", "strengths", "weaknesses",
        "team", "leadership", "conflict", "pressure", "deadline",
    ],
    "technical": [
        "explain", "design", "architecture", "system", "database", "api",
        "how does", "describe",
    ],
    "coding": [
        "write a function", "implement", "solve", "code review", "algorithm",
        "sort", "merge", "traverse",
    ],
    "managerial": [
        "manage", "prioritize", "stakeholder", "budget", "scenario",
        "cross-functional", "strategy",
    ],
}


class AutonomousInterviewEngine:
    """Orchestrates the full autonomous interview flow.

    Coordinates trigger detection, speech-to-text, agent routing,
    response generation (TTS + avatar), adaptive difficulty, and
    follow-up question handling.
    """

    def __init__(
        self,
        user_profile: Dict,
        company_context: Dict,
        stt_service=None,
        tts_service=None,
        face_service=None,
        orchestrator=None,
    ):
        self.user_profile = user_profile
        self.company_context = company_context

        self.trigger_detector = InterviewTriggerDetector()
        self.stt_service = stt_service
        self.tts_service = tts_service
        self.face_service = face_service
        self.orchestrator = orchestrator
        self.adaptive = AdaptiveDifficulty()
        self.response_generator = ResponseGenerator()

        self.is_active = False
        self.session_stats: Dict = {
            "total_questions": 0,
            "start_time": None,
            "end_time": None,
        }

    def is_running(self) -> bool:
        return self.is_active

    async def start_interview(self) -> None:
        self.is_active = True
        self.session_stats["start_time"] = time.time()

    async def stop_interview(self) -> None:
        self.is_active = False
        self.session_stats["end_time"] = time.time()

    async def process_audio(self, audio_data: bytes) -> Dict:
        if self.stt_service is None:
            return {"action": "waiting", "phase": "idle"}

        transcript = await self.stt_service.transcribe_async(audio_data)

        if not self.is_active:
            trigger_result = self.trigger_detector.analyze_transcript(transcript)

            if trigger_result["should_activate"]:
                self.is_active = True
                return await self._generate_introduction()

            return {"action": "waiting", "phase": trigger_result["phase"]}

        question = self._categorize_question(transcript)

        answer = await self._route_and_get_answer(question)

        response = await self.response_generator.generate(
            answer, tts_service=self.tts_service
        )

        self.session_stats["total_questions"] += 1
        self.adaptive.record_response(
            confidence=answer.confidence,
            response_time=0.0,
            follow_ups_count=len(answer.follow_ups),
        )

        return {
            "action": "respond",
            "transcript": transcript,
            "answer": answer.text,
            "audio": response.audio,
            "avatar": response.avatar_data,
            "confidence": answer.confidence,
        }

    async def _generate_introduction(self) -> Dict:
        response = await self.response_generator.generate_introduction(
            user_name=self.user_profile.get("name", "Candidate"),
            position=self.user_profile.get("position", ""),
            company_name=self.company_context.get("name", ""),
            tts_service=self.tts_service,
        )
        return {
            "action": "introduce",
            "answer": response.text,
            "audio": response.audio,
        }

    async def _generate_closing(self) -> Dict:
        response = await self.response_generator.generate_closing(
            user_name=self.user_profile.get("name", "Candidate"),
            company_name=self.company_context.get("name", ""),
            tts_service=self.tts_service,
        )
        return {
            "action": "closing",
            "answer": response.text,
            "audio": response.audio,
        }

    def _categorize_question(self, transcript: str) -> InterviewQuestion:
        lower = transcript.lower()
        for category, keywords in _CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in lower:
                    return InterviewQuestion(
                        text=transcript,
                        category=category,
                        difficulty=self.adaptive.current_difficulty.value,
                    )
        return InterviewQuestion(
            text=transcript,
            category="general",
            difficulty=self.adaptive.current_difficulty.value,
        )

    async def _route_and_get_answer(self, question: InterviewQuestion) -> InterviewAnswer:
        if self.orchestrator is not None:
            answer = await self.orchestrator.process_question(question)
            if answer is not None:
                return answer

        return InterviewAnswer(
            text=f"Thank you for your question: '{question.text}'. That's a great point to discuss.",
            confidence=0.5,
            follow_ups=[],
            agent_type="fallback",
        )

    async def generate_follow_up(self, original_question: str) -> Dict:
        if self.orchestrator is not None:
            answer = await self.orchestrator.process_question(
                InterviewQuestion(
                    text=original_question,
                    category="general",
                    difficulty=self.adaptive.current_difficulty.value,
                )
            )
            if answer and answer.follow_ups:
                return {"question": answer.follow_ups[0]}

        return {"question": f"Can you tell me more about your experience with that?"}

    def get_session_stats(self) -> Dict:
        return {
            "total_questions": self.session_stats["total_questions"],
            "is_active": self.is_active,
            "current_difficulty": self.adaptive.current_difficulty.value,
            "performance": self.adaptive.get_performance_summary(),
        }

    async def reset_session(self) -> None:
        self.is_active = False
        self.session_stats = {
            "total_questions": 0,
            "start_time": None,
            "end_time": None,
        }
        self.adaptive.reset()
        self.trigger_detector.reset()
