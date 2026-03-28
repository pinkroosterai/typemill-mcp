from typing import Annotated

from pydantic import Field
from mcp.server.fastmcp import FastMCP
from typemill_mcp.client import TypemillClient
from typemill_mcp.tools.types import UrlPath, compact_response

BlockIndex = Annotated[int, Field(description="0-based index of the block. Get block indices from get_page content array.", ge=0)]


def register(mcp: FastMCP, client: TypemillClient) -> None:
    @mcp.tool()
    async def add_block(
        url_path: UrlPath,
        block_id: BlockIndex,
        content: Annotated[str, Field(description="Markdown text for the new block.")],
    ) -> str:
        """Insert a new content block before the specified position. Only works on pages that already have content — use update_page for empty pages."""
        result = await client.add_block(url_path, block_id, content)
        return compact_response(result)

    @mcp.tool()
    async def update_block(
        url_path: UrlPath,
        block_id: BlockIndex,
        content: Annotated[str, Field(description="New markdown text to replace the block's content.")],
    ) -> str:
        """Replace the markdown content of an existing block."""
        result = await client.update_block(url_path, block_id, content)
        return compact_response(result)

    @mcp.tool()
    async def delete_block(url_path: UrlPath, block_id: BlockIndex) -> str:
        """Remove a content block from the page. Remaining blocks are re-indexed."""
        result = await client.delete_block(url_path, block_id)
        return compact_response(result)

    @mcp.tool()
    async def move_block(
        url_path: UrlPath,
        block_id: BlockIndex,
        new_position: Annotated[int, Field(description="Target 0-based index to move the block to.", ge=0)],
    ) -> str:
        """Move a content block to a different position within the same page."""
        result = await client.move_block(url_path, block_id, new_position)
        return compact_response(result)
