import uuid
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import get_db
from apps.auth.schemas import (
    UserRegister,
    UserResponse,
    UserLogin,
    TokenResponse,
    TokenRefreshRequest,
    AccessTokenResponse,
)
from apps.auth.service import (
    register_user,
    authenticate_user,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from apps.auth.dependencies import get_current_user
from apps.auth.models import User
from apps.auth.rate_limiter import limiter, REGISTER_LIMIT, LOGIN_LIMIT, TOKEN_REFRESH_LIMIT

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(REGISTER_LIMIT)
async def register(request: Request, body: UserRegister, db: AsyncSession = Depends(get_db)):
    try:
        user = await register_user(db, body.email, body.username, body.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        is_active=user.is_active,
        voice_profile_id=user.voice_profile_id,
        created_at=user.created_at.isoformat() if user.created_at else "",
    )


@router.post("/login", response_model=TokenResponse)
@limiter.limit(LOGIN_LIMIT)
async def login(request: Request, body: UserLogin, db: AsyncSession = Depends(get_db)):
    try:
        user = await authenticate_user(db, body.email, body.password)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token({"sub": user.email})
    refresh_token = create_refresh_token({"sub": user.email})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/refresh", response_model=AccessTokenResponse)
@limiter.limit(TOKEN_REFRESH_LIMIT)
async def refresh_token(request: Request, body: TokenRefreshRequest):
    payload = decode_token(body.refresh_token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    access_token = create_access_token({"sub": payload["sub"]})
    return AccessTokenResponse(access_token=access_token)


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        is_active=current_user.is_active,
        voice_profile_id=current_user.voice_profile_id,
        created_at=current_user.created_at.isoformat() if current_user.created_at else "",
    )
