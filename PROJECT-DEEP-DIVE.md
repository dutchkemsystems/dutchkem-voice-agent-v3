# Dutchkem Ventures Voice Agent V3 — Deep Dive Report

**Date:** 2026-09-20
**Total files:** ~220 source files (152 Python backend, 52 TS/TSX frontend, ~27 test files)

---

## 1. Architecture Overview

**Stack:** FastAPI (Python) + Next.js (React) + React Native Expo (Mobile) + Electron (Desktop)
**Orchestration:** Docker Compose (dev) / Render (prod) / Vercel (frontend) / Koyeb (backend)
**Databases:** PostgreSQL (asyncpg) + MongoDB (motor) + Redis (aioredis)
**AI/ML:** Chatterbox (voice cloning), Kokoro (TTS), faster-whisper/Vosk (STT), InsightFace (face), Ollama (LLM)

### Backend Apps (15+)
| App | Purpose | Files |
|-----|---------|-------|
| `auth` | JWT auth, encryption, rate limiting, audit | 12 files |
| `voice` | TTS/STT, Chatterbox, Kokoro, F5-TTS | 8 files |
| `orchestrator` | LLM, prompt templates, session engine | 4+ files |
| `interview` | Autonomous engine, 13 agents, adaptive difficulty | 15+ files |
| `deepfake` | Voice + video deepfake detection (numpy-only) | 5 files |
| `background` | Audio/video/face/trigger monitors, service manager | 13 files |
| `coaching` | Mode-aware coach, feedback generator | 5 files |
| `scoring` | Mode-aware scorer, realtime scorer | 3 files |
| `modes` | Mode registry, mode config, mode router | 3 files |
| `analytics` | Skill gap analyzer, performance metrics | 3 files |
| `proctoring` | Face registration, liveness detection | 3 files |
| `healer` | Auto-diagnostics, healing reports | 3 files |
| `admin` | Minimal admin dashboard (1 HTML page) | 1 file |
| `documents` | Document management (stub) | 1 file |
| `profiles` | User profiles (stub) | 1 file |

### Frontend Apps
| App | Stack | Files |
|-----|-------|-------|
| `frontend/web` | Next.js 16.3.4, React 19.2.8, Tailwind 4 | ~30 TS/TSX |
| `frontend/mobile` | React Native Expo ~57, expo-av, expo-camera | ~22 TS/TSX |
| `frontend/desktop` | Electron 33, electron-builder 25 | 2 files (package.json + config only) |

---

## 2. AI/ML Pipeline

### Voice Pipeline
```
User Audio → STTService (faster-whisper GPU → Vosk CPU fallback)
         → AutonomousInterviewEngine (category routing)
         → Agent (HR/Technical/Coding/Managerial/etc.)
         → TTS (Chatterbox voice cloning OR Kokoro accent TTS)
         → Audio Output
```

**ChatterboxEngine:** Voice cloning with GPU/CPU detection, model caching
**KokoroEngine:** Accent-based TTS — supports Nigerian, Ghanaian, UK, US, Japanese accents with phoneme mapping
**F5TTS:** Alternative TTS engine (registered but not primary)
**STTService:** faster-whisper (GPU) with Vosk (CPU) fallback, auto-detects CUDA availability

### LLM Pipeline
```
InterviewEngine → LLMService → OllamaClient (httpx, 120s timeout)
                               → llama3.1:8b (primary)
                               → llama3.2:3b (fallback)
                               → Redis caching (LRU in-memory + Redis TTL)
```

**PromptTemplates:** HR (STAR method), Technical (system design + code review), Scenario (behavioral), Coding (algorithm + debugging)

### Deepfake Detection
```
Audio → VoiceDeepfakeDetector (spectral FFT, prosody, breathing analysis)
Video → VideoDeepfakeDetector (temporal consistency, edge artifacts)
     → DeepfakeDetector (combines both, threshold-based)
```
No ML models — pure numpy/signal processing. Hardcoded thresholds.

---

## 3. Background Monitoring System

13 files in `backend/apps/background/`:

