import os
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import async_session
from apps.voice.models import VoiceProfile

logger = logging.getLogger(__name__)

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "uploads", "voice")
os.makedirs(UPLOAD_DIR, exist_ok=True)


class VoiceService:
    """Voice cloning service with PostgreSQL-backed profile storage."""

    async def create_profile(
        self,
        user_id: str,
        audio_data: bytes,
        name: str = "",
    ) -> str:
        profile_id = str(uuid.uuid4())

        audio_filename = f"{profile_id}.wav"
        audio_path = os.path.join(UPLOAD_DIR, audio_filename)
        with open(audio_path, "wb") as f:
            f.write(audio_data)

        async with async_session() as db:
            profile = VoiceProfile(
                id=uuid.UUID(profile_id),
                user_id=uuid.UUID(user_id) if len(user_id) == 36 else user_id,
                name=name,
                reference_audio_path=audio_path,
            )
            db.add(profile)
            await db.commit()

        logger.info("Created voice profile %s for user %s", profile_id, user_id)
        return profile_id

    async def get_profile(self, profile_id: str) -> Optional[dict]:
        async with async_session() as db:
            result = await db.execute(
                select(VoiceProfile).where(VoiceProfile.id == profile_id)
            )
            profile = result.scalars().first()
            if profile:
                return profile.to_dict()
        return None

    async def list_profiles(self, user_id: Optional[str] = None) -> list[dict]:
        async with async_session() as db:
            query = select(VoiceProfile)
            if user_id:
                query = query.where(VoiceProfile.user_id == user_id)
            result = await db.execute(query)
            profiles = result.scalars().all()
            return [p.to_dict() for p in profiles]

    async def delete_profile(self, profile_id: str) -> bool:
        async with async_session() as db:
            result = await db.execute(
                delete(VoiceProfile).where(VoiceProfile.id == profile_id)
            )
            await db.commit()
            return result.rowcount > 0

    async def synthesize(
        self,
        text: str,
        profile_id: str,
        exaggeration: float = 0.5,
    ) -> bytes:
        profile = await self.get_profile(profile_id)
        if not profile:
            raise ValueError(f"Voice profile {profile_id} not found")

        from apps.voice.chatterbox_engine import ChatterboxEngine

        engine = ChatterboxEngine()
        return engine.clone_and_synthesize(
            text=text,
            reference_audio_path=profile["reference_audio_path"],
            exaggeration=exaggeration,
        )


voice_service = VoiceService()
