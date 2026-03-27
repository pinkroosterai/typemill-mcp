import httpx
import pytest
import respx

from typemill_mcp.client import TypemillClient


@pytest.fixture
def client():
    return TypemillClient("https://example.com", "user", "pass")


@respx.mock
@pytest.mark.asyncio
async def test_get_article_content(client):
    respx.get("https://example.com/api/v1/article/content").mock(
        return_value=httpx.Response(
            200,
            json={
                "content": [
                    {"id": 0, "markdown": "# Hello", "html": "<h1>Hello</h1>"}
                ]
            },
        )
    )
    result = await client.get_article_content("/getting-started")
    assert result["content"][0]["markdown"] == "# Hello"


@respx.mock
@pytest.mark.asyncio
async def test_get_article_meta(client):
    respx.get("https://example.com/api/v1/article/meta").mock(
        return_value=httpx.Response(
            200,
            json={"meta": {"meta": {"title": "Test Page"}}},
        )
    )
    result = await client.get_article_meta("/getting-started")
    assert result["meta"]["meta"]["title"] == "Test Page"


@respx.mock
@pytest.mark.asyncio
async def test_create_article(client):
    respx.post("https://example.com/api/v1/article").mock(
        return_value=httpx.Response(200, json={"navigation": []})
    )
    result = await client.create_article("root", "new-page")
    assert "navigation" in result


@respx.mock
@pytest.mark.asyncio
async def test_update_draft(client):
    respx.put("https://example.com/api/v1/draft").mock(
        return_value=httpx.Response(200, json={"item": {}})
    )
    result = await client.update_draft("/test", "0", "# Title", "Some paragraph content.")
    assert "item" in result


@respx.mock
@pytest.mark.asyncio
async def test_delete_article(client):
    respx.delete("https://example.com/api/v1/article").mock(
        return_value=httpx.Response(200, json={"url": "/tm/content"})
    )
    result = await client.delete_article("/test", "0")
    assert result is not None


@respx.mock
@pytest.mark.asyncio
async def test_api_error_raises(client):
    respx.get("https://example.com/api/v1/article/content").mock(
        return_value=httpx.Response(404, text="Not found")
    )
    with pytest.raises(RuntimeError, match="404"):
        await client.get_article_content("/missing")
