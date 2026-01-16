"""
Authentication module for Executive Analytics Assistant.

Provides:
- Password hashing (bcrypt)
- JWT token management
- Auth dependencies for FastAPI
- Email services (SendGrid)
"""

from .password import hash_password, verify_password, validate_password_strength
from .jwt import create_access_token, decode_token, create_password_reset_token
from .dependencies import get_current_user

__all__ = [
    "hash_password",
    "verify_password",
    "validate_password_strength",
    "create_access_token",
    "decode_token",
    "create_password_reset_token",
    "get_current_user",
]
