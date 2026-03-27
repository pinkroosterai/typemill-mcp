import asyncio
import time
from pathlib import Path

import httpx
import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SETTINGS_DIR = FIXTURES_DIR / "settings"

TYPEMILL_IMAGE = "kixote/typemill"
TYPEMILL_PORT = 80
TYPEMILL_USERNAME = "testadmin"
TYPEMILL_PASSWORD = "testpassword123"

MAX_STARTUP_WAIT = 60  # seconds


def _docker_available() -> bool:
    try:
        import docker
        client = docker.from_env()
        client.ping()
        return True
    except Exception:
        return False


@pytest.fixture(scope="session")
def typemill_client():
    if not _docker_available():
        pytest.skip("Docker is not available — skipping integration tests")

    from testcontainers.core.container import DockerContainer

    container = (
        DockerContainer(TYPEMILL_IMAGE)
        .with_exposed_ports(TYPEMILL_PORT)
        .with_volume_mapping(
            str(SETTINGS_DIR.resolve()),
            "/var/www/html/settings",
            mode="rw",
        )
    )

    container.start()

    try:
        host = container.get_container_host_ip()
        port = container.get_exposed_port(TYPEMILL_PORT)
        base_url = f"http://{host}:{port}"

        # Wait for Typemill to be ready
        deadline = time.time() + MAX_STARTUP_WAIT
        ready = False
        while time.time() < deadline:
            try:
                resp = httpx.get(
                    f"{base_url}/api/v1/navigation",
                    auth=(TYPEMILL_USERNAME, TYPEMILL_PASSWORD),
                    timeout=5.0,
                )
                if resp.status_code in (200, 401, 403):
                    ready = True
                    break
            except (httpx.ConnectError, httpx.ReadError):
                pass
            time.sleep(1)

        if not ready:
            raise RuntimeError(
                f"Typemill container did not become ready within {MAX_STARTUP_WAIT}s"
            )

        from typemill_mcp.client import TypemillClient

        client = TypemillClient(base_url, TYPEMILL_USERNAME, TYPEMILL_PASSWORD)
        yield client

        # Cleanup client
        asyncio.get_event_loop().run_until_complete(client.close())
    finally:
        container.stop()
