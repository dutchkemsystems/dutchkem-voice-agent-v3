import os
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "uploads", "voice")
os.makedirs(UPLOAD_DIR, exist_ok=True)


class VoiceService:
    """Voice cloning service that manages profiles and synthesis.

    In-memory profile storage for now; database integration in follow-up tasks.
    """

    def __init__(self):
        self._profiles: dict[str, dict] = {}

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

        profile = {
            "profile_id": profile_id,
            "user_id": user_id,
            "name": name,
            "reference_audio_path": audio_path,
            "embedding": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self._profiles[profile_id] = profile
        logger.info("Created voice profile %s for user %s", profile_id, user_id)
        return profile_id

    async def get_profile(self, profile_id: str) -> Optional[dict]:
        return self._profiles.get(profile_id)

    async def list_profiles(self, user_id: Optional[str] = None) -> list[dict]:
        profiles = list(self._profiles.values())
        if user_id:
            profiles = [p for p in profiles if p["user_id"] == user_id]
        return profiles

    async def synthesize(
        self,
        text: str,
        profile_id: str,
        exaggeration: float = 0.5,
    ) -> bytes:
        profile = self._profiles.get(profile_id)
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
