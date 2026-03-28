"""
Integration tests against a real Typemill instance running in Docker.

Run with: pytest -m integration -v
Requires: Docker daemon running, kixote/typemill image available.
"""

import pytest

pytestmark = pytest.mark.integration

# Shared state between ordered tests
_state: dict = {}


@pytest.mark.asyncio
async def test_01_get_navigation(typemill_client):
    """Verify we can connect and retrieve the navigation tree."""
    result = await typemill_client.get_navigation(draft=True)
    assert "navigation" in result
    assert isinstance(result["navigation"], list)
    assert len(result["navigation"]) > 0


@pytest.mark.asyncio
async def test_02_get_article_content(typemill_client):
    """Get content of an existing page."""
    result = await typemill_client.get_article_content("/getting-started")
    assert "content" in result
    assert isinstance(result["content"], list)
    assert len(result["content"]) > 0
    assert "markdown" in result["content"][0]


@pytest.mark.asyncio
async def test_03_get_article_meta(typemill_client):
    """Get metadata of an existing page."""
    result = await typemill_client.get_article_meta("/getting-started")
    assert "meta" in result
    assert "meta" in result["meta"]
    assert "title" in result["meta"]["meta"]


@pytest.mark.asyncio
async def test_04_get_article_item(typemill_client):
    """Get navigation item details for a URL."""
    result = await typemill_client.get_article_item("/getting-started")
    assert "item" in result
    assert result["item"]["slug"] == "getting-started"


@pytest.mark.asyncio
async def test_05_create_article(typemill_client):
    """Create a test page at the root level."""
    result = await typemill_client.create_article(
        folder_id="root",
        item_name="integration-test-page",
    )
    assert "navigation" in result
    # Find our page in the navigation to get its item_id
    nav = result["navigation"]
    for i, item in enumerate(nav):
        if item.get("slug") == "integration-test-page":
            _state["page_url"] = item["urlRel"]
            _state["item_id"] = str(item["key"])
            _state["item_key_path"] = item["keyPath"]
            break
    assert "page_url" in _state, "Created page not found in navigation"


@pytest.mark.asyncio
async def test_06_update_draft(typemill_client):
    """Update the draft content of the created page."""
    url = _state["page_url"]
    item_id = _state["item_key_path"]
    result = await typemill_client.update_draft(
        url=url,
        item_id=item_id,
        title="# Integration Test Page",
        body="This is test content.",
    )
    assert result is not None


@pytest.mark.asyncio
async def test_07_publish(typemill_client):
    """Publish the test page."""
    url = _state["page_url"]
    item_id = _state["item_key_path"]
    result = await typemill_client.publish_article(url, item_id)
    assert "navigation" in result


@pytest.mark.asyncio
async def test_08_get_metadata(typemill_client):
    """Get metadata via the /meta endpoint."""
    url = _state["page_url"]
    result = await typemill_client.get_metadata(url)
    assert "metadata" in result


@pytest.mark.asyncio
async def test_09_update_metadata(typemill_client):
    """Update page metadata."""
    url = _state["page_url"]
    result = await typemill_client.update_metadata(
        url=url,
        metadata={"description": "Integration test description"},
    )
    assert result is not None


@pytest.mark.asyncio
async def test_10_unpublish(typemill_client):
    """Unpublish the test page."""
    url = _state["page_url"]
    item_id = _state["item_key_path"]
    result = await typemill_client.unpublish_article(url, item_id)
    assert "navigation" in result


@pytest.mark.asyncio
async def test_11_browse_images(typemill_client):
    """Browse the image library."""
    result = await typemill_client.browse_images()
    assert "images" in result
    assert isinstance(result["images"], list)


@pytest.mark.asyncio
async def test_12_browse_files(typemill_client):
    """Browse the file library."""
    result = await typemill_client.browse_files()
    assert "files" in result
    assert isinstance(result["files"], list)


@pytest.mark.asyncio
async def test_13_delete_article(typemill_client):
    """Delete the test page — cleanup."""
    url = _state["page_url"]
    item_id = _state["item_key_path"]
    result = await typemill_client.delete_article(url, item_id)
    assert result is not None
