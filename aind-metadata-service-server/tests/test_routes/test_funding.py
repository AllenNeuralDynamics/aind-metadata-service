"""Test funding routes"""

from unittest.mock import AsyncMock, patch

import pytest
from aind_smartsheet_service_async_client.models import FundingModel
from fastapi.testclient import TestClient


class TestRoute:
    """Test responses."""

    @patch(
        "aind_smartsheet_service_async_client.DefaultApi.get_funding",
        new_callable=AsyncMock,
    )
    def test_get_funding(
        self,
        mock_get_funding: AsyncMock,
        client: TestClient,
    ):
        """Tests successful funding retrieval with subproject specified"""
        discovery_project = (
            "Discovery-Neuromodulator circuit dynamics during foraging"
        )
        sub1 = (
            "Subproject 1 Electrophysiological Recordings from NM Neurons"
            " During Behavior"
        )
        mock_get_funding.return_value = [
            FundingModel(
                project_name=discovery_project,
                subproject=sub1,
                project_code="122-01-001-10",
                funding_institution="Allen Institute",
                fundees__pi=(
                    "Person Four, Person Five, Person Six, Person Seven,"
                    " Person Eight"
                ),
            ),
            FundingModel(
                project_name=discovery_project,
                subproject=sub1,
                project_code="122-01-012-20",
                funding_institution="NINDS",
                grant_number="1RF1NS131984",
                fundees__pi="Person Five, Person Six, Person Eight",
                investigators="Person Six, Person Eight",
            ),
        ]
        response = client.get(
            "/api/v2/funding/"
            "Discovery-Neuromodulator circuit dynamics during foraging -"
            " Subproject 1 Electrophysiological Recordings from NM Neurons"
            " During Behavior"
        )
        assert 200 == response.status_code
        assert 1 == len(mock_get_funding.mock_calls)

    @patch(
        "aind_smartsheet_service_async_client.DefaultApi.get_funding",
        new_callable=AsyncMock,
    )
    def test_get_funding_without_subproject(
        self,
        mock_get_funding: AsyncMock,
        client: TestClient,
    ):
        """Tests funding retrieval with subproject parameter"""
        discovery_project = (
            "Discovery-Neuromodulator circuit dynamics during foraging"
        )
        sub1 = (
            "Subproject 1 Electrophysiological Recordings from NM Neurons"
            " During Behavior"
        )
        sub2 = "Subproject 2 Molecular Anatomy Cell Types"

        mock_get_funding.return_value = [
            FundingModel(
                project_name=discovery_project,
                subproject=sub1,
                project_code="122-01-001-10",
                funding_institution="Allen Institute",
                fundees__pi=(
                    "Person Four, Person Five, Person Six, Person Seven,"
                    " Person Eight"
                ),
            ),
            FundingModel(
                project_name=discovery_project,
                subproject=sub2,
                project_code="122-01-001-10",
                funding_institution="Allen Institute",
                grant_number=None,
                fundees__pi=(
                    "Person Four, Person Five, Person Six, Person Seven,"
                    " Person Eight"
                ),
                investigators="Person Seven",
            ),
        ]
        response = client.get(
            "/api/v2/funding/Discovery-Neuromodulator circuit dynamics during "
            "foraging"
        )

        assert 406 == response.status_code
        assert 1 == len(mock_get_funding.mock_calls)

    @patch(
        "aind_smartsheet_service_async_client.DefaultApi.get_funding",
        new_callable=AsyncMock,
    )
    def test_get_project_names(
        self,
        mock_get_funding: AsyncMock,
        client: TestClient,
    ):
        """Tests successful project names retrieval"""
        discovery_project = (
            "Discovery-Neuromodulator circuit dynamics during foraging"
        )
        sub1 = (
            "Subproject 1 Electrophysiological Recordings from NM Neurons"
            " During Behavior"
        )
        sub2 = "Subproject 2 Molecular Anatomy Cell Types"

        mock_get_funding.return_value = [
            FundingModel(),
            FundingModel(
                project_name="Ephys Platform",
                funding_institution="Allen Institute",
                fundees__pi="Person One, Person Two, Person Three",
            ),
            FundingModel(
                project_name="MSMA Platform",
                project_code="122-01-001-10",
                funding_institution="Allen Institute",
                fundees__pi="Person Four",
            ),
            FundingModel(
                project_name=discovery_project,
                subproject=sub1,
                project_code="122-01-001-10",
                funding_institution="Allen Institute",
                fundees__pi=(
                    "Person Four, Person Five, Person Six, Person Seven,"
                    " Person Eight"
                ),
            ),
            FundingModel(
                project_name=discovery_project,
                subproject=sub2,
                project_code="122-01-001-10",
                funding_institution="Allen Institute",
                grant_number=None,
                fundees__pi=(
                    "Person Four, Person Five, Person Six, Person Seven,"
                    " Person Eight"
                ),
                investigators="Person Seven",
            ),
        ]
        response = client.get("/api/v2/project_names")

        project_names = response.json()
        expected_names = [
            "Discovery-Neuromodulator circuit dynamics during foraging - "
            "Subproject 1 Electrophysiological Recordings from NM Neurons "
            "During Behavior",
            "Discovery-Neuromodulator circuit dynamics during foraging - "
            "Subproject 2 Molecular Anatomy Cell Types",
            "Ephys Platform",
            "MSMA Platform",
        ]

        assert 200 == response.status_code
        assert 1 == len(mock_get_funding.mock_calls)
        assert sorted(expected_names) == sorted(project_names)

    @patch(
        "aind_smartsheet_service_async_client.DefaultApi.get_funding",
        new_callable=AsyncMock,
    )
    def test_get_funding_not_found(
        self,
        mock_get_funding: AsyncMock,
        client: TestClient,
    ):
        """Tests 404 response when no funding information is found"""
        mock_get_funding.return_value = []
        response = client.get("/api/v2/funding/Nonexistent Project Name")
        assert 404 == response.status_code
        assert 1 == len(mock_get_funding.mock_calls)

    @patch(
        "aind_smartsheet_service_async_client.DefaultApi.get_funding",
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

    @patch(
        "aind_smartsheet_service_async_client.DefaultApi.get_funding",
        new_callable=AsyncMock,
    )
    def test_get_funding_invalid_data(
        self,
        mock_get_funding: AsyncMock,
        client: TestClient,
    ):
        """Tests 404 response when API returns invalid models"""
        mock_get_funding.return_value = [
            FundingModel(),
            FundingModel(project_name=""),
        ]
        response = client.get("/api/v2/funding/Test Project")
        assert 404 == response.status_code
        assert 1 == len(mock_get_funding.mock_calls)

    @patch(
        "aind_smartsheet_service_async_client.DefaultApi.get_funding",
        new_callable=AsyncMock,
    )
    def test_get_smartsheet_funding(
        self,
        mock_get_funding: AsyncMock,
        client: TestClient,
    ):
        """Tests successful funding retrieval"""
        discovery_project = (
            "Discovery-Neuromodulator circuit dynamics during foraging"
        )
        sub1 = (
            "Subproject 1 Electrophysiological Recordings from NM Neurons"
            " During Behavior"
        )

        mock_get_funding.return_value = [
            FundingModel(
                project_name=discovery_project,
                subproject=sub1,
                project_code="122-01-001-10",
                funding_institution="Allen Institute",
                fundees__pi=(
                    "Person Four, Person Five, Person Six, Person Seven,"
                    " Person Eight"
                ),
            ),
            FundingModel(
                project_name=discovery_project,
                subproject=sub1,
                project_code="122-01-012-20",
                funding_institution="NINDS",
                grant_number="1RF1NS131984",
                fundees__pi="Person Five, Person Six, Person Eight",
                investigators="Person Six, Person Eight",
            ),
        ]
        response = client.get("/api/v2/smartsheet/funding/")
        assert 200 == response.status_code
        assert 1 == len(mock_get_funding.mock_calls)


if __name__ == "__main__":
    pytest.main([__file__])
