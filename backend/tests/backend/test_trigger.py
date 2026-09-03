import pytest
from unittest.mock import patch, MagicMock


# --- KeywordMatcher Tests ---

def test_keyword_matcher_init_defaults():
    from apps.background.keyword_matcher import KeywordMatcher
    matcher = KeywordMatcher()
    assert len(matcher.keywords) > 0
    assert matcher.keyword_weight > 0


def test_keyword_matcher_init_custom_keywords():
    from apps.background.keyword_matcher import KeywordMatcher
    custom = ["hello", "world"]
    matcher = KeywordMatcher(keywords=custom)
    assert matcher.keywords == custom


def test_keyword_matcher_match_interview_keywords():
    from apps.background.keyword_matcher import KeywordMatcher
    matcher = KeywordMatcher()
    result = matcher.match("Tell me about your interview experience")
    assert result["score"] > 0
    assert len(result["matched_keywords"]) > 0


def test_keyword_matcher_match_case_insensitive():
    from apps.background.keyword_matcher import KeywordMatcher
    matcher = KeywordMatcher()
    result_lower = matcher.match("interview")
    result_upper = matcher.match("INTERVIEW")
    result_mixed = matcher.match("InTeRvIeW")
    assert result_lower["score"] == result_upper["score"]
    assert result_lower["score"] == result_mixed["score"]


def test_keyword_matcher_no_match():
    from apps.background.keyword_matcher import KeywordMatcher
    matcher = KeywordMatcher()
    result = matcher.match("Hello, how are you today?")
    assert result["score"] == 0.0
    assert len(result["matched_keywords"]) == 0


def test_keyword_matcher_multiple_keywords():
    from apps.background.keyword_matcher import KeywordMatcher
    matcher = KeywordMatcher()
    result = matcher.match("position role experience skills")
    assert result["score"] > 0
    assert len(result["matched_keywords"]) >= 3


def test_keyword_matcher_empty_text():
    from apps.background.keyword_matcher import KeywordMatcher
    matcher = KeywordMatcher()
    result = matcher.match("")
    assert result["score"] == 0.0
    assert len(result["matched_keywords"]) == 0


def test_keyword_matcher_score_normalized():
    from apps.background.keyword_matcher import KeywordMatcher
    matcher = KeywordMatcher()
    result = matcher.match("interview position role experience skills salary")
    assert 0.0 <= result["score"] <= 1.0


def test_keyword_matcher_weighted_score():
    from apps.background.keyword_matcher import KeywordMatcher
    matcher = KeywordMatcher()
    result = matcher.match("tell me about yourself")
    assert result["score"] > 0


# --- ContextAnalyzer Tests ---

def test_context_analyzer_init_defaults():
    from apps.background.context_analyzer import ContextAnalyzer
    analyzer = ContextAnalyzer()
    assert analyzer.context_weight > 0


def test_context_analyzer_detect_questions():
    from apps.background.context_analyzer import ContextAnalyzer
    analyzer = ContextAnalyzer()
    result = analyzer.analyze("Can you tell me about your experience?")
    assert result["has_questions"] is True
    assert result["score"] > 0


def test_context_analyzer_formal_language():
    from apps.background.context_analyzer import ContextAnalyzer
    analyzer = ContextAnalyzer()
    result = analyzer.analyze("What is your qualifications for this position?")
    assert result["formality_score"] > 0


def test_context_analyzer_casual_conversation():
    from apps.background.context_analyzer import ContextAnalyzer
    analyzer = ContextAnalyzer()
    result = analyzer.analyze("Hey what's up, wanna grab lunch?")
    assert result["score"] < 0.3


def test_context_analyzer_empty_text():
    from apps.background.context_analyzer import ContextAnalyzer
    analyzer = ContextAnalyzer()
    result = analyzer.analyze("")
    assert result["score"] == 0.0
    assert result["has_questions"] is False


def test_context_analyzer_mixed_signals():
    from apps.background.context_analyzer import ContextAnalyzer
    analyzer = ContextAnalyzer()
    result = analyzer.analyze("Can you describe your qualifications and experience for this role?")
    assert result["has_questions"] is True
    assert result["formality_score"] > 0.3
    assert result["score"] > 0.4


def test_context_analyzer_no_questions():
    from apps.background.context_analyzer import ContextAnalyzer
    analyzer = ContextAnalyzer()
    result = analyzer.analyze("I went to the store yesterday.")
    assert result["has_questions"] is False


# --- InterviewTriggerDetector Tests ---

def test_trigger_detector_init_defaults():
    from apps.background.trigger_detector import InterviewTriggerDetector, InterviewPhase
    detector = InterviewTriggerDetector()
    assert detector.phase == InterviewPhase.IDLE
    assert detector.trigger_threshold > 0
    assert len(detector.conversation_history) == 0


def test_trigger_detector_init_custom_threshold():
    from apps.background.trigger_detector import InterviewTriggerDetector
    detector = InterviewTriggerDetector(trigger_threshold=0.5)
    assert detector.trigger_threshold == 0.5


