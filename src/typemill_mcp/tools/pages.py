import asyncio
import json

from mcp.server.fastmcp import FastMCP
from typemill_mcp.client import TypemillClient


def register(mcp: FastMCP, client: TypemillClient) -> None:
    @mcp.tool()
    async def get_page(url_path: str) -> str:
        """Retrieve the full content and metadata of a Typemill page by its URL path (e.g. '/getting-started'). Returns both the markdown content blocks and page metadata in a single response."""
        results = await asyncio.gather(
            client.get_article_content(url_path),
            client.get_article_meta(url_path),
            return_exceptions=True,
        )
        content_resp, meta_resp = results

        combined: dict = {}
        if isinstance(content_resp, Exception):
            combined["content"] = []
            combined["content_error"] = str(content_resp)
        else:
            combined["content"] = content_resp.get("content", [])

        if isinstance(meta_resp, Exception):
            combined["metadata"] = {}
            combined["metadata_error"] = str(meta_resp)
        else:
            combined["metadata"] = meta_resp.get("meta", {})

        return json.dumps(combined, indent=2)

    @mcp.tool()
    async def create_page(folder_id: str, item_name: str, item_type: str = "file") -> str:
        """Create a new page in Typemill. folder_id is 'root' for top-level or a key path like '0' for the first folder. item_name is the page slug (e.g. 'my-new-page'). item_type is 'file' for a page or 'folder' for a section."""
        result = await client.create_article(folder_id, item_name, item_type)
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def delete_page(url_path: str, item_id: str) -> str:
        """Delete a Typemill page by its URL path and item_id. This action is irreversible — the page and its content will be permanently removed."""
        result = await client.delete_article(url_path, item_id)
        return json.dumps(result, indent=2)
