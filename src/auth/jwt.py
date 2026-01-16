"""
JWT token management utilities.
"""
import os
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from jose import JWTError, jwt

# JWT Configuration from environment
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1440))  # 24 hours

# Password reset token expiration
PASSWORD_RESET_EXPIRE_MINUTES = 60  # 1 hour


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Data to encode in the token (must include "sub" for user ID)
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and validate a JWT token.

    Args:
        token: JWT token string

    Returns:
        Decoded payload dict if valid, None if invalid/expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def create_password_reset_token(user_id: str) -> str:
    """
    Create a secure token for password reset.

    Args:
        user_id: User's UUID as string

    Returns:
        Secure random token string (64 characters)
    """
    return secrets.token_urlsafe(48)


def get_password_reset_expiry() -> datetime:
    """
    Get expiration datetime for password reset token.

    Returns:
        DateTime when token expires (1 hour from now)
    """
    return datetime.utcnow() + timedelta(minutes=PASSWORD_RESET_EXPIRE_MINUTES)


def is_token_expired(expires_at: datetime) -> bool:
    """
    Check if a token has expired.

    Args:
        expires_at: Token expiration datetime

    Returns:
        True if expired, False otherwise
    """
    return datetime.utcnow() > expires_at
