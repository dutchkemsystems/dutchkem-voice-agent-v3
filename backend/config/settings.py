import os
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "Dutchkem Voice Agent"
    APP_VERSION: str = "3.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://dutchkem:password@localhost:5432/dutchkem_voice",
    )
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")

    JWT_SECRET: str = os.getenv(
        "JWT_SECRET", "f4bd49b39f191fc363dd29dd8d6a0aaf64e103006589eb2aec325d2510199e67"
    )
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60

    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8081"]

    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY", "default-dev-key")
    SENTRY_DSN: str = os.getenv("SENTRY_DSN", "")


settings = Settings()
