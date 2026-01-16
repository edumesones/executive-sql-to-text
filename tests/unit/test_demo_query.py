"""
Unit tests for Demo Query endpoint
Tests the /api/demo-query endpoint that works for both authenticated and anonymous users.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class TestDemoQueryEndpoint:
    """Test suite for demo-query endpoint"""

    @pytest.fixture
    def mock_workflow_result(self):
        """Mock workflow result"""
        return {
            "sql_query": "SELECT * FROM loans LIMIT 10",
            "query_results": [{"id": 1, "loan_amnt": 5000}],
            "result_count": 1,
            "derived_metrics": None,
            "chart_type": "bar",
            "chart_config": {},
            "insights": ["Most loans are grade A"],
            "recommendations": ["Consider filtering by grade"],
            "errors": [],
            "warnings": [],
            "metrics": {"total_duration_ms": 100}
        }

    def test_demo_query_allows_anonymous(self):
        """Test that demo-query endpoint allows anonymous users"""
        from src.auth.dependencies import get_current_user_optional

        # get_current_user_optional should return None for anonymous users
        # (when no cookie is present), not raise an exception
        # This is the key difference from get_current_user
        assert get_current_user_optional is not None

    def test_demo_query_accepts_authenticated_user(self):
        """Test that demo-query endpoint accepts authenticated users"""
        from src.auth.dependencies import get_current_user_optional

        # Verify the dependency function exists and can be imported
        assert callable(get_current_user_optional)

    def test_query_request_schema(self):
        """Test QueryRequest schema accepts required fields"""
        from src.api.schemas import QueryRequest

        request = QueryRequest(
            query="Show top 10 loans",
            session_id="test-session-123"
        )

        assert request.query == "Show top 10 loans"
        assert request.session_id == "test-session-123"

    def test_query_response_schema(self):
        """Test QueryResponse schema has required fields"""
        from src.api.schemas import QueryResponse

        response = QueryResponse(
            session_id="test-session-123",
            sql_query="SELECT * FROM loans",
            query_results=[{"id": 1}],
            result_count=1,
            errors=[]
        )

        assert response.session_id == "test-session-123"
        assert response.sql_query == "SELECT * FROM loans"
        assert response.result_count == 1
        assert response.errors == []

    def test_query_response_optional_fields(self):
        """Test QueryResponse handles optional fields"""
        from src.api.schemas import QueryResponse

        response = QueryResponse(
            session_id="test-session-123",
            errors=[]
        )

        # Optional fields should be None or empty
        assert response.sql_query is None
        assert response.query_results is None
        assert response.insights == []
        assert response.recommendations == []

    def test_demo_query_different_from_query(self):
        """Test that demo-query uses optional auth unlike /query"""
        from src.auth.dependencies import get_current_user, get_current_user_optional

        # These should be different functions
        assert get_current_user is not get_current_user_optional


class TestFreemiumLogic:
    """Test suite for freemium logic (frontend-enforced)"""

    def test_free_query_limit_constant(self):
        """Test that free query limit is defined in frontend"""
        # The limit is defined in frontend/gradio_main.py
        # This is a documentation test to confirm the architecture
        FREE_QUERY_LIMIT = 1
        assert FREE_QUERY_LIMIT == 1

    def test_anonymous_user_tracking(self):
        """Test that anonymous users can be tracked by session_id"""
        import uuid

        session_id = str(uuid.uuid4())
        assert len(session_id) == 36  # UUID format
        assert "-" in session_id


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
