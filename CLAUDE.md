# Typemill MCP Server

## Project Overview

Python MCP server for Typemill CMS. Uses FastMCP, httpx (async), and Pydantic. Runs via stdio (Claude Desktop/Code) or HTTP+SSE.

## Architecture

```
src/typemill_mcp/
  client.py       — TypemillClient (async httpx, Basic Auth, Referer header) + Settings (pydantic-settings)
  server.py       — FastMCP wiring, CLI entry point (stdio/sse)
  tools/
    structure.py   — explore_site, rename_page, sort_page
    pages.py       — get_page (orchestrates content+meta), create_page, delete_page
    blocks.py      — add/update/delete/move_block
    lifecycle.py   — publish/unpublish/discard_changes
    meta.py        — get_meta, update_meta
    media.py       — manage_media (unified dispatch for 10 image/file actions)
```

## Key Conventions

- **Tool registration pattern**: Each tool module exports `register(mcp, client)` which decorates async functions with `@mcp.tool()`.
- **All tools return** `json.dumps(result, indent=2)` for LLM readability.
- **Client methods** map 1:1 to Typemill API endpoints. All use `self._request()` helper.
- **Referer header** is required by Typemill's SecurityMiddleware for all POST/PUT/DELETE requests. It's set globally on the httpx client.

## Typemill API Notes

The API has two layers:
- **External/read API** (GET endpoints like `/article/content`, `/article/meta`, `/navigation`) — used for reading content, accepts query params.
- **Author/write API** (POST/PUT/DELETE like `/article`, `/draft`, `/block`, `/meta`) — used for mutations, accepts JSON body. Most write endpoints require `item_id` (the page's key path from the navigation tree).

Key quirks:
- `create_article` takes `folder_id` ("root" or key path), `item_name` (slug), `type` ("file"/"folder") — not a URL.
- `update_draft` (PUT `/draft`) replaces `update_article` — takes `item_id`, `title`, `body` (JSON array of blocks).
- `update_metadata` (POST `/meta`) requires `{url, tab, data}` structure — `tab` is usually "meta", `data` contains the fields.
- Navigation items have `key` (int) and `keyPath` (string like "0.1") — use `keyPath` as `item_id` for write operations.

## Testing

```bash
# Unit tests (mocked with respx, fast)
pytest tests/ -v --ignore=tests/test_integration.py

# Integration tests (real Typemill in Docker via testcontainers)
pytest -m integration -v
```

- Unit tests: 38 tests using respx to mock httpx responses
- Integration tests: 13 tests against a real Typemill Docker container (`kixote/typemill`)
- Integration fixture pre-seeds admin user via YAML files in `tests/fixtures/settings/`
- Per-test client fixture avoids httpx event loop issues across async tests
- Seed files copied to tmpdir to prevent container `chown` from affecting git-tracked files

## Dependencies

Runtime: `mcp[cli]`, `httpx`, `pydantic`, `pydantic-settings`, `python-dotenv`
Dev: `pytest`, `pytest-asyncio`, `respx`, `testcontainers`, `bcrypt`
