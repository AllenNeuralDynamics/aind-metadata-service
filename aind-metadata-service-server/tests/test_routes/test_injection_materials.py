"""Test injection_materials routes"""

from unittest.mock import AsyncMock, patch

import pytest
from aind_tars_service_async_client import (
    Alias,
    PrepLotData,
    ViralPrep,
    VirusData,
)
from fastapi.testclient import TestClient


class TestRoute:
    """Test responses."""

    @patch("aind_tars_service_async_client.DefaultApi.get_viruses")
    @patch("aind_tars_service_async_client.DefaultApi.get_viral_prep_lots")
    def test_get_subject(
        self,
        mock_tars_api_get_viral_prep_lots: AsyncMock,
        mock_tars_api_get_viruses: AsyncMock,
        client: TestClient,
    ):
        """Tests an invalid model response"""
        mock_tars_api_get_viral_prep_lots.return_value = [
            PrepLotData(
                lot="abc",
                viral_prep=ViralPrep(
                    virus=VirusData(
                        aliases=[Alias(is_preferred=True, name="v_123")]
                    )
                ),
            )
        ]
        mock_tars_api_get_viruses.return_value = []
        response = client.get("/tars_injection_materials/abc")
        mock_tars_api_get_viral_prep_lots.assert_called_once_with(
            lot="abc", _request_timeout=10
        )
        mock_tars_api_get_viruses.assert_called_once_with(
            name="v_123", _request_timeout=10
        )
        assert 406 == response.status_code


if __name__ == "__main__":
    pytest.main([__file__])
