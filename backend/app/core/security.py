import os
import hashlib
import base64
import bcrypt
from typing import Optional
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from app.core.config import settings


def hash_password(password: str) -> str:
    """Hash a plaintext password with bcrypt directly."""
    pwd_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its bcrypt hash."""
    pwd_bytes = plain_password.encode("utf-8")[:72]
    hash_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(pwd_bytes, hash_bytes)


def hash_token(token: str) -> str:
    """Compute SHA-256 hash of a sensitive token (refresh token, OTP, bot token)."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _get_encryption_key() -> bytes:
    """Derive a 32-byte key from settings.SECRET_KEY."""
    return hashlib.sha256(settings.SECRET_KEY.encode("utf-8")).digest()


def encrypt_sensitive_string(plain_text: str) -> str:
    """Encrypt a sensitive string using AES-256-GCM and return base64 string."""
    key = _get_encryption_key()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)  # 96-bit nonce
    encrypted = aesgcm.encrypt(nonce, plain_text.encode("utf-8"), None)
    payload = nonce + encrypted
    return base64.b64encode(payload).decode("utf-8")


def decrypt_sensitive_string(cipher_b64: str) -> str:
    """Decrypt an AES-256-GCM base64 encoded string."""
    key = _get_encryption_key()
    aesgcm = AESGCM(key)
    payload = base64.b64decode(cipher_b64.encode("utf-8"))
    nonce = payload[:12]
    ciphertext = payload[12:]
    decrypted = aesgcm.decrypt(nonce, ciphertext, None)
    return decrypted.decode("utf-8")