| Monitor | Mechanism | Status |
|---------|-----------|--------|
| `audio_monitor` | WebRTC VAD + energy fallback | Functional |
| `video_monitor` | OpenCV (cv2) + numpy fallback | Functional |
| `face_tracker` | MediaPipe with fallback | Functional |
| `voice_biometrics` | Spectral FFT embeddings, cosine similarity | Functional |
| `keyword_matcher` | Keyword set matching | Functional |
| `noise_filter` | Audio filtering | Functional |
| `process_monitor` | System process monitoring | Functional |
| `context_analyzer` | Question/formal indicators | Functional |
| `trigger_detector` | Combined keyword+context scoring, InterviewPhase state machine | Functional |
| `service_manager` | Coordinates all monitors, 3 perf modes, battery warnings | Functional |

**TriggerDetector State Machine:**
```
IDLE → DETECTING (keyword score > 0.3) → ACTIVE (context confirms, 5+ frames)
    → ENDING (silence/noise > 30s) → IDLE
```

**Performance Modes:** battery-saver / normal / high-performance (adjusts monitor intervals)

---

## 4. Interview System

### AutonomousInterviewEngine
- Category routing via `_CATEGORY_KEYWORDS` dict (hr, technical, coding, managerial, etc.)
- Adaptive difficulty: Easy ↔ Medium ↔ Hard based on confidence (0.75 promote, 0.45 demote) and response time (2.5s promote, 4.0s demote)
- Minimum 3 responses before difficulty adjustment
- Follow-up question generation

### Interview Agents (13 total)
| Agent | can_handle Keywords | Confidence |
|-------|-------------------|------------|
| HRAgent | hr, hiring, recruitment, interview, resume, cv, job | 0.85 |
| ManagerAgent | management, leadership, team, project, deadline | 0.85 |
| TechnicalAgent | technical, architecture, system design, database | 0.85 |
| CodingAgent | coding, algorithm, data structure, debug, code | 0.85 |
| ClientMeetingAgent | client, meeting, presentation, stakeholder | 0.80 |
| MentoringAgent | mentor, coaching, guidance, career, growth | 0.80 |
| PerformanceReviewAgent | performance, review, evaluation, feedback | 0.80 |
| BoardPresentationAgent | board, executive, strategy, vision | 0.80 |
| SalesAgent | sales, revenue, pipeline, deal, customer | 0.80 |
| TrainingAgent | training, workshop, learning, development | 0.80 |
| InternalCommsAgent | communication, email, memo, announcement | 0.80 |
| CustomerSupportAgent | support, ticket, complaint, service | 0.80 |
| BaseInterviewAgent | Abstract base — can_handle + generate_answer | — |

**Wiring gap:** Only 4 of 13 agents are registered in `InterviewOrchestrator`: HRAgent, ManagerAgent, TechnicalAgent, CodingAgent. The other 9 exist but are not routed to.

---

## 5. Mode System

**9 modes registered:** hr, technical, coding, managerial, client_meeting, mentoring, performance_review, board_presentation, sales

**ModeConfig dataclass:**
```python
mode_id: str
agent_classes: List[str]
scoring_overrides: Dict  # per-dimension weight overrides
coaching_tips: Dict      # mode-specific tips per dimension
feedback_templates: Dict # mode-specific feedback templates
trigger_keywords: List[str]
transitions: List[str]   # allowed mode transitions
```

**ModeAwareScorer:** Base dimensions (confidence, clarity, relevance) + mode-specific overrides. Weighted overall score.
**ModeAwareCoach:** Mode-specific tips per weakest dimension. Balanced feedback with strengths/improvements.
**ModeRouter:** Validates mode transitions, manages current mode state.

---

## 6. Frontend Architecture

### Web (Next.js 16.3.4)
- **Pages:** `/` (landing), `/login`, `/register`, `/dashboard`, `/profile`, `/interview`, `/deepfake`
- **Components:** AnimatedBackground, GradientHeader, GlassCard, GradientButton, ColourfulNav + shadcn/ui (button, card, input, badge, alert, label)
- **Auth:** Bearer token from localStorage, auto-redirect on 401/403
- **API lib:** Typed interfaces (User, TokenResponse, DashboardStats), fetch wrapper with auth headers

