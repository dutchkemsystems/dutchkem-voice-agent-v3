# Post-Hire Capabilities — Design Spec

**Date:** 2026-09-04
**Status:** Draft
**Feature:** Multi-Mode Session Engine for Dutchkem Voice Agent V3

---

## 1. Overview

Extend the Dutchkem Voice Agent from an interview-only system to a **multi-mode session engine** supporting 9 operational modes: Interview (existing) + 8 new post-hire modes (Client Meeting, Mentoring, Performance Review, Board Presentation, Sales, Training, Internal Communications, Customer Support).

### Goals
- Seamless mode switching based on context or manual selection
- Mode-specific agents, scoring, coaching, and UI
- Lifecycle hooks for mode setup/teardown
- Controlled transition rules with permissions
- Backward compatible with existing interview functionality

### Non-Goals
- Real-time multi-party calling (MVP is single-user sessions)
- External CRM/ERP integrations (API-ready but not connected)
- Voice cloning per mode (shared voice profile across modes)

---

## 2. Architecture

### 2.1 Mode Registry

A central `ModeRegistry` holds all `ModeConfig` definitions. Modes are registered at startup and queried by the engine, API, and frontend.

```
backend/apps/modes/
├── __init__.py
├── registry.py          # ModeRegistry + ModeConfig dataclass
├── schemas.py           # Pydantic request/response models
└── router.py            # FastAPI endpoints
```

### 2.2 Session Engine

The `SessionEngine` replaces `AutonomousInterviewEngine`. It is mode-agnostic — behavior is driven by the active `ModeConfig`.

```
backend/apps/orchestrator/
├── session_engine.py    # NEW - mode-agnostic engine
├── llm_service.py       # (existing, unchanged)
└── prompt_templates.py  # (extended with mode templates)
```

### 2.3 Agent Architecture

Agents are organized by mode. Some modes reuse/extend existing agents; others get dedicated implementations.

```
backend/apps/agents/
├── base_agent.py             # (existing, unchanged)
├── hr_agent.py               # (existing)
├── technical_agent.py        # (existing)
├── coding_agent.py           # (existing)
├── manager_agent.py          # (existing)
├── client_meeting_agent.py   # NEW - extends ManagerAgent
├── mentoring_agent.py        # NEW - extends TechnicalAgent
├── performance_review_agent.py # NEW - extends HRAgent
├── board_presentation_agent.py # NEW - dedicated
├── sales_agent.py            # NEW - dedicated
├── training_agent.py         # NEW - extends TechnicalAgent
├── internal_comms_agent.py   # NEW - extends ManagerAgent
└── customer_support_agent.py # NEW - dedicated
```

---

## 3. ModeConfig Dataclass

```python
@dataclass
class ModeConfig:
    # Identity
    mode_id: str                          # "interview", "client_meeting", etc.
    display_name: str                     # "Client Meeting"
    description: str                      # "Present to clients and stakeholders"
    icon: str                             # "users", "graduation-cap", etc.

    # Agents
    agent_classes: List[str]              # ["ClientMeetingAgent"]
    default_agent: str                    # "ClientMeetingAgent"

    # Trigger / Auto-Detection
    trigger_keywords: List[str]           # ["client", "project update", "deliverables"]
    trigger_context_words: List[str]      # ["stakeholder", "deadline", "budget"]
    auto_detect_enabled: bool = True      # Can this mode be auto-detected?

    # Scoring
    scoring_overrides: Dict[str, float] = field(default_factory=dict)
    # e.g., {"persuasion": 0.25, "objection_handling": 0.20}
    # Empty = use base dimensions only (confidence, clarity, relevance)

    # Prompt Templates
    system_prompt: str = ""               # Mode-specific system prompt for LLM
    response_style: str = "professional"  # professional, friendly, authoritative, empathetic

    # Coaching
    coaching_tips: Dict[str, List[str]] = field(default_factory=dict)
    feedback_templates: Dict[str, str] = field(default_factory=dict)

    # Lifecycle Hooks
    required_context: List[str] = field(default_factory=list)
    # e.g., ["agenda"] for Board, ["product_info"] for Sales
    on_enter_prompt: str = ""             # Prompt shown when mode starts
    on_exit_prompt: str = ""              # Prompt shown when mode ends

    # UI
    ui_components: List[str] = field(default_factory=lambda: ["transcript_panel"])
    default_view: str = "transcript"

    # Transitions
    allowed_transitions: List[str] = field(default_factory=list)
    # Modes this mode can transition to
    transition_permissions: List[str] = field(default_factory=list)
    # Roles that can trigger transition (empty = anyone)
```

