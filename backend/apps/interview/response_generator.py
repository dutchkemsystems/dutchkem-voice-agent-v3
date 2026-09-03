import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from apps.interview.agents.base_agent import InterviewAnswer

logger = logging.getLogger(__name__)

_EXPRESSION_MAP = {
    "hr": "friendly",
    "technical": "focused",
    "managerial": "confident",
    "coding": "analytical",
}

_EXPRESSION_BY_CONFIDENCE = [
    (0.8, "confident"),
    (0.6, "neutral"),
    (0.0, "neutral"),
]


@dataclass
class InterviewResponse:
    text: str
    audio: Optional[bytes] = None
    avatar_data: Optional[Dict] = None
    confidence: float = 0.0
    agent_type: Optional[str] = None
    follow_up_text: Optional[str] = None


class ResponseGenerator:
    """Combines agent answers with TTS audio and avatar animation data."""

    def _determine_expression(self, confidence: float, agent_type: str) -> str:
        if confidence > 0.8:
            return "confident"
        if confidence >= 0.6:
            return _EXPRESSION_MAP.get(agent_type, "neutral")
        return "neutral"

    def _build_avatar_data(self, confidence: float, agent_type: str) -> Dict:
        expression = self._determine_expression(confidence, agent_type)
        gesture_map = {
            "confident": "nod",
            "friendly": "open_hands",
            "focused": "lean_forward",
            "analytical": "point",
            "neutral": "rest",
        }
        return {
            "expression": expression,
            "gesture": gesture_map.get(expression, "rest"),
            "agent_type": agent_type,
        }

    async def generate(
        self,
        answer: InterviewAnswer,
        tts_service=None,
        voice: str = "af_heart",
    ) -> InterviewResponse:
        audio = None
        if tts_service is not None:
            try:
                audio = await tts_service.synthesize_async(answer.text, voice)
            except Exception:
                logger.warning("TTS synthesis failed, continuing without audio")
                audio = None

        return InterviewResponse(
            text=answer.text,
            audio=audio,
            avatar_data=self._build_avatar_data(answer.confidence, answer.agent_type),
            confidence=answer.confidence,
            agent_type=answer.agent_type,
        )

    async def generate_introduction(
        self,
        user_name: str,
        position: str,
        company_name: str,
        tts_service=None,
        voice: str = "af_heart",
    ) -> InterviewResponse:
        intro_text = (
            f"Hello, I'm {user_name}. Thank you for having me today. "
            f"I'm excited about this {position} opportunity at {company_name}."
        )

        audio = None
        if tts_service is not None:
            try:
                audio = await tts_service.synthesize_async(intro_text, voice)
            except Exception:
                logger.warning("TTS synthesis failed for introduction")
                audio = None

        return InterviewResponse(
            text=intro_text,
            audio=audio,
            avatar_data={"expression": "friendly", "gesture": "open_hands", "agent_type": "intro"},
            confidence=1.0,
            agent_type="intro",
        )

    async def generate_closing(
        self,
        user_name: str,
        company_name: str,
        tts_service=None,
        voice: str = "af_heart",
    ) -> InterviewResponse:
        closing_text = (
            f"Thank you so much for the opportunity to interview at {company_name}. "
            f"I'm very excited about this role and look forward to hearing from you. "
            f"Have a great day!"
        )

        audio = None
        if tts_service is not None:
            try:
                audio = await tts_service.synthesize_async(closing_text, voice)
            except Exception:
                logger.warning("TTS synthesis failed for closing")
                audio = None

        return InterviewResponse(
            text=closing_text,
            audio=audio,
            avatar_data={"expression": "friendly", "gesture": "wave", "agent_type": "closing"},
            confidence=1.0,
            agent_type="closing",
        )

    async def generate_with_follow_up(
        self,
        answer: InterviewAnswer,
        tts_service=None,
        voice: str = "af_heart",
    ) -> InterviewResponse:
        response = await self.generate(answer, tts_service=tts_service, voice=voice)
        if answer.follow_ups:
            response.follow_up_text = answer.follow_ups[0]
        return response
