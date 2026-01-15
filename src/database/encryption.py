"""
Credential encryption utilities using Fernet (AES-128).
"""
import os
from cryptography.fernet import Fernet
from typing import Optional


class CredentialEncryption:
    """Handle encryption/decryption of database credentials."""

    def __init__(self, encryption_key: Optional[str] = None):
        """
        Initialize with encryption key from environment or parameter.

        Args:
            encryption_key: Base64-encoded Fernet key. If None, reads from ENCRYPTION_KEY env var.
        """
        key = encryption_key or os.getenv("ENCRYPTION_KEY")
        if not key:
            raise ValueError(
                "ENCRYPTION_KEY not found in environment. "
                "Generate with: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
            )

        self.fernet = Fernet(key.encode() if isinstance(key, str) else key)

    def encrypt_credential(self, url: str) -> str:
        """
        Encrypt a database URL.

        Args:
            url: Plain database URL (e.g., postgresql://user:pass@host/db)

        Returns:
            Encrypted string (base64)
        """
        return self.fernet.encrypt(url.encode()).decode()

    def decrypt_credential(self, encrypted: str) -> str:
        """
        Decrypt a database URL.

        Args:
            encrypted: Encrypted URL string (base64)

        Returns:
            Plain database URL
        """
        return self.fernet.decrypt(encrypted.encode()).decode()


# Singleton instance
_encryption_instance: Optional[CredentialEncryption] = None


def get_encryption() -> CredentialEncryption:
    """Get singleton encryption instance."""
    global _encryption_instance
    if _encryption_instance is None:
        _encryption_instance = CredentialEncryption()
    return _encryption_instance


def encrypt_credential(url: str) -> str:
    """Convenience function to encrypt a database URL."""
    return get_encryption().encrypt_credential(url)


def decrypt_credential(encrypted: str) -> str:
    """Convenience function to decrypt a database URL."""
    return get_encryption().decrypt_credential(encrypted)
