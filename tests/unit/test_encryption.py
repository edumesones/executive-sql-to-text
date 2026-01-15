"""
Tests for credential encryption utilities.
"""
import pytest
import os
from cryptography.fernet import Fernet

from src.database.encryption import (
    CredentialEncryption,
    encrypt_credential,
    decrypt_credential
)


@pytest.fixture
def encryption_key():
    """Generate a test encryption key."""
    return Fernet.generate_key().decode()


@pytest.fixture
def encryption_instance(encryption_key):
    """Create encryption instance with test key."""
    return CredentialEncryption(encryption_key=encryption_key)


def test_encryption_roundtrip(encryption_instance):
    """Test that encryption and decryption work correctly."""
    original_url = "postgresql://user:password@localhost:5432/testdb"

    # Encrypt
    encrypted = encryption_instance.encrypt_credential(original_url)

    # Verify it's encrypted (not plain text)
    assert encrypted != original_url
    assert "postgresql://" not in encrypted

    # Decrypt
    decrypted = encryption_instance.decrypt_credential(encrypted)

    # Verify roundtrip
    assert decrypted == original_url


def test_encryption_different_keys():
    """Test that different keys produce different encrypted values."""
    url = "postgresql://user:password@localhost:5432/testdb"

    key1 = Fernet.generate_key().decode()
    key2 = Fernet.generate_key().decode()

    enc1 = CredentialEncryption(encryption_key=key1)
    enc2 = CredentialEncryption(encryption_key=key2)

    encrypted1 = enc1.encrypt_credential(url)
    encrypted2 = enc2.encrypt_credential(url)

    # Different keys should produce different encrypted values
    assert encrypted1 != encrypted2


def test_encryption_wrong_key_fails(encryption_key):
    """Test that decryption fails with wrong key."""
    url = "postgresql://user:password@localhost:5432/testdb"

    enc1 = CredentialEncryption(encryption_key=encryption_key)
    encrypted = enc1.encrypt_credential(url)

    # Try to decrypt with different key
    wrong_key = Fernet.generate_key().decode()
    enc2 = CredentialEncryption(encryption_key=wrong_key)

    with pytest.raises(Exception):  # Fernet raises cryptography exceptions
        enc2.decrypt_credential(encrypted)


def test_encryption_requires_key():
    """Test that encryption requires a key."""
    # Clear environment variable if set
    original_key = os.environ.get("ENCRYPTION_KEY")
    if "ENCRYPTION_KEY" in os.environ:
        del os.environ["ENCRYPTION_KEY"]

    try:
        with pytest.raises(ValueError, match="ENCRYPTION_KEY not found"):
            CredentialEncryption()
    finally:
        # Restore original key
        if original_key:
            os.environ["ENCRYPTION_KEY"] = original_key


def test_convenience_functions(encryption_key, monkeypatch):
    """Test convenience encrypt/decrypt functions."""
    monkeypatch.setenv("ENCRYPTION_KEY", encryption_key)

    # Clear singleton to force new instance with test key
    from src.database import encryption as enc_module
    enc_module._encryption_instance = None

    url = "postgresql://user:password@localhost:5432/testdb"

    encrypted = encrypt_credential(url)
    decrypted = decrypt_credential(encrypted)

    assert decrypted == url
