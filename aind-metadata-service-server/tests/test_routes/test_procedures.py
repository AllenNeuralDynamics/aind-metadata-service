"""Tests procedures route"""

import json
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from aind_labtracks_service_async_client.models import Task as LabTracksTask
from aind_sharepoint_service_async_client.models import (
    NSB2019List,
    NSB2023List,
)
from fastapi.testclient import TestClient

TEST_DIR = Path(__file__).parent / ".."
EXAMPLE_NSB2019_JSON = (
    TEST_DIR / "resources" / "nsb2019" / "raw" / "list_item1.json"
)
EXAMPLE_NSB2023_JSON = (
    TEST_DIR / "resources" / "nsb2023" / "raw" / "list_item2.json"
)


class TestRoute:
    """Test responses."""

    @patch("aind_labtracks_service_async_client.DefaultApi.get_tasks")
    @patch("aind_sharepoint_service_async_client.DefaultApi.get_las2020")
    @patch("aind_sharepoint_service_async_client.DefaultApi.get_nsb2019")
    @patch("aind_sharepoint_service_async_client.DefaultApi.get_nsb2023")
    @patch("aind_sharepoint_service_async_client.DefaultApi.get_nsb_present")
    @patch(
        "aind_slims_service_async_client.DefaultApi.get_water_restriction_data"
    )
    @patch("aind_slims_service_async_client.DefaultApi.get_histology_data")
    @patch("aind_smartsheet_service_async_client.DefaultApi.get_perfusions")
    @patch("aind_smartsheet_service_async_client.DefaultApi.get_protocols")
    def test_get_procedures_valid_data(
        self,
        mock_get_protocols: AsyncMock,
        mock_get_perfusions: AsyncMock,
        mock_get_histology: AsyncMock,
        mock_get_water_restriction: AsyncMock,
        mock_nsb_present: AsyncMock,
        mock_nsb2023: AsyncMock,
        mock_nsb2019: AsyncMock,
        mock_las: AsyncMock,
        mock_labtracks: AsyncMock,
        client: TestClient,
    ):
        """Tests successful retrieval of procedures."""
        mock_labtracks.return_value = [
            LabTracksTask(
                id="00000",
                type_name="Perfusion Gel",
                date_start=datetime(2022, 10, 11, 0, 0),
                date_end=datetime(2022, 10, 11, 4, 30),
                investigator_id="28803",
                task_object="000000",
                protocol_number="2002",
                task_status="F",
            )
        ]
        mock_las.return_value = []
        mock_nsb2019.return_value = []
        mock_get_perfusions.return_value = []
        mock_get_protocols.return_value = []
        mock_nsb2023.return_value = []
        mock_nsb_present.return_value = []
        mock_get_water_restriction.return_value = []
        mock_get_histology.return_value = []

        response = client.get("api/v2/procedures/000000")
        assert response.status_code == 200

    @patch("aind_labtracks_service_async_client.DefaultApi.get_tasks")
    @patch("aind_sharepoint_service_async_client.DefaultApi.get_las2020")
    @patch("aind_sharepoint_service_async_client.DefaultApi.get_nsb2019")
    @patch("aind_sharepoint_service_async_client.DefaultApi.get_nsb2023")
    @patch("aind_sharepoint_service_async_client.DefaultApi.get_nsb_present")
    @patch(
        "aind_slims_service_async_client.DefaultApi.get_water_restriction_data"
    )
    @patch("aind_slims_service_async_client.DefaultApi.get_histology_data")
    @patch("aind_smartsheet_service_async_client.DefaultApi.get_perfusions")
    @patch("aind_smartsheet_service_async_client.DefaultApi.get_protocols")
    def test_get_procedures_invalid_data(
        self,
        mock_get_protocols: AsyncMock,
        mock_get_perfusions: AsyncMock,
        mock_get_histology: AsyncMock,
        mock_get_water_restriction: AsyncMock,
        mock_nsb_present: AsyncMock,
        mock_nsb2023: AsyncMock,
        mock_nsb2019: AsyncMock,
        mock_las: AsyncMock,
        mock_labtracks: AsyncMock,
        client: TestClient,
    ):
        """Tests successful retrieval of procedures."""
        mock_labtracks.return_value = [
            LabTracksTask(
                id="00000",
                type_name="Perfusion Gel",
                date_start=datetime(2022, 10, 11, 0, 0),
                date_end=datetime(2022, 10, 11, 4, 30),
                investigator_id="28803",
                task_object="000000",
                protocol_number="2002",
                task_status="F",
            )
        ]
        mock_las.return_value = []
        mock_get_protocols.return_value = []
        mock_get_perfusions.return_value = []
        mock_get_water_restriction.return_value = []
        mock_get_histology.return_value = []

        with open(EXAMPLE_NSB2019_JSON) as f:
            contents_nsb2019 = json.load(f)
        with open(EXAMPLE_NSB2023_JSON) as f:
            contents_nsb2023 = json.load(f)
        mock_nsb2019.return_value = [
            NSB2019List.model_validate(contents_nsb2019)
        ]
        mock_nsb2023.return_value = [
            NSB2023List.model_validate(contents_nsb2023)
        ]
        mock_nsb_present.return_value = []

        response = client.get("api/v2/procedures/000000")
        assert response.status_code == 400

    @patch("aind_labtracks_service_async_client.DefaultApi.get_tasks")
    @patch("aind_sharepoint_service_async_client.DefaultApi.get_las2020")
    @patch("aind_sharepoint_service_async_client.DefaultApi.get_nsb2019")
    @patch("aind_sharepoint_service_async_client.DefaultApi.get_nsb2023")
    @patch("aind_sharepoint_service_async_client.DefaultApi.get_nsb_present")
    @patch(
        "aind_slims_service_async_client.DefaultApi.get_water_restriction_data"
    )
    @patch("aind_slims_service_async_client.DefaultApi.get_histology_data")
    @patch("aind_smartsheet_service_async_client.DefaultApi.get_perfusions")
    @patch("aind_smartsheet_service_async_client.DefaultApi.get_protocols")
    def test_get_procedures_no_data(
        self,
        mock_get_protocols: AsyncMock,
        mock_get_perfusions: AsyncMock,
        mock_get_histology: AsyncMock,
        mock_get_water_restriction: AsyncMock,
        mock_nsb_present: AsyncMock,
        mock_nsb2023: AsyncMock,
        mock_nsb2019: AsyncMock,
        mock_las: AsyncMock,
        mock_labtracks: AsyncMock,
        client: TestClient,
    ):
        """Tests no data found"""
        mock_labtracks.return_value = []
        mock_las.return_value = []
        mock_nsb2019.return_value = []
        mock_get_perfusions.return_value = []
        mock_get_protocols.return_value = []
        mock_nsb2023.return_value = []
        mock_nsb_present.return_value = []
        mock_get_water_restriction.return_value = []
        mock_get_histology.return_value = []

        response = client.get("api/v2/procedures/nonexistent_subject")
        assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__])
