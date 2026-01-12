"""
SQL Executor Tool - Safe query execution with connection pooling
"""
import asyncio
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
import asyncpg
from contextlib import asynccontextmanager

from ..database.connection import get_database_url


class SQLExecutor:
    """
    Safely executes SQL queries with connection pooling and result limits.
    Only allows SELECT queries to prevent data modification.
    """
    
    def __init__(
        self,
        max_results: int = 1000,
        query_timeout: int = 30,
        pool_size: int = 10
    ):
        """
        Initialize SQL Executor
        
        Args:
            max_results: Maximum number of rows to return
            query_timeout: Query timeout in seconds
            pool_size: Connection pool size
        """
        self.max_results = max_results
        self.query_timeout = query_timeout
        self.pool_size = pool_size
        self._pool: Optional[asyncpg.Pool] = None
    
    async def _get_pool(self) -> asyncpg.Pool:
        """Get or create connection pool"""
        if self._pool is None:
            database_url = get_database_url()
            self._pool = await asyncpg.create_pool(
                database_url,
                min_size=2,
                max_size=self.pool_size,
                command_timeout=self.query_timeout
            )
        return self._pool
    
    async def execute_query(
        self,
        sql: str,
        params: Dict[str, Any] = None
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Execute SELECT query safely
        
        Args:
            sql: SQL query string (must be SELECT)
            params: Optional query parameters
        
        Returns:
            Tuple of (results, metadata) where:
            - results: List of dictionaries (rows)
            - metadata: Dict with execution info
        
        Raises:
            ValueError: If query is not SELECT
            asyncpg.QueryCanceledError: If query times out
        """
        start_time = datetime.utcnow()
        
        # Validate query is SELECT only
        if not sql.strip().upper().startswith('SELECT'):
            raise ValueError("Only SELECT queries are allowed")
        
        pool = await self._get_pool()
        
        async with pool.acquire() as conn:
            try:
                # Add LIMIT if not present
                sql_with_limit = self._add_limit_clause(sql)
                
                # Execute query
                rows = await conn.fetch(sql_with_limit)
                
                # Calculate execution time
                execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                
                # Convert to list of dicts
                results = [dict(row) for row in rows]
                
                # Extract metadata
                metadata = {
                    "row_count": len(results),
                    "column_names": list(results[0].keys()) if results else [],
                    "column_types": {
                        col: str(type(results[0][col]).__name__)
                        for col in results[0].keys()
                    } if results else {},
                    "execution_time_ms": round(execution_time, 2),
                    "truncated": len(rows) >= self.max_results,
                    "query": sql_with_limit
                }
                
                return results, metadata
                
            except asyncpg.QueryCanceledError:
                raise ValueError(f"Query timeout after {self.query_timeout}s")
            except asyncpg.PostgresError as e:
                raise ValueError(f"Database error: {str(e)}")
    
    def _add_limit_clause(self, sql: str) -> str:
        """Add LIMIT clause if not present"""
        sql_upper = sql.upper()
        
        # Check if LIMIT already exists
        if 'LIMIT' in sql_upper:
            return sql
        
        # Add LIMIT at the end
        return f"{sql.rstrip(';')} LIMIT {self.max_results}"
    
    async def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Get schema information for a table
        
        Args:
            table_name: Name of the table
        
        Returns:
            List of column definitions with name, type, nullable
        """
        pool = await self._get_pool()
        
        query = """
            SELECT 
                column_name,
                data_type,
                is_nullable,
                column_default
            FROM information_schema.columns
            WHERE table_name = $1
            ORDER BY ordinal_position
        """
        
        async with pool.acquire() as conn:
            rows = await conn.fetch(query, table_name)
            return [dict(row) for row in rows]
    
    async def close(self):
        """Close connection pool"""
        if self._pool:
            await self._pool.close()
            self._pool = None


# Singleton instance
_executor: Optional[SQLExecutor] = None


def get_sql_executor() -> SQLExecutor:
    """Get or create SQL executor singleton"""
    global _executor
    if _executor is None:
        _executor = SQLExecutor()
    return _executor
