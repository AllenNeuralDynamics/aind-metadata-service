"""Set up fixtures to be used across all test modules."""

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from requests import Response
from requests_toolbelt.sessions import BaseUrlSession

from aind_metadata_service_server.main import app


@pytest.fixture(scope="session")
def client():
    """Creating a client for testing purposes."""

    with TestClient(app) as c:
        yield c