---

## 4. Mode Definitions

### 4.1 Interview (Existing — Minimal Changes)

```python
ModeConfig(
    mode_id="interview",
    display_name="Interview",
    description="Conduct job interviews as the applicant",
    icon="briefcase",
    agent_classes=["HRAgent", "TechnicalAgent", "CodingAgent", "ManagerAgent"],
    default_agent="HRAgent",
    trigger_keywords=["interview", "position", "experience", "tell me about yourself"],
    trigger_context_words=["hiring", "candidate", "qualifications", "resume"],
    scoring_overrides={},
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
```

### 4.2 Client Meeting

```python
ModeConfig(
    mode_id="client_meeting",
    display_name="Client Meeting",
    description="Present to clients and stakeholders, negotiate contracts",
    icon="users",
    agent_classes=["ClientMeetingAgent"],
    default_agent="ClientMeetingAgent",
    trigger_keywords=["client", "project update", "deliverables", "timeline", "stakeholder"],
    trigger_context_words=["budget", "scope", "requirements", "feedback"],
    scoring_overrides={"persuasion": 0.20, "stakeholder_management": 0.15},
    system_prompt="You are a senior professional presenting to clients. Be confident, clear, and solution-oriented. Address concerns proactively.",
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
```

### 4.3 Mentoring

```python
ModeConfig(
    mode_id="mentoring",
    display_name="Mentoring",
    description="Guide junior engineers, provide career development advice",
    icon="graduation-cap",
    agent_classes=["MentoringAgent"],
    default_agent="MentoringAgent",
    trigger_keywords=["mentor", "guide", "career advice", "code review", "explain"],
    trigger_context_words=["junior", "learning", "growth", "best practice"],
    scoring_overrides={"teaching_clarity": 0.30, "patience": 0.15},
    system_prompt="You are a senior mentor guiding a junior engineer. Be encouraging, patient, and provide actionable advice with examples.",
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
```

### 4.4 Performance Review

```python
ModeConfig(
    mode_id="performance_review",
    display_name="Performance Review",
    description="Conduct self-assessments, present achievements, set goals",
    icon="chart-bar",
    agent_classes=["PerformanceReviewAgent"],
    default_agent="PerformanceReviewAgent",
    trigger_keywords=["performance review", "self-assessment", "achievements", "goals", "growth"],
    trigger_context_words=["quarterly", "annual", "review", "metrics", "targets"],
    scoring_overrides={"executive_presence": 0.15},
    system_prompt="You are conducting a performance review. Present achievements with data, discuss growth areas constructively, and set measurable goals.",
    response_style="professional",
    coaching_tips={
        "confidence": ["Lead with quantified achievements", "Use specific metrics and outcomes"],
        "clarity": ["Structure as: Achievements → Areas for Growth → Goals"],
        "relevance": ["Connect goals to team/company objectives", "Reference specific projects"],
    },
    required_context=["review_period"],
    ui_components=["transcript_panel", "achievement_tracker", "goalSetter"],
    default_view="achievement_tracker",
    allowed_transitions=["internal_comms"],
)
```

### 4.5 Board Presentation

```python
ModeConfig(
    mode_id="board_presentation",
    display_name="Board Presentation",
    description="Present to board of directors, provide strategic assessments",
    icon="presentation",
    agent_classes=["BoardPresentationAgent"],
    default_agent="BoardPresentationAgent",
    trigger_keywords=["board", "strategic", "executive", "quarterly review", "investors"],
    trigger_context_words=["revenue", "growth", "market", "strategy", "risk"],
    scoring_overrides={"executive_presence": 0.30, "strategic_thinking": 0.20},
    system_prompt="You are presenting to the board of directors. Be concise, data-driven, and strategic. Focus on outcomes and strategic implications.",
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
```

### 4.6 Sales

```python
ModeConfig(
    mode_id="sales",
    display_name="Sales",
    description="Pitch products, handle objections, close deals",
    icon="trending-up",
    agent_classes=["SalesAgent"],
    default_agent="SalesAgent",
    trigger_keywords=["pitch", "demo", "pricing", "proposal", "close"],
    trigger_context_words=["objection", "competitor", "value", "ROI", "contract"],
    scoring_overrides={"persuasion": 0.25, "objection_handling": 0.20},
    system_prompt="You are a sales professional. Be persuasive, handle objections gracefully, and focus on value. Always try to advance the deal.",
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
```

