# Task Completion Checklist

When a coding task is completed, run these steps:

1. **Unit tests**: `cd typemill-mcp && uv run pytest tests/ -v --ignore=tests/test_integration.py`
2. **Verify no regressions**: All 38+ unit tests should pass
3. **If new tools added**: Ensure register() function is updated and server.py imports the module
4. **If API fields changed**: Verify field names against Typemill v2.x source code (not master branch)
5. **No linter/formatter configured** — just ensure consistent style with existing code
