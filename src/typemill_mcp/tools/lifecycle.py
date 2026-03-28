
from mcp.server.fastmcp import FastMCP
from typemill_mcp.client import TypemillClient
from typemill_mcp.tools.types import ItemId, UrlPath, compact_response


def register(mcp: FastMCP, client: TypemillClient) -> None:
    @mcp.tool()
    async def publish_page(url_path: UrlPath, item_id: ItemId) -> str:
        """Publish a draft page, making it publicly visible on the site."""
        result = await client.publish_article(url_path, item_id)
        return compact_response(result)

    @mcp.tool()
    async def unpublish_page(url_path: UrlPath, item_id: ItemId) -> str:
        """Revert a published page to draft state. Content is preserved but hidden from public view."""
        result = await client.unpublish_article(url_path, item_id)
        return compact_response(result)

    @mcp.tool()
    async def discard_changes(url_path: UrlPath, item_id: ItemId) -> str:
        """Discard all unpublished draft changes, reverting to the last published version. Irreversible — draft edits are lost."""
        result = await client.discard_article(url_path, item_id)
        return compact_response(result)
