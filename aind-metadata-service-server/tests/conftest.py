"""Set up fixtures to be used across all test modules."""

from typing import Any, Generator

import pytest
from fastapi.testclient import TestClient

from aind_metadata_service_server.main import app


@pytest.fixture(scope="session")
def client() -> Generator[TestClient, Any, None]:
    """Creating a client for testing purposes."""

    with TestClient(app) as c:
        yield c
