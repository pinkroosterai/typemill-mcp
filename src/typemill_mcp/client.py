import httpx
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    base_url: str
    username: str
    password: str
    project: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="TYPEMILL_")


class TypemillClient:
    def __init__(self, base_url: str, username: str, password: str) -> None:
        self._base_url = base_url.rstrip("/")
        self.api_url = f"{self._base_url}/api/v1"
        self._client = httpx.AsyncClient(
            auth=httpx.BasicAuth(username, password),
            headers={
                "Accept": "application/json",
                # Referer required by Typemill's SecurityMiddleware for POST/PUT/DELETE
                "Referer": self._base_url + "/",
            },
            timeout=30.0,
        )

    async def close(self) -> None:
        """Close the underlying HTTP client and release connections."""
        await self._client.aclose()

    async def _request(self, method: str, path: str, **kwargs) -> dict:
        url = f"{self.api_url}/{path.lstrip('/')}"
        resp = await self._client.request(method, url, **kwargs)
        if not resp.is_success:
            raise RuntimeError(
                f"Typemill API error {resp.status_code}: {resp.text}"
            )
        return resp.json()

    # ── Navigation ──

    async def get_navigation(self, draft: bool = True) -> dict:
        params = {"draft": "true"} if draft else {}
        return await self._request("GET", "/navigation", params=params)

    # ── Articles (read — external API) ──

    async def get_article_content(self, url: str) -> dict:
        """GET /article/content — returns markdown blocks with id, markdown, html."""
        return await self._request("GET", "/article/content", params={"url": url})

    async def get_article_meta(self, url: str) -> dict:
        """GET /article/meta — returns page metadata (navtitle, title, description, etc.)."""
        return await self._request("GET", "/article/meta", params={"url": url})

    async def get_article_item(self, url: str) -> dict:
        """GET /article/item — returns navigation item details for a URL."""
        return await self._request("GET", "/article/item", params={"url": url})

    # ── Articles (write — author API) ──

    async def create_article(self, folder_id: str, item_name: str, item_type: str = "file") -> dict:
        """POST /article — create a new page. folder_id is 'root' or a key path like '0'."""
        return await self._request(
            "POST", "/article",
            json={"folder_id": folder_id, "item_name": item_name, "type": item_type},
        )

    async def update_draft(self, url: str, item_id: str, title: str, body: str) -> dict:
        """PUT /draft — update a page's draft content. title is the H1 markdown (e.g. '# My Page'). body is raw markdown for the rest of the page."""
        return await self._request(
            "PUT", "/draft",
            json={"url": url, "item_id": item_id, "title": title, "body": body},
        )

    async def delete_article(self, url: str, item_id: str) -> dict:
        """DELETE /article — delete a page."""
        return await self._request(
            "DELETE", "/article",
            json={"url": url, "item_id": item_id},
        )

    async def publish_article(self, url: str, item_id: str) -> dict:
        """POST /article/publish — publish a draft page."""
        return await self._request(
            "POST", "/article/publish",
            json={"url": url, "item_id": item_id},
        )

    async def unpublish_article(self, url: str, item_id: str) -> dict:
        """DELETE /article/unpublish — revert a published page to draft."""
        return await self._request(
            "DELETE", "/article/unpublish",
            json={"url": url, "item_id": item_id},
        )

    async def discard_article(self, url: str, item_id: str) -> dict:
        """DELETE /article/discard — discard unpublished changes."""
        return await self._request(
            "DELETE", "/article/discard",
            json={"url": url, "item_id": item_id},
        )

    async def rename_article(self, url: str, item_id: str, new_name: str) -> dict:
        """POST /article/rename — rename a page."""
        old_slug = url.rstrip("/").rsplit("/", 1)[-1]
        return await self._request(
            "POST", "/article/rename",
            json={"url": url, "item_id": item_id, "slug": new_name, "oldslug": old_slug},
        )

    async def sort_article(self, url: str, item_id: str, parent_id: str, position: int) -> dict:
        """POST /article/sort — move a page to a new position."""
        return await self._request(
            "POST", "/article/sort",
            json={"url": url, "item_id": item_id, "parent_id": parent_id, "position": position},
        )

    # ── Blocks ──

    async def add_block(self, url: str, block_id: int, content: str) -> dict:
        return await self._request(
            "POST", "/block",
            json={"url": url, "block_id": block_id, "markdown": content},
        )

    async def update_block(self, url: str, block_id: int, content: str) -> dict:
        return await self._request(
            "PUT", "/block",
            json={"url": url, "block_id": block_id, "markdown": content},
        )

    async def delete_block(self, url: str, block_id: int) -> dict:
        return await self._request(
            "DELETE", "/block",
            json={"url": url, "block_id": block_id},
        )

    async def move_block(self, url: str, block_id: int, new_position: int) -> dict:
        return await self._request(
            "PUT", "/block/move",
            json={"url": url, "index_old": block_id, "index_new": new_position},
        )

    # ── Metadata ──

    async def get_metadata(self, url: str) -> dict:
        """GET /meta — returns full metadata for a page."""
        return await self._request("GET", "/meta", params={"url": url})

    async def update_metadata(self, url: str, metadata: dict, tab: str = "meta") -> dict:
        """POST /meta — update page metadata. tab is the metadata tab name (default 'meta')."""
        return await self._request(
            "POST", "/meta",
            json={"url": url, "tab": tab, "data": metadata},
        )

    # ── Media: Images ──

    async def browse_images(self) -> dict:
        return await self._request("GET", "/images")

    async def get_image(self, name: str) -> dict:
        return await self._request("GET", "/image", params={"name": name})

    async def upload_image(self, file: str, name: str) -> dict:
        return await self._request("POST", "/image", json={"image": file, "name": name})

    async def publish_image(self, name: str) -> dict:
        return await self._request("PUT", "/image", json={"name": name})

    async def delete_image(self, name: str) -> dict:
        return await self._request("DELETE", "/image", json={"name": name})

    # ── Media: Files ──

    async def browse_files(self) -> dict:
        return await self._request("GET", "/files")

    async def get_file(self, name: str) -> dict:
        return await self._request("GET", "/file", params={"name": name})

    async def upload_file(self, file: str, name: str) -> dict:
        return await self._request("POST", "/file", json={"file": file, "name": name})

    async def publish_file(self, name: str) -> dict:
        return await self._request("PUT", "/file", json={"name": name})

    async def delete_file(self, name: str) -> dict:
        return await self._request("DELETE", "/file", json={"name": name})
