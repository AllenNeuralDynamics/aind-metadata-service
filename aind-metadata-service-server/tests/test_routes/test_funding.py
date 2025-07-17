"""Test funding routes"""

from unittest.mock import AsyncMock, patch

import pytest
from aind_smartsheet_service_async_client.models import FundingModel
from fastapi.testclient import TestClient


class TestRoute:
    """Test responses."""

    @patch("aind_smartsheet_service_async_client.DefaultApi.get_funding")
    def test_get_funding(
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
                fundees=(
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
                fundees="Person Five, Person Six, Person Eight",
                investigators="Person Six, Person Eight",
            ),
        ]
        response = client.get(
            "/funding/"
            "Discovery-Neuromodulator circuit dynamics during foraging"
        )
        assert 300 == response.status_code
        assert 1 == len(mock_get_funding.mock_calls)

    @patch("aind_smartsheet_service_async_client.DefaultApi.get_funding")
    def test_get_funding_with_subproject(
        self,
        mock_get_funding: AsyncMock,
        client: TestClient,
    ):
        """Tests funding retrieval with subproject parameter"""
        discovery_project = (
            "Discovery-Neuromodulator circuit dynamics during foraging"
        )
        sub2 = "Subproject 2 Molecular Anatomy Cell Types"

        mock_get_funding.return_value = [
            FundingModel(
                project_name=discovery_project,
                subproject=sub2,
                project_code="122-01-001-10",
                funding_institution="Allen Institute",
                grant_number=None,
                fundees=(
                    "Person Four, Person Five, Person Six, Person Seven,"
                    " Person Eight"
                ),
                investigators="Person Seven",
            ),
        ]
        response = client.get(
            "/funding/Discovery-Neuromodulator circuit dynamics during "
            "foraging?subproject=Subproject 2 Molecular Anatomy Cell Types"
        )

        assert 200 == response.status_code
        assert 1 == len(mock_get_funding.mock_calls)

    @patch("aind_smartsheet_service_async_client.DefaultApi.get_funding")
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
                fundees="Person One, Person Two, Person Three",
            ),
            FundingModel(
                project_name="MSMA Platform",
                project_code="122-01-001-10",
                funding_institution="Allen Institute",
                fundees="Person Four",
            ),
            FundingModel(
                project_name=discovery_project,
                subproject=sub1,
                project_code="122-01-001-10",
                funding_institution="Allen Institute",
                fundees=(
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
                fundees=(
                    "Person Four, Person Five, Person Six, Person Seven,"
                    " Person Eight"
                ),
                investigators="Person Seven",
            ),
        ]
        response = client.get("/project_names")

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


if __name__ == "__main__":
    pytest.main([__file__])
