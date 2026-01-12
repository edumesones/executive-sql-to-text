"""
SQL Agent - Converts natural language to SQL queries
"""
from typing import Dict, Any
import re

from .base_agent import BaseAgent


class SQLAgent(BaseAgent):
    """
    Generates safe SQL queries from natural language questions.
    Only allows SELECT statements to prevent data modification.
    """
    
    def __init__(self):
        super().__init__(agent_name='sql_agent')
        self.allowed_operations = self.config.get('allowed_operations', ['SELECT'])
        self.forbidden_operations = self.config.get('forbidden_operations', [])
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate SQL query from user's natural language question
        
        Args:
            state: Current workflow state with user_query
            
        Returns:
            State updates with sql_query and sql_explanation
        """
        user_query = state['user_query']
        
        # Build prompt with schema context
        prompt = self._build_prompt(user_query)
        
        try:
            # Get SQL from LLM
            response = self.invoke_llm(prompt)
            
            # Extract and validate SQL
            sql_query = self._extract_sql(response)
            validated_sql = self._validate_sql(sql_query)
            
            return {
                "sql_query": validated_sql,
                "sql_explanation": response,
                "current_step": "sql_generated"
            }
            
        except Exception as e:
            return {
                "sql_query": None,
                "errors": [f"SQL generation failed: {str(e)}"],
                "current_step": "sql_error"
            }
    
    def _build_prompt(self, user_query: str) -> str:
        """Build the prompt with schema information"""
        schema_info = """
        Available table: loans
        
        Key columns:
        - loan_amnt: Loan amount in dollars (NUMERIC)
        - int_rate: Interest rate as percentage (NUMERIC)
        - grade: Loan grade A-G (VARCHAR)
        - sub_grade: Detailed grade like A1, B2 (VARCHAR)
        - loan_status: Current, Fully Paid, Charged Off, Default, etc. (VARCHAR)
        - annual_inc: Borrower's annual income (NUMERIC)
        - purpose: Loan purpose like debt_consolidation, credit_card (VARCHAR)
        - addr_state: US state code (VARCHAR)
        - term: Loan term like '36 months' or '60 months' (VARCHAR)
        - issue_d: Loan issue date (DATE)
        - dti: Debt-to-income ratio (NUMERIC)
        - home_ownership: RENT, OWN, MORTGAGE, etc. (VARCHAR)
        - emp_length: Employment length (VARCHAR)
        
        Common loan_status values:
        - 'Current' - Active and up to date
        - 'Fully Paid' - Successfully completed
        - 'Charged Off' - Defaulted
        - 'Default' - In default
        - 'Late (31-120 days)' - Delinquent
        
        Example queries:
        1. "Top 10 loan amounts" → SELECT loan_amnt, grade FROM loans ORDER BY loan_amnt DESC LIMIT 10
        2. "Default rate by grade" → SELECT grade, COUNT(*) as total, 
           COUNT(CASE WHEN loan_status IN ('Charged Off', 'Default') THEN 1 END) as defaults
           FROM loans GROUP BY grade ORDER BY grade
        """
        
        return f"""{schema_info}
        
        User Question: {user_query}
        
        Generate a PostgreSQL SELECT query that answers this question.
        Requirements:
        - Use only SELECT statements
        - Include LIMIT clause (default 1000 for safety)
        - Use proper column names from schema
        - Handle NULL values appropriately
        - Format numbers and dates correctly
        
        Return ONLY the SQL query, no explanations or markdown.
        """
    
    def _extract_sql(self, response: str) -> str:
        """Extract SQL query from LLM response"""
        # Remove markdown code blocks
        response = re.sub(r'```sql\n?', '', response)
        response = re.sub(r'```\n?', '', response)
        
        # Extract SELECT statement
        sql_match = re.search(
            r'(SELECT\s+.*?;?)\s*$',
            response,
            re.IGNORECASE | re.DOTALL
        )
        
        if sql_match:
            sql = sql_match.group(1).strip()
            # Remove trailing semicolon if present
            return sql.rstrip(';')
        
        # If no SELECT found, assume entire response is SQL
        return response.strip().rstrip(';')
    
    def _validate_sql(self, sql: str) -> str:
        """
        Validate SQL query for safety
        
        Raises:
            ValueError: If SQL contains forbidden operations
        """
        sql_upper = sql.upper()
        
        # Check for forbidden operations
        for forbidden in self.forbidden_operations:
            if forbidden in sql_upper:
                raise ValueError(f"Forbidden operation detected: {forbidden}")
        
        # Ensure it starts with SELECT
        if not sql_upper.strip().startswith('SELECT'):
            raise ValueError("Only SELECT queries are allowed")
        
        # Basic injection protection checks
        dangerous_patterns = [
            r';\s*DROP',
            r';\s*DELETE',
            r';\s*UPDATE',
            r';\s*INSERT',
            r'--',  # SQL comments
            r'/\*',  # Multi-line comments
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, sql_upper):
                raise ValueError(f"Potentially unsafe SQL pattern detected")
        
        return sql
