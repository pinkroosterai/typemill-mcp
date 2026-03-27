import json
from typing import Literal, Optional

from mcp.server.fastmcp import FastMCP
from typemill_mcp.client import TypemillClient

ACTIONS_NEEDING_NAME = {
    "get_image", "get_file",
    "publish_image", "publish_file",
    "delete_image", "delete_file",
}

ACTIONS_NEEDING_FILE = {
    "upload_image", "upload_file",
}


def register(mcp: FastMCP, client: TypemillClient) -> None:
    @mcp.tool()
    async def manage_media(
        action: Literal[
            "browse_images", "browse_files",
            "get_image", "get_file",
            "upload_image", "upload_file",
            "publish_image", "publish_file",
            "delete_image", "delete_file",
        ],
        name: Optional[str] = None,
        file: Optional[str] = None,
    ) -> str:
        """Manage media assets (images and files) in Typemill. Actions: browse_images, browse_files (list library contents), get_image, get_file (get details by name), upload_image, upload_file (create new, requires name and file), publish_image, publish_file (make live), delete_image, delete_file (remove by name)."""
        if action in ACTIONS_NEEDING_NAME and not name:
            return f"Error: '{action}' requires the 'name' parameter."
        if action in ACTIONS_NEEDING_FILE and (not name or not file):
            return f"Error: '{action}' requires both 'name' and 'file' parameters."

        dispatch = {
            "browse_images": lambda: client.browse_images(),
            "browse_files": lambda: client.browse_files(),
            "get_image": lambda: client.get_image(name),
            "get_file": lambda: client.get_file(name),
            "upload_image": lambda: client.upload_image(file, name),
            "upload_file": lambda: client.upload_file(file, name),
            "publish_image": lambda: client.publish_image(name),
            "publish_file": lambda: client.publish_file(name),
            "delete_image": lambda: client.delete_image(name),
            "delete_file": lambda: client.delete_file(name),
        }

        result = await dispatch[action]()
        return json.dumps(result, indent=2)
