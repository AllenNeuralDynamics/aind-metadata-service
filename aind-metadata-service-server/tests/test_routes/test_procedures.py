"""Tests procedures route"""

from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest
from aind_labtracks_service_async_client.models import Task as LabTracksTask
from fastapi.testclient import TestClient


class TestRoute:
    """Test responses."""

    @patch("aind_labtracks_service_async_client.DefaultApi.get_tasks")
    @patch("aind_sharepoint_service_async_client.DefaultApi.get_las2020")
    def test_get_procedures_success(
        self,
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

        response = client.get("api/v2/procedures/000000")
        assert response.status_code == 200

    @patch("aind_labtracks_service_async_client.DefaultApi.get_tasks")
    @patch("aind_sharepoint_service_async_client.DefaultApi.get_las2020")
    def test_get_procedures_no_data(
        self,
        mock_las: AsyncMock,
        mock_labtracks: AsyncMock,
        client: TestClient,
    ):
        """Tests no data found"""
        mock_labtracks.return_value = []
        mock_las.return_value = []

        response = client.get("api/v2/procedures/nonexistent_subject")
        assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__])
