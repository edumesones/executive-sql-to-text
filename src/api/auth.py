"""
Authentication API endpoints.
"""
import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.connection import get_db
from src.database.models import User, PasswordResetToken
from src.auth.password import hash_password, verify_password, validate_password_strength
from src.auth.jwt import (
    create_access_token,
    create_password_reset_token,
    get_password_reset_expiry,
    is_token_expired
)
from src.auth.dependencies import get_current_user, get_user_by_email

from .auth_schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    UserResponse,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    ChangePasswordRequest,
    MessageResponse,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Rate limiting constants
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_MINUTES = 15

# Cookie configuration
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "true").lower() == "true"
COOKIE_SAMESITE = os.getenv("COOKIE_SAMESITE", "lax")
COOKIE_MAX_AGE = 86400  # 24 hours


async def check_login_lockout(user: User) -> bool:
    """
    Check if user is currently locked out due to failed login attempts.

    Args:
        user: User object to check

    Returns:
        True if locked out, False otherwise
    """
    if user.locked_until and user.locked_until > datetime.utcnow():
        return True
    return False


async def increment_failed_attempts(user: User, db: AsyncSession):
    """
    Increment failed login attempts and lock account if threshold reached.

    Args:
        user: User object
        db: Database session
    """
    user.failed_login_attempts += 1
    if user.failed_login_attempts >= MAX_LOGIN_ATTEMPTS:
        user.locked_until = datetime.utcnow() + timedelta(minutes=LOCKOUT_MINUTES)
    await db.commit()


async def reset_failed_attempts(user: User, db: AsyncSession):
    """
    Reset failed login attempts on successful login.

    Args:
        user: User object
        db: Database session
    """
    user.failed_login_attempts = 0
    user.locked_until = None
    await db.commit()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: UserRegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user account.

    - Validates password strength
    - Checks for existing email
    - Creates user with hashed password
    """
    # Validate password strength
    is_valid, error_msg = validate_password_strength(request.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )

    # Check if email already exists
    existing_user = await get_user_by_email(db, request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    new_user = User(
        email=request.email,
        hashed_password=hash_password(request.password)
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return UserResponse(
        id=str(new_user.id),
        email=new_user.email,
        is_active=new_user.is_active,
        created_at=new_user.created_at
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: UserLoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user and set JWT cookie.

    - Validates credentials
    - Checks for account lockout
    - Sets httpOnly cookie with JWT token
    """
    # Find user by email
    user = await get_user_by_email(db, request.email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Check if account is locked
    if await check_login_lockout(user):
        remaining_time = (user.locked_until - datetime.utcnow()).seconds // 60
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"Account locked. Try again in {remaining_time + 1} minutes."
        )

    # Verify password
    if not verify_password(request.password, user.hashed_password):
        await increment_failed_attempts(user, db)

        attempts_remaining = MAX_LOGIN_ATTEMPTS - user.failed_login_attempts
        if attempts_remaining > 0:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid email or password. {attempts_remaining} attempts remaining."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail=f"Account locked for {LOCKOUT_MINUTES} minutes due to too many failed attempts."
            )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is disabled"
        )

    # Reset failed attempts on successful login
    await reset_failed_attempts(user, db)

    # Create JWT token
    access_token = create_access_token(data={"sub": str(user.id)})

    # Set httpOnly cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=COOKIE_MAX_AGE
    )

    return TokenResponse(access_token=access_token)


@router.post("/logout", response_model=MessageResponse)
async def logout(response: Response):
    """
    Logout user by clearing the JWT cookie.
    """
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE
    )
    return MessageResponse(message="Logged out successfully")


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user's information.
    """
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    request: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Initiate password reset flow.

    - Creates a password reset token
    - Sends reset email via SendGrid
    - Always returns success to prevent email enumeration
    """
    # Find user (don't reveal if email exists)
    user = await get_user_by_email(db, request.email)

    if user and user.is_active:
        # Create password reset token
        token = create_password_reset_token(str(user.id))
        expires_at = get_password_reset_expiry()

        # Save token to database
        reset_token = PasswordResetToken(
            user_id=user.id,
            token=token,
            expires_at=expires_at
        )
        db.add(reset_token)
        await db.commit()

        # Send email (import here to avoid circular imports)
        try:
            from src.auth.email import send_password_reset_email
            await send_password_reset_email(user.email, token)
        except Exception as e:
            # Log error but don't expose it to user
            print(f"Failed to send password reset email: {e}")

    # Always return success to prevent email enumeration
    return MessageResponse(
        message="If your email is registered, you will receive a password reset link."
    )


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    request: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Reset password using token from email.

    - Validates token
    - Validates new password strength
    - Updates password and invalidates token
    """
    # Validate new password strength
    is_valid, error_msg = validate_password_strength(request.new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )

    # Find the reset token
    result = await db.execute(
        select(PasswordResetToken).where(
            PasswordResetToken.token == request.token,
            PasswordResetToken.used == False
        )
    )
    reset_token = result.scalar_one_or_none()

    if not reset_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

    # Check if token is expired
    if is_token_expired(reset_token.expires_at):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired"
        )

    # Get the user
    user_result = await db.execute(
        select(User).where(User.id == reset_token.user_id)
    )
    user = user_result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset token"
        )

    # Update password
    user.hashed_password = hash_password(request.new_password)
    user.failed_login_attempts = 0
    user.locked_until = None

    # Mark token as used
    reset_token.used = True

    await db.commit()

    return MessageResponse(message="Password has been reset successfully")


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Change password for authenticated user.

    - Requires current password verification
    - Validates new password strength
    """
    # Verify current password
    if not verify_password(request.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    # Validate new password strength
    is_valid, error_msg = validate_password_strength(request.new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )

    # Update password
    current_user.hashed_password = hash_password(request.new_password)
    await db.commit()

    return MessageResponse(message="Password changed successfully")


@router.delete("/account", response_model=MessageResponse)
async def delete_account(
    response: Response,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete user account (hard delete as per spec).

    - Deletes all user data immediately
    - Clears authentication cookie
    """
    # Delete user (cascade will handle related records)
    await db.delete(current_user)
    await db.commit()

    # Clear cookie
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE
    )

    return MessageResponse(message="Account deleted successfully")
