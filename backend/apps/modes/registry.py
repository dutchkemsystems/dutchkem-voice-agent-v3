from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ModeConfig:
    """Configuration for an operational mode."""
    mode_id: str
    display_name: str
    description: str
    icon: str
    agent_classes: List[str]
    default_agent: str
    trigger_keywords: List[str] = field(default_factory=list)
    trigger_context_words: List[str] = field(default_factory=list)
    auto_detect_enabled: bool = True
    scoring_overrides: Dict[str, float] = field(default_factory=dict)
    system_prompt: str = ""
    response_style: str = "professional"
    coaching_tips: Dict[str, List[str]] = field(default_factory=dict)
    feedback_templates: Dict[str, str] = field(default_factory=dict)
    required_context: List[str] = field(default_factory=list)
    on_enter_prompt: str = ""
    on_exit_prompt: str = ""
    ui_components: List[str] = field(default_factory=lambda: ["transcript_panel"])
    default_view: str = "transcript"
    allowed_transitions: List[str] = field(default_factory=list)
    transition_permissions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "mode_id": self.mode_id,
            "display_name": self.display_name,
            "description": self.description,
            "icon": self.icon,
            "agent_classes": self.agent_classes,
            "default_agent": self.default_agent,
            "trigger_keywords": self.trigger_keywords,
            "trigger_context_words": self.trigger_context_words,
            "auto_detect_enabled": self.auto_detect_enabled,
            "scoring_overrides": self.scoring_overrides,
            "system_prompt": self.system_prompt,
            "response_style": self.response_style,
            "coaching_tips": self.coaching_tips,
            "feedback_templates": self.feedback_templates,
            "required_context": self.required_context,
            "on_enter_prompt": self.on_enter_prompt,
            "on_exit_prompt": self.on_exit_prompt,
            "ui_components": self.ui_components,
            "default_view": self.default_view,
            "allowed_transitions": self.allowed_transitions,
            "transition_permissions": self.transition_permissions,
        }


# ── All 9 Mode Definitions ──────────────────────────────────────────

MODE_CONFIGS: Dict[str, ModeConfig] = {}


