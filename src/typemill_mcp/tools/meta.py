import json
from typing import Optional

from mcp.server.fastmcp import FastMCP
from typemill_mcp.client import TypemillClient


def register(mcp: FastMCP, client: TypemillClient) -> None:
    @mcp.tool()
    async def get_meta(url_path: str) -> str:
        """Retrieve the metadata (title, description, published status, etc.) of a Typemill page by its URL path."""
        result = await client.get_article_metadata(url_path)
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def update_meta(
        url_path: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        noindex: Optional[bool] = None,
    ) -> str:
        """Update the metadata of a Typemill page. Provide url_path and any combination of title, description, or noindex flag. Only provided values will be sent — omit a field to leave it unchanged."""
        meta: dict = {}
        if title is not None:
            meta["title"] = title
        if description is not None:
            meta["description"] = description
        if noindex is not None:
            meta["noindex"] = noindex
        if not meta:
            return "No metadata values provided to update."
        result = await client.update_article_metadata(url_path, meta)
        return json.dumps(result, indent=2)
