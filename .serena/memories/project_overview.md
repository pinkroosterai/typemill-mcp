# Typemill MCP Server - Project Overview

## Purpose
Python MCP server that gives AI assistants tools to manage content in Typemill CMS via the Model Context Protocol. Supports stdio (Claude Desktop/Code) and HTTP+SSE transports.

## Tech Stack
- **Language**: Python >= 3.11
- **Framework**: FastMCP (Model Context Protocol)
- **HTTP Client**: httpx (async)
- **Config**: pydantic-settings + python-dotenv
- **Build**: hatchling
- **Package Manager**: uv
- **Testing**: pytest + pytest-asyncio + respx (mocking) + testcontainers (Docker integration)

## Architecture
```
src/typemill_mcp/
  client.py       — TypemillClient (async httpx, Basic Auth, Referer header) + Settings
  server.py       — FastMCP wiring, CLI entry point
  tools/
    structure.py  — explore_site, rename_page, sort_page
    pages.py      — get_page, create_page, update_page, delete_page
    blocks.py     — add/update/delete/move_block
    lifecycle.py  — publish/unpublish/discard_changes
    meta.py       — get_meta, update_meta
    media.py      — manage_media (unified dispatch for image/file actions)
    types.py      — shared Pydantic models
```

## Key Pattern
Each tool module exports `register(mcp, client)` which decorates async functions with `@mcp.tool()`. Server.py calls all register functions at startup.

## Config
Required env vars: TYPEMILL_BASE_URL, TYPEMILL_USERNAME, TYPEMILL_PASSWORD. Optional: TYPEMILL_PROJECT.
