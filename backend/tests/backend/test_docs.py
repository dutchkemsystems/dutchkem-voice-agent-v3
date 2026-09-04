import pytest


@pytest.mark.asyncio
async def test_api_docs_returns_html(client):
    response = await client.get("/api-docs")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


@pytest.mark.asyncio
async def test_api_docs_contains_title(client):
    response = await client.get("/api-docs")
    html = response.text
    assert "API Documentation" in html or "API Docs" in html


@pytest.mark.asyncio
async def test_api_docs_uses_colourful_palette(client):
    response = await client.get("/api-docs")
    html = response.text
    assert "FF6B35" in html or "FF4444" in html or "gradient" in html.lower()
