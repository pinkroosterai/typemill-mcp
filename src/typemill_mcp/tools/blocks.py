import json

from mcp.server.fastmcp import FastMCP
from typemill_mcp.client import TypemillClient


def register(mcp: FastMCP, client: TypemillClient) -> None:
    @mcp.tool()
    async def add_block(url_path: str, block_id: int, content: str) -> str:
        """Add a new markdown content block to a Typemill page. block_id is the 0-based position index where the block will be inserted. content is the markdown text for the block."""
        result = await client.add_block(url_path, block_id, content)
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def update_block(url_path: str, block_id: int, content: str) -> str:
        """Update an existing content block on a Typemill page. block_id is the 0-based index of the block to update. content is the new markdown text."""
        result = await client.update_block(url_path, block_id, content)
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def delete_block(url_path: str, block_id: int) -> str:
        """Delete a content block from a Typemill page. block_id is the 0-based index of the block to remove. This action is immediate."""
        result = await client.delete_block(url_path, block_id)
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def move_block(url_path: str, block_id: int, new_position: int) -> str:
        """Move a content block to a new position within the page. block_id is the current 0-based index, new_position is the target 0-based index."""
        result = await client.move_block(url_path, block_id, new_position)
        return json.dumps(result, indent=2)
