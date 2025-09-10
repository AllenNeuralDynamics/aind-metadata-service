"""Tests procedures route"""

import json
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from aind_labtracks_service_async_client.models import Task as LabTracksTask
from aind_sharepoint_service_async_client.models import (
    NSB2019List,
)
from aind_tars_service_async_client import (
    Alias,
    PrepLotData,
    ViralPrep,
    VirusData,
)
from fastapi.testclient import TestClient

TEST_DIR = Path(__file__).parent / ".."
EXAMPLE_NSB2019_JSON = (
    TEST_DIR / "resources" / "nsb2019" / "raw" / "list_item1.json"
)


class TestRoute:
    """Test responses."""

    @patch("aind_labtracks_service_async_client.DefaultApi.get_tasks")
    @patch("aind_sharepoint_service_async_client.DefaultApi.get_las2020")
    @patch("aind_sharepoint_service_async_client.DefaultApi.get_nsb2019")
    @patch("aind_smartsheet_service_async_client.DefaultApi.get_perfusions")
    @patch("aind_smartsheet_service_async_client.DefaultApi.get_protocols")
    @patch("aind_tars_service_async_client.DefaultApi.get_viral_prep_lots")
    @patch("aind_tars_service_async_client.DefaultApi.get_viruses")
    def test_get_procedures_valid_data_only_labtracks(
        self,
        mock_get_viruses: AsyncMock,
        mock_get_viral_prep_lots: AsyncMock,
        mock_get_protocols: AsyncMock,
        mock_get_perfusions: AsyncMock,
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
        mock_get_viral_prep_lots.return_value = []
        mock_get_viruses.return_value = []

        response = client.get("api/v2/procedures/000000")
        assert response.status_code == 200

    @patch("aind_labtracks_service_async_client.DefaultApi.get_tasks")
    @patch("aind_sharepoint_service_async_client.DefaultApi.get_las2020")
    @patch("aind_sharepoint_service_async_client.DefaultApi.get_nsb2019")
    @patch("aind_smartsheet_service_async_client.DefaultApi.get_perfusions")
    @patch("aind_smartsheet_service_async_client.DefaultApi.get_protocols")
    @patch("aind_tars_service_async_client.DefaultApi.get_viral_prep_lots")
    @patch("aind_tars_service_async_client.DefaultApi.get_viruses")
    def test_get_procedures_valid_data(
        self,
        mock_get_viruses: AsyncMock,
        mock_get_viral_prep_lots: AsyncMock,
        mock_get_protocols: AsyncMock,
        mock_get_perfusions: AsyncMock,
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
        mock_get_viral_prep_lots.return_value = [
            PrepLotData(
                lot="230929-12",
                viral_prep=ViralPrep(
                    virus=VirusData(
                        aliases=[Alias(is_preferred=True, name="v_123")]
                    )
                ),
            )
        ]
        mock_get_viruses.return_value = []

        with open(EXAMPLE_NSB2019_JSON) as f:
            contents_nsb2019 = json.load(f)
        mock_nsb2019.return_value = [
            NSB2019List.model_validate(contents_nsb2019)
        ]

        response = client.get("api/v2/procedures/000000")
        assert response.status_code == 200

    @patch("aind_labtracks_service_async_client.DefaultApi.get_tasks")
    @patch("aind_sharepoint_service_async_client.DefaultApi.get_las2020")
    @patch("aind_sharepoint_service_async_client.DefaultApi.get_nsb2019")
    @patch("aind_smartsheet_service_async_client.DefaultApi.get_perfusions")
    @patch("aind_smartsheet_service_async_client.DefaultApi.get_protocols")
    @patch("aind_tars_service_async_client.DefaultApi.get_viral_prep_lots")
    @patch("aind_tars_service_async_client.DefaultApi.get_viruses")
    def test_get_procedures_no_data(
        self,
        mock_get_viruses: AsyncMock,
        mock_get_viral_prep_lots: AsyncMock,
        mock_get_protocols: AsyncMock,
        mock_get_perfusions: AsyncMock,
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
        mock_get_viral_prep_lots.return_value = []
        mock_get_viruses.return_value = []

        response = client.get("api/v2/procedures/nonexistent_subject")
        assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__])
