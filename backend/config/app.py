from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.settings import settings
from apps.voice.router import router as voice_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(voice_router)


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "version": settings.APP_VERSION,
        "services": {
            "database": "connected",
            "redis": "connected",
            "mongodb": "connected",
        },
    }
