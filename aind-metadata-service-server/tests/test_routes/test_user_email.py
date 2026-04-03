"""Test user email routes"""

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient
from aind_active_directory_service_async_client.models import UserInfo
from aind_active_directory_service_async_client.exceptions import (
    NotFoundException,
)


class TestUserEmailRoute:
    """Test user email responses."""

    @patch(
        "aind_active_directory_service_async_client.DefaultApi."
        "get_user_from_active_directory"
    )
    def test_get_user_from_active_directory(
        self,
        mock_ad_api_get: AsyncMock,
        client: TestClient,
    ):
        """Tests a good response for user lookup"""
        mock_user_response = UserInfo(
            username="john.doe",
            full_name="John Doe",
            email="john.doe@alleninstitute.org",
        )
        mock_ad_api_get.return_value = mock_user_response

        response = client.get("/api/v2/active_directory/john.doe")
        assert 200 == response.status_code
        assert 1 == len(mock_ad_api_get.mock_calls)

        response_data = response.json()
        assert "username" in response_data
        assert "email" in response_data
        assert "full_name" in response_data

    @patch(
        "aind_active_directory_service_async_client.DefaultApi."
        "get_user_from_active_directory"
    )
    def test_get_missing_user_from_active_directory(
        self,
        mock_ad_api_get: AsyncMock,
        client: TestClient,
    ):
        """Tests a missing user response"""
        mock_ad_api_get.return_value = None

        response = client.get("/api/v2/active_directory/nonexistent.user")
        expected_response = {"detail": "Not found"}
        assert 404 == response.status_code
        assert expected_response == response.json()
        assert 1 == len(mock_ad_api_get.mock_calls)

    @patch(
        "aind_active_directory_service_async_client.DefaultApi."
        "get_user_from_active_directory"
    )
    def test_get_user_from_active_directory_error(
        self,
        mock_ad_api_get: AsyncMock,
        client: TestClient,
    ):
        """Tests an error response from the AD API"""
        mock_ad_api_get.side_effect = NotFoundException()

        response = client.get("/api/v2/active_directory/john.doe")
        expected_response = {"detail": "Not found"}
        assert 404 == response.status_code
        assert expected_response == response.json()
        assert 1 == len(mock_ad_api_get.mock_calls)