### 4.7 Training

```python
ModeConfig(
    mode_id="training",
    display_name="Training",
    description="Conduct new hire orientation, technical training, process documentation",
    icon="book-open",
    agent_classes=["TrainingAgent"],
    default_agent="TrainingAgent",
    trigger_keywords=["training", "onboarding", "orientation", "learn", "teach"],
    trigger_context_words=["process", "documentation", "handbook", "procedure"],
    scoring_overrides={"knowledge_transfer": 0.25, "documentation": 0.15},
    system_prompt="You are a training facilitator. Be clear, structured, and thorough. Document key points and check understanding frequently.",
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
```

### 4.8 Internal Communications

```python
ModeConfig(
    mode_id="internal_comms",
    display_name="Internal Communications",
    description="Team meetings, all-hands, project updates, decision documentation",
    icon="message-circle",
    agent_classes=["InternalCommsAgent"],
    default_agent="InternalCommsAgent",
    trigger_keywords=["team meeting", "all-hands", "standup", "retrospective", "update"],
    trigger_context_words=["decisions", "action items", "blockers", "progress"],
    scoring_overrides={},
    system_prompt="You are a team communicator. Be clear, concise, and action-oriented. Document decisions and next steps.",
    response_style="professional",
    coaching_tips={
        "clarity": ["Lead with the headline", "Separate decisions from discussions"],
        "relevance": ["Stay on agenda", "Flag off-topic items for follow-up"],
    },
    ui_components=["transcript_panel", "action_item_tracker", "decision_log"],
    default_view="action_item_tracker",
    allowed_transitions=["client_meeting", "performance_review"],
)
```

### 4.9 Customer Support

```python
ModeConfig(
    mode_id="customer_support",
    display_name="Customer Support",
    description="Handle inquiries, resolve issues, provide product training",
    icon="headphones",
    agent_classes=["CustomerSupportAgent"],
    default_agent="CustomerSupportAgent",
    trigger_keywords=["support", "issue", "bug", "help", "problem"],
    trigger_context_words=["error", "broken", "not working", "frustrated", "urgent"],
    scoring_overrides={"resolution_quality": 0.25, "empathy": 0.20},
    system_prompt="You are a customer support specialist. Be empathetic, solution-focused, and escalate when needed. Never blame the customer.",
    response_style="empathetic",
    coaching_tips={
        "empathy": ["Acknowledge the frustration first", "Use 'I understand' and 'I can help'"],
        "resolution_quality": ["Diagnose before prescribing", "Confirm the fix worked"],
        "confidence": ["Know when to escalate", "Document the issue for the team"],
    },
    ui_components=["transcript_panel", "ticket_tracker", "knowledge_base"],
    default_view="ticket_tracker",
    allowed_transitions=["training", "internal_comms"],
)
```

---

## 5. Session Engine

### 5.1 Mode-Agnostic Processing

The `SessionEngine` replaces `AutonomousInterviewEngine`. It delegates to `ModeConfig` for all mode-specific behavior.

```python
class SessionEngine:
    def __init__(self, mode: ModeConfig, ...):
        self.mode = mode
        self.agents = self._load_agents(mode.agent_classes)
        self.scorer = ModeAwareScorer(mode.scoring_overrides)
        self.coach = ModeAwareCoach(mode.coaching_tips)

    def process_audio(self, audio_data: bytes) -> Dict:
        # 1. Transcribe
        transcript = self.stt.transcribe(audio_data)

        # 2. Check trigger (if not active)
        if not self.is_active:
            if self._should_activate(transcript):
                self.is_active = True
                return self._on_enter()
            return {"action": "waiting", "mode": self.mode.mode_id}

        # 3. Route to agent
        answer = self._route_to_agent(transcript)

        # 4. Score with mode dimensions
        score = self.scorer.score(transcript, answer, audio_features)

        # 5. Get coaching tip
        tip = self.coach.get_tip(score)

        # 6. Generate response (TTS + avatar)
        response = self.response_generator.generate(answer)

        return {
            "action": "respond",
            "transcript": transcript,
            "answer": answer,
            "audio": response.audio,
            "avatar": response.avatar,
            "score": score,
            "coaching_tip": tip,
            "mode": self.mode.mode_id,
        }
```

### 5.2 Mode Transitions

