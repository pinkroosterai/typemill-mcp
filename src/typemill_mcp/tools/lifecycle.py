import json
from typing import Annotated

from pydantic import Field
from mcp.server.fastmcp import FastMCP
from typemill_mcp.client import TypemillClient

ItemId = Annotated[str, Field(description="The keyPath from the navigation tree (e.g. '0', '0.1', '2.3'). Get this from explore_site, NOT from page metadata. It is NOT the pageid hex hash.")]


def register(mcp: FastMCP, client: TypemillClient) -> None:
    @mcp.tool()
    async def publish_page(url_path: str, item_id: ItemId) -> str:
        """Publish a Typemill page, making it publicly visible on the site."""
        result = await client.publish_article(url_path, item_id)
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def unpublish_page(url_path: str, item_id: ItemId) -> str:
        """Unpublish a Typemill page, reverting it to draft state. The content is preserved but hidden from public view."""
        result = await client.unpublish_article(url_path, item_id)
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def discard_changes(url_path: str, item_id: ItemId) -> str:
        """Discard all unpublished changes to a Typemill page, reverting it to the last published version. This action is irreversible."""
        result = await client.discard_article(url_path, item_id)
        return json.dumps(result, indent=2)
