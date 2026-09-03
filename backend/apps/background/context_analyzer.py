from typing import Dict


class ContextAnalyzer:
    """Analyze conversation context for interview indicators."""

    QUESTION_INDICATORS = [
        "can you", "could you", "tell me", "describe",
        "explain", "what is", "what are", "how do", "how would",
    ]

    FORMAL_INDICATORS = [
        "position", "candidate", "qualifications", "experience",
        "role", "skills", "resume", "hiring", "interview",
    ]

    def __init__(self):
        self.context_weight = 1.0

    def analyze(self, text: str) -> Dict:
        """Analyze text for interview context signals.

        Returns:
            dict with ``score`` (0-1), ``has_questions`` bool,
            and ``formality_score`` (0-1).
        """
        if not text:
            return {"score": 0.0, "has_questions": False, "formality_score": 0.0}

        text_lower = text.lower()

        # Question detection
        has_questions = any(ind in text_lower for ind in self.QUESTION_INDICATORS)

        # Formal language detection
        formal_matches = sum(1 for ind in self.FORMAL_INDICATORS if ind in text_lower)
        formality = formal_matches / len(self.FORMAL_INDICATORS) if self.FORMAL_INDICATORS else 0.0

        score = (0.5 if has_questions else 0.0) + (formality * 0.5)

        return {
            "score": score,
            "has_questions": has_questions,
            "formality_score": formality,
        }
