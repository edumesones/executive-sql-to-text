"""
FastAPI authentication dependencies.
"""
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import APIKeyCookie
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.connection import get_db
from src.database.models import User
from .jwt import decode_token


# Cookie-based authentication scheme
cookie_scheme = APIKeyCookie(name="access_token", auto_error=False)


async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[User]:
    """
    Fetch user by ID from database.

    Args:
        db: Database session
        user_id: User's UUID as string

    Returns:
        User object if found, None otherwise
    """
    from uuid import UUID
    try:
        result = await db.execute(
            select(User).where(User.id == UUID(user_id))
        )
        return result.scalar_one_or_none()
    except (ValueError, Exception):
        return None


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """
    Fetch user by email from database.

    Args:
        db: Database session
        email: User's email address

    Returns:
        User object if found, None otherwise
    """
    result = await db.execute(
        select(User).where(User.email == email)
    )
    return result.scalar_one_or_none()


async def get_current_user(
    request: Request,
    token: Optional[str] = Depends(cookie_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    FastAPI dependency to get current authenticated user.

    Extracts JWT from httpOnly cookie, validates it,
    and returns the corresponding User object.

    Args:
        request: FastAPI request object
        token: JWT token from cookie
        db: Database session

    Returns:
        Authenticated User object

    Raises:
        HTTPException: 401 if not authenticated or invalid token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        raise credentials_exception

    payload = decode_token(token)
    if not payload:
        raise credentials_exception

    user_id = payload.get("sub")
    if not user_id:
        raise credentials_exception

    user = await get_user_by_id(db, user_id)
    if not user:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled",
        )

    return user


async def get_current_user_optional(
    request: Request,
    token: Optional[str] = Depends(cookie_scheme),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    FastAPI dependency to optionally get current user.

    Returns None if not authenticated instead of raising exception.
    Useful for endpoints that work differently for authenticated vs anonymous users.

    Args:
        request: FastAPI request object
        token: JWT token from cookie
        db: Database session

    Returns:
        User object if authenticated, None otherwise
    """
    if not token:
        return None

    payload = decode_token(token)
    if not payload:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    user = await get_user_by_id(db, user_id)
    if not user or not user.is_active:
        return None

    return user
