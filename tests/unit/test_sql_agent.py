"""
Unit tests for SQL Agent
"""
import pytest
from src.agents.sql_agent import SQLAgent
from src.graph.state import create_initial_state


class TestSQLAgent:
    """Test suite for SQL Agent"""
    
    @pytest.fixture
    def agent(self):
        """Create SQL agent instance"""
        return SQLAgent()
    
    @pytest.fixture
    def initial_state(self):
        """Create initial state"""
        return create_initial_state(
            user_query="Show me the top 10 loans by amount",
            session_id="test-session-123"
        )
    
    def test_agent_initialization(self, agent):
        """Test agent initializes correctly"""
        assert agent.agent_name == 'sql_agent'
        assert agent.llm is not None
        assert 'SELECT' in agent.allowed_operations
    
    def test_extract_sql(self, agent):
        """Test SQL extraction from LLM response"""
        # Test with markdown code blocks
        response = "```sql\nSELECT * FROM loans LIMIT 10;\n```"
        sql = agent._extract_sql(response)
        assert sql == "SELECT * FROM loans LIMIT 10"
        
        # Test without markdown
        response = "SELECT loan_amnt, grade FROM loans ORDER BY loan_amnt DESC LIMIT 10"
        sql = agent._extract_sql(response)
        assert "SELECT" in sql
        assert "loans" in sql
    
    def test_validate_sql_allows_select(self, agent):
        """Test that SELECT queries are allowed"""
        sql = "SELECT * FROM loans WHERE grade = 'A' LIMIT 100"
        validated = agent._validate_sql(sql)
        assert validated == sql
    
    def test_validate_sql_blocks_drop(self, agent):
        """Test that DROP statements are blocked"""
        sql = "DROP TABLE loans"
        with pytest.raises(ValueError, match="Forbidden operation"):
            agent._validate_sql(sql)
    
    def test_validate_sql_blocks_delete(self, agent):
        """Test that DELETE statements are blocked"""
        sql = "DELETE FROM loans WHERE grade = 'F'"
        with pytest.raises(ValueError, match="Forbidden operation"):
            agent._validate_sql(sql)
    
    def test_validate_sql_blocks_injection(self, agent):
        """Test SQL injection protection"""
        sql = "SELECT * FROM loans; DROP TABLE loans; --"
        with pytest.raises(ValueError, match="unsafe"):
            agent._validate_sql(sql)
    
    def test_validate_sql_requires_select(self, agent):
        """Test that queries must start with SELECT"""
        sql = "UPDATE loans SET grade = 'A'"
        with pytest.raises(ValueError, match="Only SELECT queries"):
            agent._validate_sql(sql)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
