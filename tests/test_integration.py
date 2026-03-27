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


@pytest.mark.asyncio
async def test_02_create_article(typemill_client):
    """Create a test page that subsequent tests will operate on."""
    result = await typemill_client.create_article(
        url="/test-integration-page",
        title="Integration Test Page",
        content="# Integration Test\n\nThis is a test page.",
    )
    _state["page_url"] = "/test-integration-page"
    assert result is not None


@pytest.mark.asyncio
async def test_03_get_article_markdown(typemill_client):
    """Retrieve the created page's markdown content."""
    url = _state.get("page_url", "/test-integration-page")
    result = await typemill_client.get_article_markdown(url)
    assert "content" in result
    assert isinstance(result["content"], list)


@pytest.mark.asyncio
async def test_04_get_article_metadata(typemill_client):
    """Retrieve the created page's metadata."""
    url = _state.get("page_url", "/test-integration-page")
    result = await typemill_client.get_article_metadata(url)
    assert "metadata" in result or "meta" in str(result).lower()


@pytest.mark.asyncio
async def test_05_update_article(typemill_client):
    """Update the page's content."""
    url = _state.get("page_url", "/test-integration-page")
    result = await typemill_client.update_article(
        url=url,
        content="# Updated Integration Test\n\nContent has been updated.",
    )
    assert result is not None


@pytest.mark.asyncio
async def test_06_add_block(typemill_client):
    """Add a new content block to the page."""
    url = _state.get("page_url", "/test-integration-page")
    result = await typemill_client.add_block(
        url=url,
        block_id=1,
        content="## New Block\n\nAdded via integration test.",
    )
    assert result is not None


@pytest.mark.asyncio
async def test_07_update_block(typemill_client):
    """Update the block we just added."""
    url = _state.get("page_url", "/test-integration-page")
    result = await typemill_client.update_block(
        url=url,
        block_id=1,
        content="## Updated Block\n\nModified via integration test.",
    )
    assert result is not None


@pytest.mark.asyncio
async def test_08_move_block(typemill_client):
    """Move a block to a different position."""
    url = _state.get("page_url", "/test-integration-page")
    try:
        result = await typemill_client.move_block(
            url=url,
            block_id=1,
            new_position=0,
        )
        assert result is not None
    except RuntimeError:
        pytest.skip("move_block not supported by this Typemill version")


@pytest.mark.asyncio
async def test_09_delete_block(typemill_client):
    """Delete the block we've been working with."""
    url = _state.get("page_url", "/test-integration-page")
    result = await typemill_client.delete_block(
        url=url,
        block_id=1,
    )
    assert result is not None


@pytest.mark.asyncio
async def test_10_update_metadata(typemill_client):
    """Update the page's metadata."""
    url = _state.get("page_url", "/test-integration-page")
    result = await typemill_client.update_article_metadata(
        url=url,
        metadata={"description": "Integration test page description"},
    )
    assert result is not None


@pytest.mark.asyncio
async def test_11_publish(typemill_client):
    """Publish the page."""
    url = _state.get("page_url", "/test-integration-page")
    result = await typemill_client.publish_article(url)
    assert result is not None


@pytest.mark.asyncio
async def test_12_unpublish(typemill_client):
    """Unpublish the page."""
    url = _state.get("page_url", "/test-integration-page")
    result = await typemill_client.unpublish_article(url)
    assert result is not None


@pytest.mark.asyncio
async def test_13_discard(typemill_client):
    """Discard unpublished changes."""
    url = _state.get("page_url", "/test-integration-page")
    try:
        result = await typemill_client.discard_article(url)
        assert result is not None
    except RuntimeError:
        pytest.skip("discard may fail if no unpublished changes exist")


@pytest.mark.asyncio
async def test_14_get_meta_definitions(typemill_client):
    """Retrieve meta field definitions."""
    result = await typemill_client.get_meta_definitions()
    assert result is not None


@pytest.mark.asyncio
async def test_15_browse_images(typemill_client):
    """Browse the media library for images."""
    result = await typemill_client.browse_images()
    assert result is not None


@pytest.mark.asyncio
async def test_16_browse_files(typemill_client):
    """Browse the media library for files."""
    result = await typemill_client.browse_files()
    assert result is not None


@pytest.mark.asyncio
async def test_17_rename_article(typemill_client):
    """Rename the test page."""
    url = _state.get("page_url", "/test-integration-page")
    try:
        result = await typemill_client.rename_article(url, "renamed-integration-page")
        _state["page_url"] = "/renamed-integration-page"
        assert result is not None
    except RuntimeError:
        pytest.skip("rename may require specific page state")


@pytest.mark.asyncio
async def test_18_delete_article(typemill_client):
    """Delete the test page — cleanup."""
    url = _state.get("page_url", "/test-integration-page")
    result = await typemill_client.delete_article(url)
    assert result is not None
