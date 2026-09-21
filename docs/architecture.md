# DutchKem Voice Agent V3 — Architecture

## System Overview

```mermaid
graph TB
    subgraph "Client Layer"
        WEB["Next.js 16 Web<br/>Port 3000"]
        MOB["React Native Expo<br/>Mobile App"]
        DESK["Electron<br/>Desktop App"]
    end

    subgraph "API Gateway"
        BE["FastAPI Backend<br/>Port 8000<br/>15 Apps"]
        HEALTH["GET /health"]
        METRICS["GET /metrics"]
    end

    subgraph "Data Layer"
        PG[("PostgreSQL 16<br/>Primary DB")]
        MONGO[("MongoDB 7<br/>Document Store")]
        REDIS[("Redis 7<br/>Cache / Queue")]
    end

    subgraph "AI / ML Services"
        TTS["Text-to-Speech"]
        STT["Speech-to-Text"]
        LLM["LLM Service"]
        DEEPFAKE["Deepfake Detection"]
    end

    subgraph "Infrastructure"
        DOCKER["Docker Compose"]
        GHA["GitHub Actions CI"]
        SENTRY["Sentry (optional)"]
    end

    WEB --> BE
    MOB --> BE
    DESK --> BE
    BE --> PG
    BE --> MONGO
    BE --> REDIS
    BE --> TTS
    BE --> STT
    BE --> LLM
    BE --> DEEPFAKE
    DOCKER -.-> BE
    DOCKER -.-> PG
    DOCKER -.-> MONGO
    DOCKER -.-> REDIS
    BE -.-> SENTRY
    BE --> HEALTH
    BE --> METRICS
```

## Backend Apps (`backend/apps/`)

| App | Purpose |
|-----|---------|
| `auth` | JWT authentication, user registration/login |
| `voice` | Voice recording, TTS/STT integration |
| `interview` | Interview session management, question flow |
| `proctoring` | Proctoring rules, face/audio monitoring |
| `coaching` | Real-time coaching feedback |
| `scoring` | Response scoring and evaluation |
| `deepfake` | Deepfake detection on video/audio |
| `modes` | Interview mode configuration |
| `orchestrator` | Multi-service orchestration |
| `analytics` | Usage analytics and reporting |
| `admin` | Admin dashboard endpoints |
| `docs` | API documentation |
| `healer` | System health healing automation |
| `background` | Background task processing |
| `llmlite` | Lightweight LLM inference |

## Data Flow — Interview Session

```mermaid
sequenceDiagram
    participant C as Client
    participant BE as FastAPI
    participant V as Voice Service
    participant I as Interview Engine
    participant S as Scoring
    participant DB as PostgreSQL

    C->>BE: POST /interview/start
    BE->>DB: Create session
    BE-->>C: {session_id}
    
    loop Each Question
        C->>BE: POST /voice/speak
        BE->>V: TTS generation
        V-->>C: Audio response
        C->>BE: POST /voice/listen
        BE->>V: STT transcription
        V-->>C: Transcription
        C->>BE: POST /interview/answer
        BE->>S: Score response
        BE->>DB: Store result
        S-->>C: Score + feedback
    end
    
    C->>BE: POST /interview/finish
    BE->>DB: Finalize session
    BE-->>C: Session summary
```

## Frontend Architecture

```
frontend/
├── web/          # Next.js 16 (App Router, pnpm, TypeScript)
├── mobile/       # React Native Expo (TypeScript)
└── desktop/      # Electron (wraps web build)
```

## Infrastructure

- **Containerization**: Docker Compose (PostgreSQL, MongoDB, Redis, backend, frontend)
- **CI/CD**: GitHub Actions — lint, test, Docker build on push/PR
- **Monitoring**: Sentry integration, Prometheus `/metrics` endpoint
- **Deployment**: Render, Koyeb, Vercel (web), Railway (backend)
