"""Test rig and instrument routes"""

import json
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

TEST_DIR = Path(__file__).parent / ".."
TEST_RIG_JSON = TEST_DIR / "resources" / "slims" / "rig_example.json"
TEST_INSTRUMENT_JSON = (
    TEST_DIR / "resources" / "slims" / "instrument_example.json"
)


class TestRoute:
    """Test responses."""

    @patch(
        "aind_slims_service_async_client.DefaultApi.get_aind_instrument",
        new_callable=AsyncMock,
    )
    def test_get_rig(
        self,
        mock_slims_api_get: AsyncMock,
        client: TestClient,
    ):
        """Tests a good response"""
        with open(TEST_RIG_JSON) as f:
            rig_data = json.load(f)
        mock_slims_api_get.return_value = [rig_data]
        response = client.get("/api/v2/rig/323_EPHYS1_20250205")

        mock_slims_api_get.assert_called_once_with(
            input_id="323_EPHYS1_20250205", partial_match=False
        )
        assert 400 == response.status_code
        assert (
            "Models have not been validated."
            == response.headers["X-Error-Message"]
        )

    @patch(
        "aind_slims_service_async_client.DefaultApi.get_aind_instrument",
        new_callable=AsyncMock,
    )
    def test_get_instrument(
        self,
        mock_slims_api_get: AsyncMock,
        client: TestClient,
    ):
        """Tests a good response"""
        with open(TEST_INSTRUMENT_JSON) as f:
            instrument_data = json.load(f)
        mock_slims_api_get.return_value = [instrument_data]
        response = client.get(
            "/api/v2/instrument/440_SmartSPIM1_20240327?partial_match=True"
        )

        mock_slims_api_get.assert_called_once_with(
            input_id="440_SmartSPIM1_20240327", partial_match=True
        )
        assert 400 == response.status_code
        assert (
            "Models have not been validated."
            == response.headers["X-Error-Message"]
        )

    @patch(
        "aind_slims_service_async_client.DefaultApi.get_aind_instrument",
        new_callable=AsyncMock,
    )
    def test_get_rig_not_found(
        self,
        mock_slims_api_get: AsyncMock,
        client: TestClient,
    ):
        """Tests 404 response when rig is not found"""
        mock_slims_api_get.return_value = []

        response = client.get("/api/v2/rig/nonexistent_rig")

        mock_slims_api_get.assert_called_once_with(
            input_id="nonexistent_rig", partial_match=False
        )
        assert 404 == response.status_code
        assert response.json()["detail"] == "Not found"

    @patch(
        "aind_slims_service_async_client.DefaultApi.get_aind_instrument",
        new_callable=AsyncMock,
    )
    def test_get_instrument_not_found(
        self,
        mock_slims_api_get: AsyncMock,
        client: TestClient,
    ):
        """Tests 404 response when instrument is not found"""
        mock_slims_api_get.return_value = []

        response = client.get("/api/v2/instrument/nonexistent_instrument")

        mock_slims_api_get.assert_called_once_with(
            input_id="nonexistent_instrument", partial_match=False
        )
        assert 404 == response.status_code
        assert response.json()["detail"] == "Not found"


if __name__ == "__main__":
    pytest.main([__file__])
