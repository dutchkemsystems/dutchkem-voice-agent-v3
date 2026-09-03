"""End-to-end encryption service for voice/face data."""
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class EncryptionService:
    def __init__(self, password: str = None):
        if password is None:
            password = os.environ.get("ENCRYPTION_KEY", "default-dev-key")

        salt = b"dutchkem-salt-v3"
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        self.cipher = Fernet(key)

    def encrypt(self, data: bytes) -> bytes:
        return self.cipher.encrypt(data)

    def decrypt(self, encrypted_data: bytes) -> bytes:
        return self.cipher.decrypt(encrypted_data)

    def encrypt_file(self, input_path: str, output_path: str):
        with open(input_path, "rb") as f:
            data = f.read()
        encrypted = self.encrypt(data)
        with open(output_path, "wb") as f:
            f.write(encrypted)
