"""
Tests for connections API endpoints.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from src.api.connections import (
    check_query_limit,
    increment_query_count,
    get_query_usage
)


@pytest.mark.asyncio
async def test_check_query_limit_under():
    """Test query limit check when under limit."""
    # Mock database session
    mock_db = AsyncMock()
    mock_usage = MagicMock()
    mock_usage.query_count = 15  # Under limit of 30

    with patch('src.api.connections.get_query_usage', return_value=mock_usage):
        result = await check_query_limit(mock_db, uuid4(), limit=30)
        assert result is True


@pytest.mark.asyncio
async def test_check_query_limit_at_limit():
    """Test query limit check when at limit."""
    mock_db = AsyncMock()
    mock_usage = MagicMock()
    mock_usage.query_count = 30  # At limit

    with patch('src.api.connections.get_query_usage', return_value=mock_usage):
        result = await check_query_limit(mock_db, uuid4(), limit=30)
        assert result is False


@pytest.mark.asyncio
async def test_check_query_limit_over():
    """Test query limit check when over limit."""
    mock_db = AsyncMock()
    mock_usage = MagicMock()
    mock_usage.query_count = 35  # Over limit

    with patch('src.api.connections.get_query_usage', return_value=mock_usage):
        result = await check_query_limit(mock_db, uuid4(), limit=30)
        assert result is False


# Integration tests (require database)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_connection_integration():
    """Integration test for creating a connection."""
    pytest.skip("Integration test - requires database")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_list_connections_integration():
    """Integration test for listing connections."""
    pytest.skip("Integration test - requires database")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_delete_connection_integration():
    """Integration test for deleting a connection."""
    pytest.skip("Integration test - requires database")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_update_tables_integration():
    """Integration test for updating enabled tables."""
    pytest.skip("Integration test - requires database")
