"""Set up fixtures to be used across all test modules."""

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from requests import Response
from requests_toolbelt.sessions import BaseUrlSession

from aind_metadata_service_server.main import app

RESOURCES_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / "resources"


@pytest.fixture()
def mock_get_example_response(mocker):
    """Mock example response"""
    with open(RESOURCES_DIR / "example_response.txt") as f:
        contents = f.read()
    mock_get = mocker.patch("requests_toolbelt.sessions.BaseUrlSession.get")
    mock_response = Response()
    mock_response.status_code = 200
    mock_response._content = contents.encode("utf-8")
    mock_get.return_value = mock_response


@pytest.fixture()
def mock_get_empty_response(mocker):
    """Mock empty string response"""

    mock_get = mocker.patch("requests_toolbelt.sessions.BaseUrlSession.get")
    mock_response = Response()
    mock_response.status_code = 200
    mock_response._content = "".encode("utf-8")
    mock_get.return_value = mock_response


@pytest.fixture(scope="session")
def get_test_session():
    """Generate a session for testing."""
    session = BaseUrlSession(base_url="example")
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="session")
def client():
    """Creating a client for testing purposes."""

    with TestClient(app) as c:
        yield c
