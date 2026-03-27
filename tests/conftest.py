import shutil
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

import httpx
import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SETTINGS_DIR = FIXTURES_DIR / "settings"

TYPEMILL_IMAGE = "kixote/typemill"
TYPEMILL_PORT = 80
TYPEMILL_USERNAME = "testadmin"
TYPEMILL_PASSWORD = "testpassword123"

MAX_STARTUP_WAIT = 90  # seconds


@dataclass
class TypemillConnection:
    base_url: str
    username: str
    password: str


def _docker_available() -> bool:
    try:
        import docker
        client = docker.from_env()
        client.ping()
        return True
    except Exception:
        return False


def _wait_for_api(base_url: str, username: str, password: str, timeout: int) -> None:
    """Poll Typemill API until it responds (not a 302 redirect to setup)."""
    deadline = time.time() + timeout
    last_error = None
    while time.time() < deadline:
        try:
            resp = httpx.get(
                f"{base_url}/api/v1/navigation",
                auth=(username, password),
                headers={"Referer": base_url + "/"},
                timeout=5.0,
            )
            if resp.status_code != 302:
                return
        except Exception as exc:
            last_error = exc
        time.sleep(2)
    raise RuntimeError(
        f"Typemill API did not become ready within {timeout}s. Last error: {last_error}"
    )


@pytest.fixture(scope="session")
def typemill_connection():
    """Session-scoped fixture that manages the Docker container lifecycle."""
    if not _docker_available():
        pytest.skip("Docker is not available — skipping integration tests")

    from testcontainers.core.container import DockerContainer

    tmp_settings = Path(tempfile.mkdtemp()) / "settings"
    shutil.copytree(SETTINGS_DIR, tmp_settings)

    container = (
        DockerContainer(TYPEMILL_IMAGE)
        .with_exposed_ports(TYPEMILL_PORT)
        .with_volume_mapping(
            str(tmp_settings),
            "/var/www/html/settings",
            mode="rw",
        )
    )

    container.start()

    try:
        host = container.get_container_host_ip()
        port = container.get_exposed_port(TYPEMILL_PORT)
        base_url = f"http://{host}:{port}"

        _wait_for_api(base_url, TYPEMILL_USERNAME, TYPEMILL_PASSWORD, MAX_STARTUP_WAIT)

        yield TypemillConnection(
            base_url=base_url,
            username=TYPEMILL_USERNAME,
            password=TYPEMILL_PASSWORD,
        )
    finally:
        container.stop()
        shutil.rmtree(tmp_settings.parent, ignore_errors=True)


@pytest.fixture
def typemill_client(typemill_connection):
    """Per-test fixture that creates a fresh TypemillClient with its own httpx client."""
    from typemill_mcp.client import TypemillClient

    return TypemillClient(
        typemill_connection.base_url,
        typemill_connection.username,
        typemill_connection.password,
    )
