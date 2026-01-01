"""
Authentication and authorization utilities for Constellation Hub.

Implements JWT-based authentication with role-based access control (RBAC).
Supports both JWT tokens and API keys for different use cases.
"""
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional, Annotated
import secrets

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from .config import get_settings


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7


class Role(str, Enum):
    """User roles with increasing privileges."""
    VIEWER = "viewer"       # Can view data
    OPERATOR = "operator"   # Can modify schedules, trigger actions
    ADMIN = "admin"         # Full access including user management


class TokenData(BaseModel):
    """Data extracted from JWT token."""
    user_id: int
    email: str
    role: Role
    exp: datetime


class TokenResponse(BaseModel):
    """Response containing access and refresh tokens."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


# Security schemes
bearer_scheme = HTTPBearer(auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def generate_api_key() -> str:
    """Generate a secure API key."""
    return secrets.token_urlsafe(32)


def create_access_token(
    user_id: int,
    email: str,
    role: Role,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create a JWT access token."""
    settings = get_settings()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {
        "sub": str(user_id),
        "email": email,
        "role": role.value,
        "exp": expire,
        "type": "access"
    }

    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(user_id: int) -> str:
    """Create a JWT refresh token."""
    settings = get_settings()

    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh"
    }

    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> TokenData:
    """Decode and validate a JWT token."""
    settings = get_settings()

    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        email = payload.get("email", "")
        role = Role(payload.get("role", "viewer"))
        exp = datetime.fromtimestamp(payload.get("exp"), tz=timezone.utc)

        return TokenData(user_id=user_id, email=email, role=role, exp=exp)
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(bearer_scheme)],
    api_key: Annotated[Optional[str], Depends(api_key_header)],
    request: Request
) -> TokenData:
    """
    Extract and validate the current user from request.

    Supports both Bearer token and API key authentication.
    Returns TokenData if valid, raises HTTPException otherwise.
    """
    settings = get_settings()

    # Check if auth is disabled (dev mode)
    if settings.auth_disabled:
        return TokenData(
            user_id=0,
            email="dev@localhost",
            role=Role.ADMIN,
            exp=datetime.now(timezone.utc) + timedelta(days=365)
        )

    # Try Bearer token first
    if credentials and credentials.credentials:
        return decode_token(credentials.credentials)

    # Try API key
    if api_key:
        # Validate API key against database or config
        # For now, check against a configured admin API key
        if api_key == settings.admin_api_key and settings.admin_api_key:
            return TokenData(
                user_id=0,
                email="api-user@localhost",
                role=Role.ADMIN,
                exp=datetime.now(timezone.utc) + timedelta(days=365)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
            )

    # No auth provided
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )


def require_auth(
    current_user: Annotated[TokenData, Depends(get_current_user)]
) -> TokenData:
    """
    Dependency that requires authentication.

    Use as: Depends(require_auth)
    """
    return current_user


def require_role(required_role: Role):
    """
    Dependency factory that requires a specific role or higher.

    Role hierarchy: viewer < operator < admin

    Usage:
        @router.post("/schedules")
        async def create_schedule(user: TokenData = Depends(require_role(Role.OPERATOR))):
            ...
    """
    role_hierarchy = {Role.VIEWER: 0, Role.OPERATOR: 1, Role.ADMIN: 2}

    async def role_checker(
        current_user: Annotated[TokenData, Depends(get_current_user)]
    ) -> TokenData:
        if role_hierarchy.get(current_user.role, 0) < role_hierarchy.get(required_role, 0):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires {required_role.value} role or higher"
            )
        return current_user

    return role_checker


# Pre-built role dependencies for convenience
require_viewer = require_role(Role.VIEWER)
require_operator = require_role(Role.OPERATOR)
require_admin = require_role(Role.ADMIN)