### Mobile (React Native Expo ~57)
- **Screens:** Login, Register, Home, Profile, Interview, FaceRegistration, VoiceClone
- **Services:** voiceService, notificationService, faceService, backgroundMonitor, authService, apiClient
- **Navigation:** Bottom tabs + native stack (AppNavigator)
- **Tests:** 8 test files (6 services + 2 components)

### Desktop (Electron 33)
- **Minimal:** Only `package.json` + `electron-builder.json5`. No main process code, no renderer. Build config exists but no implementation.

---

## 7. Deployment Topology

### Docker Compose (Development)
```
postgres:15-alpine  ←→  mongodb:7      ←→  redis:7-alpine
                          ↑                    ↑
                    backend (FastAPI)    frontend-web (Next.js)
                    4 workers (gunicorn)  dev server
```

### Production
- **Backend:** Render (auto-deploy from Git, 4 gunicorn workers)
- **Frontend Web:** Vercel (auto-deploy)
- **Mobile:** Expo Build (EAS)
- **Desktop:** electron-builder (pending)

### Render Config
- Build: `pip install -r backend/requirements/production.txt`
- Start: `cd backend && gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker`
- Health check: `/health`

---

## 8. Test Coverage

### Test Files (27 total)
| Location | Count | Focus |
|----------|-------|-------|
| `tests/backend/` | 7 | Mode system (registry, scorer, coach, API, integration), new agents, session engine |
| `backend/tests/backend/` | 19 | Health, face, docs, deepfake, coaching, auth, audio_monitor, agents, admin, STT, service_manager, security, scoring, LLM, interview_engine, video_monitor, TTS, trigger, voice |
| `backend/tests/e2e/` | 1 | Full flow end-to-end |

### Coverage Gaps
- **No frontend tests** for web (Next.js pages)
- **Mobile tests exist** but only for services/components (8 files)
- **Desktop:** Zero tests
- **Background monitors:** Only audio_monitor, video_monitor, trigger, service_manager tested
- **No integration tests** for voice pipeline (STT → LLM → TTS)
- **No load/stress tests**

---

## 9. Code Quality

### Strengths
- Consistent FastAPI patterns (routers, services, schemas separation)
- Type hints throughout Python codebase
- Abstract base classes for interview agents (ABC with can_handle/generate_answer)
- Mode system provides clean extensibility
- Background monitors have fallback chains (GPU → CPU, MediaPipe → OpenCV)

### Weaknesses
- **9 of 13 interview agents not wired** into orchestrator (dead code)
- **Placeholder implementations:** LivenessDetector returns hardcoded values (EAR=0.3, head_movement=0.2, texture_score=0.7)
- **Hardcoded confidence scores** in all agents (0.80-0.85, never varies)
- **Hardcoded follow-up questions** per agent (no dynamic generation)
- **Duplicate scoring logic:** ModeAwareScorer + RealtimeScorer with different weight schemes
- **Desktop app is empty** (Electron config exists, no code)
- **Admin dashboard is a single HTML page** (no React, no real admin functionality)
- **No rate limiting on voice endpoints** (STT/TTS are expensive GPU operations)
- **models.py files are mostly empty** (stub files)

### Security Concerns
- `.env.example` has `changeme` defaults for SECRET_KEY, JWT_SECRET, POSTGRES_PASSWORD
- No HTTPS enforcement in dev config
- Voice biometrics stored as numpy arrays (no encryption at rest mentioned)
- Deepfake detection thresholds are hardcoded (not configurable per deployment)

---

## 10. File Counts & Metrics

| Category | Count | LOC (approx) |
|----------|-------|---------------|
| Backend Python (apps) | ~100 files | ~8,000 |
| Backend Python (config) | ~8 files | ~500 |
| Backend Python (tests) | ~27 files | ~3,000 |
| Frontend Web (TS/TSX) | ~30 files | ~2,500 |
| Frontend Mobile (TS/TSX) | ~22 files | ~2,000 |
| Frontend Desktop | 2 files | ~50 |
| Docker/Config | ~10 files | ~300 |
| **Total** | **~200 files** | **~16,000 LOC** |

### Key Ratios
- **Python:TypeScript** ≈ 3:1
- **Test:Code** ≈ 1:5 (low)
- **Apps:Tests** = 15 apps, 27 test files (1.8 tests/app avg)
- **Agents:Wired** = 13 agents, 4 wired (31% utilization)
