"""Tests for Privacy & Security: encryption, audit logging, data minimization."""
import os
import tempfile
import time
from datetime import datetime, timedelta, timezone

import pytest

from apps.auth.encryption import EncryptionService
from apps.auth.audit import AuditLogger, AuditEntry
from apps.auth.data_minimization import DataMinimizationService


# ──────────────────────────────────────────────
# EncryptionService
# ──────────────────────────────────────────────


class TestEncryptionService:
    def test_encrypt_decrypt_roundtrip(self):
        svc = EncryptionService(password="test-password")
        plaintext = b"Hello, Dutchkem Voice Agent!"
        encrypted = svc.encrypt(plaintext)
        assert encrypted != plaintext
        decrypted = svc.decrypt(encrypted)
        assert decrypted == plaintext

    def test_different_passwords_produce_different_ciphertext(self):
        svc_a = EncryptionService(password="password-a")
        svc_b = EncryptionService(password="password-b")
        data = b"same data"
        enc_a = svc_a.encrypt(data)
        enc_b = svc_b.encrypt(data)
        assert enc_a != enc_b

    def test_wrong_password_fails_decryption(self):
        svc = EncryptionService(password="correct-password")
        encrypted = svc.encrypt(b"secret data")
        wrong_svc = EncryptionService(password="wrong-password")
        with pytest.raises(Exception):
            wrong_svc.decrypt(encrypted)

    def test_encrypt_file(self):
        svc = EncryptionService(password="file-test")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
            tmp.write(b"file content to encrypt")
            input_path = tmp.name
        output_path = input_path + ".enc"
        try:
            svc.encrypt_file(input_path, output_path)
            assert os.path.exists(output_path)
            with open(output_path, "rb") as f:
                encrypted = f.read()
            assert encrypted != b"file content to encrypt"
            decrypted = svc.decrypt(encrypted)
            assert decrypted == b"file content to encrypt"
        finally:
            os.unlink(input_path)
            os.unlink(output_path)

    def test_empty_data(self):
        svc = EncryptionService(password="empty-test")
        encrypted = svc.encrypt(b"")
        decrypted = svc.decrypt(encrypted)
        assert decrypted == b""

    def test_large_data(self):
        svc = EncryptionService(password="large-test")
        data = os.urandom(1024 * 1024)  # 1 MB
        encrypted = svc.encrypt(data)
        decrypted = svc.decrypt(encrypted)
        assert decrypted == data


# ──────────────────────────────────────────────
# AuditLogger
# ──────────────────────────────────────────────


class TestAuditLogger:
    def test_log_entry_created(self):
        logger = AuditLogger()
        entry = logger.log(
            action="voice_data.uploaded",
            user_id="user-123",
            details={"file_size": 1024, "format": "wav"},
        )
        assert isinstance(entry, AuditEntry)
        assert entry.action == "voice_data.uploaded"
        assert entry.user_id == "user-123"
        assert entry.timestamp is not None

    def test_log_entries_persisted(self):
        logger = AuditLogger()
        logger.log(action="action.one", user_id="u1", details={})
        logger.log(action="action.two", user_id="u2", details={})
        entries = logger.get_entries()
        assert len(entries) == 2

    def test_filter_entries_by_user(self):
        logger = AuditLogger()
        logger.log(action="a", user_id="user-a", details={})
        logger.log(action="b", user_id="user-b", details={})
        logger.log(action="c", user_id="user-a", details={})
        entries_a = logger.get_entries(user_id="user-a")
        assert len(entries_a) == 2
        entries_b = logger.get_entries(user_id="user-b")
        assert len(entries_b) == 1

    def test_filter_entries_by_action(self):
        logger = AuditLogger()
        logger.log(action="upload", user_id="u1", details={})
        logger.log(action="delete", user_id="u1", details={})
        logger.log(action="upload", user_id="u2", details={})
        uploads = logger.get_entries(action="upload")
        assert len(uploads) == 2

    def test_filter_entries_by_time_range(self):
        logger = AuditLogger()
        logger.log(action="old", user_id="u1", details={})
        time.sleep(0.05)
        cutoff = datetime.now(timezone.utc)
        time.sleep(0.05)
        logger.log(action="new", user_id="u1", details={})
        recent = logger.get_entries(since=cutoff)
        assert len(recent) == 1
        assert recent[0].action == "new"

    def test_log_with_sensitive_data_masked(self):
        logger = AuditLogger()
        entry = logger.log(
            action="face.verify",
            user_id="u1",
            details={"photo_path": "/data/photos/user1.jpg"},
        )
        assert entry.details.get("photo_path") != "/data/photos/user1.jpg"


# ──────────────────────────────────────────────
# DataMinimizationService
# ──────────────────────────────────────────────


class TestDataMinimization:
    def test_strip_voice_metadata(self):
        svc = DataMinimizationService()
        data = {
            "audio": b"audio-bytes",
            "transcript": "hello world",
            "metadata": {
                "recording_device": "Blue Yeti",
                "location": "Amsterdam",
                "os": "macOS 14",
            },
            "user_id": "u1",
        }
        minimized = svc.minimize(data, purpose="transcription")
        assert minimized["transcript"] == "hello world"
        assert minimized["user_id"] == "u1"
        assert "metadata" not in minimized

    def test_strip_face_embeddings_from_export(self):
        svc = DataMinimizationService()
        data = {
            "user_id": "u1",
            "face_embedding": [0.1, 0.2, 0.3],
            "name": "John",
            "email": "john@example.com",
        }
        minimized = svc.minimize(data, purpose="export")
        assert "face_embedding" not in minimized
        assert minimized["name"] == "John"

    def test_retain_required_fields(self):
        svc = DataMinimizationService()
        data = {
            "user_id": "u1",
            "internal_note": "debug info",
            "session_id": "s1",
            "timestamp": "2026-01-01",
        }
        minimized = svc.minimize(data, purpose="audit")
        assert minimized["user_id"] == "u1"
        assert minimized["timestamp"] == "2026-01-01"
        assert "internal_note" not in minimized

    def test_export_user_data(self):
        svc = DataMinimizationService()
        user_data = {
            "user_id": "u1",
            "name": "Jane",
            "face_embedding": [0.1],
            "voice_recording": b"data",
            "transcript": "hello",
        }
        exported = svc.export_user_data(user_data)
        assert exported["user_id"] == "u1"
        assert exported["name"] == "Jane"
        assert "face_embedding" not in exported
        assert "voice_recording" not in exported
        assert exported["transcript"] == "hello"

    def test_delete_user_data(self):
        svc = DataMinimizationService()
        deleted = svc.delete_user_data("user-to-delete")
        assert deleted["deleted"] is True
        assert deleted["user_id"] == "user-to-delete"

    def test_anonymize_for_analytics(self):
        svc = DataMinimizationService()
        data = {
            "user_id": "u12345",
            "email": "jane@example.com",
            "score": 85,
            "duration_seconds": 120,
        }
        anonymized = svc.anonymize(data)
        assert anonymized["user_id"] != "u12345"
        assert "email" not in anonymized
        assert anonymized["score"] == 85
        assert anonymized["duration_seconds"] == 120
