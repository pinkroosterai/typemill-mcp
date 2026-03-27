# typemill-mcp

MCP server for Typemill CMS — enables AI assistants to read and manage Typemill content via the Model Context Protocol.

## Prerequisites

- Python 3.11+
- A running Typemill instance with API access enabled for a user

## Installation

```bash
git clone <repo-url>
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

### stdio (Claude Desktop / Claude Code)

```bash
typemill-mcp
```

Add to Claude Desktop by editing `claude_desktop_config.json`:

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

### SSE (remote deployment)

```bash
typemill-mcp --transport sse
```

Starts an HTTP+SSE server on port 8000.

## Available Tools

| Tool | Parameters | Description |
|---|---|---|
| `get_navigation` | — | Retrieve the full navigation tree of the Typemill site |
| `get_page` | `url_path` | Retrieve Markdown content of a page by URL path |
| `create_page` | `url_path`, `title`, `content` | Create a new page |
| `update_page` | `url_path`, `content` | Update an existing page's Markdown content |
| `delete_page` | `url_path` | Delete a page (irreversible) |
| `publish_page` | `url_path` | Publish a page to make it publicly visible |
| `unpublish_page` | `url_path` | Unpublish a page without deleting it |
| `get_meta` | `url_path` | Retrieve page metadata |
| `update_meta` | `url_path`, `title?`, `description?`, `noindex?` | Update page metadata |

## Development

Run tests:

```bash
pytest tests/ -v
```
