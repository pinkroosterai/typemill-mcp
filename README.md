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

No install needed — run directly from source with `uv run`. Use `add-json` for reliable env var handling:

```bash
claude mcp add-json typemill '{
  "type": "stdio",
  "command": "uv",
  "args": ["run", "--directory", "/path/to/typemill-mcp", "typemill-mcp"],
  "env": {
    "TYPEMILL_BASE_URL": "https://your-typemill-site.com",
    "TYPEMILL_USERNAME": "your_api_username",
    "TYPEMILL_PASSWORD": "your_api_password"
  }
}'
```

Or use `uvx` to run from the git repo without cloning:

```bash
claude mcp add-json typemill '{
  "type": "stdio",
  "command": "uvx",
  "args": ["--from", "git+https://github.com/pinkroosterai/typemill-mcp.git", "typemill-mcp"],
  "env": {
    "TYPEMILL_BASE_URL": "https://your-typemill-site.com",
    "TYPEMILL_USERNAME": "your_api_username",
    "TYPEMILL_PASSWORD": "your_api_password"
  }
}'
```

If you prefer a permanent install, use `pipx`:

```bash
pipx install /path/to/typemill-mcp        # from local source
pipx install git+https://github.com/pinkroosterai/typemill-mcp.git  # from git

claude mcp add-json typemill '{
  "type": "stdio",
  "command": "typemill-mcp",
  "env": {
    "TYPEMILL_BASE_URL": "https://your-typemill-site.com",
    "TYPEMILL_USERNAME": "your_api_username",
    "TYPEMILL_PASSWORD": "your_api_password"
  }
}'
```

Use `--scope user` to make it available across all projects, or `--scope project` to share via `.mcp.json`:

```bash
claude mcp add-json typemill --scope user '{
  "type": "stdio",
  "command": "uv",
  "args": ["run", "--directory", "/path/to/typemill-mcp", "typemill-mcp"],
  "env": {
    "TYPEMILL_BASE_URL": "https://your-typemill-site.com",
    "TYPEMILL_USERNAME": "your_api_username",
    "TYPEMILL_PASSWORD": "your_api_password"
  }
}'
```

Verify it's running:

```bash
claude mcp list        # list all configured servers
claude mcp get typemill # check this server's config
```

Inside Claude Code, use `/mcp` to check server status and available tools.

### Claude Desktop

Add to `claude_desktop_config.json`. Use `uv run` to avoid a global install:

```json
{
  "mcpServers": {
    "typemill": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/typemill-mcp", "typemill-mcp"],
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
uv run --directory /path/to/typemill-mcp typemill-mcp
```

### SSE (remote deployment)

```bash
uv run --directory /path/to/typemill-mcp typemill-mcp --transport sse
```

Starts an HTTP+SSE server on port 8000.

## Available Tools

### Site Structure
| Tool | Parameters | Description |
|---|---|---|
| `explore_site` | — | Formatted site tree with page statuses and hierarchy |
| `rename_page` | `url_path`, `item_id`, `new_name` | Rename a page (title and URL slug) |
| `sort_page` | `url_path`, `item_id`, `parent_id`, `position` | Move a page in the navigation tree |

### Pages
| Tool | Parameters | Description |
|---|---|---|
| `get_page` | `url_path` | Retrieve markdown blocks + metadata in one response |
| `create_page` | `folder_id`, `item_name`, `item_type?` | Create a new page (`folder_id` is `"root"` or a key path) |
| `delete_page` | `url_path`, `item_id` | Delete a page (irreversible) |

### Content Blocks
| Tool | Parameters | Description |
|---|---|---|
| `add_block` | `url_path`, `block_id`, `content` | Insert a markdown block at a position |
| `update_block` | `url_path`, `block_id`, `content` | Edit a specific content block |
| `delete_block` | `url_path`, `block_id` | Remove a content block |
| `move_block` | `url_path`, `block_id`, `new_position` | Reorder a content block |

### Page Lifecycle
| Tool | Parameters | Description |
|---|---|---|
| `publish_page` | `url_path`, `item_id` | Publish a page to make it publicly visible |
| `unpublish_page` | `url_path`, `item_id` | Revert a page to draft state |
| `discard_changes` | `url_path`, `item_id` | Discard unpublished edits (irreversible) |

### Metadata
| Tool | Parameters | Description |
|---|---|---|
| `get_meta` | `url_path` | Retrieve page metadata |
| `update_meta` | `url_path`, `title?`, `description?`, `noindex?` | Update page metadata |

### Media
| Tool | Parameters | Description |
|---|---|---|
| `manage_media` | `action`, `name?`, `file?` | Unified media tool (browse/get/upload/publish/delete images and files) |

## Development

Run unit tests (mocked, no Docker needed):

```bash
pytest tests/ -v --ignore=tests/test_integration.py
```

Run integration tests (requires Docker):

```bash
pytest -m integration -v
```

Integration tests spin up a real Typemill instance in Docker using [testcontainers](https://testcontainers.com/), pre-seeded with an admin user. They validate all client methods against the live API and clean up automatically. The Docker image (`kixote/typemill`) is pulled on first run.
