import pytest


@pytest.mark.asyncio
async def test_health_check_returns_ok(client):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "services" in data


@pytest.mark.asyncio
async def test_health_check_includes_services(client):
    response = await client.get("/health")
    data = response.json()
    services = data["services"]
    assert "database" in services
    assert "redis" in services
    assert "mongodb" in services
