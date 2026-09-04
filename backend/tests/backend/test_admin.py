import pytest


@pytest.mark.asyncio
async def test_admin_dashboard_returns_html(client):
    response = await client.get("/admin/", follow_redirects=True)
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


@pytest.mark.asyncio
async def test_admin_dashboard_contains_dashboard_title(client):
    response = await client.get("/admin/", follow_redirects=True)
    html = response.text
    assert "Admin Dashboard" in html


@pytest.mark.asyncio
async def test_admin_dashboard_uses_colourful_palette(client):
    response = await client.get("/admin/", follow_redirects=True)
    html = response.text
    assert "FF6B6B" in html or "FF8E53" in html or "gradient" in html.lower()
