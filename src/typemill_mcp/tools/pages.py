import asyncio
import json

from mcp.server.fastmcp import FastMCP
from typemill_mcp.client import TypemillClient


def register(mcp: FastMCP, client: TypemillClient) -> None:
    @mcp.tool()
    async def get_page(url_path: str) -> str:
        """Retrieve the full content and metadata of a Typemill page by its URL path (e.g. '/getting-started'). Returns both the markdown content blocks and page metadata in a single response."""
        results = await asyncio.gather(
            client.get_article_markdown(url_path),
            client.get_article_metadata(url_path),
            return_exceptions=True,
        )
        markdown_resp, metadata_resp = results

        combined: dict = {}
        if isinstance(markdown_resp, Exception):
            combined["content"] = []
            combined["content_error"] = str(markdown_resp)
        else:
            combined["content"] = markdown_resp.get("content", [])

        if isinstance(metadata_resp, Exception):
            combined["metadata"] = {}
            combined["metadata_error"] = str(metadata_resp)
        else:
            combined["metadata"] = metadata_resp.get("metadata", {})

        return json.dumps(combined, indent=2)

    @mcp.tool()
    async def create_page(url_path: str, title: str, content: str) -> str:
        """Create a new page in Typemill. url_path is the desired relative URL (e.g. '/docs/new-page'), title is the page title, content is the Markdown body."""
        result = await client.create_article(url_path, title, content)
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def delete_page(url_path: str) -> str:
        """Delete a Typemill page by its URL path. This action is irreversible — the page and its content will be permanently removed."""
        result = await client.delete_article(url_path)
        return json.dumps(result, indent=2)
