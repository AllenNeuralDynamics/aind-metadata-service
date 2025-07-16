"""Test slims routes"""

from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from aind_data_schema.components.devices import ImagingInstrumentType, Tube
from aind_data_schema.core.instrument import Instrument
from aind_data_schema.core.rig import Rig
from aind_data_schema_models.modalities import Modality
from aind_data_schema_models.organizations import Organization
from fastapi.testclient import TestClient


class TestRoute:
    """Test responses."""

    @patch("aind_slims_service_async_client.DefaultApi.get_aind_instrument")
    def test_get_rig(
        self,
        mock_slims_api_get: MagicMock,
        client: TestClient,
    ):
        """Tests a good response"""
        mock_slims_api_get.return_value = [
            Rig(
                rig_id="abc_123_20201010",
                modification_date=date(2025, 1, 1),
                mouse_platform=Tube(name="tube", diameter=Decimal("10.0")),
                modalities=[Modality.CONFOCAL],
                calibrations=[],
            ).model_dump(mode="json", exclude_none=True)
        ]
        response = client.get("/rig/abc_123_20201010")

        mock_slims_api_get.assert_called_once_with(
            input_id="abc_123_20201010", partial_match=False
        )
        assert 422 == response.status_code
        assert (
            "Valid Request Format. Models have not been validated."
            == response.json()["message"]
        )

    @patch("aind_slims_service_async_client.DefaultApi.get_aind_instrument")
    def test_get_instrument(
        self,
        mock_slims_api_get: MagicMock,
        client: TestClient,
    ):
        """Tests a good response"""
        mock_slims_api_get.return_value = [
            Instrument(
                instrument_id="abc_123_20201010",
                modification_date=date(2025, 1, 1),
                instrument_type=ImagingInstrumentType.CONFOCAL,
                manufacturer=Organization.AIND,
                objectives=[],
            ).model_dump(mode="json", exclude_none=True)
        ]
        response = client.get("/instrument/abc_123_202010?partial_match=True")

        mock_slims_api_get.assert_called_once_with(
            input_id="abc_123_202010", partial_match=True
        )
        assert 422 == response.status_code
        assert (
            "Valid Request Format. Models have not been validated."
            == response.json()["message"]
        )


if __name__ == "__main__":
    pytest.main([__file__])
