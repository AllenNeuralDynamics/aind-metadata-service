"""Tests for acquisition routes"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import status
from fastapi.testclient import TestClient


class TestAcquisitionRoutes:
    """Tests for acquisition endpoints"""

    def test_get_acquisition(
        self,
        client: TestClient,
        mock_dataverse_smartspim_imaging: MagicMock,
    ):
        """Tests a partial acquisition is returned with validation errors,
        since Dataverse has no detector or image tile information."""
        response = client.get("/api/v2/acquisition/886598")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        errors = json.loads(response.headers["X-Error-Message"])
        assert {
            "detector",
            "images",
        } == {error["loc"][-1] for error in errors}
        acquisitions = response.json()
        assert 1 == len(acquisitions)
        assert "886598" == acquisitions[0]["subject_id"]
        assert "SmartSPIM" == acquisitions[0]["acquisition_type"]
        mock_dataverse_smartspim_imaging.assert_awaited_once_with(
            subject_id="886598", _request_timeout=30
        )

    @patch(
        "aind_dataverse_service_async_client.DefaultApi.get_smartspim_imaging"
    )
    def test_get_acquisition_not_found(
        self,
        mock_get_smartspim_imaging: AsyncMock,
        client: TestClient,
    ):
        """Tests a 404 is returned when there is no imaging data."""
        mock_get_smartspim_imaging.return_value = []
        response = client.get("/api/v2/acquisition/000000")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert {"detail": "Not found"} == response.json()
