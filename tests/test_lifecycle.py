import httpx
import pytest
import respx

from typemill_mcp.client import TypemillClient


@pytest.fixture
def client():
    return TypemillClient("https://example.com", "user", "pass")


@respx.mock
@pytest.mark.asyncio
async def test_publish_article(client):
    respx.post("https://example.com/api/v1/article/publish").mock(
        return_value=httpx.Response(200, json={"navigation": []})
    )
    result = await client.publish_article("/test", "0")
    assert "navigation" in result


@respx.mock
@pytest.mark.asyncio
async def test_unpublish_article(client):
    respx.delete("https://example.com/api/v1/article/unpublish").mock(
        return_value=httpx.Response(200, json={"navigation": []})
    )
    result = await client.unpublish_article("/test", "0")
    assert "navigation" in result


@respx.mock
@pytest.mark.asyncio
async def test_discard_article(client):
    respx.delete("https://example.com/api/v1/article/discard").mock(
        return_value=httpx.Response(200, json={"navigation": []})
    )
    result = await client.discard_article("/test", "0")
    assert "navigation" in result


@respx.mock
@pytest.mark.asyncio
async def test_publish_permission_error(client):
    respx.post("https://example.com/api/v1/article/publish").mock(
        return_value=httpx.Response(403, text="Forbidden")
    )
    with pytest.raises(RuntimeError, match="403"):
        await client.publish_article("/restricted", "0")
