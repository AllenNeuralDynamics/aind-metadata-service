"""Test orcid routes"""

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient
from orcid_service_async_client.exceptions import NotFoundException
from orcid_service_async_client.models import OrcidId


class TestOrcidRoute:
    """Test orcid responses."""

    @patch("orcid_service_async_client.DefaultApi.get_orcid")
    def test_get_orcid(
        self,
        mock_orcid_get: AsyncMock,
        client: TestClient,
    ):
        """Tests a good response for an orcid lookup"""
        mock_orcid_get.return_value = OrcidId(orcid="0000-0000-0000-0001")

        response = client.get("/api/v2/orcid/Researcher One")

        assert 200 == response.status_code
        assert "0000-0000-0000-0001" == response.json()["orcid"]
        mock_orcid_get.assert_called_once_with(
            name="Researcher One", _request_timeout=10
        )

    @patch("orcid_service_async_client.DefaultApi.get_orcid")
    def test_get_orcid_not_found(
        self,
        mock_orcid_get: AsyncMock,
        client: TestClient,
    ):
        """Tests a name with no definitive match"""
        mock_orcid_get.side_effect = NotFoundException()

        response = client.get("/api/v2/orcid/Unknown Researcher")

        assert 404 == response.status_code
        assert {"detail": "Not found"} == response.json()
