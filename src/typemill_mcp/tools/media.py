import base64
import mimetypes
from pathlib import Path
from typing import Annotated, Literal, Optional

from pydantic import Field
from mcp.server.fastmcp import FastMCP
from typemill_mcp.client import TypemillClient
from typemill_mcp.tools.types import compact_response

ACTIONS_NEEDING_NAME = {
    "get_image", "get_file",
    "publish_image", "publish_file",
    "delete_image", "delete_file",
}

ACTIONS_NEEDING_FILE_PATH = {
    "upload_image", "upload_file",
}


def _file_to_data_uri(file_path: str) -> tuple[str, str]:
    """Read a local file and return (data_uri, filename)."""
    path = Path(file_path).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")
    mime_type = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
    data = path.read_bytes()
    b64 = base64.b64encode(data).decode()
    return f"data:{mime_type};base64,{b64}", path.name


def register(mcp: FastMCP, client: TypemillClient) -> None:
    @mcp.tool()
    async def manage_media(
        action: Annotated[
            Literal[
                "browse_images", "browse_files",
                "get_image", "get_file",
                "upload_image", "upload_file",
                "publish_image", "publish_file",
                "delete_image", "delete_file",
            ],
            Field(description="browse_* lists all assets. get_* retrieves one by name. upload_* creates new (requires name + file_path). publish_* makes live. delete_* removes."),
        ],
        name: Annotated[Optional[str], Field(description="Asset filename (e.g. 'photo.png'). Required for all actions except browse_*. For upload_*, defaults to the filename from file_path if omitted.")] = None,
        file_path: Annotated[Optional[str], Field(description="Absolute path to a local file to upload (e.g. '/home/user/images/photo.png'). Required for upload_* actions only. The file is read, base64-encoded, and sent to Typemill.")] = None,
    ) -> str:
        """Manage media assets (images and files) in the Typemill media library."""
        if action in ACTIONS_NEEDING_NAME and not name and action not in ACTIONS_NEEDING_FILE_PATH:
            return f"Error: '{action}' requires the 'name' parameter."
        if action in ACTIONS_NEEDING_FILE_PATH and not file_path:
            return f"Error: '{action}' requires the 'file_path' parameter."

        if action in ACTIONS_NEEDING_FILE_PATH:
            data_uri, default_name = _file_to_data_uri(file_path)
            upload_name = name or default_name

        dispatch = {
            "browse_images": lambda: client.browse_images(),
            "browse_files": lambda: client.browse_files(),
            "get_image": lambda: client.get_image(name),
            "get_file": lambda: client.get_file(name),
            "upload_image": lambda: client.upload_image(data_uri, upload_name),
            "upload_file": lambda: client.upload_file(data_uri, upload_name),
            "publish_image": lambda: client.publish_image(name),
            "publish_file": lambda: client.publish_file(name),
            "delete_image": lambda: client.delete_image(name),
            "delete_file": lambda: client.delete_file(name),
        }

        result = await dispatch[action]()
        return compact_response(result)
