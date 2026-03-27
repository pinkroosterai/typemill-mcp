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
        self.api_url = f"{base_url.rstrip('/')}/api/v1"
        self._client = httpx.AsyncClient(
            auth=httpx.BasicAuth(username, password),
            headers={"Accept": "application/json"},
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

    # ── Articles ──

    async def get_article_markdown(self, url: str) -> dict:
        return await self._request("POST", "/article/markdown", json={"url": url})

    async def create_article(self, url: str, title: str, content: str) -> dict:
        return await self._request(
            "POST", "/article",
            json={"url": url, "title": title, "content": content},
        )

    async def update_article(self, url: str, content: str) -> dict:
        return await self._request(
            "PUT", "/article",
            json={"url": url, "content": content},
        )

    async def delete_article(self, url: str) -> dict:
        return await self._request("DELETE", "/article", json={"url": url})

    async def publish_article(self, url: str) -> dict:
        return await self._request("POST", "/article/publish", json={"url": url})

    async def unpublish_article(self, url: str) -> dict:
        return await self._request("DELETE", "/article/unpublish", json={"url": url})

    async def rename_article(self, url: str, new_name: str) -> dict:
        return await self._request(
            "POST", "/article/rename",
            json={"url": url, "new_name": new_name},
        )

    async def sort_article(self, url: str, item_id: str, parent_id: str, position: int) -> dict:
        return await self._request(
            "POST", "/article/sort",
            json={"url": url, "item_id": item_id, "parent_id": parent_id, "position": position},
        )

    async def discard_article(self, url: str) -> dict:
        return await self._request("DELETE", "/article/discard", json={"url": url})

    # ── Blocks ──

    async def add_block(self, url: str, block_id: int, content: str) -> dict:
        return await self._request(
            "POST", "/block",
            json={"url": url, "block_id": block_id, "content": content},
        )

    async def update_block(self, url: str, block_id: int, content: str) -> dict:
        return await self._request(
            "PUT", "/block",
            json={"url": url, "block_id": block_id, "content": content},
        )

    async def delete_block(self, url: str, block_id: int) -> dict:
        return await self._request(
            "DELETE", "/block",
            json={"url": url, "block_id": block_id},
        )

    async def move_block(self, url: str, block_id: int, new_position: int) -> dict:
        return await self._request(
            "PUT", "/moveblock",
            json={"url": url, "block_id": block_id, "new_position": new_position},
        )

    # ── Metadata ──

    async def get_article_metadata(self, url: str) -> dict:
        return await self._request("GET", "/article/metadata", params={"url": url})

    async def update_article_metadata(self, url: str, metadata: dict) -> dict:
        return await self._request(
            "POST", "/article/metadata",
            json={"url": url, **metadata},
        )

    async def get_meta_definitions(self) -> dict:
        return await self._request("GET", "/metadefinitions")

    # ── Media: Images ──

    async def browse_images(self) -> dict:
        return await self._request("GET", "/medialib/images")

    async def get_image(self, name: str) -> dict:
        return await self._request("GET", "/image", params={"name": name})

    async def upload_image(self, file: str, name: str) -> dict:
        return await self._request("POST", "/image", json={"file": file, "name": name})

    async def publish_image(self, name: str) -> dict:
        return await self._request("PUT", "/image", json={"name": name})

    async def delete_image(self, name: str) -> dict:
        return await self._request("DELETE", "/image", json={"name": name})

    # ── Media: Files ──

    async def browse_files(self) -> dict:
        return await self._request("GET", "/medialib/files")

    async def get_file(self, name: str) -> dict:
        return await self._request("GET", "/file", params={"name": name})

    async def upload_file(self, file: str, name: str) -> dict:
        return await self._request("POST", "/file", json={"file": file, "name": name})

    async def publish_file(self, name: str) -> dict:
        return await self._request("PUT", "/file", json={"name": name})

    async def delete_file(self, name: str) -> dict:
        return await self._request("DELETE", "/file", json={"name": name})
