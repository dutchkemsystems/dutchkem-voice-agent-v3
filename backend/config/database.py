from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from motor.motor_asyncio import AsyncIOMotorClient
import redis.asyncio as aioredis
import os


class Base(DeclarativeBase):
    pass

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://dutchkem:password@localhost:5432/dutchkem_voice")
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# PostgreSQL
engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# MongoDB
mongo_client = AsyncIOMotorClient(MONGODB_URL)
mongodb = mongo_client.dutchkem_voice

# Redis
redis_client = aioredis.from_url(REDIS_URL, decode_responses=True)

async def get_db():
    async with async_session() as session:
        yield session

async def get_redis():
    return redis_client
