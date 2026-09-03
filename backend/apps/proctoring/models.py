from sqlalchemy import Column, String, Float, DateTime
from sqlalchemy.sql import func
import uuid

from config.database import Base


class FaceProfile(Base):
    __tablename__ = "face_profiles"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, unique=True, index=True)
    embedding_vector = Column(String, nullable=False)
    photo_path = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
