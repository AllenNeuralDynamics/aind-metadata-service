"""Tests for dataverse routes"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aind_dataverse_service_async_client.exceptions import (
    ApiException,
)
from fastapi import status
from fastapi.testclient import TestClient


class TestDataverseRoutes:
    """Tests for dataverse endpoints"""

    @patch("aind_dataverse_service_async_client.DefaultApi.get_table_info")
    def test_get_dataverse_table_info_success(
        self,
        mock_api_get: AsyncMock,
        client: TestClient,
    ):
        """Test successful retrieval of table info"""
        mock_response = [
            {
                "LogicalName": "cr138_projects",
                "EntitySetName": "cr138_projects",
            },
            {
                "LogicalName": "cr138_subjects",
                "EntitySetName": "cr138_subjects",
            },
        ]
        mock_api_get.return_value = mock_response

        response = client.get("/api/v2/dataverse/tables")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == mock_response
        assert len(mock_api_get.mock_calls) == 1

    @patch("aind_dataverse_service_async_client.DefaultApi.get_table_info")
    def test_get_dataverse_table_info_empty(
        self,
        mock_api_get: AsyncMock,
        client: TestClient,
    ):
        """Test when no tables are returned"""
        mock_api_get.return_value = []

        response = client.get("/api/v2/dataverse/tables")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": "Not found"}
        assert len(mock_api_get.mock_calls) == 1

    @patch("aind_dataverse_service_async_client.DefaultApi.get_table")
    def test_get_dataverse_table_success(
        self,
        mock_api_get: AsyncMock,
        client: TestClient,
    ):
        """Test successful retrieval of specific table data"""
        mock_response = [
            {"cr138_projectid": "123", "cr138_name": "Test Project"}
        ]
        mock_api_get.return_value = mock_response

        response = client.get("/api/v2/dataverse/tables/cr138_projects")

        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert len(result) == 1
        assert result[0]["cr138_projectid"] == "123"
        assert result[0]["cr138_name"] == "Test Project"
        assert len(mock_api_get.mock_calls) == 1

    @patch("aind_dataverse_service_async_client.DefaultApi.get_table")
    def test_get_dataverse_table_not_found(
        self,
        mock_api_get: AsyncMock,
        client: TestClient,
    ):
        """Test when table is not found"""
        mock_api_get.return_value = None

        response = client.get("/api/v2/dataverse/tables/nonexistent_table")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": "Not found"}
        assert len(mock_api_get.mock_calls) == 1

    @patch("aind_dataverse_service_async_client.DefaultApi.get_table")
    def test_get_dataverse_table_api_exception(
        self,
        mock_api_get: AsyncMock,
        client: TestClient,
    ):
        """Test handling of ApiException from dataverse service"""
        mock_exception = ApiException(
            http_resp=MagicMock(status=400),
            body='{"error": "Invalid table name"}',
            data=None,
        )
        mock_exception.status = 400
        mock_exception.reason = "Bad Request"
        mock_api_get.side_effect = mock_exception

        response = client.get("/api/v2/dataverse/tables/invalid_table")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Error fetching invalid_table" in response.json()["detail"]
        assert "Bad Request" in response.json()["detail"]
        assert len(mock_api_get.mock_calls) == 1

    @patch("aind_dataverse_service_async_client.DefaultApi.get_table")
    def test_get_dataverse_table_with_columns_and_filter(
        self,
        mock_api_get: AsyncMock,
        client: TestClient,
    ):
        """Test using both columns and filter parameters together"""
        mock_response = [
            {"cr138_projectid": "123", "cr138_name": "Test Project"}
        ]
        mock_api_get.return_value = mock_response

        response = client.get(
            "/api/v2/dataverse/tables/cr138_projects",
            params={
                "columns": "cr138_projectid,cr138_name",
                "filter": "cr138_status eq 'active'",
            },
        )

        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert len(result) == 1
        assert result[0]["cr138_projectid"] == "123"
        assert result[0]["cr138_name"] == "Test Project"

        mock_api_get.assert_called_once_with(
            "cr138_projects",
            columns="cr138_projectid,cr138_name",
            filter="cr138_status eq 'active'",
            _request_timeout=10,
        )

    @patch("aind_dataverse_service_async_client.DefaultApi.get_table")
    def test_get_mouse_weight_records_success(
        self,
        mock_api_get: AsyncMock,
        client: TestClient,
    ):
        """Test successful retrieval of mouse weight records"""
        mock_response = [
            {
                "cr138_datetime": "2026-08-07T17:30:14Z",
                "_aibs_operator_value@OData.Community.Display.V1.FormattedValue": "Jaimie Kenney",
                "statuscode@OData.Community.Display.V1.FormattedValue": "Active",
                "aibs_weight": 22.1,
                "aibs_fact_mouse_weight_recordsid": "53882aa8-8592-f111-8077-3833c5ef5e4a",
                "aibs_date_time": "2026-08-07T17:30:14.710665+00:00",
                "aibs_software_source": "WL",
                "aibs_is_baseline_weight": False,
                "aibs_workstation": "FRG.13-D",
                "aibs_software_version": "4.1.0.dev7",
                "_aibs_mouse_id_value@OData.Community.Display.V1.FormattedValue": "864846",
            }
        ]
        mock_api_get.return_value = mock_response

        response = client.get("/api/v2/dataverse/mouse_weight_records/864846")

        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert len(result) == 1
        assert result[0]["mouse_id"] == "864846"
        assert result[0]["weight"] == 22.1
        assert result[0]["operator"] == "Jaimie Kenney"
        assert result[0]["workstation"] == "FRG.13-D"
        assert result[0]["status"] == "Active"
        assert result[0]["is_baseline_weight"] is False

    @patch("aind_dataverse_service_async_client.DefaultApi.get_table")
    def test_get_mouse_weight_records_with_datetime_filter(
        self,
        mock_api_get: AsyncMock,
        client: TestClient,
    ):
        """Test mouse weight records with datetime filter"""
        mock_response = [
            {
                "cr138_datetime": "2026-08-07T17:30:14Z",
                "_aibs_mouse_id_value@OData.Community.Display.V1.FormattedValue": "864846",
                "aibs_weight": 22.1,
                "aibs_fact_mouse_weight_recordsid": "record-1",
            }
        ]
        mock_api_get.return_value = mock_response

        response = client.get(
            "/api/v2/dataverse/mouse_weight_records/864846",
            params={"acquisition_datetime": "2026-08-07T00:00:00"},
        )

        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert len(result) == 1

        # Verify the filter was constructed correctly
        call_args = mock_api_get.call_args
        filter_arg = call_args.kwargs["filter"]
        assert "aibs_mouse_id/aibs_mouse_id eq '864846'" in filter_arg
        assert "cr138_datetime ge 2026-08-07T00:00:00Z" in filter_arg
        assert "cr138_datetime lt 2026-08-08T00:00:00Z" in filter_arg

    @patch("aind_dataverse_service_async_client.DefaultApi.get_table")
    def test_get_mouse_weight_records_not_found(
        self,
        mock_api_get: AsyncMock,
        client: TestClient,
    ):
        """Test when no mouse weight records are found"""
        mock_api_get.return_value = []

        response = client.get("/api/v2/dataverse/mouse_weight_records/999999")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": "Not found"}

    @patch("aind_dataverse_service_async_client.DefaultApi.get_table")
    def test_get_mouse_weight_records_api_exception(
        self,
        mock_api_get: AsyncMock,
        client: TestClient,
    ):
        """Test handling of ApiException for mouse weight records"""
        mock_exception = ApiException(
            http_resp=MagicMock(status=500),
            body='{"error": "Internal server error"}',
            data=None,
        )
        mock_exception.status = 500
        mock_exception.reason = "Internal Server Error"
        mock_api_get.side_effect = mock_exception

        response = client.get("/api/v2/dataverse/mouse_weight_records/864846")

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert (
            "Error fetching mouse weight records" in response.json()["detail"]
        )
        assert "Internal Server Error" in response.json()["detail"]

    @patch("aind_dataverse_service_async_client.DefaultApi.get_table")
    def test_get_mouse_weight_records_multiple(
        self,
        mock_api_get: AsyncMock,
        client: TestClient,
    ):
        """Test retrieval of multiple mouse weight records"""
        mock_response = [
            {
                "aibs_fact_mouse_weight_recordsid": "record-1",
                "_aibs_mouse_id_value@OData.Community.Display.V1.FormattedValue": "864846",
                "aibs_weight": 22.1,
                "cr138_datetime": "2026-08-07T10:00:00Z",
            },
            {
                "aibs_fact_mouse_weight_recordsid": "record-2",
                "_aibs_mouse_id_value@OData.Community.Display.V1.FormattedValue": "864846",
                "aibs_weight": 22.3,
                "cr138_datetime": "2026-08-07T14:00:00Z",
            },
        ]
        mock_api_get.return_value = mock_response

        response = client.get("/api/v2/dataverse/mouse_weight_records/864846")

        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert len(result) == 2
        assert result[0]["record_id"] == "record-1"
        assert result[0]["weight"] == 22.1
        assert result[1]["record_id"] == "record-2"
        assert result[1]["weight"] == 22.3


if __name__ == "__main__":
    pytest.main([__file__])
