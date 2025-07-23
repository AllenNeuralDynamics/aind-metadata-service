"""Tests procedures route"""

import json
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from aind_labtracks_service_async_client.models import Task as LabTracksTask
from aind_sharepoint_service_async_client.models.nsb2019_list import (
    NSB2019List,
)
from fastapi.testclient import TestClient

TEST_DIR = Path(__file__).parent / ".."
EXAMPLE_NSB2019_JSON = (
    TEST_DIR / "resources" / "nsb2019" / "raw" / "list_item1.json"
)


class TestRoute:
    """Test responses."""

    @patch("aind_labtracks_service_async_client.DefaultApi.get_tasks")
    @patch("aind_sharepoint_service_async_client.DefaultApi.get_nsb2019")
    @patch("aind_sharepoint_service_async_client.DefaultApi.get_nsb2023")
    @patch("aind_sharepoint_service_async_client.DefaultApi.get_nsb_present")
    @patch("aind_sharepoint_service_async_client.DefaultApi.get_las2020")
    def test_get_procedures_success(
        self,
        mock_las: AsyncMock,
        mock_nsb_present: AsyncMock,
        mock_nsb2023: AsyncMock,
        mock_nsb2019: AsyncMock,
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
        with open(EXAMPLE_NSB2019_JSON) as f:
            contents = json.load(f)
        mock_nsb2019.return_value = [NSB2019List.model_validate(contents)]
        mock_nsb2023.return_value = []
        mock_nsb_present.return_value = []
        mock_las.return_value = []

        response = client.get("/procedures/000000")
        assert response.status_code == 406

    @patch(
        "aind_sharepoint_service_async_client.DefaultApi.get_las2020",
    )
    @patch(
        "aind_sharepoint_service_async_client.DefaultApi.get_nsb_present",
    )
    @patch(
        "aind_sharepoint_service_async_client.DefaultApi.get_nsb2023",
    )
    @patch(
        "aind_sharepoint_service_async_client.DefaultApi.get_nsb2019",
    )
    @patch(
        "aind_labtracks_service_async_client.DefaultApi.get_tasks",
    )
    def test_get_procedures_no_data(
        self,
        mock_get_tasks: AsyncMock,
        mock_get_nsb2019: AsyncMock,
        mock_get_nsb2023: AsyncMock,
        mock_get_nsb_present: AsyncMock,
        mock_get_las2020: AsyncMock,
        client: TestClient,
    ):
        """Tests no data found"""
        mock_get_tasks.return_value = []
        mock_get_nsb2019.return_value = []
        mock_get_nsb2023.return_value = []
        mock_get_nsb_present.return_value = []
        mock_get_las2020.return_value = []

        response = client.get("/procedures/nonexistent_subject")
        assert 200 == response.status_code
        assert "No Data Found" in response.json()["message"]


if __name__ == "__main__":
    pytest.main([__file__])
