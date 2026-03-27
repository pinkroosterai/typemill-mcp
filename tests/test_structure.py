import httpx
import pytest
import respx

from typemill_mcp.client import TypemillClient
from typemill_mcp.tools.structure import _format_tree


@pytest.fixture
def client():
    return TypemillClient("https://example.com", "user", "pass")


NESTED_NAV = {
    "navigation": [
        {
            "elementType": "file",
            "name": "Home",
            "status": "published",
            "urlRel": "/",
        },
        {
            "elementType": "folder",
            "name": "Docs",
            "status": "published",
            "urlRel": "/docs",
            "folderContent": [
                {
                    "elementType": "file",
                    "name": "Install",
                    "status": "draft",
                    "urlRel": "/docs/install",
                },
                {
                    "elementType": "file",
                    "name": "Config",
                    "status": "published",
                    "urlRel": "/docs/config",
                },
            ],
        },
    ]
}


def test_format_tree():
    result = _format_tree(NESTED_NAV["navigation"])
    assert "[P] Home  /" in result
    assert "[P] Docs  /docs" in result
    assert "  [D] Install  /docs/install" in result
    assert "  [P] Config  /docs/config" in result


def test_format_tree_empty():
    result = _format_tree([])
    assert result == ""


@respx.mock
@pytest.mark.asyncio
async def test_explore_site(client):
    respx.get("https://example.com/api/v1/navigation").mock(
        return_value=httpx.Response(200, json=NESTED_NAV)
    )
    result = await client.get_navigation(draft=True)
    tree = _format_tree(result.get("navigation", []))
    assert "[P] Home" in tree
    assert "  [D] Install" in tree


@respx.mock
@pytest.mark.asyncio
async def test_rename_page(client):
    respx.post("https://example.com/api/v1/article/rename").mock(
        return_value=httpx.Response(200, json={"success": True})
    )
    result = await client.rename_article("/docs/old-name", "new-name")
    assert result["success"] is True


@respx.mock
@pytest.mark.asyncio
async def test_sort_page(client):
    respx.post("https://example.com/api/v1/article/sort").mock(
        return_value=httpx.Response(200, json={"success": True})
    )
    result = await client.sort_article("/docs/install", "item-1", "folder-1", 0)
    assert result["success"] is True
