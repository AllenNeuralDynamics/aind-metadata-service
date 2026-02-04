"""Tests for dataverse routes"""

from unittest.mock import AsyncMock, patch

import pytest
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
        mock_response = {
            "value": [{"cr138_projectid": "123", "cr138_name": "Test Project"}]
        }
        mock_api_get.return_value = mock_response

        response = client.get("/api/v2/dataverse/tables/cr138_projects")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == mock_response
        assert len(mock_api_get.mock_calls) == 1

    @patch("aind_dataverse_service_async_client.DefaultApi.get_table")
    def test_get_dataverse_table_not_found(
        self,
        mock_api_get: AsyncMock,
        client: TestClient,
    ):
        """Test when table is not found"""
        mock_api_get.return_value = []

        response = client.get("/api/v2/dataverse/tables/nonexistent_table")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": "Not found"}
        assert len(mock_api_get.mock_calls) == 1


if __name__ == "__main__":
    pytest.main([__file__])
