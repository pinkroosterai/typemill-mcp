import json
from typing import Annotated, Any

from pydantic import Field
from mcp.server.fastmcp import FastMCP
from typemill_mcp.client import TypemillClient

ItemId = Annotated[str, Field(description="The keyPath from the navigation tree (e.g. '0', '0.1', '2.3'). Get this from explore_site, NOT from page metadata. It is NOT the pageid hex hash.")]


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
        """Retrieve the full site structure as a readable tree showing all pages and folders with their publication status. Each line shows [P] for published or [D] for draft, the page name, and its URL path. Includes unpublished pages."""
        result = await client.get_navigation(draft=True)
        items = result.get("navigation", [])
        if not items:
            return "Site is empty — no pages found."
        return _format_tree(items)

    @mcp.tool()
    async def rename_page(url_path: str, item_id: ItemId, new_name: str) -> str:
        """Rename a Typemill page, changing its title and URL slug. url_path is the current relative URL, new_name is the desired new slug."""
        result = await client.rename_article(url_path, item_id, new_name)
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def sort_page(url_path: str, item_id: ItemId, parent_id: str, position: int) -> str:
        """Move a Typemill page to a new position in the navigation tree. url_path identifies the page, parent_id is the target parent's keyPath, and position is the 0-based target index within that folder."""
        result = await client.sort_article(url_path, item_id, parent_id, position)
        return json.dumps(result, indent=2)
