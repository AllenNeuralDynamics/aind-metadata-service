"""Test slims routes"""

from unittest.mock import MagicMock, patch

import pytest
from aind_slims_service_async_client import models
from fastapi.testclient import TestClient


class TestRoute:
    """Test responses."""

    @patch("aind_slims_service_async_client.DefaultApi.get_ecephys_sessions")
    def test_get_ecephys_workflow(
        self,
        mock_slims_api_get: MagicMock,
        client: TestClient,
    ):
        """Tests a good response"""
        mock_slims_api_get.return_value = [
            models.slims_ecephys_data.SlimsEcephysData(subject_id="12345")
        ]
        response = client.get("/slims/ecephys_sessions?subject_id=12345")
        mock_slims_api_get.assert_called_once_with(
            subject_id="12345",
            start_date_gte=None,
            end_date_lte=None,
            _request_timeout=30,
            session_name=None,
        )
        assert 200 == response.status_code

    @patch("aind_slims_service_async_client.DefaultApi.get_smartspim_imaging")
    def test_get_imaging_workflow(
        self,
        mock_slims_api_get: MagicMock,
        client: TestClient,
    ):
        """Tests a good response"""
        mock_slims_api_get.return_value = [
            models.slims_spim_data.SlimsSpimData(subject_id="12345")
        ]
        response = client.get("/slims/smartspim_imaging?subject_id=12345")
        print(mock_slims_api_get.mock_calls)
        mock_slims_api_get.assert_called_once_with(
            subject_id="12345",
            start_date_gte=None,
            end_date_lte=None,
            _request_timeout=30,
        )
        assert 200 == response.status_code

    @patch("aind_slims_service_async_client.DefaultApi.get_viral_injections")
    def test_get_viral_injections_workflow(
        self,
        mock_slims_api_get: MagicMock,
        client: TestClient,
    ):
        """Tests a good response"""
        mock_slims_api_get.return_value = [
            models.slims_viral_injection_data.SlimsViralInjectionData(
                subject_id="12345"
            )
        ]
        response = client.get("/slims/viral_injections?subject_id=12345")
        mock_slims_api_get.assert_called_once_with(
            subject_id="12345",
            start_date_gte=None,
            end_date_lte=None,
            _request_timeout=30,
        )
        assert 200 == response.status_code

    @patch(
        "aind_slims_service_async_client.DefaultApi.get_water_restriction_data"
    )
    def test_get_water_restriction_workflow(
        self,
        mock_slims_api_get: MagicMock,
        client: TestClient,
    ):
        """Tests a good response"""
        mock_slims_api_get.return_value = [
            models.slims_water_restriction_data.SlimsWaterRestrictionData(
                subject_id="12345"
            )
        ]
        response = client.get("/slims/water_restriction?subject_id=12345")
        mock_slims_api_get.assert_called_once_with(
            subject_id="12345",
            start_date_gte=None,
            end_date_lte=None,
            _request_timeout=30,
        )
        assert 200 == response.status_code

    @patch("aind_slims_service_async_client.DefaultApi.get_histology_data")
    def test_get_histology_workflow(
        self,
        mock_slims_api_get: MagicMock,
        client: TestClient,
    ):
        """Tests a good response"""
        mock_slims_api_get.return_value = [
            models.slims_histology_data.SlimsHistologyData(subject_id="12345")
        ]
        response = client.get("/slims/histology?subject_id=12345")
        mock_slims_api_get.assert_called_once_with(
            subject_id="12345",
            start_date_gte=None,
            end_date_lte=None,
            _request_timeout=30,
        )
        assert 200 == response.status_code

    @patch("aind_slims_service_async_client.DefaultApi.get_histology_data")
    def test_get_no_data(
        self,
        mock_slims_api_get: MagicMock,
        client: TestClient,
    ):
        """Tests a Not Found Response"""
        mock_slims_api_get.return_value = []
        response = client.get("/slims/histology?subject_id=12345")
        mock_slims_api_get.assert_called_once_with(
            subject_id="12345",
            start_date_gte=None,
            end_date_lte=None,
            _request_timeout=30,
        )
        assert 200 == response.status_code
        assert "No Data Found" in response.json()["message"]

    def test_non_workflow_response(
        self,
        client: TestClient,
    ):
        """Tests a non-existent workflow"""
        response = client.get("/slims/NO_WORKFLOW")
        assert 422 == response.status_code


if __name__ == "__main__":
    pytest.main([__file__])
