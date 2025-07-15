"""Test perfusion routes"""

from datetime import date
from unittest.mock import AsyncMock, patch

import pytest
from aind_smartsheet_service_async_client.models import PerfusionsModel
from fastapi.testclient import TestClient


class TestRoute:
    """Test responses."""

    @patch("aind_smartsheet_service_async_client.DefaultApi.get_perfusions")
    def test_get_perfusion(
        self,
        mock_get_perfusions: AsyncMock,
        client: TestClient,
    ):
        """Tests successful perfusion retrieval"""
        mock_get_perfusions.return_value = [
            PerfusionsModel(
                subject_id="689418.0",
                var_date=date(2023, 10, 2),
                experimenter="Person S",
                iacuc_protocol=(
                    "2109 - Analysis of brain - wide neural circuits in the"
                    " mouse"
                ),
                animal_weight_prior__g="22.0",
                output_specimen_id_s="689418.0",
                postfix_solution="1xPBS",
                notes="Good",
            ),
        ]
        response = client.get("/perfusions/689418")
        # 406 because missing Surgery protocol id
        assert 406 == response.status_code
        assert 1 == len(mock_get_perfusions.mock_calls)
        mock_get_perfusions.assert_called_once_with(
            "689418", _request_timeout=10
        )


if __name__ == "__main__":
    pytest.main([__file__])
