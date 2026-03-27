import httpx
import pytest
import respx

from typemill_mcp.client import TypemillClient


@pytest.fixture
def client():
    return TypemillClient("https://example.com", "user", "pass")


@respx.mock
@pytest.mark.asyncio
async def test_add_block(client):
    respx.post("https://example.com/api/v1/block").mock(
        return_value=httpx.Response(200, json={"success": True, "block_id": 5})
    )
    result = await client.add_block("/getting-started", 5, "## New section")
    assert result["success"] is True
    assert result["block_id"] == 5


@respx.mock
@pytest.mark.asyncio
async def test_update_block(client):
    respx.put("https://example.com/api/v1/block").mock(
        return_value=httpx.Response(200, json={"success": True})
    )
    result = await client.update_block("/getting-started", 2, "## Updated section")
    assert result["success"] is True


@respx.mock
@pytest.mark.asyncio
async def test_delete_block(client):
    respx.delete("https://example.com/api/v1/block").mock(
        return_value=httpx.Response(200, json={"success": True})
    )
    result = await client.delete_block("/getting-started", 3)
    assert result["success"] is True


@respx.mock
@pytest.mark.asyncio
async def test_move_block(client):
    respx.put("https://example.com/api/v1/block/move").mock(
        return_value=httpx.Response(200, json={"success": True})
    )
    result = await client.move_block("/getting-started", 2, 5)
    assert result["success"] is True


@respx.mock
@pytest.mark.asyncio
async def test_block_permission_error(client):
    respx.post("https://example.com/api/v1/block").mock(
        return_value=httpx.Response(403, text="Forbidden")
    )
    with pytest.raises(RuntimeError, match="403"):
        await client.add_block("/restricted", 0, "content")
