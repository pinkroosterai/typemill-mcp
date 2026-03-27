import sys

from mcp.server.fastmcp import FastMCP
from typemill_mcp.client import Settings, TypemillClient
from typemill_mcp.tools import structure, pages, blocks, lifecycle, meta, media

mcp = FastMCP("typemill-mcp")


def _init() -> TypemillClient:
    try:
        settings = Settings()
    except Exception:
        print(
            "Error: TYPEMILL_BASE_URL, TYPEMILL_USERNAME, and TYPEMILL_PASSWORD "
            "must be set as environment variables or in a .env file.",
            file=sys.stderr,
        )
        sys.exit(1)

    if not settings.base_url or not settings.username or not settings.password:
        print(
            "Error: TYPEMILL_BASE_URL, TYPEMILL_USERNAME, and TYPEMILL_PASSWORD "
            "must all be non-empty.",
            file=sys.stderr,
        )
        sys.exit(1)

    client = TypemillClient(settings.base_url, settings.username, settings.password)

    structure.register(mcp, client)
    pages.register(mcp, client)
    blocks.register(mcp, client)
    lifecycle.register(mcp, client)
    meta.register(mcp, client)
    media.register(mcp, client)

    return client


_client = _init()


def main() -> None:
    transport = "stdio"
    if "--transport" in sys.argv:
        idx = sys.argv.index("--transport")
        if idx + 1 < len(sys.argv):
            transport = sys.argv[idx + 1]

    if transport == "sse":
        mcp.run(transport="sse")
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
