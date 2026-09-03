"""Data minimization and privacy controls."""
import hashlib
from typing import Any


PURPOSE_FIELDS = {
    "transcript": {"transcript", "user_id"},
    "export": {"user_id", "name", "email", "transcript"},
    "audit": {"user_id", "timestamp", "action"},
}

STRIP_FIELDS = {
    "metadata",
    "face_embedding",
    "voice_recording",
    "audio",
    "internal_note",
}


class DataMinimizationService:
    def minimize(self, data: dict, purpose: str = "general") -> dict:
        allowed = PURPOSE_FIELDS.get(purpose)
        result = {}
        for key, value in data.items():
            if key in STRIP_FIELDS:
                continue
            if allowed is not None and key not in allowed:
                continue
            result[key] = value
        return result

    def export_user_data(self, user_data: dict) -> dict:
        sensitive = {"face_embedding", "voice_recording", "audio", "photo_path"}
        return {k: v for k, v in user_data.items() if k not in sensitive}

    def delete_user_data(self, user_id: str) -> dict:
        return {"deleted": True, "user_id": user_id}

    def anonymize(self, data: dict) -> dict:
        result = {}
        for key, value in data.items():
            if key == "user_id":
                result[key] = hashlib.sha256(str(value).encode()).hexdigest()[:12]
            elif key == "email":
                continue
            else:
                result[key] = value
        return result
