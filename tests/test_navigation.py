import json
import httpx
import pytest
import respx

from typemill_mcp.client import TypemillClient


@pytest.fixture
def client():
    return TypemillClient("https://example.com", "user", "pass")


@respx.mock
@pytest.mark.asyncio
async def test_get_navigation(client):
    respx.get("https://example.com/api/v1/navigation").mock(
        return_value=httpx.Response(
            200,
            json={"navigation": [{"title": "Home", "url": "/"}]},
        )
    )
    result = await client.get_navigation()
    assert result["navigation"][0]["title"] == "Home"


@respx.mock
@pytest.mark.asyncio
async def test_get_navigation_formatted(client):
    respx.get("https://example.com/api/v1/navigation").mock(
        return_value=httpx.Response(
            200,
            json={"navigation": [{"title": "Home", "url": "/"}]},
        )
    )
    result = await client.get_navigation()
    formatted = json.dumps(result, indent=2)
    assert "Home" in formatted


@respx.mock
@pytest.mark.asyncio
async def test_get_navigation_without_draft(client):
    route = respx.get("https://example.com/api/v1/navigation").mock(
        return_value=httpx.Response(
            200,
            json={"navigation": [{"title": "Home", "url": "/"}]},
        )
    )
    await client.get_navigation(draft=False)
    assert "draft" not in str(route.calls[0].request.url)


@respx.mock
@pytest.mark.asyncio
async def test_get_navigation_with_draft(client):
    route = respx.get("https://example.com/api/v1/navigation").mock(
        return_value=httpx.Response(
            200,
            json={"navigation": [{"title": "Home", "url": "/"}]},
        )
    )
    await client.get_navigation(draft=True)
    assert "draft=true" in str(route.calls[0].request.url)
