"""
SQL Agent - Converts natural language to SQL queries
"""
from typing import Dict, Any, Optional, List
import re
from uuid import UUID

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
            state: Current workflow state with user_query and optional connection_id

        Returns:
            State updates with sql_query and sql_explanation
        """
        user_query = state['user_query']
        connection_id = state.get('connection_id')  # Optional customer connection

        # Build prompt with schema context (dynamic or default)
        prompt = self._build_prompt(user_query, connection_id=connection_id)

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
    
    def _build_prompt(self, user_query: str, connection_id: Optional[str] = None) -> str:
        """
        Build the prompt with schema information.

        Args:
            user_query: User's natural language question
            connection_id: Optional customer connection ID for dynamic schema

        Returns:
            Formatted prompt string
        """
        if connection_id:
            # Dynamic schema from customer connection
            schema_info = self._get_dynamic_schema(connection_id)
            db_type = "SQL"  # Generic for customer DBs
        else:
            # Default hardcoded schema for demo (Lending Club)
            schema_info = self._get_default_schema()
            db_type = "PostgreSQL"

        return f"""{schema_info}

        User Question: {user_query}

        Generate a {db_type} SELECT query that answers this question.
        Requirements:
        - Use only SELECT statements
        - Include LIMIT clause (default 1000 for safety)
        - Use proper column names from schema
        - Handle NULL values appropriately
        - Format numbers and dates correctly

        Return ONLY the SQL query, no explanations or markdown.
        """

    def _get_default_schema(self) -> str:
        """Get default hardcoded schema for Lending Club demo."""
        return """
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

    def _get_dynamic_schema(self, connection_id: str) -> str:
        """
        Get dynamic schema from customer connection's enabled tables.

        Args:
            connection_id: Customer connection UUID

        Returns:
            Formatted schema information string
        """
        try:
            # Import here to avoid circular dependency
            from src.database.models import TableConfig, CustomerConnection
            from src.database.connection import db
            from sqlalchemy import select, and_
            import asyncio

            # Run async query in sync context (for now)
            # TODO: Make this fully async when agent workflow supports it
            async def fetch_tables():
                async with db.session() as session:
                    # Get enabled tables for this connection
                    result = await session.execute(
                        select(TableConfig).where(
                            and_(
                                TableConfig.connection_id == UUID(connection_id),
                                TableConfig.is_enabled == True
                            )
                        )
                    )
                    return result.scalars().all()

            # Execute async function
            tables = asyncio.run(fetch_tables())

            if not tables:
                return "No tables enabled for this connection. Please enable tables first."

            # Build schema info from enabled tables
            schema_parts = [f"Available tables ({len(tables)}):"]

            for table in tables:
                full_name = f"{table.schema_name}.{table.table_name}" if table.schema_name != 'public' else table.table_name
                schema_parts.append(f"\nTable: {full_name}")
                schema_parts.append("Columns:")

                for col in table.columns:
                    schema_parts.append(f"  - {col['name']}: {col['type']}")

            return "\n".join(schema_parts)

        except Exception as e:
            return f"Error loading schema: {str(e)}\nFalling back to demo mode."
    
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
