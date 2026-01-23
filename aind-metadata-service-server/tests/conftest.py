"""Set up fixtures to be used across all test modules."""

from typing import Any, Generator
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from pytest_mock import MockFixture
from starlette.responses import JSONResponse

from aind_metadata_service_server.main import app
from aind_metadata_service_server.sessions import (
    get_aind_data_schema_v1_session,
)


@pytest.fixture()
def mock_proxy(mocker: MockFixture) -> AsyncMock:
    """Mock the proxy method."""
    mock_response = JSONResponse({"message": "Success"})
    mock_response.status_code = 200
    mock_proxy.return_value = mock_response
    mock_get = mocker.patch(
        "aind_metadata_service_server.routes.v1_proxy.proxy"
    )
    mock_get.return_value = mock_response
    return mock_get


@pytest.fixture(scope="session")
def client() -> Generator[TestClient, Any, None]:
    """Creating a client for testing purposes."""

    def override_get_v1_session():
        """Override standard session with the one for tests."""
        yield AsyncMock()

    app.dependency_overrides[get_aind_data_schema_v1_session] = (
        override_get_v1_session
    )
    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture()
def mock_tars_prep_lot_230929():
    """Fixture for TARS prep lot 230929-12."""
    from aind_tars_service_async_client import (
        Alias,
        PrepLotData,
        ViralPrep,
        VirusData,
    )

    return PrepLotData(
        lot="230929-12",
        viral_prep=ViralPrep(
            virus=VirusData(aliases=[Alias(is_preferred=True, name="v_123")])
        ),
    )


@pytest.fixture()
def mock_tars_virus_v123():
    """Fixture for TARS virus v_123."""
    from aind_tars_service_async_client import Alias, VirusData

    return VirusData(aliases=[Alias(is_preferred=True, name="v_123")])
