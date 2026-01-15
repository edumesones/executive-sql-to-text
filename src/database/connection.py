"""
Database connection and session management
"""
import os
from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool

from .models import Base


class DatabaseConnection:
    """Manages database connections and sessions"""
    
    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or os.getenv(
            "DATABASE_URL",
            "postgresql://analyst:lending_secure_pass_2024@localhost:5432/lending_club"
        )
        
        # Create async engine for FastAPI
        self.async_engine = create_async_engine(
            self.database_url.replace("postgresql://", "postgresql+asyncpg://"),
            echo=False,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20
        )
        
        # Create sync engine for scripts
        self.sync_engine = create_engine(
            self.database_url,
            echo=False,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10
        )
        
        # Session factories
        self.async_session_factory = async_sessionmaker(
            self.async_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        self.sync_session_factory = sessionmaker(
            self.sync_engine,
            expire_on_commit=False
        )
    
    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get async database session (for FastAPI)"""
        async with self.async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    def get_sync_session(self) -> Session:
        """Get sync database session (for scripts)"""
        return self.sync_session_factory()
    
    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """Context manager for async sessions"""
        async with self.async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
    
    async def health_check(self) -> bool:
        """Check database connectivity"""
        try:
            async with self.async_engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            print(f"Database health check failed: {e}")
            return False
    
    async def create_tables(self):
        """Create all tables (for testing/setup)"""
        async with self.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def drop_tables(self):
        """Drop all tables (for testing)"""
        async with self.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    
    async def close(self):
        """Close all connections"""
        await self.async_engine.dispose()
        self.sync_engine.dispose()


# Global database instance
db = DatabaseConnection()


# Dependency for FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for database sessions"""
    async for session in db.get_async_session():
        yield session


def test_connection() -> bool:
    """
    Synchronous database connection test (for health checks)

    Returns:
        True if database is accessible, False otherwise
    """
    try:
        with db.sync_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"Database connection test failed: {e}")
        return False


class TenantConnectionManager:
    """
    Manages connections to customer databases (multi-tenant support).

    Each customer can have their own database connection with connection pooling
    and automatic retry logic.
    """

    def __init__(self):
        self._pools = {}
        self._session_factories = {}

    async def get_engine(self, connection_id: str, database_url: str):
        """
        Get or create async engine for a customer connection.

        Args:
            connection_id: UUID of the customer connection
            database_url: Decrypted database URL

        Returns:
            SQLAlchemy async engine
        """
        if connection_id not in self._pools:
            # Detect database type and adjust URL
            if database_url.startswith('postgresql://') or database_url.startswith('postgres://'):
                # PostgreSQL
                async_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
            elif database_url.startswith('mysql://'):
                # MySQL
                async_url = database_url.replace("mysql://", "mysql+aiomysql://")
            else:
                raise ValueError(f"Unsupported database URL format")

            # Create engine with connection pooling
            self._pools[connection_id] = create_async_engine(
                async_url,
                echo=False,
                pool_pre_ping=True,
                pool_size=2,  # Smaller pool for customer DBs
                max_overflow=5,
                pool_recycle=3600  # Recycle connections every hour
            )

            # Create session factory
            self._session_factories[connection_id] = async_sessionmaker(
                self._pools[connection_id],
                class_=AsyncSession,
                expire_on_commit=False
            )

        return self._pools[connection_id]

    async def get_session(self, connection_id: str, database_url: str) -> AsyncSession:
        """
        Get async session for a customer connection.

        Args:
            connection_id: UUID of the customer connection
            database_url: Decrypted database URL

        Returns:
            AsyncSession
        """
        await self.get_engine(connection_id, database_url)
        return self._session_factories[connection_id]()

    async def execute_with_retry(
        self,
        connection_id: str,
        database_url: str,
        query: str,
        params: Optional[dict] = None,
        retries: int = 3
    ):
        """
        Execute a query with automatic retry on connection loss.

        Args:
            connection_id: UUID of the customer connection
            database_url: Decrypted database URL
            query: SQL query to execute
            params: Query parameters
            retries: Number of retry attempts (default 3)

        Returns:
            Query result

        Raises:
            Exception: If all retries fail
        """
        engine = await self.get_engine(connection_id, database_url)
        last_error = None

        for attempt in range(retries):
            try:
                async with engine.connect() as conn:
                    result = await conn.execute(text(query), params or {})
                    return result
            except Exception as e:
                last_error = e
                print(f"Query failed (attempt {attempt + 1}/{retries}): {e}")

                if attempt < retries - 1:
                    # Exponential backoff: 1s, 2s, 4s
                    import asyncio
                    await asyncio.sleep(2 ** attempt)
                    continue
                else:
                    # All retries exhausted
                    raise Exception(f"Query failed after {retries} attempts: {last_error}")

    async def close_connection(self, connection_id: str):
        """
        Close and remove a customer connection pool.

        Args:
            connection_id: UUID of the customer connection
        """
        if connection_id in self._pools:
            await self._pools[connection_id].dispose()
            del self._pools[connection_id]
            del self._session_factories[connection_id]

    async def close_all(self):
        """Close all customer connection pools."""
        for conn_id in list(self._pools.keys()):
            await self.close_connection(conn_id)


# Global tenant connection manager
tenant_manager = TenantConnectionManager()
