import httpx
import pytest
import respx

from typemill_mcp.client import TypemillClient


@pytest.fixture
def client():
    return TypemillClient("https://example.com", "user", "pass")


@respx.mock
@pytest.mark.asyncio
async def test_get_article_metadata(client):
    respx.get("https://example.com/api/v1/article/metadata").mock(
        return_value=httpx.Response(
            200,
            json={"metadata": {"meta": {"title": "Test", "description": "A test page"}}},
        )
    )
    result = await client.get_article_metadata("/getting-started")
    assert result["metadata"]["meta"]["title"] == "Test"
    assert result["metadata"]["meta"]["description"] == "A test page"


@respx.mock
@pytest.mark.asyncio
async def test_update_article_metadata(client):
    respx.post("https://example.com/api/v1/article/metadata").mock(
        return_value=httpx.Response(200, json={"success": True})
    )
    result = await client.update_article_metadata(
        "/getting-started", {"title": "Updated Title"}
    )
    assert result["success"] is True


@respx.mock
@pytest.mark.asyncio
async def test_get_meta_definitions(client):
    respx.get("https://example.com/api/v1/metadefinitions").mock(
        return_value=httpx.Response(200, json={"definitions": []})
    )
    result = await client.get_meta_definitions()
    assert result["definitions"] == []


@respx.mock
@pytest.mark.asyncio
async def test_metadata_auth_error(client):
    respx.get("https://example.com/api/v1/article/metadata").mock(
        return_value=httpx.Response(401, text="Unauthorized")
    )
    with pytest.raises(RuntimeError, match="401"):
        await client.get_article_metadata("/restricted")
