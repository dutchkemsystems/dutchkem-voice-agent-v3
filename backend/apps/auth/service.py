import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from jose import jwt, JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import settings
from apps.auth.models import User


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        return None


async def register_user(db: AsyncSession, email: str, username: str, password: str) -> User:
    existing = await db.execute(
        select(User).where((User.email == email) | (User.username == username))
    )
    if existing.scalars().first():
        raise ValueError("User already exists")

    user = User(
        id=str(uuid.uuid4()),
        email=email,
        username=username,
        hashed_password=hash_password(password),
        is_active=True,
    )
    db.add(user)
    await db.commit()
    return user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()

    if not user:
        raise ValueError("Invalid credentials")
    if not user.is_active:
        raise PermissionError("Account is inactive")
    if not verify_password(password, user.hashed_password):
        raise ValueError("Invalid credentials")
    return user
