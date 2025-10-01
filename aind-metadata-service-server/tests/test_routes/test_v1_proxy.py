"""Test subject routes"""

from unittest.mock import AsyncMock, call

import pytest
from fastapi.testclient import TestClient


class TestV1ProxyRoute:
    """Test proxy responses."""

    def test_get_v1_funding(
        self,
        mock_proxy: AsyncMock,
        client: TestClient,
    ):
        """Tests a get request"""
        response = client.get("/funding/abc")
        mock_proxy.assert_called_once()
        assert 200 == response.status_code

    def test_get_v1_project_names(
        self,
        mock_proxy: AsyncMock,
        client: TestClient,
    ):
        """Tests a get request"""
        response = client.get("/project_names")
        mock_proxy.assert_called_once()
        assert 200 == response.status_code

    def test_get_v1_injection_materials(
        self,
        mock_proxy: AsyncMock,
        client: TestClient,
    ):
        """Tests a get request"""
        response = client.get("/tars_injection_materials/abc")
        mock_proxy.assert_called_once()
        assert 200 == response.status_code

    def test_get_v1_intended_measurements(
        self,
        mock_proxy: AsyncMock,
        client: TestClient,
    ):
        """Tests a get request"""
        response = client.get("/intended_measurements/abc")
        mock_proxy.assert_called_once()
        assert 200 == response.status_code

    def test_get_v1_mgi_allele(
        self,
        mock_proxy: AsyncMock,
        client: TestClient,
    ):
        """Tests a get request"""
        response = client.get("/mgi_allele/abc")
        mock_proxy.assert_called_once()
        assert 200 == response.status_code

    def test_get_v1_perfusions(
        self,
        mock_proxy: AsyncMock,
        client: TestClient,
    ):
        """Tests a get request"""
        response = client.get("/perfusions/abc")
        mock_proxy.assert_called_once()
        assert 200 == response.status_code

    def test_get_v1_procedures(
        self,
        mock_proxy: AsyncMock,
        client: TestClient,
    ):
        """Tests a get request"""
        response = client.get("/procedures/abc")
        mock_proxy.assert_called_once()
        assert 200 == response.status_code

    def test_get_v1_protocols(
        self,
        mock_proxy: AsyncMock,
        client: TestClient,
    ):
        """Tests a get request"""
        response = client.get("/protocols/abc")
        mock_proxy.assert_called_once()
        assert 200 == response.status_code

    def test_get_v1_rig(
        self,
        mock_proxy: AsyncMock,
        client: TestClient,
    ):
        """Tests a get request"""
        response = client.get("/rig/abc")
        mock_proxy.assert_called_once()
        assert 200 == response.status_code

    def test_get_v1_instrument(
        self,
        mock_proxy: AsyncMock,
        client: TestClient,
    ):
        """Tests a get request"""
        response = client.get("/instrument/abc")
        mock_proxy.assert_called_once()
        assert 200 == response.status_code

    def test_get_v1_bergamo_session(
        self,
        mock_proxy: AsyncMock,
        client: TestClient,
    ):
        """Tests a post request"""
        response = client.post("/bergamo_session", json={"foo": "bar"})
        mock_proxy.assert_called_once()
        assert 200 == response.status_code

    def test_get_v1_slims_workflow(
        self,
        mock_proxy: AsyncMock,
        client: TestClient,
    ):
        """Tests a get request"""
        response = client.get("/slims/histology?subject_id=abc")
        call_args = mock_proxy.call_args
        query_params = dict(call_args[0][3])

        mock_proxy.assert_called_once()
        assert 200 == response.status_code
        assert query_params == {"subject_id": "abc"}
        assert "None" not in query_params.values()

    def test_get_v1_slims_ecephys_workflow(
        self,
        mock_proxy: AsyncMock,
        client: TestClient,
    ):
        """Tests a get request"""
        response = client.get(
            "/slims/ecephys_sessions?subject_id=abc&session=def"
        )
        mock_proxy.assert_called_once()
        assert 200 == response.status_code

    def test_get_v1_subject(
        self,
        mock_proxy: AsyncMock,
        client: TestClient,
    ):
        """Tests a get request"""
        response = client.get("/subject/abc")
        mock_proxy.assert_called_once()
        assert 200 == response.status_code


if __name__ == "__main__":
    pytest.main([__file__])
