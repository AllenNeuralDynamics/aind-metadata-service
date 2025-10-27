"""Test slims routes"""

from unittest.mock import AsyncMock, patch

import pytest
from aind_slims_service_async_client import models
from fastapi.testclient import TestClient


class TestRoute:
    """Test responses."""

    @patch("aind_slims_service_async_client.DefaultApi.get_ecephys_sessions")
    def test_get_ecephys_workflow(
        self,
        mock_slims_api_get: AsyncMock,
        client: TestClient,
    ):
        """Tests a good response and correct parsing of stream_modules."""
        mock_slims_api_get.return_value = [
            models.slims_ecephys_data.SlimsEcephysData(
                subject_id="12345",
                stream_modules=[
                    {
                        "ccf_coordinate_unit": "&mu;m",
                        "bregma_target_unit": "&mu;m",
                        "surface_z_unit": "&mu;m",
                        "manipulator_unit": "&mu;m",
                    }
                ],
            )
        ]
        response = client.get(
            "/api/v2/slims/ecephys_sessions?subject_id=12345"
        )
        mock_slims_api_get.assert_called_once_with(
            subject_id="12345",
            start_date_gte=None,
            end_date_lte=None,
            _request_timeout=240,
            session_name=None,
        )
        assert 200 == response.status_code
        data = response.json()[0]
        # Check that micrometer units are unescaped
        assert data["stream_modules"][0]["ccf_coordinate_unit"] == "μm"
        assert data["stream_modules"][0]["bregma_target_unit"] == "μm"
        assert data["stream_modules"][0]["surface_z_unit"] == "μm"
        assert data["stream_modules"][0]["manipulator_unit"] == "μm"

    @patch("aind_slims_service_async_client.DefaultApi.get_smartspim_imaging")
    def test_get_imaging_workflow(
        self,
        mock_slims_api_get: AsyncMock,
        client: TestClient,
    ):
        """Tests a good response and protocol_id HTML parsing."""
        protocol_html = '<a href="https://example.com">Example</a>'
        mock_slims_api_get.return_value = [
            models.slims_spim_data.SlimsSpimData(
                subject_id="12345", protocol_id=protocol_html
            )
        ]
        response = client.get(
            "/api/v2/slims/smartspim_imaging?subject_id=12345"
        )
        mock_slims_api_get.assert_called_once_with(
            subject_id="12345",
            start_date_gte=None,
            end_date_lte=None,
            _request_timeout=240,
        )
        assert 200 == response.status_code
        data = response.json()[0]
        assert data["protocol_id"] == "https://example.com"

    @patch("aind_slims_service_async_client.DefaultApi.get_viral_injections")
    def test_get_viral_injections_workflow(
        self,
        mock_slims_api_get: AsyncMock,
        client: TestClient,
    ):
        """Tests a good response"""
        mock_slims_api_get.return_value = [
            models.slims_viral_injection_data.SlimsViralInjectionData(
                subject_id="12345"
            )
        ]
        response = client.get(
            "/api/v2/slims/viral_injections?subject_id=12345"
        )
        mock_slims_api_get.assert_called_once_with(
            subject_id="12345",
            start_date_gte=None,
            end_date_lte=None,
            _request_timeout=240,
        )
        assert 200 == response.status_code

    @patch(
        "aind_slims_service_async_client.DefaultApi.get_water_restriction_data"
    )
    def test_get_water_restriction_workflow(
        self,
        mock_slims_api_get: AsyncMock,
        client: TestClient,
    ):
        """Tests a good response"""
        mock_slims_api_get.return_value = [
            models.slims_water_restriction_data.SlimsWaterRestrictionData(
                subject_id="12345"
            )
        ]
        response = client.get(
            "/api/v2/slims/water_restriction?subject_id=12345"
        )
        mock_slims_api_get.assert_called_once_with(
            subject_id="12345",
            start_date_gte=None,
            end_date_lte=None,
            _request_timeout=240,
        )
        assert 200 == response.status_code

    @patch("aind_slims_service_async_client.DefaultApi.get_histology_data")
    def test_get_histology_workflow(
        self,
        mock_slims_api_get: AsyncMock,
        client: TestClient,
    ):
        """Tests a good response and protocol_id HTML parsing."""
        protocol_html = '<a href="https://histology.com">Histology</a>'
        mock_slims_api_get.return_value = [
            models.slims_histology_data.SlimsHistologyData(
                subject_id="12345", protocol_id=protocol_html
            )
        ]
        response = client.get("/api/v2/slims/histology?subject_id=12345")
        mock_slims_api_get.assert_called_once_with(
            subject_id="12345",
            start_date_gte=None,
            end_date_lte=None,
            _request_timeout=240,
        )
        assert 200 == response.status_code
        data = response.json()[0]
        assert data["protocol_id"] == "https://histology.com"

    @patch("aind_slims_service_async_client.DefaultApi.get_histology_data")
    def test_get_no_data(
        self,
        mock_slims_api_get: AsyncMock,
        client: TestClient,
    ):
        """Tests a Not Found Response"""
        mock_slims_api_get.return_value = []
        response = client.get("/api/v2/slims/histology?subject_id=12345")
        mock_slims_api_get.assert_called_once_with(
            subject_id="12345",
            start_date_gte=None,
            end_date_lte=None,
            _request_timeout=240,
        )
        assert 404 == response.status_code

    def test_non_workflow_response(
        self,
        client: TestClient,
    ):
        """Tests a non-existent workflow"""
        response = client.get("/api/v2/slims/NO_WORKFLOW")
        assert 422 == response.status_code


if __name__ == "__main__":
    pytest.main([__file__])