```python
class SessionEngine:
    def transition_to(self, new_mode_id: str, user_role: str = None) -> bool:
        new_mode = ModeRegistry.get(new_mode_id)

        # Check permissions
        if new_mode.transition_permissions:
            if user_role not in new_mode.transition_permissions:
                raise PermissionError(f"Role '{user_role}' cannot transition to '{new_mode_id}'")

        # Check allowed transitions
        if new_mode_id not in self.mode.allowed_transitions:
            raise ValueError(f"Mode '{self.mode.mode_id}' cannot transition to '{new_mode_id}'")

        # Execute lifecycle hooks
        self._on_exit()
        self.mode = new_mode
        self.agents = self._load_agents(new_mode.agent_classes)
        self.scorer = ModeAwareScorer(new_mode.scoring_overrides)
        self.coach = ModeAwareCoach(new_mode.coaching_tips)
        self._on_enter()

        return True
```

---

## 6. Scoring: Base + Overrides

### 6.1 Base Dimensions (All Modes)

| Dimension | Weight | Description |
|-----------|--------|-------------|
| confidence | 0.30 | Voice stability, pitch variation, speech rate |
| clarity | 0.30 | Filler words, pauses, speech rate |
| relevance | 0.40 | Keyword overlap, answer length |

### 6.2 Mode-Specific Overrides

When `scoring_overrides` is non-empty, the base weights are reduced proportionally and new dimensions are added:

```python
class ModeAwareScorer:
    def score(self, question, answer, audio_features):
        base = self._base_score(audio_features)  # confidence, clarity, relevance

        if self.mode.scoring_overrides:
            # Normalize base weights to make room for overrides
            base_total = sum(base.values())
            override_total = sum(self.mode.scoring_overrides.values())
            scale = 1.0 - override_total  # e.g., 1.0 - 0.45 = 0.55

            # Scale base dimensions
            for dim in base:
                base[dim] *= scale

            # Calculate override dimensions
            for dim, weight in self.mode.scoring_overrides.items():
                base[dim] = self._calculate_dimension(dim, question, answer, audio_features) * weight

        overall = sum(base.values()) * 100
        return ScoreResult(dimensions=base, overall=overall)
```

---

## 7. Lifecycle Hooks

### 7.1 Required Context

Modes can require context data before starting:

```python
# Board Presentation requires agenda
ModeConfig(required_context=["agenda", "financial_data"])

# Sales requires product info
ModeConfig(required_context=["product_info"])
```

API flow:
```
POST /session/start with mode_id + context
→ Validate required_context is provided
→ Store context in session
→ Call on_enter_prompt
→ Return session with mode config
```

### 7.2 Enter/Exit Prompts

```python
# On mode enter
on_enter_prompt = "Board presentation mode. Focus on strategic outcomes."

# On mode exit
on_exit_prompt = "Session complete. Summary saved."
```

These are injected into the LLM system prompt at transition points.

---

## 8. API Endpoints

### 8.1 Mode Management

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/modes` | GET | List all modes with metadata |
| `/modes/{mode_id}` | GET | Get full mode configuration |
| `/modes/{mode_id}/agents` | GET | List agents for a mode |
| `/modes/{mode_id}/scoring` | GET | Get scoring config for mode |

### 8.2 Session Mode Control

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/session/mode` | GET | Get current session mode |
| `/session/mode` | POST | Set mode for current session (validates transitions) |
| `/session/context` | POST | Set required context for mode |
| `/session/transition` | POST | Transition to a new mode |

### 8.3 Response Schemas

```python
class ModeResponse(BaseModel):
    mode_id: str
    display_name: str
    description: str
    icon: str
    agent_classes: List[str]
    scoring_overrides: Dict[str, float]
    ui_components: List[str]
    allowed_transitions: List[str]

class SessionModeResponse(BaseModel):
    session_id: str
    mode: ModeResponse
    is_active: bool
    context: Dict[str, Any]

class TransitionRequest(BaseModel):
    target_mode: str
    context: Optional[Dict[str, Any]] = None
```

---

## 9. Frontend Changes

### 9.1 Mode Selection

Add to dashboard layout sidebar:
- Mode selector dropdown (all 9 modes)
- Mode-specific icon and description
- Visual indicator of current mode

### 9.2 Mode-Specific Panels

