"""Test index route"""

import pytest
from fastapi.testclient import TestClient

from aind_metadata_service_server import __version__ as service_version


class TestRoute:
    """Test responses."""

    def test_index(
        self,
        client: TestClient,
    ):
        """Tests a good response"""
        response = client.get("/")
        assert 200 == response.status_code
        assert "AIND Metadata Service" in response.text
        assert service_version in response.text
        assert "Subject" in response.text
        assert "Procedures" in response.text


if __name__ == "__main__":
    pytest.main([__file__])
