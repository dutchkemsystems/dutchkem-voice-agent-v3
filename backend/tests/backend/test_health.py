import pytest


@pytest.mark.asyncio
async def test_health_check_returns_ok(client):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("ok", "degraded")
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


@pytest.mark.asyncio
async def test_health_check_reports_service_status(client):
    response = await client.get("/health")
    data = response.json()
    for service_name, status in data["services"].items():
        assert status in ("connected", "disconnected"), f"Unexpected status for {service_name}"
