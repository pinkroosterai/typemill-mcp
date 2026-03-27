import json

from mcp.server.fastmcp import FastMCP
from typemill_mcp.client import TypemillClient


def register(mcp: FastMCP, client: TypemillClient) -> None:
    @mcp.tool()
    async def publish_page(url_path: str, item_id: str) -> str:
        """Publish a Typemill page, making it publicly visible on the site. Requires both url_path and item_id (from the navigation tree)."""
        result = await client.publish_article(url_path, item_id)
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def unpublish_page(url_path: str, item_id: str) -> str:
        """Unpublish a Typemill page, reverting it to draft state. The content is preserved but hidden from public view."""
        result = await client.unpublish_article(url_path, item_id)
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def discard_changes(url_path: str, item_id: str) -> str:
        """Discard all unpublished changes to a Typemill page, reverting it to the last published version. This action is irreversible."""
        result = await client.discard_article(url_path, item_id)
        return json.dumps(result, indent=2)
