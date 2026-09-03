# DutchKem Voice Agent V3

AI-powered voice agent platform with voice cloning, speech-to-text, face recognition, and real-time monitoring capabilities.

## Architecture

```
dutchkem-voice-agent-v3/
├── backend/              # Django REST API + FastAPI AI services
│   ├── apps/            # Application modules
│   │   ├── auth/        # Authentication & authorization
│   │   ├── documents/   # Document management
│   │   ├── profiles/    # User profiles
│   │   ├── voice/       # Voice processing (TTS/STT/Clone)
│   │   ├── background/  # Background monitoring
│   │   ├── interview/   # Interview agents
│   │   ├── deepfake/    # Deepfake detection
│   │   ├── scoring/     # AI scoring
│   │   ├── proctoring/  # Proctoring system
│   │   ├── coaching/    # Coaching features
│   │   ├── analytics/   # Analytics & reporting
│   │   └── orchestrator/ # Service orchestration
│   ├── config/          # Django settings
│   └── requirements/    # Python dependencies
├── frontend/
│   ├── web/             # Next.js web application
│   ├── mobile/          # React Native Expo mobile app
│   └── desktop/         # Electron desktop app
├── docs/                # Documentation
├── tests/               # Test suites
└── docker-compose.yml   # Service orchestration
```

## Tech Stack

- **Backend**: Django REST Framework + FastAPI
- **Database**: PostgreSQL + MongoDB + Redis
- **AI/ML**: Chatterbox (Voice Cloning), faster-whisper (STT), InsightFace (Face Recognition)
- **Frontend**: Next.js (Web), React Native Expo (Mobile), Electron (Desktop)
- **Containerization**: Docker & Docker Compose

## Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- NVIDIA GPU (recommended for AI features)

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd dutchkem-voice-agent-v3

# Copy environment files
cp backend/.env.example backend/.env
cp frontend/web/.env.example frontend/web/.env.local
```

### 2. Start Infrastructure

```bash
# Start PostgreSQL, MongoDB, and Redis
docker-compose up -d postgres mongodb redis

# Verify services
docker-compose ps
```

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements/dev.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

### 4. Frontend Web Setup

```bash
cd frontend/web

# Install dependencies
npm install

# Start development server
npm run dev
```

### 5. Frontend Mobile Setup

```bash
cd frontend/mobile

# Install dependencies
npm install

# Start Expo development server
npx expo start
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `POST /api/auth/login/` | User authentication |
| `POST /api/auth/register/` | User registration |
| `GET /api/voice/clone/` | Voice cloning |
| `POST /api/voice/transcribe/` | Speech-to-text |
| `POST /api/voice/synthesize/` | Text-to-speech |
| `POST /api/deepfake/detect/` | Deepfake detection |
| `GET /api/background/monitor/` | Background monitoring |
| `POST /api/interview/start/` | Start interview session |
| `GET /api/analytics/dashboard/` | Analytics dashboard |

## Development

### Code Quality

```bash
# Backend
cd backend
black .
ruff check .
mypy .

# Frontend
cd frontend/web
npm run lint
npm run type-check
```

### Testing

```bash
# Backend tests
cd backend
pytest
pytest --cov=apps --cov-report=html

# Frontend tests
cd frontend/web
npm test
npm run test:e2e
```

## Docker Deployment

```bash
# Build and start all services
docker-compose up -d --build

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

## Environment Variables

See `backend/.env.example` and `frontend/web/.env.local.example` for required configuration.

## License

Proprietary - DutchKem Ventures
