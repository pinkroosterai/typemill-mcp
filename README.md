# typemill-mcp

MCP server for Typemill CMS — enables AI assistants to read and manage Typemill content via the Model Context Protocol.

## Prerequisites

- Python 3.11+
- A running Typemill instance with API access enabled for a user

## Installation

```bash
git clone https://github.com/pinkroosterai/typemill-mcp.git
cd typemill-mcp
pip install -e .
```

For development (includes test dependencies):

```bash
pip install -e ".[dev]"
```

## Configuration

Copy `.env.example` to `.env` and fill in your Typemill credentials:

```bash
cp .env.example .env
```

| Variable | Required | Description |
|---|---|---|
| `TYPEMILL_BASE_URL` | Yes | Full URL of your Typemill site (e.g. `https://mysite.com`) |
| `TYPEMILL_USERNAME` | Yes | Username of a Typemill user with API access enabled |
| `TYPEMILL_PASSWORD` | Yes | Password for that user |
| `TYPEMILL_PROJECT` | No | Project slug for multi-project Typemill setups |

## Usage

### Claude Code (CLI)

Add the server with a single command:

```bash
claude mcp add --transport stdio \
  --env TYPEMILL_BASE_URL=https://your-typemill-site.com \
  --env TYPEMILL_USERNAME=your_api_username \
  --env TYPEMILL_PASSWORD=your_api_password \
  typemill -- typemill-mcp
```

This registers the server for your current project. Use `--scope user` to make it available across all projects, or `--scope project` to share it with your team via `.mcp.json`:

```bash
# Available across all your projects
claude mcp add --scope user --transport stdio \
  --env TYPEMILL_BASE_URL=https://your-typemill-site.com \
  --env TYPEMILL_USERNAME=your_api_username \
  --env TYPEMILL_PASSWORD=your_api_password \
  typemill -- typemill-mcp

# Shared with team (committed to .mcp.json)
claude mcp add --scope project --transport stdio \
  typemill -- typemill-mcp
```

Verify it's running:

```bash
claude mcp list        # list all configured servers
claude mcp get typemill # check this server's config
```

Inside Claude Code, use `/mcp` to check server status and available tools.

### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "typemill": {
      "command": "typemill-mcp",
      "env": {
        "TYPEMILL_BASE_URL": "https://your-typemill-site.com",
        "TYPEMILL_USERNAME": "your_api_username",
        "TYPEMILL_PASSWORD": "your_api_password"
      }
    }
  }
}
```

### stdio (direct)

```bash
typemill-mcp
```

### SSE (remote deployment)

```bash
typemill-mcp --transport sse
```

Starts an HTTP+SSE server on port 8000.

## Available Tools

| Tool | Parameters | Description |
|---|---|---|
| `explore_site` | — | Formatted site tree with page statuses and hierarchy |
| `rename_page` | `url_path`, `new_name` | Rename a page (title and URL slug) |
| `sort_page` | `url_path`, `item_id`, `parent_id`, `position` | Move a page in the navigation tree |
| `get_page` | `url_path` | Retrieve markdown blocks + metadata in one response |
| `create_page` | `url_path`, `title`, `content` | Create a new page |
| `delete_page` | `url_path` | Delete a page (irreversible) |
| `add_block` | `url_path`, `block_id`, `content` | Insert a content block at a position |
| `update_block` | `url_path`, `block_id`, `content` | Edit a specific content block |
| `delete_block` | `url_path`, `block_id` | Remove a content block |
| `move_block` | `url_path`, `block_id`, `new_position` | Reorder a content block |
| `publish_page` | `url_path` | Publish a page to make it publicly visible |
| `unpublish_page` | `url_path` | Revert a page to draft state |
| `discard_changes` | `url_path` | Discard unpublished edits (irreversible) |
| `get_meta` | `url_path` | Retrieve page metadata |
| `update_meta` | `url_path`, `title?`, `description?`, `noindex?` | Update page metadata |
| `manage_media` | `action`, `name?`, `file?` | Unified media tool (browse/get/upload/publish/delete images and files) |

## Development

Run tests:

```bash
pytest tests/ -v
```
