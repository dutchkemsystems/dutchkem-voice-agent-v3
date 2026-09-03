from typing import Dict, List


class KeywordMatcher:
    """Match interview-related keywords in transcript text."""

    DEFAULT_KEYWORDS = [
        "interview", "position", "role", "experience", "skills",
        "tell me about yourself", "why do you want", "salary",
        "availability", "references", "background check",
        "qualification", "resume", "hiring", "candidate",
    ]

    def __init__(self, keywords: List[str] | None = None):
        self.keywords = keywords if keywords is not None else list(self.DEFAULT_KEYWORDS)
        self.keyword_weight = 1.0

    def match(self, text: str) -> Dict:
        """Score text against known interview keywords.

        Returns:
            dict with ``score`` (0-1), ``matched_keywords`` list, and
            ``total_keywords`` count.
        """
        if not text:
            return {"score": 0.0, "matched_keywords": [], "total_keywords": len(self.keywords)}

        text_lower = text.lower()
        matched = [kw for kw in self.keywords if kw in text_lower]

        score = min(len(matched) / 3, 1.0) if matched else 0.0

        return {
            "score": score,
            "matched_keywords": matched,
            "total_keywords": len(self.keywords),
        }
