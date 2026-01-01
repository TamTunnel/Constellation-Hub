"""
Authentication API routes.

These routes handle user authentication, token management, and user CRUD operations.
Mount this router in each service that needs auth endpoints.
"""
from datetime import datetime, timezone, timedelta
from typing import List, Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from .auth import (
    Role, TokenData, get_password_hash, verify_password,
    create_access_token, create_refresh_token, decode_token,
    generate_api_key, require_auth, require_role,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from .schemas import (
    UserCreate, UserUpdate, UserResponse, UserInDB,
    LoginRequest, TokenResponse, RefreshRequest,
    ChangePasswordRequest, APIKeyResponse, RoleEnum
)
from .models.user import UserORM


router = APIRouter(prefix="/auth", tags=["Authentication"])


async def get_user_by_email(db: AsyncSession, email: str) -> UserORM | None:
    """Get user by email address."""
    result = await db.execute(select(UserORM).where(UserORM.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int) -> UserORM | None:
    """Get user by ID."""
    return await db.get(UserORM, user_id)


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession
):
    """
    Authenticate user and return access/refresh tokens.

    - **email**: User's email address
    - **password**: User's password

    Returns JWT tokens for authenticated requests.
    """
    user = await get_user_by_email(db, request.email)

    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )

    # Update last login
    user.last_login = datetime.now(timezone.utc)
    await db.commit()

    # Create tokens
    access_token = create_access_token(
        user_id=user.id,
        email=user.email,
        role=Role(user.role)
    )
    refresh_token = create_refresh_token(user_id=user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshRequest,
    db: AsyncSession
):
    """
    Refresh access token using a valid refresh token.
    """
    try:
        # Decode refresh token (it doesn't have email/role, just user_id)
        from jose import jwt
        from .config import get_settings
        settings = get_settings()
        payload = jwt.decode(request.refresh_token, settings.jwt_secret_key, algorithms=["HS256"])

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )

        user_id = int(payload.get("sub"))
        user = await get_user_by_id(db, user_id)

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or disabled"
            )

        # Create new tokens
        access_token = create_access_token(
            user_id=user.id,
            email=user.email,
            role=Role(user.role)
        )
        new_refresh_token = create_refresh_token(user_id=user.id)

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid refresh token: {str(e)}"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Annotated[TokenData, Depends(require_auth)],
    db: AsyncSession
):
    """
    Get information about the currently authenticated user.
    """
    user = await get_user_by_id(db, current_user.user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse.model_validate(user)


@router.get("/users", response_model=List[UserResponse])
async def list_users(
    _: Annotated[TokenData, Depends(require_role(Role.ADMIN))],
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100
):
    """
    List all users (admin only).
    """
    result = await db.execute(
        select(UserORM).offset(skip).limit(limit)
    )
    users = result.scalars().all()
    return [UserResponse.model_validate(u) for u in users]


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    _: Annotated[TokenData, Depends(require_role(Role.ADMIN))],
    db: AsyncSession
):
    """
    Create a new user (admin only).
    """
    # Check if email already exists
    existing = await get_user_by_email(db, user_data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user
    user = UserORM(
        email=user_data.email,
        name=user_data.name,
        role=user_data.role.value,
        hashed_password=get_password_hash(user_data.password),
        is_active=True
    )

    db.add(user)

    try:
        await db.commit()
        await db.refresh(user)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    return UserResponse.model_validate(user)


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    _: Annotated[TokenData, Depends(require_role(Role.ADMIN))],
    db: AsyncSession
):
    """
    Update a user (admin only).
    """
    user = await get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update fields
    if user_data.email is not None:
        user.email = user_data.email
    if user_data.name is not None:
        user.name = user_data.name
    if user_data.role is not None:
        user.role = user_data.role.value
    if user_data.is_active is not None:
        user.is_active = user_data.is_active

    await db.commit()
    await db.refresh(user)

    return UserResponse.model_validate(user)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    _: Annotated[TokenData, Depends(require_role(Role.ADMIN))],
    db: AsyncSession
):
    """
    Delete a user (admin only).
    """
    user = await get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    await db.delete(user)
    await db.commit()


@router.post("/me/password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: Annotated[TokenData, Depends(require_auth)],
    db: AsyncSession
):
    """
    Change current user's password.
    """
    user = await get_user_by_id(db, current_user.user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if not verify_password(request.current_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    user.hashed_password = get_password_hash(request.new_password)
    await db.commit()

    return {"message": "Password changed successfully"}


@router.post("/me/api-key", response_model=APIKeyResponse)
async def generate_user_api_key(
    current_user: Annotated[TokenData, Depends(require_auth)],
    db: AsyncSession
):
    """
    Generate a new API key for the current user.

    Warning: The API key is only shown once. Store it securely.
    """
    user = await get_user_by_id(db, current_user.user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Generate new API key
    api_key = generate_api_key()
    user.api_key = get_password_hash(api_key)  # Store hashed
    await db.commit()

    return APIKeyResponse(api_key=api_key)


# Bootstrap route for initial admin setup
@router.post("/bootstrap", response_model=UserResponse)
async def bootstrap_admin(
    user_data: UserCreate,
    db: AsyncSession
):
    """
    Create the initial admin user.

    This endpoint only works when no users exist in the database.
    After the first admin is created, this endpoint returns 403.
    """
    # Check if any users exist
    result = await db.execute(select(UserORM).limit(1))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bootstrap is disabled - users already exist"
        )

    # Create admin user
    user = UserORM(
        email=user_data.email,
        name=user_data.name,
        role="admin",  # Force admin role
        hashed_password=get_password_hash(user_data.password),
        is_active=True
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return UserResponse.model_validate(user)
