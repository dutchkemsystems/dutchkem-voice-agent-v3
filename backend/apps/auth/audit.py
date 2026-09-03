"""Audit logging for privacy and compliance."""
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Optional


SENSITIVE_KEYS = {"photo_path", "face_embedding", "voice_recording", "audio", "password", "token"}


@dataclass
class AuditEntry:
    action: str
    user_id: str
    details: dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class AuditLogger:
    def __init__(self):
        self._entries: list[AuditEntry] = []

    def log(self, action: str, user_id: str, details: dict = None) -> AuditEntry:
        if details is None:
            details = {}
        masked = self._mask_sensitive(details)
        entry = AuditEntry(action=action, user_id=user_id, details=masked)
        self._entries.append(entry)
        return entry

    def get_entries(
        self,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        since: Optional[datetime] = None,
    ) -> list[AuditEntry]:
        result = self._entries
        if user_id is not None:
            result = [e for e in result if e.user_id == user_id]
        if action is not None:
            result = [e for e in result if e.action == action]
        if since is not None:
            result = [e for e in result if e.timestamp >= since]
        return result

    def _mask_sensitive(self, details: dict) -> dict:
        masked = {}
        for key, value in details.items():
            if key in SENSITIVE_KEYS:
                if isinstance(value, str) and ("/" in value or "\\" in value):
                    masked[key] = "[REDACTED]"
                else:
                    masked[key] = "[REDACTED]"
            else:
                masked[key] = value
        return masked
