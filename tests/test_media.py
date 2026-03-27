import httpx
import pytest
import respx

from typemill_mcp.client import TypemillClient


@pytest.fixture
def client():
    return TypemillClient("https://example.com", "user", "pass")


@respx.mock
@pytest.mark.asyncio
async def test_browse_images(client):
    respx.get("https://example.com/api/v1/medialib/images").mock(
        return_value=httpx.Response(
            200, json={"images": ["photo.jpg", "diagram.png"]}
        )
    )
    result = await client.browse_images()
    assert "photo.jpg" in result["images"]


@respx.mock
@pytest.mark.asyncio
async def test_browse_files(client):
    respx.get("https://example.com/api/v1/medialib/files").mock(
        return_value=httpx.Response(200, json={"files": ["readme.pdf"]})
    )
    result = await client.browse_files()
    assert "readme.pdf" in result["files"]


@respx.mock
@pytest.mark.asyncio
async def test_get_image(client):
    respx.get("https://example.com/api/v1/image").mock(
        return_value=httpx.Response(
            200, json={"name": "photo.jpg", "url": "/media/photo.jpg"}
        )
    )
    result = await client.get_image("photo.jpg")
    assert result["name"] == "photo.jpg"


@respx.mock
@pytest.mark.asyncio
async def test_upload_image(client):
    respx.post("https://example.com/api/v1/image").mock(
        return_value=httpx.Response(200, json={"success": True})
    )
    result = await client.upload_image("base64data...", "new-photo.jpg")
    assert result["success"] is True


@respx.mock
@pytest.mark.asyncio
async def test_publish_image(client):
    respx.put("https://example.com/api/v1/image").mock(
        return_value=httpx.Response(200, json={"success": True})
    )
    result = await client.publish_image("photo.jpg")
    assert result["success"] is True


@respx.mock
@pytest.mark.asyncio
async def test_delete_image(client):
    respx.delete("https://example.com/api/v1/image").mock(
        return_value=httpx.Response(200, json={"success": True})
    )
    result = await client.delete_image("photo.jpg")
    assert result["success"] is True


@respx.mock
@pytest.mark.asyncio
async def test_get_file(client):
    respx.get("https://example.com/api/v1/file").mock(
        return_value=httpx.Response(
            200, json={"name": "readme.pdf", "url": "/media/readme.pdf"}
        )
    )
    result = await client.get_file("readme.pdf")
    assert result["name"] == "readme.pdf"


@respx.mock
@pytest.mark.asyncio
async def test_upload_file(client):
    respx.post("https://example.com/api/v1/file").mock(
        return_value=httpx.Response(200, json={"success": True})
    )
    result = await client.upload_file("base64data...", "new-doc.pdf")
    assert result["success"] is True


@respx.mock
@pytest.mark.asyncio
async def test_publish_file(client):
    respx.put("https://example.com/api/v1/file").mock(
        return_value=httpx.Response(200, json={"success": True})
    )
    result = await client.publish_file("readme.pdf")
    assert result["success"] is True


@respx.mock
@pytest.mark.asyncio
async def test_delete_file(client):
    respx.delete("https://example.com/api/v1/file").mock(
        return_value=httpx.Response(200, json={"success": True})
    )
    result = await client.delete_file("readme.pdf")
    assert result["success"] is True


@respx.mock
@pytest.mark.asyncio
async def test_media_permission_error(client):
    respx.post("https://example.com/api/v1/image").mock(
        return_value=httpx.Response(403, text="Forbidden")
    )
    with pytest.raises(RuntimeError, match="403"):
        await client.upload_image("base64data...", "blocked.jpg")
