"""Test subject routes"""

from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest
from aind_labtracks_service_async_client import MouseCustomClass
from aind_labtracks_service_async_client.models.subject import (
    Subject as LabtrackSubject,
)
from fastapi.testclient import TestClient


class TestRoute:
    """Test responses."""

    @patch("aind_mgi_service_async_client.DefaultApi.get_allele_info")
    @patch("aind_labtracks_service_async_client.DefaultApi.get_subject")
    def test_get_subject(
        self,
        mock_lb_api_get: AsyncMock,
        mock_mg_api_get: AsyncMock,
        client: TestClient,
        caplog: pytest.LogCaptureFixture
    ):
        """Tests a good response"""
        mock_lb_api_get.return_value = [
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
        mock_mg_api_get.return_value = []
        response = client.get("/subject/632269")
        assert 200 == response.status_code
        assert 1 == len(mock_lb_api_get.mock_calls)
        # Temporary patch
        assert 0 == len(mock_mg_api_get.mock_calls)
        assert caplog is not None


if __name__ == "__main__":
    pytest.main([__file__])
