from typing import Dict, List, Optional
from enum import Enum

from apps.background.keyword_matcher import KeywordMatcher
from apps.background.context_analyzer import ContextAnalyzer


class InterviewPhase(Enum):
    IDLE = "idle"
    DETECTING = "detecting"
    ACTIVE = "active"
    ENDING = "ending"


class InterviewTriggerDetector:
    """Detect interview conversations by combining keyword and context signals."""

    def __init__(
        self,
        trigger_threshold: float = 0.7,
        keywords: List[str] | None = None,
    ):
        self.phase = InterviewPhase.IDLE
        self.trigger_threshold = trigger_threshold
        self.conversation_history: List[str] = []

        self.keyword_matcher = KeywordMatcher(keywords=keywords)
        self.context_analyzer = ContextAnalyzer()

        self.keywords = self.keyword_matcher.keywords

    def analyze_transcript(self, transcript: str) -> Dict:
        """Analyze a transcript segment for interview triggers.

        Returns:
            dict with phase, score, keyword_score, context_score,
            and should_activate flag.
        """
        self.conversation_history.append(transcript)

        # Keyword matching
        kw_result = self.keyword_matcher.match(transcript)
        keyword_score = kw_result["score"]

        # Context analysis
        ctx_result = self.context_analyzer.analyze(transcript)
        context_score = ctx_result["score"]

        # Combined score (weighted)
        combined_score = keyword_score * 0.6 + context_score * 0.4

        # Phase transition logic
        if combined_score > self.trigger_threshold:
            if self.phase == InterviewPhase.IDLE:
                self.phase = InterviewPhase.DETECTING
            elif self.phase == InterviewPhase.DETECTING:
                self.phase = InterviewPhase.ACTIVE
        elif combined_score < 0.1:
            if self.phase == InterviewPhase.ACTIVE:
                self.phase = InterviewPhase.ENDING

        return {
            "phase": self.phase.value,
            "score": combined_score,
            "keyword_score": keyword_score,
            "context_score": context_score,
            "should_activate": self.phase == InterviewPhase.ACTIVE,
        }

    def deactivate(self) -> None:
        """Deactivate detector and reset state."""
        self.phase = InterviewPhase.IDLE
        self.conversation_history.clear()

    def reset(self) -> None:
        """Full reset of detector state."""
        self.phase = InterviewPhase.IDLE
        self.conversation_history.clear()

    def set_threshold(self, threshold: float) -> None:
        """Set the activation threshold."""
        self.trigger_threshold = threshold

    def update_keywords(self, new_keywords: List[str]) -> None:
        """Add new keywords to the matcher."""
        self.keywords.extend(new_keywords)
        self.keyword_matcher.keywords = self.keywords
