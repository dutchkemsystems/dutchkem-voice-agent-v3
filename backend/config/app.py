from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from config.settings import settings
from config.database import init_db, check_db_health, check_redis_health, check_mongodb_health
from apps.auth.router import router as auth_router
from apps.proctoring.router import router as proctoring_router
from apps.voice.router import router as voice_router
from apps.coaching.router import router as coaching_router
from apps.modes.router import router as modes_router
from apps.scoring.router import router as scoring_router
from apps.deepfake.router import router as deepfake_router
from apps.background.router import router as background_router
from apps.orchestrator.router import router as orchestrator_router
from apps.analytics.router import router as analytics_router
from apps.admin.router import router as admin_router
from apps.docs.router import router as docs_router
from apps.healer.router import router as healer_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(proctoring_router)
app.include_router(voice_router)
app.include_router(coaching_router)
app.include_router(modes_router)
app.include_router(scoring_router)
app.include_router(deepfake_router)
app.include_router(background_router)
app.include_router(orchestrator_router)
app.include_router(analytics_router)
app.include_router(admin_router)
app.include_router(docs_router)
app.include_router(healer_router)


@app.get("/health")
async def health_check():
    db_ok = await check_db_health()
    redis_ok = await check_redis_health()
    mongo_ok = await check_mongodb_health()

    all_healthy = db_ok and redis_ok and mongo_ok

    return {
        "status": "healthy" if all_healthy else "degraded",
        "version": settings.APP_VERSION,
        "services": {
            "database": "connected" if db_ok else "disconnected",
            "redis": "connected" if redis_ok else "disconnected",
            "mongodb": "connected" if mongo_ok else "disconnected",
        },
    }
