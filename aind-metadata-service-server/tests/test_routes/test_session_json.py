"""Test session_json routes"""

from unittest.mock import MagicMock, patch

import pytest
from aind_session_json_service_async_client import (
    InputSource,
    JobResponse,
    JobSettings,
)
from fastapi.testclient import TestClient


class TestRoute:
    """Test responses."""

    @patch("aind_session_json_service_async_client.DefaultApi.get_session")
    def test_get_bergamo_session(
        self,
        mock_session_json_api_get: MagicMock,
        client: TestClient,
    ):
        """Tests a good response"""
        mock_session_json_api_get.return_value = JobResponse(
            status_code=200, message="All good", data='{"abc": "def"}'
        )
        job_settings = JobSettings(
            input_source=InputSource("abc/def"),
            experimenter_full_name=["Person One"],
            subject_id="123445",
            imaging_laser_wavelength=920,
            fov_imaging_depth=200,
            fov_targeted_structure="M1",
            notes=None,
        )
        post_request_content = job_settings.model_dump(mode="json")
        response = client.post("/bergamo_session", json=post_request_content)
        assert 200 == response.status_code

    @patch("aind_session_json_service_async_client.DefaultApi.get_session")
    def test_get_bergamo_session_bad_post(
        self,
        mock_session_json_api_get: MagicMock,
        client: TestClient,
    ):
        """Tests a 422 response"""
        post_request_content = {"abc": "def"}
        response = client.post("/bergamo_session", json=post_request_content)
        mock_session_json_api_get.assert_not_called()
        assert 422 == response.status_code


if __name__ == "__main__":
    pytest.main([__file__])
