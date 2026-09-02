"""Set up fixtures to be used across all test modules."""

import warnings
from contextlib import contextmanager
from typing import Any, Generator
from unittest.mock import AsyncMock, patch

import pytest
from aind_smartsheet_service_async_client.models import ExaSPIMInfo
from aind_tars_service_async_client import (
    Alias,
    PrepLotData,
    ViralPrep,
    VirusData,
)
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
    return PrepLotData(
        lot="230929-12",
        viral_prep=ViralPrep(
            virus=VirusData(aliases=[Alias(is_preferred=True, name="v_123")])
        ),
    )


@pytest.fixture()
def mock_tars_virus_v123():
    """Fixture for TARS virus v_123."""
    return VirusData(aliases=[Alias(is_preferred=True, name="v_123")])


@pytest.fixture()
def mock_smartsheet_exaspim_info():
    """Fixture for Smartsheet ExaSPIM info."""
    exaspim_data = {
        "mouse_tracker_info": [
            {
                "num": 1,
                "sample_name": "Test Sample",
                "virus_mix_total_volume_injected_ro_ul": "100",
                "virus1_injection_date": "2023-03-31",
                "virus1": "Test Virus",
                "virus1_id": "V123",
                "virus1_stock_titer_gc_ml": "1.35E+14",
            }
        ],
        "sample_tracking_info": [
            {
                "sample": "822178",
                "processing_lead": "Test Experimenter",
                "status": "Imaged",
                "dcm_delipidation_start": "2023-07-20",
                "sbip_delipidation_end": "2023-08-14",
            }
        ],
        "imaging_queue_info": [
            {
                "sample": "822178",
                "imaging_start_date": "2024-01-08",
                "microscope": "ExaSPIM",
            }
        ],
        "qc_sheet_info": [],
    }
    return ExaSPIMInfo.model_validate(exaspim_data)


@contextmanager
def suppress_pydantic_serialization_warnings():
    """
    Context manager to suppress expected Pydantic serialization warnings.
    """
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            category=UserWarning,
            message=".*Pydantic serializer warnings.*",
        )
        yield


@pytest.fixture(autouse=False)
def mock_emapa_api():
    """
    Fixture to mock the EMAPA ontology API calls.

    This prevents tests from making actual HTTP requests to the external
    EMAPA ontology service, which can fail if the service is down.

    The fixture mocks common anatomical structures used in injection targets.
    """

    def mock_search(class_name):
        """Mock responses for common anatomical structures."""
        emapa_responses = {
            "peritoneal cavity": [
                {
                    "iri": "http://purl.obolibrary.org/obo/EMAPA_16246",
                    "label": "peritoneal cavity",
                }
            ],
            "venous sinus": [
                {
                    "iri": "http://purl.obolibrary.org/obo/EMAPA_17180",
                    "label": "venous sinus",
                }
            ],
        }
        return emapa_responses.get(class_name, [])

    with patch(
        "aind_data_schema_models.mouse_anatomy.search_emapa_exact_match",
        side_effect=mock_search,
    ) as mock:
        yield mock
