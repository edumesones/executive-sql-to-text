"""
Database introspection utilities for PostgreSQL and MySQL.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine


@dataclass
class ColumnInfo:
    """Column metadata."""
    name: str
    data_type: str
    is_nullable: bool


@dataclass
class TableInfo:
    """Table metadata."""
    schema_name: str
    table_name: str
    columns: List[ColumnInfo]


@dataclass
class ConnectionResult:
    """Connection test result."""
    success: bool
    message: str
    details: Optional[Dict[str, Any]] = None


class DatabaseAdapter(ABC):
    """Abstract adapter for database-specific operations."""

    @abstractmethod
    async def introspect_schema(self, url: str) -> List[TableInfo]:
        """
        Introspect database schema to get all tables and columns.

        Args:
            url: Database connection URL

        Returns:
            List of TableInfo objects
        """
        pass

    @abstractmethod
    async def test_connection(self, url: str, timeout: int = 5) -> ConnectionResult:
        """
        Test database connection.

        Args:
            url: Database connection URL
            timeout: Connection timeout in seconds

        Returns:
            ConnectionResult with success status and message
        """
        pass


class PostgreSQLAdapter(DatabaseAdapter):
    """PostgreSQL-specific adapter."""

    async def test_connection(self, url: str, timeout: int = 5) -> ConnectionResult:
        """Test PostgreSQL connection."""
        try:
            # Create async engine for testing
            engine = create_async_engine(url, pool_pre_ping=True)

            # Test connection with timeout
            async with asyncio.timeout(timeout):
                async with engine.connect() as conn:
                    result = await conn.execute(text("SELECT version()"))
                    version = result.scalar()

                    await engine.dispose()

                    return ConnectionResult(
                        success=True,
                        message="Connection successful",
                        details={"version": version}
                    )

        except asyncio.TimeoutError:
            return ConnectionResult(
                success=False,
                message=f"Connection timeout after {timeout} seconds"
            )
        except Exception as e:
            return ConnectionResult(
                success=False,
                message=f"Connection failed: {str(e)}"
            )

    async def introspect_schema(self, url: str) -> List[TableInfo]:
        """Introspect PostgreSQL schema."""
        try:
            engine = create_async_engine(url)

            query = text("""
                SELECT
                    table_schema,
                    table_name,
                    column_name,
                    data_type,
                    is_nullable
                FROM information_schema.columns
                WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
                ORDER BY table_schema, table_name, ordinal_position
            """)

            async with engine.connect() as conn:
                result = await conn.execute(query)
                rows = result.fetchall()

                await engine.dispose()

            # Group by table
            tables_dict: Dict[tuple, List[ColumnInfo]] = {}
            for row in rows:
                key = (row[0], row[1])  # (schema, table)
                if key not in tables_dict:
                    tables_dict[key] = []

                tables_dict[key].append(ColumnInfo(
                    name=row[2],
                    data_type=row[3],
                    is_nullable=(row[4] == 'YES')
                ))

            # Convert to TableInfo list
            tables = [
                TableInfo(
                    schema_name=schema,
                    table_name=table,
                    columns=columns
                )
                for (schema, table), columns in tables_dict.items()
            ]

            return tables

        except Exception as e:
            raise RuntimeError(f"Failed to introspect PostgreSQL schema: {str(e)}")


class MySQLAdapter(DatabaseAdapter):
    """MySQL-specific adapter."""

    async def test_connection(self, url: str, timeout: int = 5) -> ConnectionResult:
        """Test MySQL connection."""
        try:
            # Convert to aiomysql-compatible URL
            mysql_url = url.replace('mysql://', 'mysql+aiomysql://')
            engine = create_async_engine(mysql_url, pool_pre_ping=True)

            # Test connection with timeout
            async with asyncio.timeout(timeout):
                async with engine.connect() as conn:
                    result = await conn.execute(text("SELECT VERSION()"))
                    version = result.scalar()

                    await engine.dispose()

                    return ConnectionResult(
                        success=True,
                        message="Connection successful",
                        details={"version": version}
                    )

        except asyncio.TimeoutError:
            return ConnectionResult(
                success=False,
                message=f"Connection timeout after {timeout} seconds"
            )
        except Exception as e:
            return ConnectionResult(
                success=False,
                message=f"Connection failed: {str(e)}"
            )

    async def introspect_schema(self, url: str) -> List[TableInfo]:
        """Introspect MySQL schema."""
        try:
            # Convert to aiomysql-compatible URL
            mysql_url = url.replace('mysql://', 'mysql+aiomysql://')
            engine = create_async_engine(mysql_url)

            query = text("""
                SELECT
                    TABLE_SCHEMA,
                    TABLE_NAME,
                    COLUMN_NAME,
                    DATA_TYPE,
                    IS_NULLABLE
                FROM information_schema.columns
                WHERE TABLE_SCHEMA = DATABASE()
                ORDER BY TABLE_SCHEMA, TABLE_NAME, ORDINAL_POSITION
            """)

            async with engine.connect() as conn:
                result = await conn.execute(query)
                rows = result.fetchall()

                await engine.dispose()

            # Group by table
            tables_dict: Dict[tuple, List[ColumnInfo]] = {}
            for row in rows:
                key = (row[0], row[1])  # (schema, table)
                if key not in tables_dict:
                    tables_dict[key] = []

                tables_dict[key].append(ColumnInfo(
                    name=row[2],
                    data_type=row[3],
                    is_nullable=(row[4] == 'YES')
                ))

            # Convert to TableInfo list
            tables = [
                TableInfo(
                    schema_name=schema,
                    table_name=table,
                    columns=columns
                )
                for (schema, table), columns in tables_dict.items()
            ]

            return tables

        except Exception as e:
            raise RuntimeError(f"Failed to introspect MySQL schema: {str(e)}")


def detect_db_type(url: str) -> str:
    """
    Detect database type from URL.

    Args:
        url: Database connection URL

    Returns:
        'postgresql' or 'mysql'

    Raises:
        ValueError: If database type is not supported
    """
    if url.startswith('postgresql://') or url.startswith('postgres://'):
        return 'postgresql'
    elif url.startswith('mysql://'):
        return 'mysql'
    else:
        raise ValueError(f"Unsupported database URL format: {url[:20]}...")


def get_adapter(url: str) -> DatabaseAdapter:
    """
    Factory function to get appropriate database adapter.

    Args:
        url: Database connection URL

    Returns:
        DatabaseAdapter instance (PostgreSQLAdapter or MySQLAdapter)

    Raises:
        ValueError: If database type is not supported
    """
    db_type = detect_db_type(url)

    if db_type == 'postgresql':
        return PostgreSQLAdapter()
    elif db_type == 'mysql':
        return MySQLAdapter()
    else:
        raise ValueError(f"Unsupported database type: {db_type}")
