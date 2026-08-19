"""Test subject routes"""

from unittest.mock import AsyncMock

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
