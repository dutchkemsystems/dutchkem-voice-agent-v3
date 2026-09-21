# DutchKem Voice Agent V3 — Onboarding Guide

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.14.2+ | Backend runtime |
| Node.js | 20+ | Frontend runtime |
| pnpm | 9+ | Frontend package manager |
| Docker | 24+ | Containerization |
| Docker Compose | v2 | Multi-service orchestration |
| Git | 2.40+ | Version control |

## 1. Clone & Environment Setup

```bash
git clone <repo-url>
cd dutchkem-voice-agent-v3

# Copy env file
cp .env.example .env
```

Edit `.env` and set **at minimum**:
```
POSTGRES_PASSWORD=<secure-password>
SECRET_KEY=<random-64-char-string>
JWT_SECRET=<random-64-char-string>
```

## 2. Backend Setup

```bash
cd backend

# Create venv
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install deps (dev)
pip install -r requirements/dev.txt
# OR production:
pip install -r requirements/production.txt
```

### Run Backend Locally

```bash
uvicorn config.app:app --reload --host 0.0.0.0 --port 8000
```

Requires PostgreSQL, MongoDB, Redis running (use Docker Compose for these):

```bash
# From project root — start only data services
docker compose up -d postgres mongodb redis
```

### Verify Backend

```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy","version":"3.0.0","services":{...}}
```

## 3. Frontend Setup (Web)

```bash
cd frontend/web
pnpm install
pnpm dev
```

Opens at `http://localhost:3000`. Points to backend at `http://localhost:8000`.

## 4. Mobile Setup (React Native Expo)

```bash
cd frontend/mobile
npm install
npx expo start
```

Scan QR code with Expo Go on your device.

## 5. Desktop Setup (Electron)

```bash
cd frontend/desktop
npm install
npm start
```

## 6. Docker (Full Stack)

```bash
# From project root
docker compose up -d --build

# Services:
#   - PostgreSQL:  localhost:5432
#   - MongoDB:     localhost:27017
#   - Redis:       localhost:6379
#   - Backend:     localhost:8000
#   - Frontend:    localhost:3000
```

## 7. Running Tests

```bash
cd backend

# Run all tests
pytest tests/backend/ -v --tb=short

# Run specific test file
pytest tests/backend/test_auth.py -v
```

**Note**: The test suite uses `conftest.py` that imports `from config app` at module level — this triggers service initialization. Tests mock external dependencies.

## 8. Git Workflow

| Branch | Purpose |
|--------|---------|
| `main` | Production-ready code |
| `develop` | Integration branch |
| `feature/*` | New features |
| `fix/*` | Bug fixes |
| `chore/*` | Maintenance tasks |

**Commit convention**: `<type>: <description>`
- Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`, `ci`

## 9. API Documentation

When running locally with `DEBUG=true`:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI spec: `docs/openapi.json`

## 10. Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `POSTGRES_PASSWORD` | Yes | — | PostgreSQL password |
| `SECRET_KEY` | Yes | — | Application secret key |
| `JWT_SECRET` | Yes | — | JWT signing secret |
| `DEBUG` | No | `false` | Enable debug mode |
| `DATABASE_URL` | No | `postgresql+asyncpg://dutchkem:password@localhost:5432/dutchkem_voice` | PostgreSQL connection string |
| `MONGODB_URL` | No | `mongodb://localhost:27017` | MongoDB connection string |
| `REDIS_URL` | No | `redis://localhost:6379` | Redis connection string |
| `SENTRY_DSN` | No | — | Sentry error tracking DSN |
| `GPU_ENABLED` | No | `true` | Enable GPU for ML inference |
| `MODEL_CACHE_DIR` | No | `./models` | ML model cache directory |
