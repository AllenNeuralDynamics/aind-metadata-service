"""Test funding routes"""

from unittest.mock import AsyncMock, patch

import pytest
from aind_smartsheet_service_async_client.models import FundingModel
from fastapi.testclient import TestClient
from orcid_service_async_client.exceptions import NotFoundException
from orcid_service_async_client.models import OrcidId


def funding_row(**kwargs) -> FundingModel:
    """Build a smartsheet funding row for the orcid tests."""
    return FundingModel(
        project_name="Project",
        funding_institution="Allen Institute",
        **kwargs,
    )


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
    def test_get_investigators(
        self,
        mock_get_funding: AsyncMock,
        client: TestClient,
    ):
        """
        Tests successful investigators retrieval with subproject specified
        """
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
            "/api/v2/investigators/"
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
    def test_get_investigators_without_subproject(
        self,
        mock_get_funding: AsyncMock,
        client: TestClient,
    ):
        """Tests investigators retrieval without subproject parameter"""
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
        response = client.get(
            "/api/v2/investigators/Discovery-Neuromodulator circuit dynamics "
            "during foraging"
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

    @patch("orcid_service_async_client.DefaultApi.get_orcid")
    @patch(
        "aind_smartsheet_service_async_client.DefaultApi.get_funding",
        new_callable=AsyncMock,
    )
    def test_investigators_get_orcids(
        self,
        mock_get_funding: AsyncMock,
        mock_get_orcid: AsyncMock,
        client: TestClient,
    ):
        """Tests registry_identifier is filled in for each investigator"""
        mock_get_funding.return_value = [
            funding_row(investigators="Person One, Person Two")
        ]
        mock_get_orcid.side_effect = [
            OrcidId(orcid="0000-0000-0000-0001"),
            OrcidId(orcid="0000-0000-0000-0002"),
        ]

        response = client.get("/api/v2/investigators/Project")

        assert 200 == response.status_code
        assert ["0000-0000-0000-0001", "0000-0000-0000-0002"] == [
            person["registry_identifier"] for person in response.json()
        ]

    @patch("orcid_service_async_client.DefaultApi.get_orcid")
    @patch(
        "aind_smartsheet_service_async_client.DefaultApi.get_funding",
        new_callable=AsyncMock,
    )
    def test_investigators_look_up_each_name_once(
        self,
        mock_get_funding: AsyncMock,
        mock_get_orcid: AsyncMock,
        client: TestClient,
    ):
        """Tests a repeated name is only looked up once"""
        mock_get_funding.return_value = [
            funding_row(investigators="Person One"),
            funding_row(investigators="Person One"),
        ]
        mock_get_orcid.return_value = OrcidId(orcid="0000-0000-0000-0001")

        response = client.get("/api/v2/investigators/Project")

        assert 200 == response.status_code
        assert 1 == mock_get_orcid.await_count

    @pytest.mark.parametrize(
        "failure", [NotFoundException(), ConnectionError("boom")]
    )
    @patch("orcid_service_async_client.DefaultApi.get_orcid")
    @patch(
        "aind_smartsheet_service_async_client.DefaultApi.get_funding",
        new_callable=AsyncMock,
    )
    def test_investigators_when_orcid_gives_nothing(
        self,
        mock_get_funding: AsyncMock,
        mock_get_orcid: AsyncMock,
        failure: Exception,
        client: TestClient,
    ):
        """Tests investigators are still returned when no iD comes back"""
        mock_get_funding.return_value = [
            funding_row(investigators="Person One")
        ]
        mock_get_orcid.side_effect = failure

        response = client.get("/api/v2/investigators/Project")

        assert 200 == response.status_code
        assert "Person One" == response.json()[0]["name"]
        assert response.json()[0]["registry_identifier"] is None

    @patch("aind_metadata_service_server.routes.funding.ORCID_BUDGET", 0)
    @patch("orcid_service_async_client.DefaultApi.get_orcid")
    @patch(
        "aind_smartsheet_service_async_client.DefaultApi.get_funding",
        new_callable=AsyncMock,
    )
    def test_investigators_stop_looking_up_past_the_budget(
        self,
        mock_get_funding: AsyncMock,
        mock_get_orcid: AsyncMock,
        client: TestClient,
    ):
        """Tests a slow ORCID cannot stall a project with many people"""
        mock_get_funding.return_value = [
            funding_row(investigators="Person One, Person Two")
        ]

        response = client.get("/api/v2/investigators/Project")

        assert 200 == response.status_code
        assert 0 == mock_get_orcid.await_count
        assert [None, None] == [
            person["registry_identifier"] for person in response.json()
        ]

    @patch("orcid_service_async_client.DefaultApi.get_orcid")
    @patch(
        "aind_smartsheet_service_async_client.DefaultApi.get_funding",
        new_callable=AsyncMock,
    )
    def test_funding_fundees_get_orcids(
        self,
        mock_get_funding: AsyncMock,
        mock_get_orcid: AsyncMock,
        client: TestClient,
    ):
        """Tests registry_identifier is filled in for each fundee"""
        mock_get_funding.return_value = [funding_row(fundees="Person One")]
        mock_get_orcid.return_value = OrcidId(orcid="0000-0000-0000-0001")

        response = client.get("/api/v2/funding/Project")

        assert 200 == response.status_code
        fundee = response.json()[0]["fundee"][0]
        assert "0000-0000-0000-0001" == fundee["registry_identifier"]

    @patch(
        "aind_smartsheet_service_async_client.DefaultApi.get_funding",
        new_callable=AsyncMock,
    )
    def test_get_investigators_not_found(
        self,
        mock_get_funding: AsyncMock,
        client: TestClient,
    ):
        """Tests 404 response when no investigators information is found"""
        mock_get_funding.return_value = []
        response = client.get("/api/v2/investigators/Nonexistent Project Name")
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
        response = client.get("/api/v2/smartsheet/funding/")
        assert 200 == response.status_code
        assert 1 == len(mock_get_funding.mock_calls)


if __name__ == "__main__":
    pytest.main([__file__])
