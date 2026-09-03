from sqlalchemy import Column, String, DateTime, Boolean, LargeBinary
from datetime import datetime, timezone

from config.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    voice_profile_id = Column(String, nullable=True)
    face_embedding = Column(LargeBinary, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
