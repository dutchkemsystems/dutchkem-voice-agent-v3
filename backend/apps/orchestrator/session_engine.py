import time
from typing import Dict, List, Optional

from apps.modes.registry import ModeConfig, ModeRegistry
from apps.scoring.mode_scorer import ModeAwareScorer
from apps.coaching.mode_coach import ModeAwareCoach


class SessionEngine:
    """Mode-agnostic session orchestrator."""

    def __init__(self, mode_id: str = "interview") -> None:
        self.current_mode = ModeRegistry.get(mode_id) or ModeRegistry.get("interview")
        self.scorer = ModeAwareScorer(self.current_mode)
        self.coach = ModeAwareCoach(self.current_mode)
        self.start_time = time.time()
        self.turn_count = 0
        self.scores_history: List[Dict] = []

    def switch_mode(self, mode_id: str) -> bool:
        """Switch to a different mode."""
        new_mode = ModeRegistry.get(mode_id)
        if not new_mode:
            return False

        if mode_id not in self.current_mode.allowed_transitions:
            return False

        self.current_mode = new_mode
        self.scorer = ModeAwareScorer(new_mode)
        self.coach = ModeAwareCoach(new_mode)
        return True

    def get_mode_config(self) -> ModeConfig:
        """Get current mode configuration."""
        return self.current_mode

    def get_available_modes(self) -> List[Dict]:
        """Get list of all available modes."""
        return [m.to_dict() for m in ModeRegistry.get_all()]

    def can_transition(self, target_mode: str) -> bool:
        """Check if transition to target mode is allowed."""
        return target_mode in self.current_mode.allowed_transitions

    def process_response(self, question: str, answer: str, audio_features: Dict) -> Dict:
        """Process a response and return scoring + coaching."""
        self.turn_count += 1

        scores = self.scorer.score(question, answer, audio_features)
        self.scores_history.append(scores)

        tip = self.coach.get_tip(scores)

        return {
            "scores": scores,
            "coaching_tip": tip,
            "turn": self.turn_count,
            "mode": self.current_mode.mode_id,
        }

    def get_session_stats(self) -> Dict:
        """Get session statistics."""
        duration = time.time() - self.start_time
        avg_scores = {}
        if self.scores_history:
            for dim in self.scores_history[0]:
                avg_scores[dim] = sum(s[dim] for s in self.scores_history) / len(self.scores_history)

        return {
            "mode": self.current_mode.mode_id,
            "duration": duration,
            "turns": self.turn_count,
            "average_scores": avg_scores,
        }
