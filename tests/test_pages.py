import httpx
import pytest
import respx

from typemill_mcp.client import TypemillClient


@pytest.fixture
def client():
    return TypemillClient("https://example.com", "user", "pass")


@respx.mock
@pytest.mark.asyncio
async def test_get_article_markdown(client):
    respx.post("https://example.com/api/v1/article/markdown").mock(
        return_value=httpx.Response(
            200,
            json={
                "content": [
                    {"id": 0, "markdown": "# Hello", "html": "<h1>Hello</h1>"}
                ]
            },
        )
    )
    result = await client.get_article_markdown("/getting-started")
    assert result["content"][0]["markdown"] == "# Hello"


@respx.mock
@pytest.mark.asyncio
async def test_get_article_metadata(client):
    respx.get("https://example.com/api/v1/article/metadata").mock(
        return_value=httpx.Response(
            200,
            json={"metadata": {"meta": {"title": "Test Page"}}},
        )
    )
    result = await client.get_article_metadata("/getting-started")
    assert result["metadata"]["meta"]["title"] == "Test Page"


@respx.mock
@pytest.mark.asyncio
async def test_create_article(client):
    respx.post("https://example.com/api/v1/article").mock(
        return_value=httpx.Response(200, json={"success": True})
    )
    result = await client.create_article("/docs/new", "New Page", "# Content")
    assert result["success"] is True


@respx.mock
@pytest.mark.asyncio
async def test_update_article(client):
    respx.put("https://example.com/api/v1/article").mock(
        return_value=httpx.Response(200, json={"success": True})
    )
    result = await client.update_article("/docs/test", "# Updated")
    assert result["success"] is True


@respx.mock
@pytest.mark.asyncio
async def test_delete_article(client):
    respx.delete("https://example.com/api/v1/article").mock(
        return_value=httpx.Response(200, json={"success": True})
    )
    result = await client.delete_article("/docs/test")
    assert result["success"] is True


@respx.mock
@pytest.mark.asyncio
async def test_api_error_raises(client):
    respx.post("https://example.com/api/v1/article/markdown").mock(
        return_value=httpx.Response(404, text="Not found")
    )
    with pytest.raises(RuntimeError, match="404"):
        await client.get_article_markdown("/missing")
