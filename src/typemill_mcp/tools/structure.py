import json
from typing import Annotated, Any

from pydantic import Field
from mcp.server.fastmcp import FastMCP
from typemill_mcp.client import TypemillClient
from typemill_mcp.tools.types import ItemId, UrlPath


def _format_tree(items: list[dict[str, Any]], indent: int = 0) -> str:
    lines: list[str] = []
    prefix = "  " * indent
    for item in items:
        status = item.get("status", "draft")
        marker = "[P]" if status == "published" else "[D]"
        name = item.get("name", "Untitled")
        url = item.get("urlRel", "")
        key_path = item.get("keyPath", "?")
        lines.append(f"{prefix}{marker} {name}  {url}  (keyPath: {key_path})")
        children = item.get("folderContent", [])
        if isinstance(children, dict):
            children = list(children.values())
        if children:
            lines.append(_format_tree(children, indent + 1))
    return "\n".join(lines)


def register(mcp: FastMCP, client: TypemillClient) -> None:
    @mcp.tool()
    async def explore_site() -> str:
        """List all pages and folders as a tree with publication status, URL paths, and keyPaths. Call this first to discover pages and get the keyPath needed by other tools."""
        result = await client.get_navigation(draft=True)
        items = result.get("navigation", [])
        if not items:
            return "Site is empty — no pages found."
        return _format_tree(items)

    @mcp.tool()
    async def rename_page(
        url_path: UrlPath,
        item_id: ItemId,
        new_name: Annotated[str, Field(description="New URL slug for the page (e.g. 'my-new-name'). Lowercase, hyphens only.")],
    ) -> str:
        """Rename a page, changing its URL slug and navigation title. Creates a draft change — publish to make it live."""
        result = await client.rename_article(url_path, item_id, new_name)
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def sort_page(
        url_path: UrlPath,
        item_id: ItemId,
        parent_id: Annotated[str, Field(description="keyPath of the target parent folder (e.g. '0' for first folder, 'root' for top level).")],
        position: Annotated[int, Field(description="0-based target index within the parent folder.", ge=0)],
    ) -> str:
        """Move a page to a new position in the navigation tree."""
        result = await client.sort_article(url_path, item_id, parent_id, position)
        return json.dumps(result, indent=2)
