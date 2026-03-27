"""Shared annotated types for tool parameters."""

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
