# Code Style and Conventions

## Naming
- Snake_case for functions, variables, modules
- PascalCase for classes and Pydantic models
- Tool functions are async, registered via `@mcp.tool()` decorator

## Type Hints
- Full type annotations on all function signatures
- Pydantic BaseModel with `Field(description=...)` for complex tool parameters
- `Literal[...]` to constrain parameter values
- `Annotated[type, Field(description=...)]` for tool parameters

## Tool Design
- Each tool does one thing (single-purpose)
- All tools return `json.dumps(result, indent=2)`
- Descriptions: lead with verb + resource, 1-2 sentences max
- Parameter descriptions include format, examples, valid values
- Never require caller to pass serialized JSON strings

## Testing
- Unit tests use respx to mock httpx
- asyncio_mode = "auto" (no need for @pytest.mark.asyncio)
- Integration tests use testcontainers with Docker

## Key Quirk
- All POST/PUT/DELETE requests require a Referer header (Typemill SecurityMiddleware)
