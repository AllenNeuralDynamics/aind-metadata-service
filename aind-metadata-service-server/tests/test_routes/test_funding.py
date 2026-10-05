"""Test funding routes"""

from unittest.mock import AsyncMock, patch

import pytest
from aind_data_schema.components.identifiers import Person
from fastapi.testclient import TestClient

from aind_metadata_service_server.routes.funding import resolve_orcid


class TestRoute:
    """Test responses."""

    @patch("orcid_service_async_client.DefaultApi", new_callable=AsyncMock)
    async def test_resolve_orcid_error(
        self, mock_get_orcid: AsyncMock, caplog
    ):
        """Tests resolve orcid when error happens."""
        mock_get_orcid.get_orcid.side_effect = Exception("ERROR!")
        _ = await resolve_orcid(
            person=Person(name="A"), orcid_api_instance=mock_get_orcid
        )
        assert "ORCID lookup failed" in caplog.text

    def test_get_funding(
        self,
        mock_dataverse_funding,
        mock_orcid,
        client: TestClient,
    ):
        """Tests successful funding retrieval specified"""
        response = client.get("/api/v2/funding/PROJECT1")
        print(response)
        assert 200 == response.status_code
        assert 1 == len(mock_dataverse_funding.mock_calls)
        assert 3 == len(mock_orcid.mock_calls)

    def test_get_investigators(
        self,
        mock_dataverse_funding,
        mock_orcid,
        client: TestClient,
    ):
        """
        Tests successful investigators retrieval
        """
        response = client.get("/api/v2/investigators/PROJECT1")

        assert 200 == response.status_code
        assert 1 == len(mock_dataverse_funding.mock_calls)
        assert 1 == len(mock_orcid.mock_calls)

    def test_get_project_names(
        self,
        mock_dataverse_funding,
        client: TestClient,
    ):
        """Tests successful project names retrieval"""

        response = client.get("/api/v2/project_names")

        project_names = response.json()
        expected_names = ["PROJECT1", "PROJECT2-SUB_G"]

        assert expected_names == project_names
        assert 200 == response.status_code
        assert 1 == len(mock_dataverse_funding.mock_calls)

    def test_get_funding_not_found(
        self,
        mock_dataverse_funding,
        mock_orcid,
        client: TestClient,
    ):
        """Tests 404 response when no funding information is found"""
        response = client.get("/api/v2/funding/Nonexistent Project Name")
        assert 404 == response.status_code
        assert 1 == len(mock_dataverse_funding.mock_calls)
        assert 0 == len(mock_orcid.mock_calls)

    def test_get_investigators_not_found(
        self,
        mock_dataverse_funding,
        mock_orcid,
        client: TestClient,
    ):
        """Tests 404 response when no investigators information is found"""
        response = client.get("/api/v2/investigators/Nonexistent Project Name")
        assert 404 == response.status_code
        assert 1 == len(mock_dataverse_funding.mock_calls)
        assert 0 == len(mock_orcid.mock_calls)

    @patch(
        "aind_dataverse_service_async_client.DefaultApi.get_funding",
        new_callable=AsyncMock,
    )
    def test_get_project_names_not_found(
        self,
        mock_get_funding: AsyncMock,
        client: TestClient,
    ):
        """Tests 404 response when no project names are found"""
        mock_get_funding.return_value = []
        response = client.get("/api/v2/project_names")

        assert 404 == response.status_code
        assert 1 == len(mock_get_funding.mock_calls)

    def test_get_dataverse_funding(
        self,
        mock_dataverse_funding,
        client: TestClient,
    ):
        """Tests get_dataverse_funding route."""
        response = client.get("/api/v2/dataverse/funding")
        assert 200 == response.status_code
        assert 1 == len(mock_dataverse_funding.mock_calls)


if __name__ == "__main__":
    pytest.main([__file__])
