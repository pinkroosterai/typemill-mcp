import httpx
import pytest
import respx

from typemill_mcp.client import TypemillClient


@pytest.fixture
def client():
    return TypemillClient("https://example.com", "user", "pass")


@respx.mock
@pytest.mark.asyncio
async def test_get_metadata(client):
    respx.get("https://example.com/api/v1/meta").mock(
        return_value=httpx.Response(
            200,
            json={"metadata": {"meta": {"title": "Test", "description": "A test page"}}},
        )
    )
    result = await client.get_metadata("/getting-started")
    assert result["metadata"]["meta"]["title"] == "Test"


@respx.mock
@pytest.mark.asyncio
async def test_update_metadata(client):
    respx.post("https://example.com/api/v1/meta").mock(
        return_value=httpx.Response(200, json={"success": True})
    )
    result = await client.update_metadata(
        "/getting-started", {"title": "Updated Title"}
    )
    assert result["success"] is True


@respx.mock
@pytest.mark.asyncio
async def test_metadata_auth_error(client):
    respx.get("https://example.com/api/v1/meta").mock(
        return_value=httpx.Response(401, text="Unauthorized")
    )
    with pytest.raises(RuntimeError, match="401"):
        await client.get_metadata("/restricted")