def _register_modes():
    global MODE_CONFIGS

    interview = ModeConfig(
        mode_id="interview",
        display_name="Interview",
        description="Conduct job interviews as the applicant",
        icon="briefcase",
        agent_classes=["HRAgent", "TechnicalAgent", "CodingAgent", "ManagerAgent"],
        default_agent="HRAgent",
        trigger_keywords=["interview", "position", "experience", "tell me about yourself"],
        trigger_context_words=["hiring", "candidate", "qualifications", "resume"],
        system_prompt="You are a professional job candidate. Answer interview questions naturally and confidently.",
        response_style="professional",
        coaching_tips={
            "confidence": ["Speak more slowly and clearly", "Maintain consistent volume", "Use positive language"],
            "clarity": ["Structure answers with STAR method", "Avoid filler words", "Be specific with examples"],
            "relevance": ["Address the question directly", "Connect experience to the role", "Show company knowledge"],
        },
        ui_components=["scorecard_panel", "transcript_panel"],
        default_view="scorecard_panel",
        allowed_transitions=["client_meeting", "mentoring", "training"],
    )

    client_meeting = ModeConfig(
        mode_id="client_meeting",
        display_name="Client Meeting",
        description="Present to clients and stakeholders, negotiate contracts",
        icon="users",
        agent_classes=["ClientMeetingAgent"],
        default_agent="ClientMeetingAgent",
        trigger_keywords=["client", "project update", "deliverables", "timeline", "stakeholder"],
        trigger_context_words=["budget", "scope", "requirements", "feedback"],
        scoring_overrides={"persuasion": 0.20, "stakeholder_management": 0.15},
        system_prompt="You are a senior professional presenting to clients. Be confident, clear, and solution-oriented.",
        response_style="professional",
        coaching_tips={
            "confidence": ["Lead with key outcomes", "Use data to support claims"],
            "persuasion": ["Quantify value delivered", "Address concerns before they arise"],
            "clarity": ["Structure updates as: Status → Risks → Next Steps", "Use visual aids when possible"],
        },
        required_context=["project_name"],
        on_enter_prompt="Client meeting mode activated. Present project updates professionally.",
        ui_components=["transcript_panel", "project_timeline", "action_items"],
        default_view="transcript_panel",
        allowed_transitions=["interview", "internal_comms"],
    )

    mentoring = ModeConfig(
        mode_id="mentoring",
        display_name="Mentoring",
        description="Guide junior engineers, provide career development advice",
        icon="graduation-cap",
        agent_classes=["MentoringAgent"],
        default_agent="MentoringAgent",
        trigger_keywords=["mentor", "guide", "career advice", "code review", "explain"],
        trigger_context_words=["junior", "learning", "growth", "best practice"],
        scoring_overrides={"teaching_clarity": 0.30, "patience": 0.15},
        system_prompt="You are a senior mentor guiding a junior engineer. Be encouraging, patient, and provide actionable advice.",
        response_style="friendly",
        coaching_tips={
            "teaching_clarity": ["Use concrete examples", "Break complex topics into steps"],
            "patience": ["Let them think through problems", "Ask guiding questions before giving answers"],
            "confidence": ["Share your own learning experiences", "Acknowledge what they did well first"],
        },
        ui_components=["transcript_panel", "code_viewer", "learning_path"],
        default_view="transcript_panel",
        allowed_transitions=["training", "internal_comms"],
    )

    performance_review = ModeConfig(
        mode_id="performance_review",
        display_name="Performance Review",
        description="Conduct self-assessments, present achievements, set goals",
        icon="chart-bar",
        agent_classes=["PerformanceReviewAgent"],
        default_agent="PerformanceReviewAgent",
        trigger_keywords=["performance review", "self-assessment", "achievements", "goals", "growth"],
        trigger_context_words=["quarterly", "annual", "review", "metrics", "targets"],
        scoring_overrides={"executive_presence": 0.15},
        system_prompt="You are conducting a performance review. Present achievements with data, discuss growth areas constructively.",
        response_style="professional",
        coaching_tips={
            "confidence": ["Lead with quantified achievements", "Use specific metrics and outcomes"],
            "clarity": ["Structure as: Achievements → Areas for Growth → Goals"],
            "relevance": ["Connect goals to team/company objectives", "Reference specific projects"],
        },
        required_context=["review_period"],
        ui_components=["transcript_panel", "achievement_tracker", "goal_setter"],
        default_view="achievement_tracker",
        allowed_transitions=["internal_comms"],
    )

    board_presentation = ModeConfig(
        mode_id="board_presentation",
        display_name="Board Presentation",
        description="Present to board of directors, provide strategic assessments",
        icon="presentation",
        agent_classes=["BoardPresentationAgent"],
        default_agent="BoardPresentationAgent",
        trigger_keywords=["board", "strategic", "executive", "quarterly review", "investors"],
        trigger_context_words=["revenue", "growth", "market", "strategy", "risk"],
        scoring_overrides={"executive_presence": 0.30, "strategic_thinking": 0.20},
        system_prompt="You are presenting to the board of directors. Be concise, data-driven, and strategic.",
        response_style="authoritative",
        coaching_tips={
            "executive_presence": ["Open with the headline number", "Anticipate tough questions"],
            "strategic_thinking": ["Connect tactical results to strategic vision", "Address risks proactively"],
            "clarity": ["Use the Pyramid Principle: conclusion first", "Keep slides minimal, talk to the data"],
        },
        required_context=["agenda", "financial_data"],
        on_enter_prompt="Board presentation mode. Focus on strategic outcomes and data-driven insights.",
        ui_components=["transcript_panel", "agenda_tracker", "financial_dashboard"],
        default_view="agenda_tracker",
        allowed_transitions=["client_meeting", "internal_comms"],
    )

    sales = ModeConfig(
        mode_id="sales",
        display_name="Sales",
        description="Pitch products, handle objections, close deals",
        icon="trending-up",
        agent_classes=["SalesAgent"],
        default_agent="SalesAgent",
        trigger_keywords=["pitch", "demo", "pricing", "proposal", "close"],
        trigger_context_words=["objection", "competitor", "value", "ROI", "contract"],
        scoring_overrides={"persuasion": 0.25, "objection_handling": 0.20},
        system_prompt="You are a sales professional. Be persuasive, handle objections gracefully, and focus on value.",
        response_style="friendly",
        coaching_tips={
            "persuasion": ["Lead with the problem, not the product", "Use social proof and case studies"],
            "objection_handling": ["Acknowledge the concern, then reframe", "Use 'Feel, Felt, Found' technique"],
            "confidence": ["Speak with conviction about your product", "Don't discount — add value instead"],
        },
        required_context=["product_info"],
        on_enter_prompt="Sales mode activated. Focus on value proposition and advancing the deal.",
        ui_components=["transcript_panel", "objection_tracker", "deal_pipeline"],
        default_view="deal_pipeline",
        allowed_transitions=["client_meeting", "training"],
    )

    training = ModeConfig(
        mode_id="training",
        display_name="Training",
        description="Conduct new hire orientation, technical training, process documentation",
        icon="book-open",
        agent_classes=["TrainingAgent"],
        default_agent="TrainingAgent",
        trigger_keywords=["training", "onboarding", "orientation", "learn", "teach"],
        trigger_context_words=["process", "documentation", "handbook", "procedure"],
        scoring_overrides={"knowledge_transfer": 0.25, "documentation": 0.15},
        system_prompt="You are a training facilitator. Be clear, structured, and thorough.",
        response_style="friendly",
        coaching_tips={
            "knowledge_transfer": ["Check understanding after each section", "Use real-world examples"],
            "documentation": ["Summarize key takeaways in writing", "Provide reference materials"],
            "clarity": ["Structure training as: Explain → Demonstrate → Practice → Verify"],
        },
        ui_components=["transcript_panel", "training_outline", "quiz_panel"],
        default_view="training_outline",
        allowed_transitions=["mentoring", "internal_comms"],
    )

    internal_comms = ModeConfig(
        mode_id="internal_comms",
        display_name="Internal Communications",
        description="Team meetings, all-hands, project updates, decision documentation",
        icon="message-circle",
        agent_classes=["InternalCommsAgent"],
        default_agent="InternalCommsAgent",
        trigger_keywords=["standup", "team update", "all-hands", "project update", "decision"],
        trigger_context_words=["sync", "retrospective", "planning", "status"],
        scoring_overrides={"clarity": 0.20, "conciseness": 0.15},
        system_prompt="You are facilitating internal communications. Be concise, action-oriented, and inclusive.",
        response_style="professional",
        coaching_tips={
            "clarity": ["Lead with the key message", "Use bullet points for action items"],
            "conciseness": ["Keep updates under 2 minutes", "Focus on what changed, not what's the same"],
            "relevance": ["Connect to team priorities", "Mention blockers and dependencies"],
        },
        ui_components=["transcript_panel", "action_items", "decision_log"],
        default_view="transcript_panel",
        allowed_transitions=["mentoring", "training"],
    )

    customer_support = ModeConfig(
        mode_id="customer_support",
        display_name="Customer Support",
        description="Handle customer complaints, troubleshoot issues, provide solutions",
        icon="headphones",
        agent_classes=["CustomerSupportAgent"],
        default_agent="CustomerSupportAgent",
        trigger_keywords=["support", "help", "issue", "problem", "bug", "complaint", "ticket"],
        trigger_context_words=["troubleshoot", "resolve", "escalate", "customer"],
        scoring_overrides={"empathy": 0.25, "resolution_quality": 0.30},
        system_prompt="You are a customer support specialist. Be empathetic, efficient, and solution-focused.",
        response_style="friendly",
        coaching_tips={
            "empathy": ["Acknowledge the frustration first", "Use 'I understand' and 'I'm here to help'"],
            "resolution_quality": ["Ask targeted questions to diagnose", "Provide step-by-step solutions"],
            "clarity": ["Explain what you're doing and why", "Set clear expectations for resolution"],
        },
        required_context=["issue_type"],
        on_enter_prompt="Customer support mode. Focus on understanding the issue and providing solutions.",
        ui_components=["transcript_panel", "ticket_tracker", "knowledge_base"],
        default_view="ticket_tracker",
        allowed_transitions=["internal_comms"],
    )

    MODE_CONFIGS = {
        "interview": interview,
        "client_meeting": client_meeting,
        "mentoring": mentoring,
        "performance_review": performance_review,
        "board_presentation": board_presentation,
        "sales": sales,
        "training": training,
        "internal_comms": internal_comms,
        "customer_support": customer_support,
    }


_register_modes()


class ModeRegistry:
    """Central registry for all operational modes."""

    @staticmethod
    def get_all() -> List[ModeConfig]:
        return list(MODE_CONFIGS.values())

    @staticmethod
    def get(mode_id: str) -> Optional[ModeConfig]:
        return MODE_CONFIGS.get(mode_id)

    @staticmethod
    def get_ids() -> List[str]:
        return list(MODE_CONFIGS.keys())

    @staticmethod
    def get_default_agent(mode_id: str) -> Optional[str]:
        mode = MODE_CONFIGS.get(mode_id)
        return mode.default_agent if mode else None

    @staticmethod
    def get_mode_ids() -> List[str]:
        return list(MODE_CONFIGS.keys())
