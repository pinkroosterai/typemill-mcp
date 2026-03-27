import asyncio
import json
from typing import Annotated

from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP
from typemill_mcp.client import TypemillClient

ItemId = Annotated[str, Field(description="The keyPath from the navigation tree (e.g. '0', '0.1', '2.3'). Get this from explore_site, NOT from page metadata. It is NOT the pageid hex hash.")]


class ContentBlock(BaseModel):
    """A single content block on a Typemill page."""
    markdown: str = Field(description="The markdown text for this block, e.g. '# Hello World' or 'A paragraph of text.'")


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
    async def update_page(url_path: str, item_id: ItemId, title: str, blocks: list[ContentBlock]) -> str:
        """Replace the full draft content of a Typemill page. Use this to set initial content on newly created (empty) pages, or to replace all content at once. title is the page heading (without '# ' — it is added automatically). Each block is a separate content element (paragraph, list, code block, etc.). Do NOT include the title as a block."""
        heading = "# " + title
        body = "\n\n".join(b.markdown for b in blocks)
        result = await client.update_draft(url_path, item_id, heading, body)
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def delete_page(url_path: str, item_id: ItemId) -> str:
        """Delete a Typemill page by its URL path and item_id. This action is irreversible — the page and its content will be permanently removed."""
        result = await client.delete_article(url_path, item_id)
        return json.dumps(result, indent=2)