| Mode | Primary Panel | Secondary Panels |
|------|--------------|-----------------|
| Interview | Scorecard | Transcript, Coaching Tips |
| Client Meeting | Transcript | Project Timeline, Action Items |
| Mentoring | Transcript | Code Viewer, Learning Path |
| Performance Review | Achievement Tracker | Goal Setter, Transcript |
| Board Presentation | Agenda Tracker | Financial Dashboard, Transcript |
| Sales | Deal Pipeline | Objection Tracker, Transcript |
| Training | Training Outline | Quiz Panel, Transcript |
| Internal Comms | Action Item Tracker | Decision Log, Transcript |
| Customer Support | Ticket Tracker | Knowledge Base, Transcript |

### 9.3 Mode Transition UI

- Transition button (only shows allowed transitions)
- Confirmation dialog for mode switch
- Context upload for modes with `required_context`

---

## 10. Testing Strategy

### 10.1 Unit Tests

| Test File | Coverage |
|-----------|----------|
| `test_mode_registry.py` | ModeConfig creation, validation, all 9 modes |
| `test_session_engine.py` | Mode-agnostic processing, transitions, lifecycle hooks |
| `test_mode_scorer.py` | Base scoring, override scoring, dimension calculation |
| `test_mode_coach.py` | Mode-specific tips, feedback templates |
| `test_agents.py` | All 8 new agents (can_handle, generate_answer) |
| `test_mode_router.py` | API endpoints for mode management |

### 10.2 Integration Tests

| Test | Coverage |
|------|----------|
| Mode transition flow | Start → Transition → End with validation |
| Required context flow | Missing context → Error, Provided → Success |
| Agent routing per mode | Correct agent handles correct mode questions |
| Scoring with overrides | Dimensions calculated correctly with overrides |

### 10.3 Target

- **150+ new tests** across all new modules
- **Zero regressions** in existing 475 tests

---

## 11. File Summary

### New Files (20)

| File | Purpose |
|------|---------|
| `backend/apps/modes/__init__.py` | Mode module exports |
| `backend/apps/modes/registry.py` | ModeRegistry + ModeConfig + all 9 mode definitions |
| `backend/apps/modes/schemas.py` | Pydantic models for mode API |
| `backend/apps/modes/router.py` | FastAPI mode endpoints |
| `backend/apps/agents/client_meeting_agent.py` | ClientMeetingAgent |
| `backend/apps/agents/mentoring_agent.py` | MentoringAgent |
| `backend/apps/agents/performance_review_agent.py` | PerformanceReviewAgent |
| `backend/apps/agents/board_presentation_agent.py` | BoardPresentationAgent |
| `backend/apps/agents/sales_agent.py` | SalesAgent |
| `backend/apps/agents/training_agent.py` | TrainingAgent |
| `backend/apps/agents/internal_comms_agent.py` | InternalCommsAgent |
| `backend/apps/agents/customer_support_agent.py` | CustomerSupportAgent |
| `backend/apps/orchestrator/session_engine.py` | SessionEngine (replaces interview engine) |
| `backend/apps/scoring/mode_scorer.py` | ModeAwareScorer (base + overrides) |
| `backend/apps/coaching/mode_coach.py` | ModeAwareCoach (mode-specific tips) |
| `tests/backend/test_mode_registry.py` | Mode registry tests |
| `tests/backend/test_session_engine.py` | Session engine tests |
| `tests/backend/test_mode_scorer.py` | Mode-aware scorer tests |
| `tests/backend/test_new_agents.py` | All 8 new agent tests |
| `tests/backend/test_mode_api.py` | Mode API endpoint tests |

### Modified Files (5)

| File | Changes |
|------|---------|
| `backend/config/app.py` | Add modes router, update imports |
| `backend/apps/agents/__init__.py` | Export new agents |
| `backend/apps/scoring/realtime_scorer.py` | Add mode-aware scoring method |
| `backend/apps/coaching/coach.py` | Add mode-aware coaching method |
| `frontend/web/src/lib/api.ts` | Add mode API methods |

---

## 12. Migration Path

### Backward Compatibility

- The existing `AutonomousInterviewEngine` is preserved but marked as deprecated
- `SessionEngine` wraps the same underlying logic
- Existing interview tests continue to pass unchanged
- API endpoints for interview mode remain unchanged

### Rollout Order

1. **Phase 1:** ModeConfig registry + ModeAwareScorer + ModeAwareCoach (foundation)
2. **Phase 2:** 8 new agents (one at a time, test-driven)
3. **Phase 3:** SessionEngine (mode-agnostic orchestrator)
4. **Phase 4:** API endpoints + frontend mode selection
5. **Phase 5:** Auto-detection engine + integration tests

---

*Spec v1.0 — Ready for review.*
