"""Test routes"""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from aind_labtracks_service_async_client import MouseCustomClass
from aind_labtracks_service_async_client.models.subject import (
    Subject as LabtrackSubject,
)
from fastapi.testclient import TestClient


class TestRoute:
    """Test healthcheck responses."""

    def test_get_health(self, client: TestClient):
        """Tests a good response"""
        response = client.get("/healthcheck")
        assert 200 == response.status_code
        assert "OK" == response.json()["status"]

    @patch("aind_labtracks_service_async_client.ApiClient")
    @patch("aind_labtracks_service_async_client.DefaultApi.get_subject")
    def test_get_subject(
        self,
        mock_get_subject: MagicMock,
        mock_labtrack_client: MagicMock,
        client: TestClient,
    ):
        """Tests a good response"""
        mock_get_subject.return_value = [
            LabtrackSubject(
                id="632269",
                class_values=MouseCustomClass(
                    reserved_by="Person A",
                    reserved_date="2022-07-14T00:00:00-07:00",
                    reason=None,
                    solution="1xPBS",
                    full_genotype=(
                        "Pvalb-IRES-Cre/wt;RCL-somBiPoles_mCerulean-WPRE/wt"
                    ),
                    phenotype=(
                        "P19: TSTW. Small body, large head, slightly "
                        "dehydrated. 3.78g. P22: 5.59g. P26: 8.18g. "
                        "Normal body proportions. "
                    ),
                ),
                sex="F",
                birth_date=datetime(2022, 5, 1, 0, 0),
                species_name="mouse",
                cage_id="-99999999999999",
                room_id="-99999999999999.0000000000",
                paternal_id="623236",
                paternal_class_values=MouseCustomClass(
                    reserved_by="Person One ",
                    reserved_date="2022-11-01T00:00:00",
                    reason="eu-retire",
                    solution=None,
                    full_genotype="RCL-somBiPoles_mCerulean-WPRE/wt",
                    phenotype="P87: F.G. P133: Barberer. ",
                ),
                maternal_id="615310",
                maternal_class_values=MouseCustomClass(
                    reserved_by="Person One ",
                    reserved_date="2022-08-03T00:00:00",
                    reason="Eu-retire",
                    solution=None,
                    full_genotype="Pvalb-IRES-Cre/wt",
                    phenotype="P100: F.G.",
                ),
                group_name="Exp-ND-01-001-2109",
                group_description="BALB/c",
            )
        ]
        response = client.get("/subject/632269")
        mock_labtrack_client.assert_called_once()
        assert 200 == response.status_code


if __name__ == "__main__":
    pytest.main([__file__])
