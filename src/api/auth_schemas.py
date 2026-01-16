"""
Pydantic schemas for authentication endpoints.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    """Request schema for user registration"""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(
        ...,
        min_length=8,
        description="Password (min 8 chars, must contain uppercase, lowercase, and digit)"
    )


class UserLoginRequest(BaseModel):
    """Request schema for user login"""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")


class TokenResponse(BaseModel):
    """Response schema for successful authentication"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")


class UserResponse(BaseModel):
    """Response schema for user information"""
    id: str = Field(..., description="User's UUID")
    email: str = Field(..., description="User's email address")
    is_active: bool = Field(..., description="Whether user account is active")
    created_at: datetime = Field(..., description="Account creation timestamp")

    class Config:
        from_attributes = True


class ForgotPasswordRequest(BaseModel):
    """Request schema for forgot password flow"""
    email: EmailStr = Field(..., description="Email address for password reset")


class ResetPasswordRequest(BaseModel):
    """Request schema for password reset"""
    token: str = Field(..., description="Password reset token from email")
    new_password: str = Field(
        ...,
        min_length=8,
        description="New password (min 8 chars, must contain uppercase, lowercase, and digit)"
    )


class ChangePasswordRequest(BaseModel):
    """Request schema for changing password (when logged in)"""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(
        ...,
        min_length=8,
        description="New password (min 8 chars, must contain uppercase, lowercase, and digit)"
    )


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str = Field(..., description="Response message")
