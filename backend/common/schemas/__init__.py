"""
Pydantic schemas for user authentication.
"""
from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel, EmailStr, Field


class RoleEnum(str, Enum):
    """User role enumeration."""
    VIEWER = "viewer"
    OPERATOR = "operator"
    ADMIN = "admin"


class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=255)
    role: RoleEnum = RoleEnum.VIEWER


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8, max_length=128)


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    email: Optional[EmailStr] = None
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    role: Optional[RoleEnum] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for user response (excludes password)."""
    id: int
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    model_config = {"from_attributes": True}


class UserInDB(UserResponse):
    """User with hashed password (internal use only)."""
    hashed_password: str
    api_key: Optional[str] = None


class LoginRequest(BaseModel):
    """Schema for login request."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Schema for token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class RefreshRequest(BaseModel):
    """Schema for token refresh request."""
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    """Schema for password change."""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)


class APIKeyResponse(BaseModel):
    """Schema for API key generation response."""
    api_key: str
    message: str = "API key generated. Store it securely - it cannot be retrieved again."
