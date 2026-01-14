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


# Global database instance (lazy initialization)
_db_instance: Optional[DatabaseConnection] = None


def _get_db_instance() -> DatabaseConnection:
    """Get or create database instance (lazy initialization)"""
    global _db_instance
    if _db_instance is None:
        try:
            _db_instance = DatabaseConnection()
        except Exception as e:
            print(f"Error creating database connection: {e}")
            raise
    return _db_instance


# Lazy database instance - initialized on first access
class _LazyDB:
    """Lazy wrapper for database connection"""
    def __getattr__(self, name):
        return getattr(_get_db_instance(), name)
    
    def __call__(self):
        return _get_db_instance()


# Global database instance (lazy)
db = _LazyDB()


def get_database_url() -> str:
    """Get the database URL from environment or default"""
    return os.getenv(
        "DATABASE_URL",
        "postgresql://analyst:lending_secure_pass_2024@localhost:5432/lending_club"
    )


# Dependency for FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for database sessions"""
    db_instance = _get_db_instance()
    async for session in db_instance.get_async_session():
        yield session


def test_connection() -> bool:
    """
    Synchronous database connection test (for health checks)
    
    Returns:
        True if database is accessible, False otherwise
    """
    try:
        db_instance = _get_db_instance()
        with db_instance.sync_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"Database connection test failed: {e}")
        return False
