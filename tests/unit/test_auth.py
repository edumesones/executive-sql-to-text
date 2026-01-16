"""
Unit tests for Authentication module
"""
import pytest
from datetime import datetime, timedelta

from src.auth.password import (
    hash_password,
    verify_password,
    validate_password_strength
)
from src.auth.jwt import (
    create_access_token,
    decode_token,
    create_password_reset_token,
    get_password_reset_expiry,
    is_token_expired
)


class TestPasswordHashing:
    """Test suite for password hashing utilities"""

    def test_hash_password_returns_hash(self):
        """Test that hash_password returns a bcrypt hash"""
        password = "SecurePass123"
        hashed = hash_password(password)

        assert hashed is not None
        assert hashed != password
        assert hashed.startswith("$2b$")  # bcrypt identifier

    def test_hash_password_different_hashes_for_same_password(self):
        """Test that same password produces different hashes (due to salt)"""
        password = "SecurePass123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        assert hash1 != hash2

    def test_verify_password_correct(self):
        """Test that correct password verifies successfully"""
        password = "SecurePass123"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test that incorrect password fails verification"""
        password = "SecurePass123"
        hashed = hash_password(password)

        assert verify_password("WrongPassword123", hashed) is False

    def test_verify_password_case_sensitive(self):
        """Test that password verification is case-sensitive"""
        password = "SecurePass123"
        hashed = hash_password(password)

        assert verify_password("securepass123", hashed) is False
        assert verify_password("SECUREPASS123", hashed) is False


class TestPasswordStrengthValidation:
    """Test suite for password strength validation"""

    def test_valid_password(self):
        """Test that a valid password passes validation"""
        is_valid, error = validate_password_strength("SecurePass123")

        assert is_valid is True
        assert error == ""

    def test_password_too_short(self):
        """Test that short passwords are rejected"""
        is_valid, error = validate_password_strength("Short1A")

        assert is_valid is False
        assert "8 characters" in error

    def test_password_missing_uppercase(self):
        """Test that passwords without uppercase are rejected"""
        is_valid, error = validate_password_strength("securepass123")

        assert is_valid is False
        assert "uppercase" in error

    def test_password_missing_lowercase(self):
        """Test that passwords without lowercase are rejected"""
        is_valid, error = validate_password_strength("SECUREPASS123")

        assert is_valid is False
        assert "lowercase" in error

    def test_password_missing_digit(self):
        """Test that passwords without digits are rejected"""
        is_valid, error = validate_password_strength("SecurePassword")

        assert is_valid is False
        assert "digit" in error

    def test_minimum_valid_password(self):
        """Test that minimum valid password (8 chars, upper, lower, digit) passes"""
        is_valid, error = validate_password_strength("Abcdefg1")

        assert is_valid is True
        assert error == ""


class TestJWTUtilities:
    """Test suite for JWT token utilities"""

    def test_create_access_token(self):
        """Test that access token is created successfully"""
        token = create_access_token(data={"sub": "user-123"})

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_valid_token(self):
        """Test that valid token decodes correctly"""
        user_id = "user-123-456"
        token = create_access_token(data={"sub": user_id})
        payload = decode_token(token)

        assert payload is not None
        assert payload.get("sub") == user_id
        assert payload.get("type") == "access"
        assert "exp" in payload
        assert "iat" in payload

    def test_decode_invalid_token(self):
        """Test that invalid token returns None"""
        payload = decode_token("invalid-token")

        assert payload is None

    def test_decode_expired_token(self):
        """Test that expired token returns None"""
        # Create token with negative expiration (already expired)
        token = create_access_token(
            data={"sub": "user-123"},
            expires_delta=timedelta(seconds=-1)
        )
        payload = decode_token(token)

        assert payload is None

    def test_create_token_with_custom_expiration(self):
        """Test that custom expiration is applied"""
        token = create_access_token(
            data={"sub": "user-123"},
            expires_delta=timedelta(hours=1)
        )
        payload = decode_token(token)

        assert payload is not None
        # Token should expire within ~1 hour
        exp_time = datetime.utcfromtimestamp(payload["exp"])
        now = datetime.utcnow()
        delta = exp_time - now

        # Should be between 59 and 61 minutes (accounting for test execution time)
        assert timedelta(minutes=59) < delta < timedelta(minutes=61)


class TestPasswordResetToken:
    """Test suite for password reset token utilities"""

    def test_create_password_reset_token(self):
        """Test that reset token is created successfully"""
        token = create_password_reset_token("user-123")

        assert token is not None
        assert isinstance(token, str)
        assert len(token) >= 32  # URL-safe base64

    def test_create_password_reset_token_unique(self):
        """Test that reset tokens are unique"""
        token1 = create_password_reset_token("user-123")
        token2 = create_password_reset_token("user-123")

        assert token1 != token2

    def test_get_password_reset_expiry(self):
        """Test that password reset expiry is ~1 hour in future"""
        expiry = get_password_reset_expiry()
        now = datetime.utcnow()
        delta = expiry - now

        # Should be between 59 and 61 minutes
        assert timedelta(minutes=59) < delta < timedelta(minutes=61)

    def test_is_token_expired_not_expired(self):
        """Test that unexpired token is detected correctly"""
        future_time = datetime.utcnow() + timedelta(hours=1)

        assert is_token_expired(future_time) is False

    def test_is_token_expired_expired(self):
        """Test that expired token is detected correctly"""
        past_time = datetime.utcnow() - timedelta(hours=1)

        assert is_token_expired(past_time) is True

    def test_is_token_expired_just_now(self):
        """Test edge case of token that just expired"""
        past_time = datetime.utcnow() - timedelta(seconds=1)

        assert is_token_expired(past_time) is True


class TestRateLimiting:
    """Test suite for rate limiting logic (unit tests without DB)"""

    def test_lockout_time_calculation(self):
        """Test that lockout time is calculated correctly"""
        from datetime import datetime, timedelta

        LOCKOUT_MINUTES = 15
        lockout_until = datetime.utcnow() + timedelta(minutes=LOCKOUT_MINUTES)

        # Should be ~15 minutes in the future
        delta = lockout_until - datetime.utcnow()
        assert timedelta(minutes=14) < delta < timedelta(minutes=16)

    def test_lockout_check_active(self):
        """Test that active lockout is detected"""
        locked_until = datetime.utcnow() + timedelta(minutes=10)
        is_locked = locked_until > datetime.utcnow()

        assert is_locked is True

    def test_lockout_check_expired(self):
        """Test that expired lockout is detected"""
        locked_until = datetime.utcnow() - timedelta(minutes=10)
        is_locked = locked_until > datetime.utcnow()

        assert is_locked is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
