import pytest
from httpx import AsyncClient, ASGITransport
from backend.config.app import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_list_modes():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/modes/")
    assert response.status_code == 200
    data = response.json()
    assert "modes" in data
    assert data["count"] == 9
    mode_ids = [m["mode_id"] for m in data["modes"]]
    assert "interview" in mode_ids
    assert "client_meeting" in mode_ids
    assert "sales" in mode_ids


@pytest.mark.anyio
async def test_get_mode_interview():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/modes/interview")
    assert response.status_code == 200
    data = response.json()
    assert data["mode_id"] == "interview"
    assert data["display_name"] == "Interview"
    assert "agent_classes" in data
    assert len(data["agent_classes"]) > 0


@pytest.mark.anyio
async def test_get_mode_not_found():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/modes/nonexistent")
    assert response.status_code == 404


@pytest.mark.anyio
async def test_switch_mode():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/modes/switch",
            json={"mode_id": "client_meeting"},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["mode"]["mode_id"] == "client_meeting"
    assert "Switched to" in data["message"]


@pytest.mark.anyio
async def test_switch_mode_invalid():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/modes/switch",
            json={"mode_id": "invalid_mode"},
        )
    assert response.status_code == 400


@pytest.mark.anyio
async def test_get_all_mode_fields():
    """Verify every mode returns all expected fields."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        list_resp = await client.get("/api/modes/")
    modes = list_resp.json()["modes"]
    expected_fields = {
        "mode_id", "display_name", "description", "icon",
        "agent_classes", "default_agent", "required_context",
        "ui_components", "default_view",
    }
    for mode in modes:
        assert expected_fields.issubset(mode.keys()), f"Mode {mode['mode_id']} missing fields"
