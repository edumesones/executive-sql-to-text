"""
Tests for database introspection utilities.
"""
import pytest
from src.database.introspection import (
    detect_db_type,
    get_adapter,
    PostgreSQLAdapter,
    MySQLAdapter
)


def test_detect_db_type_postgresql():
    """Test PostgreSQL URL detection."""
    urls = [
        "postgresql://user:pass@host/db",
        "postgres://user:pass@host/db",
    ]

    for url in urls:
        assert detect_db_type(url) == "postgresql"


def test_detect_db_type_mysql():
    """Test MySQL URL detection."""
    url = "mysql://user:pass@host/db"
    assert detect_db_type(url) == "mysql"


def test_detect_db_type_unsupported():
    """Test that unsupported URLs raise ValueError."""
    unsupported_urls = [
        "sqlite:///test.db",
        "mongodb://host/db",
        "redis://host:6379",
    ]

    for url in unsupported_urls:
        with pytest.raises(ValueError, match="Unsupported database URL"):
            detect_db_type(url)


def test_get_adapter_postgresql():
    """Test getting PostgreSQL adapter."""
    url = "postgresql://user:pass@host/db"
    adapter = get_adapter(url)
    assert isinstance(adapter, PostgreSQLAdapter)


def test_get_adapter_mysql():
    """Test getting MySQL adapter."""
    url = "mysql://user:pass@host/db"
    adapter = get_adapter(url)
    assert isinstance(adapter, MySQLAdapter)


def test_get_adapter_unsupported():
    """Test that unsupported URLs raise ValueError."""
    url = "sqlite:///test.db"
    with pytest.raises(ValueError):
        get_adapter(url)


# Integration tests (require actual database connections)
@pytest.mark.asyncio
@pytest.mark.integration
async def test_postgresql_connection():
    """Test PostgreSQL connection (requires test database)."""
    # This would require a test PostgreSQL instance
    # Skipped in unit tests
    pytest.skip("Integration test - requires PostgreSQL")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_mysql_connection():
    """Test MySQL connection (requires test database)."""
    # This would require a test MySQL instance
    # Skipped in unit tests
    pytest.skip("Integration test - requires MySQL")
