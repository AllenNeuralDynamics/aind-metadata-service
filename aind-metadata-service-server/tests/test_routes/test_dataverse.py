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
        mock_response = {
            "value": [{"cr138_projectid": "123", "cr138_name": "Test Project"}]
        }
        mock_api_get.return_value = mock_response

        response = client.get("/api/v2/dataverse/tables/cr138_projects")

        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert "value" in result
        assert len(result["value"]) == 1
        assert result["value"][0]["cr138_projectid"] == "123"
        assert result["value"][0]["cr138_name"] == "Test Project"
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
    def test_get_dataverse_table_with_filters_success(
        self,
        mock_api_get: AsyncMock,
        client: TestClient,
    ):
        """Test successful filtering of table data"""
        mock_response = {
            "value": [
                {
                    "cr138_projectid": "123",
                    "cr138_name": "Test Project",
                    "cr138_status": "active",
                    "cr138_owner": "jdoe",
                },
                {
                    "cr138_projectid": "124",
                    "cr138_name": "Another Project",
                    "cr138_status": "inactive",
                    "cr138_owner": "jdoe",
                },
                {
                    "cr138_projectid": "125",
                    "cr138_name": "Third Project",
                    "cr138_status": "active",
                    "cr138_owner": "alice",
                },
            ]
        }
        mock_api_get.return_value = mock_response

        # Test filtering by single parameter
        response = client.get(
            "/api/v2/dataverse/tables/cr138_projects?cr138_status=active"
        )

        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert "value" in result
        assert len(result["value"]) == 2
        assert all(
            record["cr138_status"] == "active" for record in result["value"]
        )
        assert len(mock_api_get.mock_calls) == 1

    @patch("aind_dataverse_service_async_client.DefaultApi.get_table")
    def test_get_dataverse_table_with_multiple_filters(
        self,
        mock_api_get: AsyncMock,
        client: TestClient,
    ):
        """Test filtering with multiple parameters (AND logic)"""
        mock_response = {
            "value": [
                {
                    "cr138_projectid": "123",
                    "cr138_name": "Test Project",
                    "cr138_status": "active",
                    "cr138_owner": "jdoe",
                },
                {
                    "cr138_projectid": "124",
                    "cr138_name": "Another Project",
                    "cr138_status": "inactive",
                    "cr138_owner": "jdoe",
                },
                {
                    "cr138_projectid": "125",
                    "cr138_name": "Third Project",
                    "cr138_status": "active",
                    "cr138_owner": "alice",
                },
            ]
        }
        mock_api_get.return_value = mock_response

        # Test filtering by multiple parameters
        response = client.get(
            "/api/v2/dataverse/tables/cr138_projects?"
            "cr138_status=active&cr138_owner=jdoe"
        )

        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert "value" in result
        assert len(result["value"]) == 1
        assert result["value"][0]["cr138_projectid"] == "123"
        assert result["value"][0]["cr138_status"] == "active"
        assert result["value"][0]["cr138_owner"] == "jdoe"

    @patch("aind_dataverse_service_async_client.DefaultApi.get_table")
    def test_get_dataverse_table_no_filters(
        self,
        mock_api_get: AsyncMock,
        client: TestClient,
    ):
        """Test that no filters returns full table"""
        mock_response = {
            "value": [
                {"cr138_projectid": "123", "cr138_name": "Test Project"},
                {"cr138_projectid": "124", "cr138_name": "Another Project"},
            ]
        }
        mock_api_get.return_value = mock_response

        response = client.get("/api/v2/dataverse/tables/cr138_projects")

        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert "value" in result
        assert len(result["value"]) == 2  # Should return all records
        assert len(mock_api_get.mock_calls) == 1

    @patch("aind_dataverse_service_async_client.DefaultApi.get_table")
    def test_get_dataverse_table_invalid_filter_parameter(
        self,
        mock_api_get: AsyncMock,
        client: TestClient,
    ):
        """Test that invalid filter parameter returns empty results"""
        mock_response = {
            "value": [
                {"cr138_projectid": "123", "cr138_name": "Test Project"},
            ]
        }
        mock_api_get.return_value = mock_response

        response = client.get(
            "/api/v2/dataverse/tables/cr138_projects?invalid_column=test"
        )

        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert "value" in result
        assert result["value"] == []  # Should return empty list for invalid column

    @patch("aind_dataverse_service_async_client.DefaultApi.get_table")
    def test_get_dataverse_table_no_matching_rows(
        self,
        mock_api_get: AsyncMock,
        client: TestClient,
    ):
        """Test that no matching rows returns empty list"""
        mock_response = {
            "value": [
                {"cr138_projectid": "123", "cr138_status": "active"},
                {"cr138_projectid": "124", "cr138_status": "active"},
            ]
        }
        mock_api_get.return_value = mock_response

        response = client.get(
            "/api/v2/dataverse/tables/cr138_projects?cr138_status=inactive"
        )

        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert "value" in result
        assert result["value"] == []  # Should return empty list

    @patch("aind_dataverse_service_async_client.DefaultApi.get_table")
    def test_get_dataverse_table_case_insensitive_filtering(
        self,
        mock_api_get: AsyncMock,
        client: TestClient,
    ):
        """Test that filtering is case-insensitive"""
        mock_response = {
            "value": [
                {"cr138_projectid": "123", "cr138_status": "Active"},
                {"cr138_projectid": "124", "cr138_status": "ACTIVE"},
                {"cr138_projectid": "125", "cr138_status": "inactive"},
            ]
        }
        mock_api_get.return_value = mock_response

        # Test case-insensitive filtering
        response = client.get(
            "/api/v2/dataverse/tables/cr138_projects?cr138_status=active"
        )

        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert "value" in result
        assert (
            len(result["value"]) == 2
        )  # Should match both "Active" and "ACTIVE"
        assert result["value"][0]["cr138_projectid"] == "123"
        assert result["value"][1]["cr138_projectid"] == "124"

    @patch("aind_dataverse_service_async_client.DefaultApi.get_table")
    def test_get_dataverse_table_empty_table_with_filters(
        self,
        mock_api_get: AsyncMock,
        client: TestClient,
    ):
        """Test filtering on empty table"""
        mock_response = {"value": []}
        mock_api_get.return_value = mock_response

        response = client.get(
            "/api/v2/dataverse/tables/cr138_projects?cr138_status=active"
        )

        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert "value" in result
        assert result["value"] == []


if __name__ == "__main__":
    pytest.main([__file__])
