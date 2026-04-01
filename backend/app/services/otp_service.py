"""
OTP Service
-----------
Handles OTP generation, storage (Redis), and verification.
Place this file at: app/services/otp_service.py
"""

import random
import string

from app.config import settings
from app.redis_client import redis_client


def _build_key(email: str, purpose: str) -> str:
    """
    Build a namespaced Redis key.
    Examples:
        otp:login:user@example.com
        otp:forgot_password:user@example.com
    """
    return f"otp:{purpose}:{email}"


def _build_attempts_key(email: str, purpose: str) -> str:
    """Track failed verification attempts."""
    return f"otp_attempts:{purpose}:{email}"


MAX_ATTEMPTS = 5


def generate_otp() -> str:
    """Return a random numeric OTP of configured length."""
    return "".join(random.choices(string.digits, k=settings.OTP_LENGTH))


def store_otp(email: str, otp: str, purpose: str = "login") -> None:
    """
    Save OTP in Redis with a TTL equal to OTP_EXPIRE_SECONDS.
    Overwrites any existing OTP for the same email + purpose.
    Also resets the attempt counter.
    """
    key = _build_key(email, purpose)
    attempts_key = _build_attempts_key(email, purpose)

    redis_client.setex(key, settings.OTP_EXPIRE_SECONDS, otp)
    redis_client.delete(attempts_key)


def verify_otp(email: str, otp: str, purpose: str = "login") -> bool:
    """
    Compare the submitted OTP against the stored value.
    Returns True on match (and deletes the key so it can't be reused).
    Returns False on mismatch or expiry.
    Raises ValueError if max attempts exceeded.
    """
    key = _build_key(email, purpose)
    attempts_key = _build_attempts_key(email, purpose)

    # Check attempt count
    attempts = redis_client.get(attempts_key)
    if attempts and int(attempts) >= MAX_ATTEMPTS:
        # Clean up and block
        redis_client.delete(key)
        redis_client.delete(attempts_key)
        raise ValueError("Too many failed attempts. Please request a new OTP.")

    stored_otp = redis_client.get(key)

    if stored_otp is None:
        return False  # expired or never existed

    if stored_otp == otp:
        # Success — clean up
        redis_client.delete(key)
        redis_client.delete(attempts_key)
        return True

    # Wrong OTP — increment attempts
    redis_client.incr(attempts_key)
    redis_client.expire(attempts_key, settings.OTP_EXPIRE_SECONDS)
    return False