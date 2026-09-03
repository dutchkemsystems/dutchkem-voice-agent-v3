import pytest
import bcrypt as _bcrypt
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI

from config.app import app
from config.database import get_db
from apps.auth.dependencies import get_current_user


def _hash_password(password: str) -> str:
    return _bcrypt.hashpw(password.encode(), _bcrypt.gensalt()).decode()


def _make_mock_session(return_value=None):
    mock_session = AsyncMock()
    mock_session.execute = AsyncMock(
        return_value=MagicMock(
            scalars=MagicMock(
                return_value=MagicMock(first=MagicMock(return_value=return_value))
            )
        )
    )
    mock_session.commit = AsyncMock()
    return mock_session


async def _override_get_db():
    yield _make_mock_session()


async def _override_get_db_with_user(user):
    async def _gen():
        yield _make_mock_session(return_value=user)
    return _gen()


@pytest.fixture(autouse=True)
def setup_overrides():
    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Registration tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_register_success(client):
    """Registering a new user returns 201 with user info (no password leak)."""
    payload = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "StrongPass1!",
    }
    response = await client.post("/auth/register", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"
    assert "password" not in data
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    """Registering with an existing email returns 409."""
    existing_user = MagicMock()
    existing_user.email = "dup@example.com"

    async def _override_with_existing():
        yield _make_mock_session(return_value=existing_user)

    app.dependency_overrides[get_db] = _override_with_existing

    payload = {
        "email": "dup@example.com",
        "username": "user1",
        "password": "StrongPass1!",
    }
    response = await client.post("/auth/register", json=payload)

    assert response.status_code == 409
    assert "already exists" in response.json()["detail"].lower() or "already registered" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_register_weak_password(client):
    """Registering with a weak password returns 422."""
    payload = {
        "email": "weak@example.com",
        "username": "weakuser",
        "password": "123",
    }
    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Login tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_login_success(client):
    """Valid credentials return access + refresh tokens."""
    payload = {"email": "login@example.com", "password": "StrongPass1!"}
    mock_user = MagicMock()
    mock_user.email = "login@example.com"
    mock_user.username = "loginuser"
    mock_user.hashed_password = _hash_password("StrongPass1!")
    mock_user.is_active = True

    async def _override_with_user():
        yield _make_mock_session(return_value=mock_user)

    app.dependency_overrides[get_db] = _override_with_user

    response = await client.post("/auth/login", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    """Wrong password returns 401."""
    payload = {"email": "login@example.com", "password": "WrongPass1!"}
    mock_user = MagicMock()
    mock_user.email = "login@example.com"
    mock_user.hashed_password = _hash_password("StrongPass1!")
    mock_user.is_active = True

    async def _override_with_user():
        yield _make_mock_session(return_value=mock_user)

    app.dependency_overrides[get_db] = _override_with_user

    response = await client.post("/auth/login", json=payload)

    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower() or "incorrect" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_nonexistent_user(client):
    """Login with non-existent email returns 401."""
    payload = {"email": "nobody@example.com", "password": "StrongPass1!"}
    response = await client.post("/auth/login", json=payload)

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_inactive_user(client):
    """Login for inactive user returns 403."""
    payload = {"email": "inactive@example.com", "password": "StrongPass1!"}
    mock_user = MagicMock()
    mock_user.email = "inactive@example.com"
    mock_user.hashed_password = _hash_password("StrongPass1!")
    mock_user.is_active = False

    async def _override_with_user():
        yield _make_mock_session(return_value=mock_user)

    app.dependency_overrides[get_db] = _override_with_user

    response = await client.post("/auth/login", json=payload)

    assert response.status_code == 403
    assert "inactive" in response.json()["detail"].lower() or "disabled" in response.json()["detail"].lower()


# ---------------------------------------------------------------------------
# Token refresh tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_token_refresh_success(client):
    """Valid refresh token returns new access token."""
    from apps.auth.service import create_refresh_token

    refresh_token = create_refresh_token({"sub": "user@example.com"})

    response = await client.post("/auth/refresh", json={"refresh_token": refresh_token})

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_token_refresh_invalid_token(client):
    """Invalid refresh token returns 401."""
    response = await client.post("/auth/refresh", json={"refresh_token": "invalid.token.here"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_token_refresh_expired_token(client):
    """Expired refresh token returns 401."""
    from jose import jwt
    from config.settings import settings

    expired_payload = {
        "sub": "user@example.com",
        "exp": datetime.now(timezone.utc) - timedelta(hours=1),
        "type": "refresh",
    }
    expired_token = jwt.encode(expired_payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

    response = await client.post("/auth/refresh", json={"refresh_token": expired_token})
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Get current user (protected endpoint) tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_current_user_success(client):
    """Valid access token returns current user info."""
    from apps.auth.service import create_access_token

    token = create_access_token({"sub": "user@example.com"})
    headers = {"Authorization": f"Bearer {token}"}

    mock_user = MagicMock()
    mock_user.id = "user-uuid-123"
    mock_user.email = "user@example.com"
    mock_user.username = "testuser"
    mock_user.is_active = True
    mock_user.voice_profile_id = None
    mock_user.created_at = datetime.now(timezone.utc)

    async def _override_with_user():
        yield _make_mock_session(return_value=mock_user)

    app.dependency_overrides[get_db] = _override_with_user

    response = await client.get("/auth/me", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "user@example.com"


@pytest.mark.asyncio
async def test_get_current_user_no_token(client):
    """Missing token returns 401."""
    response = await client.get("/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_expired_token(client):
    """Expired access token returns 401."""
    from jose import jwt
    from config.settings import settings

    expired_payload = {
        "sub": "user@example.com",
        "exp": datetime.now(timezone.utc) - timedelta(hours=1),
        "type": "access",
    }
    expired_token = jwt.encode(expired_payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    headers = {"Authorization": f"Bearer {expired_token}"}

    response = await client.get("/auth/me", headers=headers)
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Token service unit tests
# ---------------------------------------------------------------------------

def test_create_access_token():
    """create_access_token returns a valid JWT string."""
    from apps.auth.service import create_access_token

    token = create_access_token({"sub": "test@example.com"})
    assert isinstance(token, str)
    assert len(token) > 0


def test_create_refresh_token():
    """create_refresh_token returns a valid JWT string."""
    from apps.auth.service import create_refresh_token

    token = create_refresh_token({"sub": "test@example.com"})
    assert isinstance(token, str)
    assert len(token) > 0


def test_decode_valid_token():
    """decode_token returns payload for a valid token."""
    from apps.auth.service import create_access_token, decode_token

    token = create_access_token({"sub": "test@example.com"})
    payload = decode_token(token)
    assert payload["sub"] == "test@example.com"


def test_decode_invalid_token():
    """decode_token returns None for an invalid token."""
    from apps.auth.service import decode_token

    result = decode_token("not.a.valid.token")
    assert result is None
