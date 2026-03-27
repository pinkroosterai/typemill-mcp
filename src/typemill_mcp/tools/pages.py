import asyncio
import json

from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP
from typemill_mcp.client import TypemillClient
from typemill_mcp.tools.types import ItemId, UrlPath, compact_response


class ContentBlock(BaseModel):
    """A single content block on a Typemill page."""
    markdown: str = Field(description="Markdown text for this block (e.g. 'A paragraph.' or '* Item one\\n* Item two').")


def register(mcp: FastMCP, client: TypemillClient) -> None:
    @mcp.tool()
    async def get_page(url_path: UrlPath) -> str:
        """Get the full content blocks and metadata of a page. Returns partial results if one API call fails (e.g. content missing for unpublished pages)."""
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
    async def create_page(
        folder_id: str = Field(description="Parent location: 'root' for top-level, or a keyPath like '0' for the first folder."),
        item_name: str = Field(description="URL slug for the new page (e.g. 'my-new-page'). Lowercase, hyphens only."),
        item_type: str = Field(default="file", description="'file' for a page, 'folder' for a section that can contain sub-pages."),
    ) -> str:
        """Create a new empty page or folder. The page has no content until you call update_page."""
        result = await client.create_article(folder_id, item_name, item_type)
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def update_page(
        url_path: UrlPath,
        item_id: ItemId,
        title: str = Field(description="Page title text (e.g. 'Welcome to Clarive'). The '# ' heading prefix is added automatically."),
        blocks: list[ContentBlock] = Field(description="Content blocks below the title. Each block is a separate paragraph, list, code block, etc. Do NOT include the title as a block."),
    ) -> str:
        """Replace the full draft content of a page. Use after create_page to set initial content, or to overwrite all content at once."""
        heading = "# " + title
        body = "\n\n".join(b.markdown for b in blocks)
        result = await client.update_draft(url_path, item_id, heading, body)
        return compact_response(result)

    @mcp.tool()
    async def delete_page(url_path: UrlPath, item_id: ItemId) -> str:
        """Permanently delete a page and its content. This action is irreversible."""
        result = await client.delete_article(url_path, item_id)
        return compact_response(result)
