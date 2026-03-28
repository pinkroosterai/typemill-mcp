from typing import Annotated, Optional

from pydantic import Field
from mcp.server.fastmcp import FastMCP
from typemill_mcp.client import TypemillClient
from typemill_mcp.tools.types import UrlPath, compact_response


def register(mcp: FastMCP, client: TypemillClient) -> None:
    @mcp.tool()
    async def get_meta(url_path: UrlPath) -> str:
        """Get page metadata including title, description, author, dates, and visibility settings."""
        result = await client.get_metadata(url_path)
        return compact_response(result)

    @mcp.tool()
    async def update_meta(
        url_path: UrlPath,
        navtitle: Annotated[Optional[str], Field(description="Navigation title shown in the sidebar menu. Omit to leave unchanged.")] = None,
        title: Annotated[Optional[str], Field(description="Meta title for SEO and browser tab. Omit to leave unchanged.")] = None,
        description: Annotated[Optional[str], Field(description="Meta description for SEO. Omit to leave unchanged.")] = None,
        noindex: Annotated[Optional[bool], Field(description="If true, adds noindex tag and excludes from sitemap. Omit to leave unchanged.")] = None,
    ) -> str:
        """Update metadata fields on a page. Only provided fields are changed — omit a field to keep its current value."""
        meta: dict = {}
        if navtitle is not None:
            meta["navtitle"] = navtitle
        if title is not None:
            meta["title"] = title
        if description is not None:
            meta["description"] = description
        if noindex is not None:
            meta["noindex"] = noindex
        if not meta:
            return "No metadata values provided to update."
        result = await client.update_metadata(url_path, meta)
        return compact_response(result)
