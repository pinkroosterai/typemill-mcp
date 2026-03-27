"""Shared annotated types and helpers for tool modules."""

import json
from typing import Annotated

from pydantic import Field

ItemId = Annotated[
    str,
    Field(
        description=(
            "The page's keyPath from the navigation tree (e.g. '0', '0.1', '2.3'). "
            "Get this from explore_site output. NOT the pageid hex hash from metadata."
        )
    ),
]

UrlPath = Annotated[
    str,
    Field(
        description="Relative URL path of the page (e.g. '/welcome-to-clarive', '/news/fast-website')."
    ),
]


def compact_response(result: dict) -> str:
    """Strip the bulky navigation array from API responses to reduce token usage.

    Typemill returns the full navigation tree in most write responses. This is
    useful for the browser UI but wastes LLM context. We keep only the fields
    that carry actionable information: item, content, metadata, message, url,
    rename, errors.
    """
    if "navigation" in result:
        trimmed = {k: v for k, v in result.items() if k != "navigation"}
        if not trimmed:
            # Response was navigation-only (e.g. create_page) — summarize it
            return json.dumps({"message": "OK", "navigation_items": len(result["navigation"])}, indent=2)
        return json.dumps(trimmed, indent=2)
    return json.dumps(result, indent=2)
