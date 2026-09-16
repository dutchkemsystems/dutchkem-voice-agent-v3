from sqlalchemy import Column, String, Float, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from datetime import datetime, timezone
import uuid

from config.database import Base


class VoiceProfile(Base):
    __tablename__ = "voice_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    name = Column(String(255), default="")
    reference_audio_path = Column(Text, nullable=False)
    embedding = Column(ARRAY(Float), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "profile_id": str(self.id),
            "user_id": str(self.user_id),
            "name": self.name,
            "reference_audio_path": self.reference_audio_path,
            "embedding": self.embedding,
            "created_at": self.created_at.isoformat() if self.created_at else "",
        }