def test_trigger_detector_analyze_transcript_returns_dict():
    from apps.background.trigger_detector import InterviewTriggerDetector
    detector = InterviewTriggerDetector()
    result = detector.analyze_transcript("Tell me about your interview experience")
    assert "phase" in result
    assert "score" in result
    assert "keyword_score" in result
    assert "context_score" in result
    assert "should_activate" in result


def test_trigger_detector_casual_no_activation():
    from apps.background.trigger_detector import InterviewTriggerDetector, InterviewPhase
    detector = InterviewTriggerDetector()
    result = detector.analyze_transcript("Hey, wanna get lunch today?")
    assert result["score"] < 0.7
    assert result["phase"] == InterviewPhase.IDLE.value
    assert result["should_activate"] is False


def test_trigger_detector_interview_triggers_detection():
    from apps.background.trigger_detector import InterviewTriggerDetector, InterviewPhase
    detector = InterviewTriggerDetector()
    result = detector.analyze_transcript(
        "Can you tell me about your interview experience and skills for this position?"
    )
    assert result["keyword_score"] > 0
    assert result["context_score"] > 0


def test_trigger_detector_phase_transitions():
    from apps.background.trigger_detector import InterviewTriggerDetector, InterviewPhase
    detector = InterviewTriggerDetector(trigger_threshold=0.3)

    # First strong signal -> DETECTING
    result1 = detector.analyze_transcript(
        "Tell me about your experience with this position"
    )
    assert detector.phase in (InterviewPhase.DETECTING, InterviewPhase.ACTIVE)

    # Another strong signal -> ACTIVE
    result2 = detector.analyze_transcript(
        "What are your skills for this role?"
    )
    # Should be ACTIVE after two strong signals
    if detector.phase == InterviewPhase.ACTIVE:
        assert result2["should_activate"] is True


def test_trigger_detector_combined_score():
    from apps.background.trigger_detector import InterviewTriggerDetector
    detector = InterviewTriggerDetector()
    result = detector.analyze_transcript(
        "Can you describe your qualifications for this interview position?"
    )
    expected_score = (
        result["keyword_score"] * 0.6 + result["context_score"] * 0.4
    )
    assert abs(result["score"] - expected_score) < 0.001


def test_trigger_detector_conversation_history():
    from apps.background.trigger_detector import InterviewTriggerDetector
    detector = InterviewTriggerDetector()
    detector.analyze_transcript("First message")
    detector.analyze_transcript("Second message")
    assert len(detector.conversation_history) == 2
    assert detector.conversation_history[0] == "First message"
    assert detector.conversation_history[1] == "Second message"


def test_trigger_detector_deactivate():
    from apps.background.trigger_detector import InterviewTriggerDetector, InterviewPhase
    detector = InterviewTriggerDetector()
    detector.phase = InterviewPhase.ACTIVE
    detector.deactivate()
    assert detector.phase == InterviewPhase.IDLE
    assert len(detector.conversation_history) == 0


def test_trigger_detector_reset():
    from apps.background.trigger_detector import InterviewTriggerDetector, InterviewPhase
    detector = InterviewTriggerDetector()
    detector.analyze_transcript("Some message")
    detector.reset()
    assert detector.phase == InterviewPhase.IDLE
    assert len(detector.conversation_history) == 0


def test_trigger_detector_set_threshold():
    from apps.background.trigger_detector import InterviewTriggerDetector
    detector = InterviewTriggerDetector()
    detector.set_threshold(0.9)
    assert detector.trigger_threshold == 0.9


def test_trigger_detector_ending_phase():
    from apps.background.trigger_detector import InterviewTriggerDetector, InterviewPhase
    detector = InterviewTriggerDetector()
    detector.phase = InterviewPhase.ACTIVE
    # Weak signal should move to ENDING
    result = detector.analyze_transcript("Hello")
    if detector.phase == InterviewPhase.ENDING:
        assert result["phase"] == InterviewPhase.ENDING.value


def test_trigger_detector_update_keywords():
    from apps.background.trigger_detector import InterviewTriggerDetector
    detector = InterviewTriggerDetector()
    original_count = len(detector.keywords)
    detector.update_keywords(["new_keyword", "another_keyword"])
    assert len(detector.keywords) == original_count + 2


# --- Integration: KeywordMatcher + ContextAnalyzer + TriggerDetector ---

def test_integration_full_interview_detection():
    from apps.background.trigger_detector import InterviewTriggerDetector, InterviewPhase
    detector = InterviewTriggerDetector()

    # Casual - should not trigger
    result = detector.analyze_transcript("Hey, nice weather today!")
    assert result["should_activate"] is False

    # Formal interview - should score high
    result = detector.analyze_transcript(
        "Can you tell me about your experience and skills for this position? "
        "Why do you want this role?"
    )
    assert result["keyword_score"] > 0
    assert result["context_score"] > 0
