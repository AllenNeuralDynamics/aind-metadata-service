"""Test MGI allele routes"""

from unittest.mock import MagicMock, patch

import pytest
from aind_mgi_service_async_client.models import MgiSummaryRow
from fastapi.testclient import TestClient


class TestRoute:
    """Test responses."""

    @patch("aind_mgi_service_async_client.DefaultApi.get_allele_info")
    def test_get_mgi_allele(
        self,
        mock_mgi_api_get: MagicMock,
        client: TestClient,
    ):
        """Tests a good response"""
        mock_mgi_api_get.return_value = [
            MgiSummaryRow(
                detail_uri="/allele/MGI:5558086",
                feature_type="Targeted allele",
                strand=None,
                chromosome="9",
                stars="****",
                best_match_text="Ai93",
                best_match_type="Synonym",
                name=(
                    "intergenic site 7; " "targeted mutation 93, Hongkui Zeng"
                ),
                location="syntenic",
                symbol="Igs7<tm93.1(tetO-GCaMP6f)Hze>",
            ),
            MgiSummaryRow(
                detail_uri="/allele/MGI:1234567",
                feature_type="Gene",
                strand=None,
                chromosome="X",
                stars="**",
                best_match_text="Test",
                best_match_type="Gene",
                name="Test gene",
                location="syntenic",
                symbol="TestGene",
            ),
        ]

        response = client.get("/api/v2/mgi_allele/Parvalbumin-IRES-Cre")

        assert 200 == response.status_code
        assert 1 == len(mock_mgi_api_get.mock_calls)

        mock_mgi_api_get.assert_called_once_with(
            allele_name="Parvalbumin-IRES-Cre", _request_timeout=10
        )

    @patch("aind_mgi_service_async_client.DefaultApi.get_allele_info")
    def test_get_mgi_allele_not_found(
        self,
        mock_mgi_api_get: MagicMock,
        client: TestClient,
    ):
        """Tests 404 when no MGI alleles are found"""
        mock_mgi_api_get.return_value = []
        response = client.get("/api/v2/mgi_allele/unknown_allele")
        assert 404 == response.status_code


if __name__ == "__main__":
    pytest.main([__file__])
