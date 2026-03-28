# Suggested Commands

## Development
```bash
# Install dependencies
cd typemill-mcp && uv sync --dev

# Run MCP server (stdio mode)
cd typemill-mcp && uv run typemill-mcp
```

## Testing
```bash
# Unit tests (mocked, fast, no Docker)
cd typemill-mcp && uv run pytest tests/ -v --ignore=tests/test_integration.py

# Single test
cd typemill-mcp && uv run pytest tests/test_blocks.py::test_add_block -v

# Integration tests (requires Docker)
cd typemill-mcp && uv run pytest -m integration -v
```

## System Utils (Linux)
- `git` — version control
- `uv` — Python package manager (replaces pip/poetry)
- `ls`, `cd`, `grep`, `find` — standard Linux utils
